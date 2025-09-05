import asyncio
import logging
import os
import json
import traceback

import jwt.exceptions
import uvicorn
import orjson

from asyncpg.exceptions import UniqueViolationError, ForeignKeyViolationError, CheckViolationError
from fastapi.exceptions import RequestValidationError, ValidationError
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordBearer
from starlette.types import Message
from typing import Optional

from bracelet_lib.controllers import passwords, email, storage
from lib import config, exceptions as api_exceptions, logs
from bracelet_lib import exceptions
from bracelet_lib import models, cache
from bracelet_lib.exceptions.sentry import sentry_logger
from routes import app_router



app = FastAPI(
    title                  = "bracelet REST API",
    description            = "This is the REST API for the bracelet Project",
    version                = "0.1.0",
    default_response_class = ORJSONResponse,
    openapi_url            = '/v1/openapi.json',
    docs_url               = '/v1/docs',
    redoc_url              = '/v1/redoc'
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

app.include_router(
    app_router,
    prefix = '/v1'
)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": '%(asctime)s (%(name)s) [%(levelname)s]: %(message)s'
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        }
    },
    "loggers": {
        "api": {"handlers": ["default"], "level": "INFO"}
    },
}

# noinspection PyUnresolvedReferences
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("api")

# disable server access logs
logging.getLogger('uvicorn.access').handlers = []
logging.getLogger('uvicorn.access').propagate = False


async def http_exception(request: Optional[Request], exc) -> ORJSONResponse:
    status_code    = 500
    response_data  = {}
    headers        = {}
    exc_type       = type(exc)  # We use type() because in some exceptions we don't want to catch parents of main class

    if exc_type in (RequestValidationError, ValidationError):
        status_code    = 422
        response_data  = orjson.loads(exc.json())[0]

    elif exc_type == exceptions.ValidationError:
        status_code    = 422
        response_data  = exc.get_data()

    elif exc_type == exceptions.NotFoundError:
        status_code   = 404
        response_data = None

    elif exc_type == exceptions.DataConflictError:
        status_code   = 409
        response_data = exc.get_data()

    elif isinstance(exc, api_exceptions.AuthException):
        status_code     = 401
        response_detail = exc.msg
        headers         = exc.headers
        response_data   = { 'detail': [response_detail] }

    elif isinstance(exc, api_exceptions.OAuthException):
        status_code    = 400
        response_data  = {
            'error'  : exc.error,
            'detail' : [ exc.error_description ]
        }

    elif isinstance(exc, jwt.exceptions.ExpiredSignatureError):
        status_code     = 401
        response_detail = 'Expired token'
        headers         = { 'WWW-Authenticate' : 'Bearer' }
        response_data   = { 'detail': [response_detail] }

    elif isinstance(exc, jwt.exceptions.PyJWTError):
        status_code     = 401
        response_detail = 'Invalid token'
        headers         = { 'WWW-Authenticate' : 'Bearer' }
        response_data   = { 'detail': [response_detail] }

    elif isinstance(exc, UniqueViolationError) or isinstance(exc, CheckViolationError):
        status_code    = 409
        if isinstance(exc, UniqueViolationError):
            trans_func = exceptions.DataConflictError.translate_unique_violation
        else:
            trans_func = exceptions.DataConflictError.translate_check_violation

        translated_exc = trans_func(exc)

        if translated_exc is None:
            # noinspection PyUnresolvedReferences
            translated_exc = exceptions.DataConflictError(
                loc  = [ exc.table_name ],
                msg  = f'{exc.message}. {exc.detail}',
                type = exceptions.ErrorType.DATA_CONFLICT
            )

        response_data = translated_exc.get_data()

    elif isinstance(exc, ForeignKeyViolationError):
        status_code    = 409
        # noinspection PyUnresolvedReferences
        exc = exceptions.DataConflictError(
            loc  = [ exc.table_name ],
            msg  = f'{exc.message}. {exc.detail}',
            type = exceptions.ErrorType.DATA_CONFLICT
        )
        response_data  = exc.get_data()

    response = ORJSONResponse(response_data, status_code=status_code, headers=headers)

    if request is not None:  # This will be None while handling websockets exceptions
        log_entry = await logs.create_log_entry(request, status_code=status_code, app_version=app.version)

        logger.error(log_entry.json(by_alias=True))

        # noinspection PyTypeChecker
        if status_code in (422, 500, 409) or config.settings.sentry_debug:
            response_json = json.dumps(response_data, indent=2)
            tb_str        = traceback.format_exception(exc)

            logger.error( f'Response: {response_json}' )
            logger.error( ''.join(tb_str) )

            # log to sentry (non blocking)
            asyncio.ensure_future(
                sentry_logger.log(
                    error        = exc,
                    action       = api_exceptions.get_sentry_log_action(error_code=status_code),
                    request_info = {
                        **log_entry.dict(by_alias=True),
                        'response' : response_data,
                        'headers'  : request.headers
                    }
                )
            )

    else:
        response_json = orjson.dumps(response_data)  # This is used to handle more special types, datetime, for instance
        response_json = json.dumps( orjson.loads(response_json), indent=2 )  # Nice formatting
        tb_str        = traceback.format_exception(exc)

        logger.error( f'Response: {response_json}' )
        logger.error( ''.join(tb_str) )

    return response


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request, exc) -> ORJSONResponse:
    return await http_exception(request, exc)


async def set_body(request: Request, body: bytes):
    async def receive() -> Message:
        return {"type": "http.request", "body": body}

    request._receive = receive

@app.on_event("startup")
async def startup():
    # Init db connection
    models.database_manager.init(config.settings.test_db_url or config.settings.db_url)
    await models.database_manager.open()

    # Init redis connection
    await cache.cache.init(redis_url=config.settings.redis_url)

    main_api_dir = os.path.dirname(os.path.abspath(__file__))

    # Configure email server
    email.email_ctrl.init(
        email_smtp_hostname  = config.settings.email_smtp_hostname,
        email_smtp_port      = config.settings.email_smtp_port,
        email_from_real_name = config.settings.email_from_real_name,
        email_from_email     = config.settings.email_from_email,
        email_user_account   = config.settings.email_user_account,
        email_password       = config.settings.email_password,
        email_enable_ssl     = config.settings.email_enable_ssl,
        email_enable_tls     = config.settings.email_enable_tls,
        email_template_dir   = f'{main_api_dir}/templates'
    )

    # Configure storage controller
    storage.blob_storage_ctrl.init(
        s3_access_key_id     = config.settings.s3_access_key_id,
        s3_secret_access_key = config.settings.s3_secret_access_key,
        s3_region            = config.settings.s3_region,
        s3_bucket            = config.settings.s3_bucket,
        s3_ttl               = config.settings.s3_ttl
    )

    # Configure password controller
    passwords.password_ctrl.init(
        jwt_secret_key                      = config.settings.jwt_secret_key,
        jwt_algorithm                       = config.settings.jwt_algorithm,
        jwt_access_token_expire_minutes     = config.settings.jwt_access_token_expire_minutes,
        jwt_refresh_token_expire_minutes    = config.settings.jwt_refresh_token_expire_minutes,
        login_max_attempts_until_block      = config.settings.login_max_attempts_until_block,
        login_attempts_ttl_minutes          = config.settings.login_attempts_ttl_minutes,
        account_block_duration_hours        = config.settings.account_block_duration_hours,
        new_account_token_expire_minutes    = config.settings.new_account_token_expire_minutes,
        unlock_account_token_expire_minutes = config.settings.unlock_account_token_expire_minutes,
        reset_password_token_expire_minutes = config.settings.reset_password_token_expire_minutes
    )

    # Configure sentry logger
    sentry_logger.init(
        sentry_dsn  = config.settings.sentry_dsn,
        app_version = app.version,
        app_name    = 'bracelet-api',
        app_debug   = config.settings.sentry_debug
    )


@app.on_event("shutdown")
async def shutdown():
    # noinspection PyUnresolvedReferences
    await models.database_manager.close()


@app.middleware("http")
async def logs_interceptor(request: Request, call_next):
    try:
        body = await request.body()
        await set_body(request, body)
        response  = await call_next(request)
        log_entry = await logs.create_log_entry(request, status_code=response.status_code, app_version=app.version)

        logger.info(log_entry.json(by_alias=True))

        return response

    except Exception as exc:
        return await http_exception(request, exc)


if __name__ == '__main__':
    env_port = os.environ.get('API_PORT')
    port     = int(env_port) if env_port else 8000

    uvicorn.run('main:app', host='0.0.0.0', port=port, lifespan="on", reload=True)

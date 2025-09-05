from typing import Optional

from fastapi import Depends, APIRouter, Response, Query
from fastapi.params import Form
from starlette.status import HTTP_204_NO_CONTENT

from controllers.oauth import OauthCtrl
from lib import exceptions
from models.oauth import OAuthTokenRevoke, OAuthTokenResponse, GrantTypeEnum, ScopeEnum
from routes.common import HTTPResponses
from bracelet_lib.controllers.passwords import password_ctrl

router = APIRouter()


class OAuth2PasswordRequestForm:
    def __init__(
            self,
            grant_type : str = Form(
                ...,
                regex       = f"{'|'.join(GrantTypeEnum.values())}",
                description = f"Available values: {', '.join(GrantTypeEnum.values())}"
            ),
            username : str           = Form(None),
            password : str           = Form(None),
            scope    : Optional[str] = Form(
                'full',
                regex       = f"{'|'.join(ScopeEnum.values())}",
                description = f"Available values: {', '.join(ScopeEnum.values())}"
            ),
            client_id     : Optional[str] = Form(None),
            client_secret : Optional[str] = Form(None),
            refresh_token : Optional[str] = Form(None)
    ):
        self.grant_type    = grant_type
        self.username      = username
        self.password      = password
        self.scope         = scope
        self.client_id     = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token


@router.post(
    '/oauth/token',
    response_model       = OAuthTokenResponse,
    summary              = 'Create or refresh auth token using oauth 2.0 standard',
    description          = 'Use this with the resource owner password flow to create new tokens or update them',
    response_description = 'Token created or refreshed successfully',
    responses            = {**HTTPResponses.post}
)
async def oauth_token(form_data: OAuth2PasswordRequestForm = Depends()):
    tokens = None

    if form_data.grant_type == GrantTypeEnum.password and form_data.username and form_data.password:
        tokens = await OauthCtrl.create_token(
            username = form_data.username,
            password = form_data.password,
            scope    = form_data.scope
        )

    if form_data.grant_type == GrantTypeEnum.refresh_token and form_data.refresh_token:
        tokens = await OauthCtrl.create_token(
            refresh_token = form_data.refresh_token
        )

    if tokens:
        return OAuthTokenResponse(**tokens)

    raise exceptions.AuthException()


@router.post(
    '/oauth/revoke',
    summary              = 'Revoke refresh token',
    description          = "Use this to revoke a refresh token that has not expired yet",
    response_description = 'Token revoked successfully',
    status_code          = HTTP_204_NO_CONTENT,
    responses            = {**HTTPResponses.post},
    response_class       = Response
)
async def oauth_token_revoke(token: OAuthTokenRevoke):
    await OauthCtrl.revoke_token(token.token)


@router.get(
    '/oauth/check',
    response_model_exclude_unset = True,
    summary                      = 'Check security token',
    description                  = 'Allows to check security token generated for actions as register or edit password',
    response_description         = 'Security token valid',
    status_code                  = HTTP_204_NO_CONTENT,
    responses                    = {**HTTPResponses.get},
    response_class               = Response
)
async def check_token(
        token : str = Query(..., description='Security token')
):
    await password_ctrl.check_security_token(token=token)

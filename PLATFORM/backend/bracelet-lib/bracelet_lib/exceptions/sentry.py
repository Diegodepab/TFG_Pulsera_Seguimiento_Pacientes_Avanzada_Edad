import asyncio
import concurrent.futures
import platform
import socket
from enum import Enum
from typing import Dict

import sentry_sdk


class SentryLogLevel(str, Enum):
    FATAL   = 'fatal'
    ERROR   = 'error'
    WARNING = 'warning'
    INFO    = 'info'
    DEBUG   = 'debug'


class SentryLogAction:

    def __init__(
            self,
            report : bool            = True,
            level  : SentryLogLevel  = SentryLogLevel.ERROR
    ):
        self.report = report
        self.level  = level


class SentryLogger:

    def __init__(self):
        self._executor  = concurrent.futures.ThreadPoolExecutor(max_workers=20)
        self._app_debug = False
        self.__init     = False

    def init(
            self,
            sentry_dsn  : str,
            app_version : str,
            app_name    : str,
            app_debug   : bool = False
    ):
        # init sentry client
        sentry_sdk.init(
            sentry_dsn,
            traces_sample_rate   = 1.0,
            default_integrations = False,
            release              = app_version
        )

        # configure global scope
        with sentry_sdk.configure_scope() as scope:
            scope.set_level(SentryLogLevel.ERROR)
            scope.set_tag('logger', app_name)
            scope.set_user({
                'ip_address': socket.gethostbyname(socket.gethostname())
            })
            scope.set_extra('device', {
                'name'   : socket.gethostname(),
                'system' : platform.system()
            })

        self._app_debug = app_debug
        self.__init     = True

    # noinspection PyDefaultArgument
    def _report_error(
            self,
            error        : Exception,
            action       : SentryLogAction,
            request_info : Dict = {},
            user_info    : Dict = {},
            extra_config : Dict = {},
    ):
        if action and action.report and not self._app_debug:

            # create push scope
            with sentry_sdk.push_scope() as scope:
                scope.set_level( action.level if action else SentryLogLevel.ERROR )
                if request_info:
                    scope.set_context('request', request_info)
                if user_info:
                    scope.set_user(user_info)
                if extra_config:
                    scope.set_extra('configuration', extra_config)

                # report error
                event_id = sentry_sdk.capture_exception(error)
                if event_id:
                    print(f'Success sentry log! Event ID: {event_id}')

    # noinspection PyDefaultArgument
    async def log(
            self,
            error        : Exception,
            action       : SentryLogAction,
            request_info : Dict = {},
            user_info    : Dict = {},
            extra_config : Dict = {},
    ):
        assert self.__init, "You need to init() sentry logger first"

        args = [ error, action, request_info, user_info, extra_config ]
        loop = asyncio.get_event_loop()
        await asyncio.wait(fs=[loop.run_in_executor(self._executor, self._report_error, *args)])


sentry_logger = SentryLogger()

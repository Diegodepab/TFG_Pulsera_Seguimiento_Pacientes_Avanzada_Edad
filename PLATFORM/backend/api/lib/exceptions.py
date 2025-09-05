from antlr4.error import ErrorListener

from bracelet_lib.exceptions import ValidationError, ErrorType
from bracelet_lib.exceptions.sentry import SentryLogLevel, SentryLogAction


class ParserErrorListener(ErrorListener.ErrorListener):
    # noinspection PyInitNewSignature
    def __init__(self, parser: str, msg: str):
        super().__init__()
        self.parser = parser
        self.msg    = msg

    # noinspection PyPep8Naming
    def syntaxError(self, recognizer, offending_symbol, line, column, msg, e):
        raise ValidationError(
            loc  = [ 'query',  self.parser ],
            msg  = f'{self.msg}. {msg.capitalize()}',
            type = ErrorType.QUERY_PARSER_ERROR
        )


class OAuthException(Exception):
    """
    Creates a object to directly return that is compatible as return body of the OAuth2 specification
    https://tools.ietf.org/html/rfc6749#section-5.2
    This is used to report internal problems during the oauth process,
    for invalid data from the user use AuthException
    """
    def __init__(
            self,
            error             : str = 'invalid_request',
            error_description : str = 'Invalid body'
    ):
        super().__init__()
        self.error             = error
        self.error_description = error_description


class AuthException(Exception):
    """
    This class is used to return authentication or authorization errors,
    like 'invalid credentials' or 'Not enough permissions'
    """
    def __init__(
            self,
            msg         : str = 'Invalid credentials',
            auth_header : str = 'Bearer'
    ):
        super().__init__()
        self.msg     = msg
        self.headers = { 'WWW-Authenticate' : auth_header }


def get_sentry_log_action(error_code: int) -> SentryLogAction:
    report = False
    level = SentryLogLevel.INFO

    if error_code == 409:
        report = True
        level  = SentryLogLevel.ERROR

    elif error_code == 500:
        report = True
        level  = SentryLogLevel.ERROR

    return SentryLogAction(report=report, level=level)

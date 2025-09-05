import typing
from enum import Enum
from asyncpg import UniqueViolationError, CheckViolationError

class ErrorType(Enum):
    BAD_REQUEST         = 1
    DATA_CONFLICT       = 2
    QUERY_PARSER_ERROR  = 3

    # Users custom messages
    USER_EMAIL_DUPLICATED           = 1000
    USER_ALREADY_ACTIVATED          = 1001
    # USER_DISABLED                 = 1002
    # USER_ALREADY_DELETED          = 1003

    #Patient custom messages
    PATIENT_DUPLICATED = 2000

    # Login custom messages
    LOGIN_INVALID_CREDENTIALS              = 1004
    LOGIN_INVALID_CREDENTIALS_USER_BLOCKED = 1005

    def error_msg(self) -> str:
        error_codes: typing.Dict[int, str] = {
            self.USER_EMAIL_DUPLICATED.value:
                'The email used for the user is duplicated, please change it',
            self.USER_ALREADY_ACTIVATED.value:
                'This user is already activated',
            # self.USER_ALREADY_DELETED.value:
            #     'This user is already disabled',
            # self.USER_DISABLED.value:
            #     'This user is disabled'
            self.PATIENT_DUPLICATED.value:
                'The patient is duplicated',

            self.LOGIN_INVALID_CREDENTIALS.value:
                'Invalid credentials to login',
            self.LOGIN_INVALID_CREDENTIALS_USER_BLOCKED.value:
                'The user was blocked due to several login attempts. Email sent.'
        }

        return error_codes[self.value]

    def user_text(self) -> str:
        return str(self.name).capitalize().replace('_', ' ')


class ValidationError(Exception):
    # noinspection PyDefaultArgument
    def __init__(
            self,
            loc   : typing.List  = [],
            msg   : str          = "",
            type  : ErrorType    = ...,
            extra : typing.Dict = {}
    ):
        super().__init__()
        self.loc  = loc
        self.msg  = msg   # This can be empty for specific subtypes, those available at error_codes dict.
        self.type = type
        self.extra = extra  # Used to store extra data to send to the caller, only sent in some cases

    def get_data(self) -> typing.Dict:
        return {
            'loc'  : self.loc,
            'type' : self.type.user_text(),
            'code' : self.type.value,
            'msg'  : self.msg or self.type.error_msg(),
            'extra' : self.extra
        }


class DataConflictError(ValidationError):
    # noinspection PyDefaultArgument
    def __init__(
            self,
            loc   : typing.List  = [],
            msg   : str          = "",
            type  : ErrorType    = ErrorType.DATA_CONFLICT,
            extra : typing.Dict = {}
    ):
        super().__init__(loc, msg, type, extra)

    # noinspection PyUnresolvedReferences
    @staticmethod
    def translate_unique_violation(exc: UniqueViolationError) -> typing.Optional['DataConflictError']:
        unique_exc_map = {
            'user_account_email_key': ErrorType.USER_EMAIL_DUPLICATED,
            'patient_code_key': ErrorType.PATIENT_DUPLICATED
        }

        tbl_name = exc.table_name
        full_msg = f'{exc.message}. {exc.detail}'

        for constraint_name in unique_exc_map.keys():
            if constraint_name in full_msg:
                return DataConflictError(
                    loc  = [ tbl_name ],
                    type = unique_exc_map[constraint_name]
                )


class NotFoundError(Exception): pass


class EmailException(Exception):
    """
    This class si used to return connection or authentication errors
    to email server
    """
    def __init__(
            self,
            error             : str = 'email_host_error',
            error_description : str = 'Error when try to connect to smtp host'
    ):
        super().__init__()
        self.error             = error
        self.error_description = error_description

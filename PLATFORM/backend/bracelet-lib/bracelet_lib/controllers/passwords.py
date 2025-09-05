from datetime import datetime, timedelta
from typing import Dict, Optional

import jwt
import orjson

from enum import Enum
# noinspection PyCompatibility
from .. import exceptions
from ..cache import cache
from ..models.users import UserAccount


class TokenType(Enum):
    ACCESS             = 1
    REFRESH            = 2
    RESET_PASSWORD     = 2
    NEW_ACCOUNT_TOKEN  = 3


class PasswordsCtrl:

    # noinspection PyTypeChecker
    def __init__(self):
        self.jwt_secret_key                         : str = None
        self.jwt_algorithm                          : str = None
        self.jwt_access_token_expire_minutes        : int = None
        self.jwt_refresh_token_expire_minutes       : int = None
        self.login_max_attempts_until_block         : int = None
        self.login_attempts_ttl_minutes             : int = None
        self.account_block_duration_hours           : int = None
        self.reset_password_token_expire_minutes    : int = None
        self.unlock_account_token_expire_minutes    : int = None
        self.new_account_token_expire_minutes       : int = None

    def init(
            self,
            jwt_secret_key                         : str,
            jwt_algorithm                          : str = 'HS256',
            jwt_access_token_expire_minutes        : int = 30,
            jwt_refresh_token_expire_minutes       : int = 24*60,
            login_max_attempts_until_block         : int = 10,
            login_attempts_ttl_minutes             : int = 60*5,
            account_block_duration_hours           : int = 24,
            reset_password_token_expire_minutes    : int = 24*60,
            unlock_account_token_expire_minutes    : int = 24*60,
            new_account_token_expire_minutes       : int = 48*60
    ):
        self.jwt_secret_key                         = jwt_secret_key
        self.jwt_algorithm                          = jwt_algorithm
        self.jwt_access_token_expire_minutes        = jwt_access_token_expire_minutes
        self.jwt_refresh_token_expire_minutes       = jwt_refresh_token_expire_minutes
        self.login_max_attempts_until_block         = login_max_attempts_until_block
        self.login_attempts_ttl_minutes             = login_attempts_ttl_minutes
        self.account_block_duration_hours           = account_block_duration_hours
        self.reset_password_token_expire_minutes    = reset_password_token_expire_minutes
        self.unlock_account_token_expire_minutes    = unlock_account_token_expire_minutes
        self.new_account_token_expire_minutes       = new_account_token_expire_minutes

    @property
    def is_configured(self):
        return self.jwt_secret_key is not None

    def check_configured(self):
        if not self.is_configured:
            raise Exception('Password controller is not initialized')

    def create_token(
            self,
            token_type   : TokenType,
            user_id      : int,
            role         : str = '',
            extra_fields : Optional[Dict] = None,
            expiry_ts    : Optional[datetime] = None
    ):
        self.check_configured()

        if expiry_ts is None:
            expire_minutes = 0
            if token_type == TokenType.ACCESS:
                expire_minutes = self.jwt_access_token_expire_minutes
            elif token_type == TokenType.REFRESH:
                expire_minutes = self.jwt_refresh_token_expire_minutes
            elif token_type == TokenType.RESET_PASSWORD:
                expire_minutes = self.reset_password_token_expire_minutes
            elif token_type == TokenType.NEW_ACCOUNT_TOKEN:
                expire_minutes = self.new_account_token_expire_minutes

            expiry_ts = datetime.utcnow() + timedelta(minutes=expire_minutes)

        data = {
            'sub'  : user_id,
            'iss'  : 'https://bracelet.com',
            'exp'  : expiry_ts,
            'role' : role
        }

        if extra_fields is not None:
            data.update( extra_fields )

        return self.encode_token(data)

    def encode_token(self, data: Dict):
        return jwt.encode(data, self.jwt_secret_key, algorithm=self.jwt_algorithm)

    def get_redis_refresh_token_info(self, token: str, stringify: bool = True) -> Dict:
        self.check_configured()

        payload = jwt.decode(token, self.jwt_secret_key, algorithms=[self.jwt_algorithm])

        return {
            "key" : f"token-{payload.get('sub')}-exp-{payload.get('exp')}",
            "data": orjson.dumps(payload) if stringify else payload
        }

    async def check_security_token(self, token: str):
        security_token_redis_info  = self.get_redis_refresh_token_info(token, stringify=False)

        if not await cache.get(security_token_redis_info['key']):
            raise exceptions.DataConflictError(
                loc=['query', 'token'],
                msg='Invalid token'
            )

    async def edit_user_password(self, security_token: str, new_password: str) -> UserAccount:
        from ..controllers.users import UserAccountCtrl

        security_token_redis_info = self.get_redis_refresh_token_info(security_token, stringify=False)

        user = await UserAccountCtrl.edit_password(
            user_id      = security_token_redis_info['data']['sub'],
            new_password = new_password
        )

        await cache.delete(security_token_redis_info['key'])
        return user


password_ctrl = PasswordsCtrl()

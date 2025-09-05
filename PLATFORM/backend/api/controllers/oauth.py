from typing import Dict

from bracelet_lib.controllers.passwords import password_ctrl, TokenType
from lib import exceptions, config
from models.oauth import ScopeEnum

from bracelet_lib.cache import cache
from bracelet_lib.controllers.users import UserAccountCtrl
from bracelet_lib.models.users import UserStatusNameEnum


class OauthCtrl:
    """
    This is a special controller because it's used to validate and generate tokens
    """

    def __init__(self):
        pass

    @classmethod
    async def create_token(
            cls,
            username      : str = None,
            password      : str = None,
            scope         : str = None,
            refresh_token : str = None
    ) -> Dict:
        current_refresh_token_redis = None
        token_expiry_ts             = None
        create_refresh_token        = True    # Not used for guest tokens

        if username and password:
            if scope == ScopeEnum.full:
                user_login = await UserAccountCtrl.get_user_login(username, password)

                if not user_login:
                    raise exceptions.AuthException()

                user_id   = user_login.id
                user_role = user_login.user_role_name

            else:
                raise exceptions.AuthException()

        elif refresh_token:
            current_refresh_token_redis = password_ctrl.get_redis_refresh_token_info(refresh_token, stringify=False)

            if not await cache.get(current_refresh_token_redis['key']):
                raise exceptions.AuthException()

            user_id   = current_refresh_token_redis['data']['sub']
            user_role = current_refresh_token_redis['data']['role']

            user = await UserAccountCtrl.get(user_id)
            if user is None or user.user_status_name != UserStatusNameEnum.ACTIVE:
                raise exceptions.AuthException()

        else:
            raise exceptions.AuthException()

        access_token = password_ctrl.create_token(
            TokenType.ACCESS,
            user_id,
            role      = user_role,
            expiry_ts = token_expiry_ts
        )

        refresh_token = None
        if create_refresh_token:
            refresh_token       = password_ctrl.create_token(TokenType.REFRESH, user_id, role=user_role)
            refresh_token_redis = password_ctrl.get_redis_refresh_token_info(refresh_token)

            await cache.set(
                refresh_token_redis['key'],
                refresh_token_redis['data'],
                config.settings.jwt_refresh_token_expire_minutes * 60
            )

            if current_refresh_token_redis:
                await cache.delete(current_refresh_token_redis['key'])

        tokens  = {
            'access_token'  : access_token,
            'refresh_token' : refresh_token,
            'expires_in'    : config.settings.jwt_access_token_expire_minutes * 60,
            'token_type'    : 'Bearer'
        }

        return tokens

    @classmethod
    async def revoke_token(cls, token):
        refresh_token_redis = password_ctrl.get_redis_refresh_token_info(token)
        await cache.delete(refresh_token_redis['key'])

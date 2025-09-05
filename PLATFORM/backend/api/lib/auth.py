import jwt
import functools
import typing

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, HTTPBasic, HTTPBasicCredentials

from lib import config, exceptions


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/oauth/token", auto_error=False)
basic_scheme  = HTTPBasic(auto_error=False)


async def check_user_authenticated( token: str = Depends(oauth2_scheme) ) -> typing.Dict[str, typing.Union[str, int]]:
    """
    Function to check if a JWT token is valid
    :param token: the JWT token, this will be decoded and check for validity
    :return: user_id of the decoded token
    """
    print(f"DEBUG AUTH: check_user_authenticated called")
    print(f"DEBUG AUTH: token present: {token is not None}")
    print(f"DEBUG AUTH: token length: {len(token) if token else 0}")
    
    if token is None:
        print(f"DEBUG AUTH: No token present - raising AuthException")
        raise exceptions.AuthException( msg='Token not present' )

    try:
        payload   = jwt.decode(token, config.settings.jwt_secret_key, algorithms=[config.settings.jwt_algorithm])
        user_id   = payload.get("sub")
        user_role = payload.get("role")
        
        print(f"DEBUG AUTH: Token decoded successfully")
        print(f"DEBUG AUTH: user_id: {user_id}, user_role: {user_role}")

        if not user_id or not user_role:
            print(f"DEBUG AUTH: Invalid token payload - missing user_id or user_role")
            raise exceptions.AuthException( msg='Invalid token' )
        
        print(f"DEBUG AUTH: Authentication successful for user {user_id} with role {user_role}")
        return {
            'user_id'   : int(user_id),
            'user_role' : user_role
        }
    
    except jwt.ExpiredSignatureError:
        print(f"DEBUG AUTH: Token expired")
        raise exceptions.AuthException( msg='Token expired' )
    except jwt.InvalidTokenError as e:
        print(f"DEBUG AUTH: Invalid token: {e}")
        raise exceptions.AuthException( msg='Invalid token' )
    except Exception as e:
        print(f"DEBUG AUTH: Unexpected error: {e}")
        raise exceptions.AuthException( msg='Authentication failed' )

    return {
        'user_id'   : int(user_id),
        'user_role' : user_role
    }


async def check_client_authenticated(
        credentials : HTTPBasicCredentials = Depends(basic_scheme)
) -> typing.Optional[str]:
    """
    Function to authenticate the request using Basic Auth
    :param credentials: are injected using "Depends" system
    :return:
    """
    if credentials is None:
        return

    found = False

    for client_id, secret in config.settings.clients.items():
        if credentials.username == client_id and credentials.password == secret:
            found = True
            break

    return credentials.username if found else None

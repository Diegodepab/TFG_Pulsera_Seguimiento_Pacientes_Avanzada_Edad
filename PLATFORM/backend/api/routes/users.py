from typing import Dict, Union
from fastapi import APIRouter, Depends, Path, Response, Query, Body
from pydantic import EmailStr
from starlette.requests import Request
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from controllers.bracelet_ctrl_proxy import braceletCtrlProxy
from bracelet_lib.controllers.passwords import password_ctrl, TokenType
from bracelet_lib.controllers.users import UserAccountCtrl, PermissionCtrl

from controllers.oauth import OauthCtrl
from lib import auth, config, exceptions as lib_exceptions
from bracelet_lib import exceptions
from models.oauth import OAuthTokenResponse
from bracelet_lib.controllers.users import UserRoleCtrl

from bracelet_lib.models.query_builder import QueryBuilder
from bracelet_lib.models.users import UserAccount, UserRole, UserStatusNameEnum, Permission

from bracelet_lib.models.common import StrEnum

from routes.common import HTTPResponses, BasicQueryParams, FieldsQueryParam, build_embed_query_param

router = APIRouter()


class UserEmbedEnum(StrEnum):
    patients = 'patients'


@router.get(
    '/users/allowed-roles',
    response_model               = UserRole.SearchValidator,
    response_model_exclude_unset = True,
    summary                      = 'Get allowed user roles per role',
    description                  = 'Allows to perform users roles search allowed by role',
    response_description         = 'User roles list allowed per role',
    responses                    = {**HTTPResponses.search}
)
async def search_user_roles(
        request        : Request,
        query_params   : BasicQueryParams           = Depends(BasicQueryParams),
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = query_params.get_dict()

    builder: QueryBuilder = UserRoleCtrl.get_allowed_users_role_builder(auth_user_info['user_role'])
    return await braceletCtrlProxy.search(UserRoleCtrl, request, builder=builder, **options)


@router.get(
    '/users',
    response_model               = UserAccount.SearchValidator,
    response_model_exclude_unset = True,
    summary                      = 'Search users',
    description                  = 'Allows to perform users search',
    response_description         = 'Users list',
    responses                    = {**HTTPResponses.search}
)
async def search_users(
        request           : Request,
        query_params      : BasicQueryParams           = Depends(BasicQueryParams),
        embed             : str                        = Depends(build_embed_query_param(UserEmbedEnum)),
        auth_user_info    : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated),
        fts               : str                        = Query(
            None,
            description = 'Texto para usar en la búsqueda Full Text Search.',
            example     = 'user@example.com Michael'
        )
):
    options                   = query_params.get_dict()
    options['embed']          = embed
    options['auth_user_info'] = auth_user_info
    options['extra_args']     = {
        'fts': fts
    }

    return await braceletCtrlProxy.search(UserAccountCtrl, request, **options)


@router.get(
    '/users/{user_account_id}',
    response_model               = UserAccount.FullValidator,
    response_model_exclude_unset = True,
    summary                      = 'Get user',
    description                  = 'Returns a user record based on their ID',
    response_description         = 'User record',
    responses                    = {**HTTPResponses.get}
)
async def get_user(
        user_account_id : int                        = Path(..., description='User ID'),
        embed           : str                        = Depends(build_embed_query_param(UserEmbedEnum)),
        fields          : FieldsQueryParam           = Depends(FieldsQueryParam),
        auth_user_info  : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {
        'embed'          : embed,
        'auth_user_info' : auth_user_info
    }

    return await braceletCtrlProxy.get(UserAccountCtrl, user_account_id, fields.fields, **options)


@router.delete(
    '/users/{user_account_id}',
    summary              = 'Delete user',
    description          = 'Allows to perform delete a user record',
    response_description = 'Empty',
    status_code          = HTTP_204_NO_CONTENT,
    responses            = {**HTTPResponses.delete},
    response_class       = Response
)
async def delete_user(
        user_account_id : int                        = Path(..., description='User ID to delete'),
        auth_user_info  : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {
        'auth_user_info': auth_user_info
    }
    
    await braceletCtrlProxy.delete(UserAccountCtrl, user_account_id, **options)


@router.put(
    '/users/{user_account_id}',
    summary              = 'Update user',
    description          = 'Allows to perform full update a user record',
    response_description = 'Empty',
    status_code          = HTTP_204_NO_CONTENT,
    responses            = {**HTTPResponses.put},
    response_class       = Response
)
async def put_user(
        user_account_in     : UserAccount.UpdateValidator,
        user_account_id     : int = Path(..., description='User ID to update'),
        auth_user_info      : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {
        'auth_user_info': auth_user_info
    }

    await UserAccountCtrl.check_valid_changes(auth_user_info['user_id'], auth_user_info['user_role'], user_account_in)

    # noinspection PyTypeChecker
    await braceletCtrlProxy.update(UserAccountCtrl, user_account_id, user_account_in, validate=False, **options)


@router.put(
    '/users/{user_id}/password',
    summary              = 'Change user account password',
    description          = 'Allow to change user account password',
    response_description = 'Empty',
    status_code          = HTTP_204_NO_CONTENT,
    responses            = {**HTTPResponses.put},
    response_class       = Response
)
async def put_change_user_password(
        password_in    : UserAccount.UserAccountChangePassword,
        user_id        : int                                   = Path(..., description='User ID to change password'),
        auth_user_info : Dict[str, Union[str, int]]            = Depends(auth.check_user_authenticated)
):
    # We also check permissions with this
    await braceletCtrlProxy.get(UserAccountCtrl, user_id, auth_user_info=auth_user_info)

    await UserAccountCtrl.change_password(user_id, password_in.old_password, password_in.new_password)


@router.post(
    '/users',
    response_model       = UserAccount.FullValidator,
    summary              = 'Create user',
    description          = 'Allows to perform create new user',
    response_description = 'Record created',
    status_code          = HTTP_201_CREATED,
    responses            = {**HTTPResponses.post}
)
async def post_user(
        user_account_in : UserAccount.CreateValidator,
        auth_user_info  : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    # We check this here because in the validator is not a good idea, it breaks the seed for example
    if user_account_in.user_status_name not in (None, 'pending'):
        raise exceptions.ValidationError(
            loc  = ['body', 'user_status_name'],
            msg  = f"Invalid user_status_name, should be 'pending' at creation time",
            type = exceptions.ErrorType.BAD_REQUEST
        )

    # noinspection PyTypeChecker
    user: UserAccount.FullValidator = await braceletCtrlProxy.create(
        UserAccountCtrl,
        user_account_in,
        validate       = False,
        auth_user_info = auth_user_info
    )

    await UserAccountCtrl.send_token_operations_email(
        user_email   = user.email,
        redirect_url = config.settings.activate_account_redirect_url,
        token_type   = TokenType.NEW_ACCOUNT_TOKEN
    )

    return user


@router.patch(
    '/users/{user_account_id}',
    response_model       = UserAccount.FullValidator,
    summary              = 'Partial update user',
    description          = 'Allows to perform partial update of a user record',
    response_description = 'Record updated',
    responses            = {**HTTPResponses.put}
)
async def patch_user(
        user_account_in     : UserAccount.MergeValidator,
        user_account_id     : int                         = Path(..., description='User ID to update'),
        auth_user_info      : Dict[str, Union[str, int]]  = Depends(auth.check_user_authenticated)
):
    user_account_in.id = user_account_id
    await UserAccountCtrl.check_valid_changes(
        auth_user_info[ 'user_id' ],
        auth_user_info[ 'user_role' ],
        user_account_in
    )

    return await braceletCtrlProxy.merge(
        UserAccountCtrl,
        id             = user_account_id,
        data           = user_account_in,
        validate       = False,
        auth_user_info = auth_user_info
    )


@router.post(
    '/users/{user_account_id}/activate',
    response_model       = UserAccount.FullValidator,
    summary              = 'Final step on user creation, activation',
    description          = 'Activate the user after checking the token',
    response_description = 'Activated user',
    responses            = {**HTTPResponses.post}
)
async def activate_user(
        user_activate_in : UserAccount.UserAccountActivate,
        user_account_id  : int                              = Path(..., description='User ID to activate'),
        token            : OAuthTokenResponse               = Depends(auth.oauth2_scheme),
        auth_user_info   : Dict[str, Union[str, int]]       = Depends(auth.check_user_authenticated)
):
    if auth_user_info['user_id'] != user_account_id:
        raise lib_exceptions.AuthException(msg='Not enough permissions to use this resource')

    user : UserAccount = await UserAccountCtrl.get(user_account_id)
    if user.user_status_name == UserStatusNameEnum.ACTIVE:
        raise exceptions.DataConflictError(
            loc  = [ 'path', 'user_account_id' ],
            type = exceptions.ErrorType.USER_ALREADY_ACTIVATED
        )

    data = user_activate_in.dict()
    data['user_status_name'] = UserStatusNameEnum.ACTIVE

    user = await braceletCtrlProxy.merge(
        ctrl           = UserAccountCtrl,
        id             = user_account_id,
        data           = data,
        auth_user_info = auth_user_info
    )

    await OauthCtrl.revoke_token(token)

    return user


# @router.post(
#     '/users/{user_account_id}/delete-account',
#     response_model       = UserAccount.MergeValidator,
#     summary              = 'Alternative final step on user creation, deletion',
#     description          = 'Delete the user after checking the token',
#     response_description = 'Delete user',
#     responses            = {**HTTPResponses.post}
# )
# async def deletion_user(
#         user_account_id    : int                        = Path(..., description='User ID to deletion'),
#         token_str          : OAuthTokenResponse         = Depends(auth.oauth2_scheme),
#         auth_user_info     : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
# ):
#     # We also check permissions with this
#     await braceletCtrlProxy.get(
#         UserAccountCtrl,
#         user_account_id,
#         auth_user_info = auth_user_info
#     )
#
#     user = await UserAccountCtrl.delete_account(
#         user_id      = user_account_id,
#         auth_user_id = auth_user_info.get("user_id"),
#     )
#
#     await OauthCtrl.revoke_token(token_str)


@router.get(
    '/password/reset',
    summary              = 'Reset password',
    description          = 'Send email to allow user reset password',
    response_description = 'Empty',
    status_code          = HTTP_204_NO_CONTENT,
    responses            = {**HTTPResponses.get},
    response_class       = Response
)
async def send_reset_password_email(
        email : EmailStr = Query(..., description='User email')
):
    current_user = await UserAccountCtrl.get(
        id         = email,
        field_name = 'email',
        fields_map = { 'user_status_name': True }
    )

    # This specific status change needs to send an email
    if current_user.user_status_name in [ UserStatusNameEnum.PENDING, UserStatusNameEnum.INACTIVE ]:
        raise exceptions.NotFoundError()

    await UserAccountCtrl.send_token_operations_email(
        user_email   = email,
        redirect_url = config.settings.edit_password_redirect_url,
        token_type   = TokenType.RESET_PASSWORD
    )


@router.post(
    '/password/edit',
    response_model       = UserAccount.FullValidator,
    summary              = 'Edit user account password',
    description          = 'Allow to change user account password',
    response_description = 'Password changed successfully',
    status_code          = HTTP_201_CREATED,
    responses            = {**HTTPResponses.post}
)
async def edit_password(
        token       : str                                 = Query(..., description='Security token'),
        password_in : UserAccount.UserAccountEditPassword = Body(...)
):
    user = await password_ctrl.edit_user_password(security_token=token, new_password=password_in.password)
    return UserAccount.FullValidator.from_model(user)


@router.get(
    '/permissions',
    response_model               = Permission.SearchValidator,
    response_model_exclude_unset = True,
    summary                      = 'Search permissions',
    description                  = 'Allows to perform permissions search',
    response_description         = 'Permissions list',
    responses                    = {**HTTPResponses.search}
)
async def search_permissions(
        request        : Request,
        query_params   : BasicQueryParams           = Depends(BasicQueryParams),
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options                   = query_params.get_dict()
    options['auth_user_info'] = auth_user_info
    options['extra_args']     = {
        "user_id": auth_user_info['user_id']
    }

    return await braceletCtrlProxy.search(PermissionCtrl, request, **options)

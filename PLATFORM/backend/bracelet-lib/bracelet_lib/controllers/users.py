import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Union, Any, OrderedDict, Sequence, Tuple, Mapping, List

import sqlalchemy as sa
from sqlalchemy import Column

from .. import exceptions
from ..cache import cache
from ..exceptions import ErrorType
from ..models import database_manager
from ..models.query_builder import JoinMeta
from ..models.users import (
    UserAccount,
    UserRole,
    UserStatus,
    PermissionGrant,
    Permission,
    Entity,
    UserRoleNameEnum,
    UserStatusNameEnum
)

from ..models.query_builder import QueryBuilder

from ..controllers.base_ctrl import braceletBaseCtrl
from ..controllers.email import email_ctrl
from ..controllers.passwords import TokenType, password_ctrl


class UserAccountCtrl(braceletBaseCtrl):
    Model       = UserAccount
    OwnerColumn = UserAccount.Table.c.id

    @classmethod
    async def check_valid_changes(cls, user_id: int, user_role: str, data: UserAccount.UpdateValidator):
        user = await cls.get(id=data.id)

        def _check_user(col_names):
            for col_name in col_names:
                if not data.is_set(col_name):
                    continue

                old_value = getattr(user, col_name)
                new_value = getattr(data, col_name)
                if col_name == 'approval_toc_ts':
                    old_value = old_value.replace(microsecond=0)
                    new_value = old_value.replace(microsecond=0)

                if old_value != new_value:
                    raise exceptions.DataConflictError(
                        loc=[ 'body', col_name ],
                        msg=f"{col_name} can't be modified"
                    )

        if user_id == data.id:  # the user changing its own record
            _check_user([
                'password',
                'owner_id',
                'user_status_name',
                'deleted_ts',
                'user_role_name',
                'approval_toc_ts'
            ])

        if user_role == 'owner':
            _check_user([ 'password', 'owner_id', 'deleted_ts', 'approval_toc_ts' ])

            if user.user_role_name != data.user_role_name:
                allowed_roles = UserRoleCtrl.get_allowed_users_role(user_role)
                if data.user_role_name is not None and data.user_role_name not in allowed_roles:
                    raise exceptions.DataConflictError(
                        loc = [ 'body', 'user_role_name' ],
                        msg = 'Invalid user role change'
                    )

        status_change_forbidden_map = {
            UserStatusNameEnum.ACTIVE: [UserStatusNameEnum.PENDING],
            UserStatusNameEnum.PENDING: [UserStatusNameEnum.ACTIVE, UserStatusNameEnum.INACTIVE],
            UserStatusNameEnum.INACTIVE: [UserStatusNameEnum.PENDING]
        }

        if not user.approval_toc_ts:
            status_change_forbidden_map[UserStatusNameEnum.INACTIVE] = [
                UserStatusNameEnum.ACTIVE,
                UserStatusNameEnum.PENDING
            ]

        if (
                data.user_status_name
                and (data.user_status_name in status_change_forbidden_map[user.user_status_name]
                     or data.user_status_name not in UserStatusNameEnum.values())
        ):
            raise exceptions.DataConflictError(
                loc = [ 'body', 'user_status_name' ],
                msg = 'Invalid user status change'
            )

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.Model.get_password_hash(plain_password) == hashed_password

    @classmethod
    async def send_email_unlock_account(cls, user_account: UserAccount):
        password_token = password_ctrl.create_token(
            user_id    = user_account.id,
            role       = user_account.user_role_name,
            token_type = TokenType.RESET_PASSWORD
        )

        email_subject = f'Your account has been locked out due to several login attempts!'
        tpl_fpath = f'{email_ctrl.email_template_dir}/email_unlock_account.mako'
        with open(tpl_fpath, encoding='utf-8') as fh:
            tpl      = fh.read()
            tpl_data = {
                'user'         : user_account,
                'token'        : password_token,
                'prefix_url'   : 'https://localhost/',
                'unlock_hours' : password_ctrl.account_block_duration_hours
            }

            email_html = email_ctrl.render_tpl(tpl, tpl_data)

        password_token_info = password_ctrl.get_redis_refresh_token_info(password_token)
        cache_timeout       = password_ctrl.unlock_account_token_expire_minutes * 60
        await cache.set( password_token_info['key'], password_token_info['data'], cache_timeout )
        await email_ctrl.send_email(email_subject, [user_account.email], body_html=email_html)

    @classmethod
    async def get_login_redis_info(cls, email: str) -> Dict:
        data = await cache.get(f"login-failed-{email}")
        key  = f"login-failed-{email}"

        return {
            "key"      : key,
            "attempts" : int(data) if data is not None else 0,
            "ttl"      : password_ctrl.login_attempts_ttl_minutes
        }

    @classmethod
    async def get_user_login(cls, email: str, password: str) -> Optional[UserAccount]:
        user_account = await cls.get(id=email, field_name='email', raise_not_found=False)

        if user_account is None or user_account.user_status_name in ('pending', 'inactive'):
            return

        if user_account.blocked_ts is not None:
            if user_account.blocked_ts + timedelta(hours=password_ctrl.account_block_duration_hours) \
                    >= datetime.now(timezone.utc):
                raise exceptions.DataConflictError(
                    loc   = [ 'user_account' ],
                    type  = exceptions.ErrorType.LOGIN_INVALID_CREDENTIALS_USER_BLOCKED,
                )

            user_account.blocked_ts = None
            await cls.update(user_account.id, user_account)

        login_redis_info = await cls.get_login_redis_info(email)
        if cls.verify_password(plain_password=password, hashed_password=user_account.password):
            if login_redis_info is not None:
                await cache.delete(login_redis_info['key'])
            return user_account

        if login_redis_info['attempts'] == password_ctrl.login_max_attempts_until_block - 1:
            user_account.blocked_ts = datetime.now(timezone.utc)
            await cls.update(user_account.id, user_account)
            await cache.delete(login_redis_info['key'])
            await cls.send_email_unlock_account(user_account)
            raise exceptions.DataConflictError(
                loc   = [ 'user_account' ],
                type  = exceptions.ErrorType.LOGIN_INVALID_CREDENTIALS_USER_BLOCKED,
            )

        else:
            current_attempt = login_redis_info['attempts']
            login_redis_info['attempts'] += 1
            await cache.set(
                login_redis_info['key'],
                str(login_redis_info['attempts']),
                login_redis_info['ttl']
            )

            delay = 0.1 * current_attempt
            await asyncio.sleep(delay)
            raise exceptions.DataConflictError(
                loc   = [ 'user_account' ],
                type  = exceptions.ErrorType.LOGIN_INVALID_CREDENTIALS,
                extra = {
                    'attempts_left' : password_ctrl.login_max_attempts_until_block - login_redis_info['attempts']
                }
            )

    @classmethod
    async def edit_password(cls, user_id: int, new_password: str) -> UserAccount:
        user_account           = await cls.get(user_id)
        user_account.password  = new_password

        if user_account.blocked_ts is not None:
            user_account.blocked_ts = None

        return await cls.update(user_id, user_account)

    @classmethod
    async def change_password(cls, user_id: int, old_password: str, new_password: str):
        user_account = await cls.get(user_id, fields_map={'password': True})

        if user_account.password != cls.Model.get_password_hash(old_password):
            raise exceptions.ValidationError(
                loc  = ['body', 'old_password'],
                msg  = 'Invalid old password',
                type = ErrorType.BAD_REQUEST
            )

        await cls.edit_password(user_id, new_password)

    @classmethod
    async def delete_account(cls, user_id: int, auth_user_id: Union[str, int]) -> UserAccount:
        user: UserAccount = await UserAccountCtrl.get(user_id)

        user_data = {
            'email'            : f'{user.id}_{auth_user_id}@delete.net',
            'password'         : 'deleted',
            'first_name'       : f'{user.id} first',
            'last_name'        : f'{user.id} last',
            'user_status_name' : UserStatusNameEnum.INACTIVE,
            'phone'            : None
        }

        # await cls.delete_related_records(user_id)

        tx = await database_manager.get_db_conn().transaction()
        try:


            user = await cls.merge(
                id               = user_id,
                data             = user_data,
                with_transaction = False
            )

        except Exception as e:
            await tx.rollback()
            raise e

        await tx.commit()

        return user

    @classmethod
    async def send_token_operations_email(
            cls,
            user_email   : str,
            redirect_url : str,
            token_type   : TokenType
    ):
        user_account: UserAccount = await cls.get(id=user_email, field_name='email')

        password_token = password_ctrl.create_token(
            user_id    = user_account.id,
            role       = user_account.user_role_name,
            token_type = token_type
        )

        if token_type == TokenType.RESET_PASSWORD:
            tpl_fname     = 'email_account_password_reset.mako'
            cache_timeout = password_ctrl.reset_password_token_expire_minutes * 60
            email_subject = 'Digital bracelet platform password reset'
        elif token_type == TokenType.NEW_ACCOUNT_TOKEN:
            tpl_fname     = 'email_account_activate.mako'
            cache_timeout = password_ctrl.new_account_token_expire_minutes * 60
            email_subject = 'Digital bracelet platform account created'
        else:
            raise NotImplemented("This token_type is not supported in this function")

        tpl_fpath = f'{email_ctrl.email_template_dir}/{tpl_fname}'
        with open(tpl_fpath, encoding='utf-8') as fh:
            tpl      = fh.read()
            tpl_data = {
                'user'  : user_account,
                'prefix_url': 'https://localhost/',
                # 'prefix_url'   : redirect_url,
                'token' : password_token
            }

            email_html = email_ctrl.render_tpl(tpl, tpl_data)

        password_token_info = password_ctrl.get_redis_refresh_token_info(password_token)

        await cache.set( password_token_info['key'], password_token_info['data'], cache_timeout )

        await email_ctrl.send_email(email_subject, [user_email], body_html=email_html)

    # noinspection PyDefaultArgument
    @classmethod
    async def _apply_fts_sort_builder(
            cls,
            builder    : QueryBuilder                  = None,
            fts        : str                           = "",
            fields_map : Dict[Union[str, Column], Any] = {},
            sort_map   : OrderedDict                   = {}
    ):
        if not builder:
            builder = QueryBuilder(cls.Model)

        user_t = cls.Model.Table
        # This expression is the same used for the trigram gist index
        col_expr = user_t.c.email \
            .concat(' ') \
            .concat(user_t.c.first_name) \
            .concat(' ') \
            .concat(user_t.c.first_name) \
            .concat(' ') \
            .concat(user_t.c.last_name) \
            .concat(
            sa.func.coalesce(
                sa.literal(' ').concat(user_t.c.phone),
                sa.literal('')
            )
        )

        # We use to filter both % and %>, the later being word similarity, this is needed to find small search texts
        # the full column is too big to search in all the text with only a keyword, you don't pass the threshold
        fts_query = sa.select([
            *user_t.c,
            sa.cast(
                col_expr.op('<->')(fts),
                sa.Numeric(5, 4)
            ).label('match_distance')
        ]).select_from(
            user_t
        ).where(
            sa.or_(
                col_expr % fts,
                col_expr.op('%>')(fts)

            )
        ).alias('fts')

        builder = builder.add_join(
            JoinMeta(
                table    = fts_query,
                onclause = JoinMeta.OnClause(
                    left  = cls.Model.Table.c.id,
                    right = fts_query.c.id
                )
            )
        )

        builder = cls.apply_special_sort(
            builder    = builder,
            column     = fts_query.c.match_distance,
            sort_order = 'asc',
            fields_map = fields_map,
            sort_map   = sort_map
        )

        return builder

    # noinspection PyDefaultArgument
    @classmethod
    async def search(
            cls,
            builder            : QueryBuilder                             = None,
            fields_map         : Dict[Union[str, Column], Any]            = {},
            embed_map          : Dict[str, Union[bool, Dict]]             = {},
            sort_map           : Union[OrderedDict, Dict]                 = {},
            reverse_query_sort : bool                                     = False,
            reverse_records    : bool                                     = False,
            limit              : Optional[int]                            = None,
            offset             : Optional[int]                            = None,
            where_conds        : Sequence[Tuple[str, Mapping]]            = (),
            extra_args         : Dict[str, Any]                           = {},
            dynamic_rel_context : Dict[ str, Dict[str, Union[str, int]] ] = {}
    ) -> Tuple[List[UserAccount], bool]:
        fts_text = extra_args.get('fts')

        if not builder:
            builder = QueryBuilder(cls.Model)

        if fts_text is not None:
            builder = await cls._apply_fts_sort_builder(
                builder    = builder,
                fts        = fts_text,
                fields_map = fields_map,
                sort_map   = sort_map
            )

        return await super().search(
            builder             = builder,
            fields_map          = fields_map,
            embed_map           = embed_map,
            sort_map            = sort_map,
            reverse_query_sort  = reverse_query_sort,
            reverse_records     = reverse_records,
            limit               = limit,
            offset              = offset,
            where_conds         = where_conds,
            extra_args          = extra_args,
            dynamic_rel_context = dynamic_rel_context
        )


class UserStatusCtrl(braceletBaseCtrl):
    Model = UserStatus


class UserRoleCtrl(braceletBaseCtrl):
    Model = UserRole

    @classmethod
    def get_allowed_users_role(cls, user_role : str) -> List[UserRoleNameEnum]:
        allowed_roles = []
        if user_role == UserRoleNameEnum.ADMIN:
            allowed_roles = UserRoleNameEnum.values()

        return allowed_roles

    @classmethod
    def get_allowed_users_role_builder(cls, user_role : str) -> QueryBuilder:
        allowed_roles = cls.get_allowed_users_role(user_role)

        return QueryBuilder(cls.Model).where(
            cls.Model.Table.c.name.in_(tuple(allowed_roles))
        )


class EntityCtrl(braceletBaseCtrl):
    Model = Entity


class PermissionGrantCtrl(braceletBaseCtrl):
    Model = PermissionGrant


class PermissionCtrl(braceletBaseCtrl):
    Model = Permission

    @classmethod
    async def get_user_permission(cls, user_id: int, entity_name: str) -> Optional[Permission]:
        user = await UserAccountCtrl.get(user_id, fields_map={'user_role_name': True}, raise_not_found=False)

        if not user:
            return

        return await cls.get([user.user_role_name, entity_name], raise_not_found=False)

    # noinspection PyDefaultArgument
    @classmethod
    async def search(
            cls,
            builder            : QueryBuilder                  = None,
            fields_map         : Dict[Union[str, Column], Any] = {},
            embed_map          : Dict[str, Union[bool, Dict]]  = {},
            sort_map           : Union[OrderedDict, Dict]      = {},
            reverse_query_sort : bool                          = False,
            reverse_records    : bool                          = False,
            limit              : Optional[int]                 = None,
            offset             : Optional[int]                 = None,
            where_conds        : Sequence[Tuple[str, Mapping]] = (),
            extra_args         : Dict[str, Any]                = {},
            dynamic_rel_context : Dict[ str, Dict[str, Union[str, int]] ] = {}
    ) -> Tuple[List[Permission], bool]:
        user_id = extra_args.get('user_id')
        if user_id is not None:
            user = await UserAccountCtrl.get(user_id)
            if builder is None:
                builder = QueryBuilder(cls.Model)

            builder = cls.get_filtered_builder(
                builder       = builder,
                where_clauses = {
                    cls.Model.Table.c.user_role_name: user.user_role_name
                }
            )

        return await super().search(
            builder             = builder,
            fields_map          = fields_map,
            embed_map           = embed_map,
            sort_map            = sort_map,
            reverse_query_sort  = reverse_query_sort,
            reverse_records     = reverse_records,
            limit               = limit,
            offset              = offset,
            where_conds         = where_conds,
            extra_args          = extra_args,
            dynamic_rel_context = dynamic_rel_context
        )

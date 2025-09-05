import functools
import hashlib
from datetime import datetime
from typing import Dict, Optional, List, Union

import sqlalchemy as sa
from pydantic import Field, SecretStr, EmailStr

from ..models import database_manager, relation
from ..models.base_model import braceletBaseModel
from .common import CustomBaseModel, UTCTimeStamp, AllowBaseModel, StrEnum


def get_user_account_schema() -> Dict:
    return {
        'id': {
            'ge'      : 1,
            'example' : 1
        },
        'email': {
            'example'    : 'admin@bracelet.io'
        },
        'password': {
            'max_length' : 255,
            'example'    : 'admin123'
        },
        'user_role_name': {
            'max_length' : 64,
            "description": "Role name, FK to user_role.name",
            'example'    : 'admin'
        },
        "user_status_name": {
            'max_length'  : 64,
            "description" : "Status name, FK to user_status.name",
            "example"     : 'active'
        },
        'first_name': {
            'max_length' : 255,
            'example'    : 'Billy'
        },
        'last_name': {
            'max_length' : 255,
            'example'    : 'Armstrong'
        },
        'phone': {
            'max_length' : 64,
            'example'    : '+1 789-897-5689'
        },
        "approval_toc_ts": {
            'description' : 'Set when the user approves the terms and conditions',
            'example'     : '2020-10-05 14:05:25.643021+00:00'
        },
        'blocked_ts': {
            'description' : 'If set, this user is blocked since this date until the next day',
            'example'     : '2020-10-05 14:05:25.643021+00:00'
        },
        'create_ts': {
            'example' : '2020-10-05 14:05:25.643021+00:00'
        },
        'update_ts': {
            'example' : '2020-10-05 14:05:25.643021+00:00'
        }
    }


def get_user_status_schema() -> Dict:
    return {
        'name': {
            'max_length' : 64,
            'example'    : 'active'
        },
        'create_ts': {
            'example' : '2020-10-05 14:05:25.643021+00:00'
        },
        'update_ts': {
            'example' : '2020-10-05 14:05:25.643021+00:00'
        }
    }


def get_user_role_schema() -> Dict:
    return {
        'name': {
            'max_length' : 64,
            'example'    : 'admin'
        },
        'create_ts': {
            'example' : '2020-10-05 14:05:25.643021+00:00'
        },
        'update_ts': {
            'example' : '2020-10-05 14:05:25.643021+00:00'
        }
    }


def get_entity_schema() -> Dict:
    return {
        'name': {
            'max_length' : 255,
            'example'    : 'users'
        },
        'create_ts': {
            'example' : '2020-10-05 14:05:25.643021'
        },
        'update_ts': {
            'example' : '2020-10-05 14:05:25.643021'
        }
    }


def get_permission_grant_schema() -> Dict:
    return {
        'name': {
            'max_length' : 255,
            'example'    : 'all'
        },
        'create_ts': {
            'example' : '2020-10-05 14:05:25.643021'
        },
        'update_ts': {
            'example' : '2020-10-05 14:05:25.643021'
        }
    }


def get_permission_schema() -> Dict:
    return {
        'user_role_name': {
            'max_length' : 255,
            "description": "Role name, FK to user_role.name",
            'example'    : 'admin'
        },
        'entity_name': {
            'max_length' : 255,
            "description": "Endpoint name, FK to entity.name",
            'example'    : 'users'
        },
        'read': {
            'max_length' : 255,
            "description": "Permission granted for read, FK to permission_grant.name",
            'example'    : 'all'
        },
        'write': {
            'max_length' : 255,
            "description": "Permission granted for write, FK to permission_grant.name",
            'example'    : 'none'
        },
        'delete': {
            'max_length' : 255,
            "description": "Permission granted for delete, FK to permission_grant.name",
            'example'    : 'own'
        },
        'ui_visibility': {
            "description": "This defines if the entity will be available in the frontend for the specified role",
            'example'    : True
        },
        'create_ts': {
            'example' : '2020-10-05 14:05:25.643021'
        },
        'update_ts': {
            'example' : '2020-10-05 14:05:25.643021'
        }
    }


user_account_schema     = get_user_account_schema()
user_status_schema      = get_user_status_schema()
user_role_schema        = get_user_role_schema()
entity_schema           = get_entity_schema()
permission_grant_schema = get_permission_grant_schema()
permission_schema       = get_permission_schema()


class UserRoleNameEnum(StrEnum):
    ADMIN  = 'admin'
    USER   = 'user'


class UserStatusNameEnum(StrEnum):
    ACTIVE   = 'active'
    PENDING  = 'pending'
    INACTIVE = 'inactive'


class UserAccount(braceletBaseModel):
    class UserAccountCreate(CustomBaseModel):
        id               : Optional[int]                = Field(None, **user_account_schema['id'])
        email            : EmailStr                     = Field(..., **user_account_schema['email'])
        password         : Optional[str]                = Field(None, **user_account_schema['password'])
        user_role_name   : UserRoleNameEnum             = Field(..., **user_account_schema['user_role_name'])
        user_status_name : Optional[UserStatusNameEnum] = Field(None, **user_account_schema['user_status_name'])
        first_name       : str                          = Field(..., **user_account_schema['first_name'])
        last_name        : str                          = Field(..., **user_account_schema['last_name'])
        phone            : Optional[str]                = Field(None, **user_account_schema['phone'])
        approval_toc_ts  : Optional[datetime]           = Field(None, **user_account_schema['approval_toc_ts'])
        blocked_ts       : Optional[datetime]           = Field(None, **user_account_schema['blocked_ts'])
        create_ts        : Optional[datetime]           = Field(None, **user_account_schema['create_ts'])
        update_ts        : Optional[datetime]           = Field(None, **user_account_schema['update_ts'])

    class UserAccountFull(AllowBaseModel):
        id               : Optional[int]                = Field(None, **user_account_schema['id'])
        email            : Optional[EmailStr]           = Field(None, **user_account_schema['email'])
        password         : Optional[str]                = Field(None, **user_account_schema['password'])
        user_role_name   : Optional[UserRoleNameEnum]   = Field(None, **user_account_schema['user_role_name'])
        user_status_name : Optional[UserStatusNameEnum] = Field(None, **user_account_schema['user_status_name'])
        first_name       : Optional[str]                = Field(None, **user_account_schema['first_name'])
        last_name        : Optional[str]                = Field(None, **user_account_schema['last_name'])
        phone            : Optional[str]                = Field(None, **user_account_schema['phone'])
        approval_toc_ts  : Optional[datetime]           = Field(None, **user_account_schema['approval_toc_ts'])
        blocked_ts       : Optional[datetime]           = Field(None, **user_account_schema['blocked_ts'])
        create_ts        : Optional[datetime]           = Field(None, **user_account_schema['create_ts'])
        update_ts        : Optional[datetime]           = Field(None, **user_account_schema['update_ts'])

    class UserAccountUpdate(CustomBaseModel):
        id               : int                = Field(..., **user_account_schema['id'])
        email            : EmailStr           = Field(..., **user_account_schema['email'])
        password         : str                = Field(..., **user_account_schema['password'])
        user_role_name   : UserRoleNameEnum   = Field(..., **user_account_schema['user_role_name'])
        user_status_name : UserStatusNameEnum = Field(..., **user_account_schema['user_status_name'])
        first_name       : str                = Field(..., **user_account_schema['first_name'])
        last_name        : str                = Field(..., **user_account_schema['last_name'])
        phone            : Optional[str]      = Field(..., **user_account_schema['phone'])
        approval_toc_ts  : Optional[datetime] = Field(..., **user_account_schema['approval_toc_ts'])
        blocked_ts       : Optional[datetime] = Field(..., **user_account_schema['blocked_ts'])
        create_ts        : datetime           = Field(..., **user_account_schema['create_ts'])
        update_ts        : datetime           = Field(..., **user_account_schema['update_ts'])

    class UserAccountMerge(UserAccountFull):
        class Config:
            extra = 'forbid'

    class UserAccountChangePassword(CustomBaseModel):
        old_password : str
        new_password : str

    class UserAccountEditPassword(CustomBaseModel):
        password : str

    class UserAccountActivate(CustomBaseModel):
        password        : str
        approval_toc_ts : datetime

    # noinspection PyTypeChecker
    _search_tpl = braceletBaseModel.create_search_schema_static(
        'UserAccountSearch',
        List[UserAccountFull],
        'users'
    )
    class UserAccountSearch(_search_tpl): pass

    CreateValidator = UserAccountCreate
    FullValidator   = UserAccountFull
    UpdateValidator = UserAccountUpdate
    MergeValidator  = UserAccountMerge
    SearchValidator = UserAccountSearch

    Table = sa.Table(
        'user_account',
        database_manager.get_metadata(),
        sa.Column('id', sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column('email', sa.VARCHAR(255), nullable=False, unique=True),
        sa.Column('password', sa.VARCHAR(255), nullable=False),
        sa.Column(
            'user_role_name',
            sa.VARCHAR(64),
            sa.ForeignKey('user_role.name', onupdate='CASCADE'),
            nullable = False,
            index    = True
        ),
        sa.Column(
            'user_status_name',
            sa.VARCHAR(64),
            sa.ForeignKey('user_status.name', onupdate='CASCADE'),
            nullable = False,
            index    = True
        ),
        sa.Column('first_name', sa.VARCHAR(255), nullable=False),
        sa.Column('last_name', sa.VARCHAR(255), nullable=False),
        sa.Column('phone', sa.VARCHAR(64), index=True),
        sa.Column('approval_toc_ts', UTCTimeStamp()),
        sa.Column('blocked_ts', UTCTimeStamp()),
        sa.Column('create_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()')),
        sa.Index('user_account_fullname_idx', 'first_name', 'last_name')
    )

    id               : int      = None
    email            : str      = None
    password         : str      = None
    user_role_name   : str      = None
    user_status_name : str      = None
    first_name       : str      = None
    last_name        : str      = None
    phone            : str      = None
    approval_toc_ts  : datetime = None
    blocked_ts       : datetime = None
    create_ts        : datetime = None
    update_ts        : datetime = None

    @classmethod
    @functools.lru_cache()
    def get_relations(cls) -> Dict:
        from bracelet_lib.models.patients import Patient

        return {
            'patients': relation.Relation(
                rel_type  = relation.RelationType.HasManyRelation,
                model     = Patient,
                join      = relation.JoinMeta(
                    left  = cls.Table.c.id,
                    right = Patient.Table.c.owner_user_id
                )
            )
        }

    @classmethod
    async def save_static(
            cls,
            data: Dict,
            with_transaction    : bool = True,
            ignore_rel_entities : bool = False
    ) -> 'UserAccount':
        if data.get('password'):
            data['password'] = cls.get_password_hash(data['password'])
        else:
            data['password'] = 'initial'

        return await super().save_static(
            data,
            with_transaction    = with_transaction,
            ignore_rel_entities = ignore_rel_entities
        )

    @classmethod
    async def update_static(
            cls,
            id               : Union[int, str, List[Union[int, str]]],
            data             : Dict,
            raise_not_found  : bool = True,
            with_transaction : bool = True,
            ignore_rel_entities : bool = False
    ) -> Optional['UserAccount']:
        from bracelet_lib.controllers.users import UserAccountCtrl

        curr_user    = await UserAccountCtrl.get(id)
        payload_pass = data.get('password')
        masked_pass  = str(SecretStr('sample'))  # Example of a masked value

        # If the payload is empty, or it's masked we use the old one
        if payload_pass is None or payload_pass == masked_pass:
            data['password'] = curr_user.password
        elif payload_pass != curr_user.password:  # If is a new one we need to hash it
            data['password'] = cls.get_password_hash(data['password'])

        return await super().update_static(
            id,
            data,
            raise_not_found  = raise_not_found,
            with_transaction = with_transaction
        )

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        # Create entropy for password
        text     = f'_a21_{password}_12a_'
        hash_obj = hashlib.sha256()
        hash_obj.update(text.encode())

        return hash_obj.hexdigest()


class UserStatus(braceletBaseModel):
    class UserStatusCreate(CustomBaseModel):
        name      : str                = Field(..., **user_status_schema['name'])
        create_ts : Optional[datetime] = Field(None, **user_status_schema['create_ts'])
        update_ts : Optional[datetime] = Field(None, **user_status_schema['update_ts'])

    # noinspection DuplicatedCode
    class UserStatusFull(AllowBaseModel):
        name      : Optional[str]      = Field(None, **user_status_schema['name'])
        create_ts : Optional[datetime] = Field(None, **user_status_schema['create_ts'])
        update_ts : Optional[datetime] = Field(None, **user_status_schema['update_ts'])

    class UserStatusUpdate(CustomBaseModel):
        name      : str                = Field(..., **user_status_schema['name'])
        create_ts : Optional[datetime] = Field(..., **user_status_schema['create_ts'])
        update_ts : Optional[datetime] = Field(..., **user_status_schema['update_ts'])

    # noinspection PyTypeChecker
    _search_tpl = braceletBaseModel.create_search_schema_static(
        'UserStatusSearch',
        List[UserStatusFull],
        'users-statuses'
    )
    class UserStatusSearch(_search_tpl): pass

    CreateValidator = UserStatusCreate
    FullValidator   = UserStatusFull
    UpdateValidator = UserStatusUpdate
    SearchValidator = UserStatusSearch

    Table = sa.Table(
        'user_status',
        database_manager.get_metadata(),
        sa.Column('name', sa.VARCHAR(64), primary_key=True),
        sa.Column('create_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'))
    )

    name      : str      = None
    create_ts : datetime = None
    update_ts : datetime = None


class UserRole(braceletBaseModel):
    class UserRoleCreate(CustomBaseModel):
        name      : str                = Field(..., **user_role_schema['name'])
        create_ts : Optional[datetime] = Field(None, **user_role_schema['create_ts'])
        update_ts : Optional[datetime] = Field(None, **user_role_schema['update_ts'])

    # noinspection DuplicatedCode
    class UserRoleFull(AllowBaseModel):
        name      : Optional[str]      = Field(None, **user_role_schema['name'])
        create_ts : Optional[datetime] = Field(None, **user_role_schema['create_ts'])
        update_ts : Optional[datetime] = Field(None, **user_role_schema['update_ts'])

    class UserRoleUpdate(CustomBaseModel):
        name      : str                = Field(..., **user_role_schema['name'])
        create_ts : Optional[datetime] = Field(..., **user_role_schema['create_ts'])
        update_ts : Optional[datetime] = Field(..., **user_role_schema['update_ts'])

    # noinspection PyTypeChecker
    _search_tpl = braceletBaseModel.create_search_schema_static(
        'UserRoleSearch',
        List[UserRoleFull],
        'users-roles'
    )
    class UserRoleSearch(_search_tpl): pass

    CreateValidator = UserRoleCreate
    FullValidator   = UserRoleFull
    UpdateValidator = UserRoleUpdate
    SearchValidator = UserRoleSearch

    Table = sa.Table(
        'user_role',
        database_manager.get_metadata(),
        sa.Column('name', sa.VARCHAR(64), primary_key=True),
        sa.Column('create_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'))
    )

    name      : str      = None
    create_ts : datetime = None
    update_ts : datetime = None


class Entity(braceletBaseModel):
    class EntityCreate(CustomBaseModel):
        name      : str                = Field(..., **entity_schema['name'])
        create_ts : Optional[datetime] = Field(None, **entity_schema['create_ts'])
        update_ts : Optional[datetime] = Field(None, **entity_schema['update_ts'])

    # noinspection DuplicatedCode
    class EntityFull(AllowBaseModel):
        name      : Optional[str]      = Field(None, **entity_schema['name'])
        create_ts : Optional[datetime] = Field(None, **entity_schema['create_ts'])
        update_ts : Optional[datetime] = Field(None, **entity_schema['update_ts'])

    class EntityUpdate(CustomBaseModel):
        name      : str                = Field(..., **entity_schema['name'])
        create_ts : Optional[datetime] = Field(..., **entity_schema['create_ts'])
        update_ts : Optional[datetime] = Field(..., **entity_schema['update_ts'])

    # noinspection PyTypeChecker
    _search_tpl = braceletBaseModel.create_search_schema_static(
        'EndpointSearch',
        List[EntityFull],
        'endpoints'
    )
    class EntitySearch(_search_tpl): pass

    CreateValidator = EntityCreate
    FullValidator   = EntityFull
    UpdateValidator = EntityUpdate
    SearchValidator = EntitySearch

    Table = sa.Table(
        'entity',
        database_manager.get_metadata(),
        sa.Column('name', sa.VARCHAR(255), primary_key=True),
        sa.Column('create_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()')),
        sa.Column('update_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'))
    )

    name      : str      = None
    create_ts : datetime = None
    update_ts : datetime = None


class PermissionGrant(braceletBaseModel):
    class PermissionGrantCreate(CustomBaseModel):
        name      : str                = Field(..., **permission_grant_schema['name'])
        create_ts : Optional[datetime] = Field(None, **permission_grant_schema['create_ts'])
        update_ts : Optional[datetime] = Field(None, **permission_grant_schema['update_ts'])

    # noinspection DuplicatedCodes
    class PermissionGrantFull(AllowBaseModel):
        name      : Optional[str]      = Field(None, **permission_grant_schema['name'])
        create_ts : Optional[datetime] = Field(None, **permission_grant_schema['create_ts'])
        update_ts : Optional[datetime] = Field(None, **permission_grant_schema['update_ts'])

    class PermissionGrantUpdate(CustomBaseModel):
        name      : str                = Field(..., **permission_grant_schema['name'])
        create_ts : Optional[datetime] = Field(..., **permission_grant_schema['create_ts'])
        update_ts : Optional[datetime] = Field(..., **permission_grant_schema['update_ts'])

    # noinspection PyTypeChecker
    _search_tpl = braceletBaseModel.create_search_schema_static(
        'PermissionGrantSearch',
        List[PermissionGrantFull],
        'permissions-grant'
    )
    class PermissionGrantSearch(_search_tpl): pass

    CreateValidator = PermissionGrantCreate
    FullValidator   = PermissionGrantFull
    UpdateValidator = PermissionGrantUpdate
    SearchValidator = PermissionGrantSearch

    Table = sa.Table(
        'permission_grant',
        database_manager.get_metadata(),
        sa.Column('name', sa.VARCHAR(255), primary_key=True),
        sa.Column('create_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()')),
        sa.Column('update_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'))
    )

    name      : str      = None
    create_ts : datetime = None
    update_ts : datetime = None


class Permission(braceletBaseModel):
    class PermissionCreate(CustomBaseModel):
        user_role_name : str                = Field(..., **permission_schema['user_role_name'])
        entity_name    : str                = Field(..., **permission_schema['entity_name'])
        read           : str                = Field(..., **permission_schema['read'])
        write          : str                = Field(..., **permission_schema['write'])
        delete         : str                = Field(..., **permission_schema['delete'])
        ui_visibility  : Optional[bool]     = Field(None, **permission_schema['ui_visibility'])
        create_ts      : Optional[datetime] = Field(None, **permission_schema['create_ts'])
        update_ts      : Optional[datetime] = Field(None, **permission_schema['update_ts'])

    # noinspection DuplicatedCode
    class PermissionFull(AllowBaseModel):
        user_role_name : Optional[str]      = Field(None, **permission_schema['user_role_name'])
        entity_name    : Optional[str]      = Field(None, **permission_schema['entity_name'])
        read           : Optional[str]      = Field(None, **permission_schema['read'])
        write          : Optional[str]      = Field(None, **permission_schema['write'])
        delete         : Optional[str]      = Field(None, **permission_schema['delete'])
        ui_visibility  : Optional[bool]     = Field(None, **permission_schema['ui_visibility'])
        create_ts      : Optional[datetime] = Field(None, **permission_schema['create_ts'])
        update_ts      : Optional[datetime] = Field(None, **permission_schema['update_ts'])

    class PermissionUpdate(CustomBaseModel):
        user_role_name : str                = Field(..., **permission_schema['user_role_name'])
        entity_name    : str                = Field(..., **permission_schema['entity_name'])
        read           : str                = Field(..., **permission_schema['read'])
        write          : str                = Field(..., **permission_schema['write'])
        delete         : str                = Field(..., **permission_schema['delete'])
        ui_visibility  : bool               = Field(..., **permission_schema['ui_visibility'])
        create_ts      : Optional[datetime] = Field(..., **permission_schema['create_ts'])
        update_ts      : Optional[datetime] = Field(..., **permission_schema['update_ts'])

    # noinspection PyTypeChecker
    _search_tpl = braceletBaseModel.create_search_schema_static(
        'PermissionSearch',
        List[PermissionFull],
        'permissions'
    )
    class PermissionSearch(_search_tpl): pass

    CreateValidator = PermissionCreate
    FullValidator   = PermissionFull
    UpdateValidator = PermissionUpdate
    SearchValidator = PermissionSearch

    Table = sa.Table(
        'permission',
        database_manager.get_metadata(),
        sa.Column(
            'user_role_name',
            sa.VARCHAR(255),
            sa.ForeignKey('user_rol.name', onupdate='CASCADE', ondelete='CASCADE'),
            nullable=False,
            primary_key=True
        ),
        sa.Column(
            'entity_name',
            sa.VARCHAR(255),
            sa.ForeignKey('endpoint.name', onupdate='CASCADE', ondelete='CASCADE'),
            nullable=False,
            primary_key=True
        ),
        sa.Column(
            'read',
            sa.VARCHAR(255),
            sa.ForeignKey('permission_grant.name', onupdate='CASCADE', ondelete='CASCADE'),
            nullable=False
        ),
        sa.Column(
            'write',
            sa.VARCHAR(255),
            sa.ForeignKey('permission_grant.name', onupdate='CASCADE', ondelete='CASCADE'),
            nullable=False
        ),
        sa.Column(
            'delete',
            sa.VARCHAR(255),
            sa.ForeignKey('permission_grant.name', onupdate='CASCADE', ondelete='CASCADE'),
            nullable=False
        ),
        sa.Column(
            'ui_visibility',
            sa.BOOLEAN,
            nullable = False,
            server_default = sa.text('TRUE')
        ),
        sa.Column('create_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()')),
        sa.Column('update_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'))
    )

    user_role_name : str      = None
    entity_name    : str      = None
    read           : str      = None
    write          : str      = None
    delete         : str      = None
    create_ts      : datetime = None
    update_ts      : datetime = None

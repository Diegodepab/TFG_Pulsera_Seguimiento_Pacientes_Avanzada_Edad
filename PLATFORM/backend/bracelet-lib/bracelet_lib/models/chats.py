from datetime import datetime
from typing import Dict, Optional, List, Union
from pydantic import Field
import sqlalchemy as sa

from . import relation
from .common import UTCTimeStamp, CustomBaseModel, AllowBaseModel
from ..models import database_manager
from ..models.base_model import braceletBaseModel


def get_chat_schema() -> Dict:
    return {
        'id': {
            'ge': 1,
            'example': 1
        },
        'user1_id': {
            'ge': 1,
            'example': 1
        },
        'user2_id': {
            'ge': 1,
            'example': 2
        },
        'administration': {
            'example': False,
            'description': 'True if one of the participants is an admin (technical support chat)'
        },
        'create_ts': {
            'example': '2025-05-26T12:34:56Z'
        },
        'update_ts': {
            'example': '2025-05-26T12:34:56Z'
        }
    }

chat_schema = get_chat_schema()


class Chat(braceletBaseModel):
    class ChatCreate(CustomBaseModel):
        id            : Optional[int]       = Field(None, **chat_schema['id'])
        user1_id      : int                 = Field(..., **chat_schema['user1_id'])
        user2_id      : int                 = Field(..., **chat_schema['user2_id'])
        administration: Optional[bool]      = Field(False, **chat_schema['administration'])
        create_ts     : Optional[datetime]  = Field(None, **chat_schema['create_ts'])
        update_ts     : Optional[datetime]  = Field(None, **chat_schema['update_ts'])

    class ChatFull(AllowBaseModel):
        id            : Optional[int]      = Field(None, **chat_schema['id'])
        user1_id      : Optional[int]      = Field(None, **chat_schema['user1_id'])
        user2_id      : Optional[int]      = Field(None, **chat_schema['user2_id'])
        administration: Optional[bool]     = Field(None, **chat_schema['administration'])
        create_ts     : Optional[datetime] = Field(None, **chat_schema['create_ts'])
        update_ts     : Optional[datetime] = Field(None, **chat_schema['update_ts'])

    class ChatUpdate(CustomBaseModel):
        id            : int                = Field(..., **chat_schema['id'])
        user1_id      : int                = Field(..., **chat_schema['user1_id'])
        user2_id      : int                = Field(..., **chat_schema['user2_id'])
        administration: bool               = Field(..., **chat_schema['administration'])
        create_ts     : datetime           = Field(..., **chat_schema['create_ts'])
        update_ts     : datetime           = Field(..., **chat_schema['update_ts'])

    class ChatMerge(ChatFull):
        class Config:
            extra = 'forbid'

    _search_tpl = braceletBaseModel.create_search_schema_static(
        'ChatSearch',
        List[ChatFull],
        'chats'
    )

    class ChatSearch(_search_tpl):
        pass

    CreateValidator = ChatCreate
    FullValidator   = ChatFull
    UpdateValidator = ChatUpdate
    MergeValidator  = ChatMerge
    SearchValidator = ChatSearch

    Table = sa.Table(
        'chat',
        database_manager.get_metadata(),
        sa.Column('id', sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column('user1_id', sa.INTEGER(), sa.ForeignKey('user_account.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user2_id', sa.INTEGER(), sa.ForeignKey('user_account.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('administration', sa.BOOLEAN(), nullable=False, default=False, index=True),
        sa.Column('create_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'))
    )

    id            : int      = None
    user1_id      : int      = None
    user2_id      : int      = None
    administration: bool     = None
    create_ts     : datetime = None
    update_ts     : datetime = None

    # Related data
    user1 : 'UserAccount' = None
    user2 : 'UserAccount' = None

    @classmethod
    def get_relations(cls) -> Dict:
        from ..models.users import UserAccount
        # Sólo definimos las relaciones a usuarios, sin importar mensajes
        return {
            'user1': relation.Relation(
                rel_type=relation.RelationType.BelongsToOneRelation,
                model=UserAccount,
                join=relation.JoinMeta(
                    left=cls.Table.c.user1_id,
                    right=UserAccount.Table.c.id
                )
            ),
            'user2': relation.Relation(
                rel_type=relation.RelationType.BelongsToOneRelation,
                model=UserAccount,
                join=relation.JoinMeta(
                    left=cls.Table.c.user2_id,
                    right=UserAccount.Table.c.id
                )
            )
        }

    @classmethod
    async def save_static(
        cls,
        data: Dict,
        with_transaction    : bool = True,
        ignore_rel_entities : bool = False
    ) -> 'Chat':
        return await super().save_static(
            data,
            with_transaction    = with_transaction,
            ignore_rel_entities = ignore_rel_entities
        )

    @classmethod
    async def update_static(
        cls,
        id: Union[int, str],
        data: Dict,
        raise_not_found: bool = True,
        with_transaction: bool = True,
        ignore_rel_entities : bool = False
    ) -> Optional['Chat']:
        return await super().update_static(
            id,
            data,
            raise_not_found  = raise_not_found,
            with_transaction = with_transaction
        )

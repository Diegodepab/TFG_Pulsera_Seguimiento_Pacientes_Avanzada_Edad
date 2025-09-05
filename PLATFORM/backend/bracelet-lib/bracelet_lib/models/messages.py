from datetime import datetime
from typing import Dict, Optional, List, Union
from pydantic import Field
import sqlalchemy as sa

from . import relation
from .common import UTCTimeStamp, CustomBaseModel, AllowBaseModel
from ..models import database_manager
from ..models.base_model import braceletBaseModel


def get_message_schema() -> Dict:
    return {
        'id': {
            'ge': 1,
            'example': 1
        },
        'chat_id': {
            'ge': 1,
            'example': 1
        },
        'sender_id': {
            'ge': 1,
            'example': 1
        },
        'content': {
            'max_length': 1000,
            'example': 'Hello, how are you?'
        },
        'ts': {
            'example': '2025-05-26T12:34:56Z'
        },
        'create_ts': {
            'example': '2025-05-26T12:34:56Z'
        },
        'update_ts': {
            'example': '2025-05-26T12:34:56Z'
        }
    }

message_schema = get_message_schema()

class Message(braceletBaseModel):
    class MessageCreate(CustomBaseModel):
        id        : Optional[int]   = Field(None, **message_schema['id'])
        chat_id   : int             = Field(..., **message_schema['chat_id'])
        sender_id : Optional[int]   = Field(None, **message_schema['sender_id'])
        content   : str             = Field(..., **message_schema['content'])
        ts        : datetime        = Field(..., **message_schema['ts'])
        create_ts : Optional[datetime] = Field(None, **message_schema['create_ts'])
        update_ts : Optional[datetime] = Field(None, **message_schema['update_ts'])

    class MessageFull(AllowBaseModel):
        id        : Optional[int]   = Field(None, **message_schema['id'])
        chat_id   : Optional[int]   = Field(None, **message_schema['chat_id'])
        sender_id : Optional[int]   = Field(None, **message_schema['sender_id'])
        content   : Optional[str]   = Field(None, **message_schema['content'])
        ts        : Optional[datetime] = Field(None, **message_schema['ts'])
        create_ts : Optional[datetime] = Field(None, **message_schema['create_ts'])
        update_ts : Optional[datetime] = Field(None, **message_schema['update_ts'])

    class MessageUpdate(CustomBaseModel):
        id        : int             = Field(..., **message_schema['id'])
        chat_id   : int             = Field(..., **message_schema['chat_id'])
        sender_id : Optional[int]   = Field(..., **message_schema['sender_id'])
        content   : str             = Field(..., **message_schema['content'])
        ts        : datetime        = Field(..., **message_schema['ts'])
        create_ts : datetime        = Field(..., **message_schema['create_ts'])
        update_ts : datetime        = Field(..., **message_schema['update_ts'])

    class MessageMerge(MessageFull):
        class Config:
            extra = 'forbid'

    # Search schema
    _search_tpl = braceletBaseModel.create_search_schema_static(
        'MessageSearch',
        List[MessageFull],
        'messages'
    )
    class MessageSearch(_search_tpl): pass

    CreateValidator = MessageCreate
    FullValidator   = MessageFull
    UpdateValidator = MessageUpdate
    MergeValidator  = MessageMerge
    SearchValidator = MessageSearch

    Table = sa.Table(
        'message',
        database_manager.get_metadata(),
        sa.Column('id', sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column('chat_id', sa.INTEGER(), sa.ForeignKey('chat.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('sender_id', sa.INTEGER(), sa.ForeignKey('user_account.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('content', sa.TEXT(), nullable=False, comment="Message body"),
        sa.Column('ts', sa.TIMESTAMP(), nullable=False, comment="Time when message was sent"),
        sa.Column('create_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'))
    )

    id        : int      = None
    chat_id   : int      = None
    sender_id : int      = None
    content   : str      = None
    ts        : datetime = None
    create_ts : datetime = None
    update_ts : datetime = None

    # Related data
    chat   : 'Chat'        = None
    sender : 'UserAccount' = None

    @classmethod
    def get_relations(cls) -> Dict:
        from ..models.chats import Chat
        from ..models.users import UserAccount
        return {
            'chat': relation.Relation(
                rel_type = relation.RelationType.BelongsToOneRelation,
                model    = Chat,
                join     = relation.JoinMeta(
                    left  = cls.Table.c.chat_id,
                    right = Chat.Table.c.id
                )
            ),
            'sender': relation.Relation(
                rel_type = relation.RelationType.BelongsToOneRelation,
                model    = UserAccount,
                join     = relation.JoinMeta(
                    left  = cls.Table.c.sender_id,
                    right = UserAccount.Table.c.id
                )
            )
        }

    @classmethod
    async def save_static(
        cls,
        data: Dict,
        with_transaction    : bool = True,
        ignore_rel_entities : bool = False
    ) -> 'Message':
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
    ) -> Optional['Message']:
        return await super().update_static(
            id,
            data,
            raise_not_found  = raise_not_found,
            with_transaction = with_transaction
        )
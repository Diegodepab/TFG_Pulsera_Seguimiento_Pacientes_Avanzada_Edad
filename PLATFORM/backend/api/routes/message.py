from typing import Dict, Union, List, Optional
from fastapi import APIRouter, Depends, Path, Query, Response
from starlette.requests import Request
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from controllers.bracelet_ctrl_proxy import braceletCtrlProxy
from lib import auth
from bracelet_lib.controllers.message import MessageCtrl
from bracelet_lib.models.common import StrEnum
from bracelet_lib.models.messages import Message
from routes.common import HTTPResponses, BasicQueryParams, FieldsQueryParam, build_embed_query_param

router = APIRouter()

class MessageEmbedEnum(StrEnum):
    chat   = 'chat'
    sender = 'sender'

@router.get(
    '/messages',
    response_model               = Message.SearchValidator,
    response_model_exclude_unset = True,
    summary                      = 'Search messages',
    description                  = 'Allows to perform messages search',
    response_description         = 'Message list',
    responses                    = {**HTTPResponses.search}
)
async def search_messages(
        request        : Request,
        query_params   : BasicQueryParams = Depends(BasicQueryParams),
        embed          : str = Depends(build_embed_query_param(MessageEmbedEnum)),
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated),
        chat_id        : Optional[int] = Query(None, description='Filter by chat ID'),
        sender_id      : Optional[int] = Query(None, description='Filter by sender ID'),
        ts_from        : Optional[str] = Query(None, description='Filter from timestamp'),
        ts_to          : Optional[str] = Query(None, description='Filter to timestamp')
):
    options                   = query_params.get_dict()
    options['embed']          = embed
    options['auth_user_info'] = auth_user_info
    options['extra_args']     = {
        'chat_id': chat_id,
        'sender_id': sender_id,
        'ts_from': ts_from,
        'ts_to': ts_to
    }
    return await braceletCtrlProxy.search(MessageCtrl, request, **options)

@router.get(
    '/messages/{message_id}',
    response_model               = Message.FullValidator,
    response_model_exclude_unset = True,
    summary                      = 'Get message',
    description                  = 'Returns a message record based on ID',
    response_description         = 'Message record',
    responses                    = {**HTTPResponses.get}
)
async def get_message(
        message_id    : int = Path(..., description='Message ID'),
        fields        : FieldsQueryParam = Depends(FieldsQueryParam),
        auth_user_info: Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {'auth_user_info': auth_user_info}
    return await braceletCtrlProxy.get(MessageCtrl, message_id, fields.fields, **options)

@router.post(
    '/messages',
    response_model               = Message.FullValidator,
    response_model_exclude_unset = True,
    summary                      = 'Create message',
    description                  = 'Creates a new message record',
    response_description         = 'Created message record',
    status_code                  = HTTP_201_CREATED,
    responses                    = {**HTTPResponses.post}
)
async def create_message(
        message        : Message.CreateValidator,
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {'auth_user_info': auth_user_info}
    return await braceletCtrlProxy.create(MessageCtrl, message, **options)

@router.put(
    '/messages/{message_id}',
    summary              = 'Update message',
    description          = 'Allows full update of a message record',
    response_description = 'Empty',
    status_code          = HTTP_204_NO_CONTENT,
    responses            = {**HTTPResponses.put},
    response_class       = Response
)
async def update_message(
        message        : Message.UpdateValidator,
        message_id     : int                        = Path(..., description='Message ID'),
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {'auth_user_info': auth_user_info}
    await braceletCtrlProxy.update(MessageCtrl, message_id, message, **options)

@router.patch(
    '/messages/{message_id}',
    response_model       = Message.FullValidator,
    summary              = 'Partial update message',
    description          = 'Allows partial update of a message record',
    response_description = 'Record updated',
    responses            = {**HTTPResponses.put}
)
async def patch_message(
        message_in      : Message.MergeValidator,
        message_id      : int                        = Path(..., description='Message ID to update'),
        auth_user_info  : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    message_in.id = message_id
    return await braceletCtrlProxy.merge(
        MessageCtrl,
        id             = message_id,
        data           = message_in,
        validate       = False,
        auth_user_info = auth_user_info
    )

@router.delete(
    '/messages/{message_id}',
    summary              = 'Delete message',
    description          = 'Allows to delete a message record',
    response_description = 'Empty',
    status_code          = HTTP_204_NO_CONTENT,
    responses            = {**HTTPResponses.delete},
    response_class       = Response
)
async def delete_message(
        message_id      : int                        = Path(..., description='Message ID to delete'),
        auth_user_info  : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {'auth_user_info': auth_user_info}
    await braceletCtrlProxy.delete(MessageCtrl, message_id, **options)


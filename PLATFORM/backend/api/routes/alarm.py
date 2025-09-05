from typing import Dict, Union, List, Optional
from fastapi import APIRouter, Depends, Path, Query, Response
from starlette.requests import Request
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from controllers.bracelet_ctrl_proxy import braceletCtrlProxy
from lib import auth
from bracelet_lib.controllers.alarm import AlarmCtrl
from bracelet_lib.models.common import StrEnum
from bracelet_lib.models.alarm import Alarm
from routes.common import HTTPResponses, BasicQueryParams, FieldsQueryParam, build_embed_query_param

router = APIRouter()

class AlarmEmbedEnum(StrEnum):
    patient = 'patient'

@router.get(
    '/alarms',
    response_model               = Alarm.SearchValidator,
    response_model_exclude_unset = True,
    summary                      = 'Search alarms',
    description                  = 'Allows to perform alarms search',
    response_description         = 'Alarm list',
    responses                    = {**HTTPResponses.search}
)
async def search_alarms(
        request        : Request,
        query_params   : BasicQueryParams = Depends(BasicQueryParams),
        embed          : str = Depends(build_embed_query_param(AlarmEmbedEnum)),
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated),
        patient_id     : Optional[int] = Query(None, description='Filter by patient ID'),
        is_urgent      : Optional[bool] = Query(None, description='Filter urgent alarms'),
        ts_from        : Optional[str] = Query(None, description='Filter from timestamp'),
        ts_to          : Optional[str] = Query(None, description='Filter to timestamp')
):
    options                   = query_params.get_dict()
    options['embed']          = embed
    options['auth_user_info'] = auth_user_info
    options['extra_args']     = {
        'patient_id': patient_id,
        'is_urgent': is_urgent,
        'ts_from': ts_from,
        'ts_to': ts_to
    }
    return await braceletCtrlProxy.search(AlarmCtrl, request, **options)

@router.get(
    '/alarms/{alarm_id}',
    response_model               = Alarm.FullValidator,
    response_model_exclude_unset = True,
    summary                      = 'Get alarm',
    description                  = 'Returns an alarm record based on ID',
    response_description         = 'Alarm record',
    responses                    = {**HTTPResponses.get}
)
async def get_alarm(
        alarm_id       : int = Path(..., description='Alarm ID'),
        fields         : FieldsQueryParam = Depends(FieldsQueryParam),
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {'auth_user_info': auth_user_info}
    return await braceletCtrlProxy.get(AlarmCtrl, alarm_id, fields.fields, **options)

@router.post(
    '/alarms',
    response_model               = Alarm.FullValidator,
    response_model_exclude_unset = True,
    summary                      = 'Create alarm',
    description                  = 'Creates a new alarm record',
    response_description         = 'Created alarm record',
    status_code                  = HTTP_201_CREATED,
    responses                    = {**HTTPResponses.post}
)
async def create_alarm(
        alarm          : Alarm.CreateValidator,
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {'auth_user_info': auth_user_info}
    return await braceletCtrlProxy.create(AlarmCtrl, alarm, **options)

@router.put(
    '/alarms/{alarm_id}',
    summary              = 'Update alarm',
    description          = 'Allows full update of an alarm record',
    response_description = 'Empty',
    status_code          = HTTP_204_NO_CONTENT,
    responses            = {**HTTPResponses.put},
    response_class       = Response
)
async def update_alarm(
        alarm          : Alarm.UpdateValidator,
        alarm_id       : int = Path(..., description='Alarm ID'),
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {'auth_user_info': auth_user_info}
    await braceletCtrlProxy.update(AlarmCtrl, alarm_id, alarm, **options)

@router.patch(
    '/alarms/{alarm_id}',
    response_model       = Alarm.FullValidator,
    summary              = 'Partial update alarm',
    description          = 'Allows partial update of an alarm record',
    response_description = 'Record updated',
    responses            = {**HTTPResponses.put}
)
async def patch_alarm(
        alarm_in       : Alarm.MergeValidator,
        alarm_id       : int = Path(..., description='Alarm ID to update'),
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    alarm_in.id = alarm_id
    return await braceletCtrlProxy.merge(
        AlarmCtrl,
        id             = alarm_id,
        data           = alarm_in,
        validate       = False,
        auth_user_info = auth_user_info
    )

@router.delete(
    '/alarms/{alarm_id}',
    summary              = 'Delete alarm',
    description          = 'Allows to delete an alarm record',
    response_description = 'Empty',
    status_code          = HTTP_204_NO_CONTENT,
    responses            = {**HTTPResponses.delete},
    response_class       = Response
)
async def delete_alarm(
        alarm_id       : int = Path(..., description='Alarm ID to delete'),
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {'auth_user_info': auth_user_info}
    await braceletCtrlProxy.delete(AlarmCtrl, alarm_id, **options)

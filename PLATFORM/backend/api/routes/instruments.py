from typing import Dict, Union
from fastapi import APIRouter, Depends, Path, Response, Query
from starlette.requests import Request
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED

from controllers.bracelet_ctrl_proxy import braceletCtrlProxy, PermissionGrantType
from bracelet_lib.controllers.instruments import InstrumentCtrl
from bracelet_lib.controllers.users import PermissionCtrl
from bracelet_lib.models.instruments import Instrument
from routes.common import HTTPResponses, BasicQueryParams, FieldsQueryParam
from bracelet_lib.models.storage import SignedUrlResponse, SignedUrlRequest, BlobOpType
from lib import auth, exceptions as lib_exceptions


router = APIRouter()


@router.get(
    '/instruments',
    response_model               = Instrument.SearchValidator,
    response_model_exclude_unset = True,
    summary                      = 'Search instruments',
    description                  = 'Allows to perform instruments search',
    response_description         = 'Instrument list',
    responses                    = {**HTTPResponses.search}
)
async def search_instruments(
        request              : Request,
        query_params         : BasicQueryParams           = Depends(BasicQueryParams),
        auth_user_info       : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated),
        add_blob_display_url : bool                       = Query(
            False,
            description = 'Includes the signed URL to access the blob resource'
        ),
        fts            : str                        = Query(
            None,
            description = 'Text for Full Text Search.',
            example     = 'Guitar Violin'
        )
):
    options                   = query_params.get_dict()
    options['auth_user_info'] = auth_user_info
    options['extra_args']     = {
        'fts': fts
    }

    search_data = await braceletCtrlProxy.search(InstrumentCtrl, request, **options)
    if add_blob_display_url:
        await InstrumentCtrl.bulk_add_signed_display_url(search_data.items)

    return search_data


@router.post(
    '/instruments',
    response_model               = Instrument.FullValidator,
    response_model_exclude_unset = True,
    summary                      = 'Create instrument',
    description                  = 'Creates a new instrument record',
    response_description         = 'Created instrument record',
    status_code                  = HTTP_201_CREATED,
    responses                    = {**HTTPResponses.post}
)
async def create_instrument(
        instrument: Instrument.CreateValidator,
        auth_user_info: Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {'auth_user_info': auth_user_info}
    return await braceletCtrlProxy.create(InstrumentCtrl, instrument, **options)


@router.post(
    '/instruments/bs-signed-url',
    response_model               = SignedUrlResponse.PostSignedUrlResponse,
    response_model_exclude_unset = True,
    summary                      = 'Generate a signed URL to post a resource on blob storage',
    description                  = 'Returns a signed URL to post a model on blob storage for an instrument',
    response_description         = 'Signed URL to post instrument',
    status_code                  = HTTP_201_CREATED,
    responses                    = {**HTTPResponses.post}
)
async def post_instrument_signed_url(
        signed_request : SignedUrlRequest.PostSignedUrlRequest,
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    user_id = auth_user_info['user_id']
    permissions = await PermissionCtrl.get_user_permission(
        user_id,
        entity_name = InstrumentCtrl.Model.Table.name
    )

    if permissions.write == PermissionGrantType.none:
        raise lib_exceptions.AuthException(msg='Not enough permissions to use this resource')

    return await InstrumentCtrl.generate_signed_url(
        operation  = BlobOpType.post,
        data       = signed_request,
        prefix_url = f"user/{user_id}/instrument"
    )


@router.get(
    '/instruments/{instrument_id}',
    response_model               = Instrument.FullValidator,
    response_model_exclude_unset = True,
    summary                      = 'Get instrument',
    description                  = 'Returns an instrument record based on their ID',
    response_description         = 'Instrument record',
    responses                    = {**HTTPResponses.get}
)
async def get_instrument(
        instrument_id        : int                        = Path(..., description='Instrument ID'),
        fields               : FieldsQueryParam           = Depends(FieldsQueryParam),
        auth_user_info       : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated),
        add_blob_display_url : bool                       = Query(
            False,
            description = 'Includes the signed URL to access the blob resource'
        )
):
    options = {
        'auth_user_info': auth_user_info,
        'extra_args'     : {
            'add_blob_display_url' : add_blob_display_url
        }
    }

    return await braceletCtrlProxy.get(InstrumentCtrl, instrument_id, fields.fields, **options)


@router.get(
    '/instruments/{instrument_id}/bs-signed-url',
    response_model               = SignedUrlResponse.GetSignedUrlResponse,
    response_model_exclude_unset = True,
    summary                      = 'Generate a signed URL for access to a resource from blob storage',
    description                  = 'Obtain a signed URL for access to the model from a instrument based on its ID',
    response_description         = 'Signed URL to display model',
    responses                    = {**HTTPResponses.get}
)
async def get_instrument_signed_url(
        instrument_id  : int                        = Path(..., description='Instrument ID'),
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    instrument = await braceletCtrlProxy.get(
        ctrl           = InstrumentCtrl,
        id             = instrument_id,
        auth_user_info = auth_user_info
    )

    return await InstrumentCtrl.generate_signed_url(
        operation = BlobOpType.get,
        blob_url  = instrument.url
    )




@router.delete(
    '/instruments/{instrument_id}/bs-signed-url',
    response_model               = SignedUrlResponse.DeleteSignedUrlResponse,
    response_model_exclude_unset = True,
    summary                      = 'Generate a signed URL to delete a resource from blob storage',
    description                  = 'Returns a signed URL to delete a instrument from blob storage based on its ID',
    response_description         = 'Signed URL to delete model',
    responses                    = {**HTTPResponses.delete}
)
async def delete_instrument_signed_url(
        instrument_id  : int                        = Path(..., description='instrument ID'),
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    instrument = await braceletCtrlProxy.get(
        ctrl           = InstrumentCtrl,
        id             = instrument_id,
        auth_user_info = auth_user_info
    )

    return await InstrumentCtrl.generate_signed_url(
        operation   = BlobOpType.delete,
        blob_url    = instrument.url
    )


@router.put(
    '/instruments/{instrument_id}',
    summary              = 'Update instrument',
    description          = 'Allows to perform full update of an instrument record',
    response_description = 'Empty',
    status_code          = HTTP_204_NO_CONTENT,
    responses            = {**HTTPResponses.put},
    response_class       = Response
)
async def update_instrument(
        instrument      : Instrument.UpdateValidator,
        instrument_id   : int                        = Path(..., description='Instrument ID'),
        auth_user_info  : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {'auth_user_info': auth_user_info}
    await braceletCtrlProxy.update(InstrumentCtrl, instrument_id, instrument, **options)


@router.patch(
    '/instruments/{instrument_id}',
    response_model       = Instrument.FullValidator,
    summary              = 'Partial update instrument',
    description          = 'Allows to perform partial update of an instrument record',
    response_description = 'Record updated',
    responses            = {**HTTPResponses.put}
)
async def patch_instrument(
        instrument_in     : Instrument.MergeValidator,
        instrument_id     : int                        = Path(..., description='Instrument ID to update'),
        auth_user_info    : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    instrument_in.id = instrument_id

    return await braceletCtrlProxy.merge(
        InstrumentCtrl,
        id             = instrument_id,
        data           = instrument_in,
        validate       = False,
        auth_user_info = auth_user_info
    )


@router.delete(
    '/instruments/{instrument_id}',
    summary              = 'Delete instrument',
    description          = 'Allows to perform delete an instrument record',
    response_description = 'Empty',
    status_code          = HTTP_204_NO_CONTENT,
    responses            = {**HTTPResponses.delete},
    response_class       = Response
)
async def delete_instrument(
        instrument_id   : int                        = Path(..., description='Instrument ID to delete'),
        auth_user_info  : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {
        'auth_user_info': auth_user_info
    }

    await braceletCtrlProxy.delete(InstrumentCtrl, instrument_id, **options)

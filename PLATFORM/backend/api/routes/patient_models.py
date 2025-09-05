from typing import Dict, Union
from fastapi import APIRouter, Depends, Path, Response, Query
from starlette.requests import Request
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED

from controllers.bracelet_ctrl_proxy import braceletCtrlProxy, PermissionGrantType
from bracelet_lib.controllers.patient_models import PatientModelCtrl
from bracelet_lib.controllers.users import PermissionCtrl
from bracelet_lib.models.patient_models import PatientModel
from bracelet_lib.models.common import StrEnum
from routes.common import HTTPResponses, BasicQueryParams, FieldsQueryParam, build_embed_query_param
from bracelet_lib.models.storage import SignedUrlResponse, SignedUrlRequest, BlobOpType
from lib import auth, exceptions as lib_exceptions

router = APIRouter()


class PatientModelEmbedEnum(StrEnum):
    patient = 'patient'


@router.get(
    '/patient-models',
    response_model               = PatientModel.SearchValidator,
    response_model_exclude_unset = True,
    summary                      = 'Search patient models',
    description                  = 'Allows to perform patient models search',
    response_description         = 'PatientModel list',
    responses                    = {**HTTPResponses.search}
)
async def search_patient_models(
        request              : Request,
        query_params         : BasicQueryParams           = Depends(BasicQueryParams),
        embed                : str                        = Depends(build_embed_query_param(PatientModelEmbedEnum)),
        auth_user_info       : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated),
        add_blob_display_url : bool                       = Query(
            False,
            description = 'Includes the signed URL to access the blob resource'
        ),
        fts            : str                        = Query(
            None,
            description = 'Text for Full Text Search.',
            example     = 'Heart Kidney'
        )
):
    options                   = query_params.get_dict()
    options['embed']          = embed
    options['auth_user_info'] = auth_user_info
    options['extra_args']     = {
        'fts': fts
    }

    search_data = await braceletCtrlProxy.search(PatientModelCtrl, request, **options)
    if add_blob_display_url:
        await PatientModelCtrl.bulk_add_signed_display_url(search_data.items)

    return search_data


@router.post(
    '/patient-models',
    response_model               = PatientModel.FullValidator,
    response_model_exclude_unset = True,
    summary                      = 'Create patient model',
    description                  = 'Creates a new patient model record',
    response_description         = 'Created patient model record',
    status_code                  = HTTP_201_CREATED,
    responses                    = {**HTTPResponses.post}
)
async def create_patient_model(
        patient_model   : PatientModel.CreateValidator,
        auth_user_info  : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {'auth_user_info': auth_user_info}
    return await braceletCtrlProxy.create(PatientModelCtrl, patient_model, **options)


@router.post(
    '/patient-models/bs-signed-url',
    response_model               = SignedUrlResponse.PostSignedUrlResponse,
    response_model_exclude_unset = True,
    summary                      = 'Generate a signed URL to post a resource on blob storage',
    description                  = 'Returns a signed URL to post a model on blob storage for a patient model',
    response_description         = 'Signed URL to post patient model',
    status_code                  = HTTP_201_CREATED,
    responses                    = {**HTTPResponses.post}
)
async def post_patient_model_signed_url(
        signed_request : SignedUrlRequest.PostSignedUrlRequest,
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    user_id = auth_user_info['user_id']
    permissions = await PermissionCtrl.get_user_permission(
        user_id,
        entity_name = PatientModelCtrl.Model.Table.name
    )
    if permissions.write == PermissionGrantType.none:
        raise lib_exceptions.AuthException(msg='Not enough permissions to use this resource')

    return await PatientModelCtrl.generate_signed_url(
        operation  = BlobOpType.post,
        data       = signed_request,
        prefix_url = f"user/{user_id}/patient-models"
    )


@router.get(
    '/patient-models/{patient_model_id}',
    response_model               = PatientModel.FullValidator,
    response_model_exclude_unset = True,
    summary                      = 'Get patient model',
    description                  = 'Returns an patient model record based on their ID',
    response_description         = 'PatientModel record',
    responses                    = {**HTTPResponses.get}
)
async def get_patient_model(
        patient_model_id     : int                        = Path(..., description='PatientModel ID'),
        embed                : str                        = Depends(build_embed_query_param(PatientModelEmbedEnum)),
        fields               : FieldsQueryParam           = Depends(FieldsQueryParam),
        auth_user_info       : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated),
        add_blob_display_url : bool                       = Query(
            False,
            description = 'Includes the signed URL to access the blob resource'
        )
):
    options = {
        'embed'          : embed,
        'auth_user_info': auth_user_info,
        'extra_args'     : {
            'add_blob_display_url' : add_blob_display_url
        }
    }

    return await braceletCtrlProxy.get(PatientModelCtrl, patient_model_id, fields.fields, **options)


@router.get(
    '/patient-models/{patient_model_id}/bs-signed-url',
    response_model               = SignedUrlResponse.GetSignedUrlResponse,
    response_model_exclude_unset = True,
    summary                      = 'Generate a signed URL for access to a resource from blob storage',
    description                  = 'Obtain a signed URL for access to the model from a patient model based on its ID',
    response_description         = 'Signed URL to display model',
    responses                    = {**HTTPResponses.get}
)
async def get_patient_model_signed_url(
        patient_model_id : int                        = Path(..., description='Patient model ID'),
        auth_user_info   : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    patient_model_id = await braceletCtrlProxy.get(
        ctrl           = PatientModelCtrl,
        id             = patient_model_id,
        auth_user_info = auth_user_info
    )

    return await PatientModelCtrl.generate_signed_url(
        operation = BlobOpType.get,
        blob_url  = patient_model_id.url
    )


# @router.put(
#     '/patient_models/{patient_model_id}/bs-signed-url',
#     response_model               = SignedUrlResponse.PutSignedUrlResponse,
#     response_model_exclude_unset = True,
#     summary                      = 'Generate a signed URL for update a resource on blob storage',
#     description                  = 'Returns a signed URL for update a model on blob storage for an patient model',
#     response_description         = 'Signed URL for update an patient model',
#     status_code                  = HTTP_204_NO_CONTENT,
#     responses                    = {**HTTPResponses.put}
# )
# async def put_patient_model_signed_url(
#         signed_request : SignedUrlRequest.PutSignedUrlRequest,
#         patient_model_id  : int,
#         auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
# ):
#     patient_model = await TwinCtrlProxy.get(
#         ctrl           = PatientModelCtrl,
#         id             = patient_model_id,
#         auth_user_info = auth_user_info
#     )
#
#     return await PatientModelCtrl.generate_signed_url(
#         operation  = BlobOpType.put,
#         data       = signed_request,
#         blob_url   = patient_model.url
#     )


@router.delete(
    '/patient-models/{patient_model_id}/bs-signed-url',
    response_model               = SignedUrlResponse.DeleteSignedUrlResponse,
    response_model_exclude_unset = True,
    summary                      = 'Generate a signed URL to delete a resource from blob storage',
    description                  = 'Returns a signed URL to delete a patient model from blob storage based on its ID',
    response_description         = 'Signed URL to delete model',
    responses                    = {**HTTPResponses.delete}
)
async def delete_patient_model_signed_url(
        patient_model_id  : int                        = Path(..., description='Patient model ID'),
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    patient_model = await braceletCtrlProxy.get(
        ctrl           = PatientModelCtrl,
        id             = patient_model_id,
        auth_user_info = auth_user_info
    )

    return await PatientModelCtrl.generate_signed_url(
        operation   = BlobOpType.delete,
        blob_url    = patient_model.url
    )


@router.put(
    '/patient-models/{patient_model_id}',
    summary              = 'Update patient model',
    description          = 'Allows to perform full update of an patient model record',
    response_description = 'Empty',
    status_code          = HTTP_204_NO_CONTENT,
    responses            = {**HTTPResponses.put},
    response_class       = Response
)
async def update_patient_model(
        patient_model    : PatientModel.UpdateValidator,
        patient_model_id : int                        = Path(..., description='PatientModel ID'),
        auth_user_info   : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {'auth_user_info': auth_user_info}
    await braceletCtrlProxy.update(PatientModelCtrl, patient_model_id, patient_model, **options)


@router.patch(
    '/patient-models/{patient_model_id}',
    response_model       = PatientModel.FullValidator,
    summary              = 'Partial update patient model',
    description          = 'Allows to perform partial update of an patient model record',
    response_description = 'Record updated',
    responses            = {**HTTPResponses.put}
)
async def patch_patient_model(
        patient_model_in        : PatientModel.MergeValidator,
        patient_model_id        : int                        = Path(..., description='PatientModel ID to update'),
        auth_user_info  : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    patient_model_in.id = patient_model_id

    return await braceletCtrlProxy.merge(
        PatientModelCtrl,
        id             = patient_model_id,
        data           = patient_model_in,
        validate       = False,
        auth_user_info = auth_user_info
    )


@router.delete(
    '/patient-models/{patient_model_id}',
    summary              = 'Delete patient model',
    description          = 'Allows to perform delete an patient model record',
    response_description = 'Empty',
    status_code          = HTTP_204_NO_CONTENT,
    responses            = {**HTTPResponses.delete},
    response_class       = Response
)
async def delete_patient_model(
        patient_model_id : int                        = Path(..., description='PatientModel ID to delete'),
        auth_user_info   : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {
        'auth_user_info': auth_user_info
    }

    await braceletCtrlProxy.delete(PatientModelCtrl, patient_model_id, **options)

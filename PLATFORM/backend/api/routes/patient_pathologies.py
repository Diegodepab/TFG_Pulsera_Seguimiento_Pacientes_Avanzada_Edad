from typing import Dict, Union, List
from fastapi import APIRouter, Depends, Path, Response, Query
from starlette.requests import Request
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED

from controllers.bracelet_ctrl_proxy import braceletCtrlProxy
from lib import auth
from bracelet_lib.controllers.patient_pathologies import PatientPathologyCtrl
from bracelet_lib.models.common import StrEnum
from bracelet_lib.models.patient_pathologies import PatientPathology
from routes.common import HTTPResponses, BasicQueryParams, FieldsQueryParam, build_embed_query_param

router = APIRouter()


class PatientPathologyEmbedEnum(StrEnum):
    patient   = 'patient'
    pathology = 'pathology'


@router.get(
    '/patient-pathologies',
    response_model               = PatientPathology.SearchValidator,
    response_model_exclude_unset = True,
    summary                      = 'Search patient pathologies',
    description                  = 'Allows to perform patient pathologies search',
    response_description         = 'Patient pathology list',
    responses                    = {**HTTPResponses.search}
)
async def search_patient_pathologies(
        request        : Request,
        query_params   : BasicQueryParams = Depends(BasicQueryParams),
        embed          : str                        = Depends(build_embed_query_param(PatientPathologyEmbedEnum)),
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated),
        patient_id     : int = Query(None, description='Filter by patient ID'),
        pathology_id   : int = Query(None, description='Filter by pathology ID')
):
    options                   = query_params.get_dict()
    options['embed']          = embed
    options['auth_user_info'] = auth_user_info
    options['extra_args']     = {
        'patient_id': patient_id,
        'pathology_id': pathology_id
    }

    return await braceletCtrlProxy.search(PatientPathologyCtrl, request, **options)


@router.get(
    '/patient-pathologies/{record_id}',
    response_model               = PatientPathology.FullValidator,
    response_model_exclude_unset = True,
    summary                      = 'Get patient pathology',
    description                  = 'Returns a patient pathology record based on ID',
    response_description         = 'Patient pathology record',
    responses                    = {**HTTPResponses.get}
)
async def get_patient_pathology(
        record_id      : int                        = Path(..., description='Patient Pathology ID'),
        fields         : FieldsQueryParam           = Depends(FieldsQueryParam),
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {'auth_user_info': auth_user_info}

    return await braceletCtrlProxy.get(PatientPathologyCtrl, record_id, fields.fields, **options)


@router.delete(
    '/patient-pathologies/{record_id}',
    summary              = 'Delete patient pathology',
    description          = 'Allows to delete a patient pathology record',
    response_description = 'Empty',
    status_code          = HTTP_204_NO_CONTENT,
    responses            = {**HTTPResponses.delete},
    response_class       = Response
)
async def delete_patient_pathology(
        record_id      : int                        = Path(..., description='Patient Pathology ID to delete'),
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {'auth_user_info': auth_user_info}

    await braceletCtrlProxy.delete(PatientPathologyCtrl, record_id, **options)


@router.put(
    '/patient-pathologies/{record_id}',
    summary              = 'Update patient pathology',
    description          = 'Allows to perform full update of a patient pathology record',
    response_description = 'Empty',
    status_code          = HTTP_204_NO_CONTENT,
    responses            = {**HTTPResponses.put},
    response_class       = Response
)
async def update_patient_pathology(
        record         : PatientPathology.UpdateValidator,
        record_id      : int                        = Path(..., description='Patient Pathology ID'),
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {'auth_user_info': auth_user_info}
    await braceletCtrlProxy.update(PatientPathologyCtrl, record_id, record, **options)


@router.post(
    '/patient-pathologies',
    response_model               = PatientPathology.FullValidator,
    response_model_exclude_unset = True,
    summary                      = 'Create patient pathology',
    description                  = 'Creates a new patient pathology record',
    response_description         = 'Created patient pathology record',
    status_code                  = HTTP_201_CREATED,
    responses                    = {**HTTPResponses.post}
)
async def create_patient_pathology(
        record: PatientPathology.CreateValidator,
        auth_user_info: Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {'auth_user_info': auth_user_info}
    return await braceletCtrlProxy.create(PatientPathologyCtrl, record, **options)


@router.post(
    '/patient-pathologies/multi',
    response_model               = List[PatientPathology.FullValidator],
    response_model_exclude_unset = True,
    summary                      = 'Create multiple patient pathology',
    description                  = 'Creates a multiple new patient pathology record',
    response_description         = 'Created multiple patient pathology record',
    status_code                  = HTTP_201_CREATED,
    responses                    = {**HTTPResponses.post}
)
async def create_patient_pathologies_multi(patient_pathology_multi_in: PatientPathology.PatientPathologyMultiple):
    return await PatientPathologyCtrl.link_patient_pathologies(
        patient_pathology_multi_in.patient_id,
        patient_pathology_multi_in.pathologies
    )


@router.patch(
    '/patient-pathologies/{record_id}',
    response_model       = PatientPathology.FullValidator,
    summary              = 'Partial update patient pathology',
    description          = 'Allows to perform partial update of a patient pathology record',
    response_description = 'Record updated',
    responses            = {**HTTPResponses.put}
)
async def patch_patient_pathology(
        record_in      : PatientPathology.MergeValidator,
        record_id      : int                        = Path(..., description='Patient Pathology ID to update'),
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    record_in.id = record_id

    return await braceletCtrlProxy.merge(
        PatientPathologyCtrl,
        id             = record_id,
        data           = record_in,
        validate       = False,
        auth_user_info = auth_user_info
    )

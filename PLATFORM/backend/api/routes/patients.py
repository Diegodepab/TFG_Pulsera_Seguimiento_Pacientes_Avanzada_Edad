from typing import Dict, Union
from fastapi import APIRouter, Depends, Path, Response, Query
from starlette.requests import Request
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED

from controllers.bracelet_ctrl_proxy import braceletCtrlProxy
from lib import auth
from bracelet_lib.controllers.patients import PatientCtrl, GenderTypeCtrl
from bracelet_lib.models.common import StrEnum
from bracelet_lib.models.patients import Patient, GenderType
from routes.common import HTTPResponses, BasicQueryParams, FieldsQueryParam, build_embed_query_param

router = APIRouter()


class PatientEmbedEnum(StrEnum):
    patient_pathologies = 'patient_pathologies'
    # pathologies         = 'pathologies'
    patients_models     = 'patient_models'
    owner_user          = 'owner_user'


@router.get(
    '/patients/gender-types',
    response_model               = GenderType.SearchValidator,
    response_model_exclude_unset = True,
    summary                      = 'Get gender types',
    description                  = 'Allows to perform gender types search',
    response_description         = 'Gender types list allowed',
    responses                    = {**HTTPResponses.search}
)
async def search_gender_types(
        request        : Request,
        query_params   : BasicQueryParams = Depends(BasicQueryParams),
):
    options = query_params.get_dict()

    return await braceletCtrlProxy.search(GenderTypeCtrl, request, **options)


@router.get(
    '/patients',
    response_model               = Patient.SearchValidator,
    response_model_exclude_unset = True,
    summary                      = 'Search patients',
    description                  = 'Allows to perform patients search',
    response_description         = 'Patient list',
    responses                    = {**HTTPResponses.search}
)
async def search_patients(
        request        : Request,
        query_params   : BasicQueryParams           = Depends(BasicQueryParams),
        embed          : str                        = Depends(build_embed_query_param(PatientEmbedEnum)),
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated),
        fts            : str                        = Query(
            None,
            description = 'Text for Full Text Search.',
            example     = '12234'
        )
):
    options                   = query_params.get_dict()
    options['embed']          = embed
    options['auth_user_info'] = auth_user_info
    options['extra_args']     = {
        'fts': fts
    }

    return await braceletCtrlProxy.search(PatientCtrl, request, **options)


@router.get(
    '/patients/myinfo',
    response_model               = Patient.FullValidator,
    response_model_exclude_unset = True,
    summary                      = 'Get my patient information',
    description                  = 'Returns the patient record associated with the authenticated user account',
    response_description         = 'Patient record for the authenticated user',
    responses                    = {**HTTPResponses.get}
)
async def get_my_patient_info(
        embed          : str                        = Depends(build_embed_query_param(PatientEmbedEnum)),
        fields         : FieldsQueryParam           = Depends(FieldsQueryParam),
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    """
    Endpoint específico para que los pacientes accedan a su propia información.
    Solo funciona si el usuario autenticado tiene rol 'patient' y existe un registro
    de paciente con patient_user_id igual al ID del usuario autenticado.
    """
    user_role = auth_user_info.get('user_role')
    user_id = auth_user_info.get('user_id')
    
    # Verificar que el usuario sea un paciente
    if user_role != 'patient':
        from fastapi import HTTPException
        from starlette.status import HTTP_403_FORBIDDEN
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Only patients can access this endpoint"
        )
    
    # Buscar el paciente asociado al usuario autenticado
    from bracelet_lib.models.query_builder import QueryBuilder
    
    builder = QueryBuilder(PatientCtrl.Model)
    builder = builder.add_where_condition(
        PatientCtrl.Model.Table.c.patient_user_id == user_id
    )
    
    options = {
        'embed': embed,
        'auth_user_info': auth_user_info,
        'extra_args': {
            'auth_user_info': auth_user_info
        }
    }
    
    # Buscar el paciente con embeds
    from bracelet_lib.services.utils.query_utils import QueryParamsEmbed
    embed_map = {}
    if embed:
        embed_map = QueryParamsEmbed.parse_embed_string(embed)
    
    # Buscar el paciente
    results, _ = await PatientCtrl.search(
        builder=builder,
        embed_map=embed_map,
        extra_args=options.get('extra_args', {}),
        limit=1
    )
    
    if not results:
        from fastapi import HTTPException
        from starlette.status import HTTP_404_NOT_FOUND
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="No patient record found for the authenticated user"
        )
    
    return results[0]


@router.get(
    '/patients/{patient_id}',
    response_model               = Patient.FullValidator,
    response_model_exclude_unset = True,
    summary                      = 'Get patient',
    description                  = 'Returns a patient record based on their ID',
    response_description         = 'Patient record',
    responses                    = {**HTTPResponses.get}
)
async def get_patient(
        patient_id      : int                        = Path(..., description='Patient ID'),
        embed           : str                        = Depends(build_embed_query_param(PatientEmbedEnum)),
        fields          : FieldsQueryParam           = Depends(FieldsQueryParam),
        auth_user_info  : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {
        'embed'          : embed,
        'auth_user_info' : auth_user_info
    }

    return await braceletCtrlProxy.get(PatientCtrl, patient_id, fields.fields, **options)


@router.delete(
    '/patients/{patient_id}',
    summary              = 'Delete patient',
    description          = 'Allows to perform delete a patient record',
    response_description = 'Empty',
    status_code          = HTTP_204_NO_CONTENT,
    responses            = {**HTTPResponses.delete},
    response_class       = Response
)
async def delete_patient(
        patient_id      : int                        = Path(..., description='Patient ID to delete'),
        auth_user_info  : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {
        'auth_user_info': auth_user_info
    }

    await braceletCtrlProxy.delete(PatientCtrl, patient_id, **options)


@router.put(
    '/patients/{patient_id}',
    summary              = 'Update patient',
    description          = 'Allows to perform full update of a patient record',
    response_description = 'Empty',
    status_code          = HTTP_204_NO_CONTENT,
    responses            = {**HTTPResponses.put},
    response_class       = Response
)
async def update_patient(
        patient         : Patient.UpdateValidator,
        patient_id      : int                        = Path(..., description='Patient ID'),
        auth_user_info  : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {'auth_user_info': auth_user_info}
    await braceletCtrlProxy.update(PatientCtrl, patient_id, patient, **options)


@router.post(
    '/patients',
    response_model               = Patient.FullValidator,
    response_model_exclude_unset = True,
    summary                      = 'Create patient',
    description                  = 'Creates a new patient record',
    response_description         = 'Created patient record',
    status_code                  = HTTP_201_CREATED,
    responses                    = {**HTTPResponses.post}
)
async def create_patient(
        patient: Patient.CreateValidator,
        auth_user_info: Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {'auth_user_info': auth_user_info}
    return await braceletCtrlProxy.create(PatientCtrl, patient, **options)


@router.patch(
    '/patients/{patient_id}',
    response_model       = Patient.FullValidator,
    summary              = 'Partial update patient',
    description          = 'Allows to perform partial update of a patient record',
    response_description = 'Record updated',
    responses            = {**HTTPResponses.put}
)
async def patch_patient(
        patient_in      : Patient.MergeValidator,
        patient_id      : int                        = Path(..., description='Patient ID to update'),
        auth_user_info  : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    patient_in.id = patient_id

    return await braceletCtrlProxy.merge(
        PatientCtrl,
        id             = patient_id,
        data           = patient_in,
        validate       = False,
        auth_user_info = auth_user_info
    )

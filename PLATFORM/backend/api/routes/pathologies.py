from typing import Dict, Union
from fastapi import APIRouter, Depends, Path, Response, Query
from starlette.requests import Request
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED

from controllers.bracelet_ctrl_proxy import braceletCtrlProxy
from lib import auth
from bracelet_lib.controllers.pathologies import PathologyCtrl
from bracelet_lib.models.common import StrEnum
from bracelet_lib.models.pathologies import Pathology
from routes.common import HTTPResponses, BasicQueryParams, FieldsQueryParam, build_embed_query_param

router = APIRouter()


class PathologyEmbedEnum(StrEnum):
    # patients            = 'patients',
    patient_pathologies = 'patient_pathologies'



@router.get(
    '/pathologies',
    response_model               = Pathology.SearchValidator,
    response_model_exclude_unset = True,
    summary                      = 'Search pathologies',
    description                  = 'Allows to perform pathologies search',
    response_description         = 'Pathology list',
    responses                    = {**HTTPResponses.search}
)
async def search_pathologies(
        request        : Request,
        query_params   : BasicQueryParams           = Depends(BasicQueryParams),
        embed          : str                        = Depends(build_embed_query_param(PathologyEmbedEnum)),
        auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated),
        fts            : str                        = Query(
            None,
            description = 'Text for Full Text Search.',
            example     = 'Diabetes'
        )
):
    options                   = query_params.get_dict()
    options['embed']          = embed
    options['auth_user_info'] = auth_user_info
    options['extra_args']     = {
        'fts': fts
    }

    return await braceletCtrlProxy.search(PathologyCtrl, request, **options)


@router.get(
    '/pathologies/{pathology_id}',
    response_model               = Pathology.FullValidator,
    response_model_exclude_unset = True,
    summary                      = 'Get pathology',
    description                  = 'Returns a pathology record based on their ID',
    response_description         = 'Pathology record',
    responses                    = {**HTTPResponses.get}
)
async def get_pathology(
        pathology_id    : int                        = Path(..., description='Pathology ID'),
        embed           : str                        = Depends(build_embed_query_param(PathologyEmbedEnum)),
        fields          : FieldsQueryParam           = Depends(FieldsQueryParam),
        auth_user_info  : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {
        'embed'          : embed,
        'auth_user_info' : auth_user_info
    }

    return await braceletCtrlProxy.get(PathologyCtrl, pathology_id, fields.fields, **options)


@router.delete(
    '/pathologies/{pathology_id}',
    summary              = 'Delete pathology',
    description          = 'Allows to perform delete a pathology record',
    response_description = 'Empty',
    status_code          = HTTP_204_NO_CONTENT,
    responses            = {**HTTPResponses.delete},
    response_class       = Response
)
async def delete_pathology(
        pathology_id    : int                        = Path(..., description='Pathology ID to delete'),
        auth_user_info  : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {
        'auth_user_info': auth_user_info
    }

    await braceletCtrlProxy.delete(PathologyCtrl, pathology_id, **options)


@router.put(
    '/pathologies/{pathology_id}',
    summary              = 'Update pathology',
    description          = 'Allows to perform full update of a pathology record',
    response_description = 'Empty',
    status_code          = HTTP_204_NO_CONTENT,
    responses            = {**HTTPResponses.put},
    response_class       = Response
)
async def update_pathology(
        pathology       : Pathology.UpdateValidator,
        pathology_id    : int                        = Path(..., description='Pathology ID'),
        auth_user_info  : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {'auth_user_info': auth_user_info}
    await braceletCtrlProxy.update(PathologyCtrl, pathology_id, pathology, **options)


@router.post(
    '/pathologies',
    response_model               = Pathology.FullValidator,
    response_model_exclude_unset = True,
    summary                      = 'Create pathology',
    description                  = 'Creates a new pathology record',
    response_description         = 'Created pathology record',
    status_code                  = HTTP_201_CREATED,
    responses                    = {**HTTPResponses.post}
)
async def create_pathology(
        pathology: Pathology.CreateValidator,
        auth_user_info: Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    options = {'auth_user_info': auth_user_info}
    return await braceletCtrlProxy.create(PathologyCtrl, pathology, **options)


@router.patch(
    '/pathologies/{pathology_id}',
    response_model       = Pathology.FullValidator,
    summary              = 'Partial update pathology',
    description          = 'Allows to perform partial update of a pathology record',
    response_description = 'Record updated',
    responses            = {**HTTPResponses.put}
)
async def patch_pathology(
        pathology_in     : Pathology.MergeValidator,
        pathology_id     : int                        = Path(..., description='Pathology ID to update'),
        auth_user_info   : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    pathology_in.id = pathology_id

    return await braceletCtrlProxy.merge(
        PathologyCtrl,
        id             = pathology_id,
        data           = pathology_in,
        validate       = False,
        auth_user_info = auth_user_info
    )

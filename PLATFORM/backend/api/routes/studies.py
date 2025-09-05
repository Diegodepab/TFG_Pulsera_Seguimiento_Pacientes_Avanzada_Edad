from typing import Dict, Union, List, Optional
from fastapi import APIRouter, Depends, Path, Query, Response
from starlette.requests import Request
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
import sqlalchemy as sa
from pydantic import BaseModel

from controllers.bracelet_ctrl_proxy import braceletCtrlProxy
from lib import auth

from bracelet_lib.controllers.studies import StudyCtrl
from bracelet_lib.models.studies import Study           # Pydantic con SearchValidator, FullValidator
from bracelet_lib.models.studies import Study as StudyModel  # SQLAlchemy model con .Table.c.ts, .Table.c.patient_id
from routes.common import HTTPResponses, BasicQueryParams, FieldsQueryParam, build_embed_query_param
from bracelet_lib.models.common import StrEnum
# Importa tu database_manager tal como lo hace tu base_ctrl
from bracelet_lib.models import database_manager
router = APIRouter()


class StudyEmbedEnum(StrEnum):
    patient = 'patient'


# ------------------------------------------------------------------
# Modelos Pydantic internos para /studies/dates
# ------------------------------------------------------------------
class StudyDateItem(BaseModel):
    studyDate: str           # fecha del estudio (p. ej. "2025-05-26")  
    count: int               # total de registros en esa fecha
    firstTime: str           # hora de la primera medición (p. ej. "08:01:40")
    lastTime: str            # hora de la última medición (p. ej. "22:59:14")
    lastStepCount: int       # step_count correspondiente a la última medición


class PagedStudyDates(BaseModel):
    items: List[StudyDateItem]
    cursor: Optional[str] = None


# ------------------------------------------------------------------
# 1) /studies → SearchValidator (añadimos filtros ts_from / ts_to)
# ------------------------------------------------------------------
@router.get(
    '/studies',
    response_model               = Study.SearchValidator,
    response_model_exclude_unset = True,
    summary                      = 'Search studies',
    description                  = 'Allows to perform studies search (con rangos de ts)',
    response_description         = 'Study list',
    responses                    = {**HTTPResponses.search}
)
async def search_studies(
    request        : Request,
    query_params   : BasicQueryParams = Depends(BasicQueryParams),
    embed          : str              = Depends(build_embed_query_param(StudyEmbedEnum)),
    auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated),
    patient_id     : Optional[int]    = Query(None, description='Filter by patient ID'),
    ts_from        : Optional[str]    = Query(None, description='Filter from timestamp (ISO8601)'),
    ts_to          : Optional[str]    = Query(None, description='Filter to timestamp (ISO8601)')
):
    opts = query_params.get_dict()
    opts['embed']          = embed
    opts['auth_user_info'] = auth_user_info

    # Pasar los filtros al controlador a través de extra_args
    opts['extra_args'] = opts.get('extra_args', {})
    
    if patient_id is not None:
        opts['extra_args']['patient_id'] = patient_id
    
    if ts_from:
        # Convertir string ISO8601 a datetime para PostgreSQL
        from datetime import datetime
        try:
            dt_from = datetime.fromisoformat(ts_from.replace('Z', '+00:00'))
            opts['extra_args']['ts_from'] = dt_from
        except ValueError as e:
            print(f"Error parsing ts_from '{ts_from}': {e}")
            # Si no se puede parsear, ignorar el filtro
        
    if ts_to:
        # Convertir string ISO8601 a datetime para PostgreSQL  
        from datetime import datetime
        try:
            dt_to = datetime.fromisoformat(ts_to.replace('Z', '+00:00'))
            opts['extra_args']['ts_to'] = dt_to
        except ValueError as e:
            print(f"Error parsing ts_to '{ts_to}': {e}")
            # Si no se puede parsear, ignorar el filtro

    return await braceletCtrlProxy.search(StudyCtrl, request, **opts)


# ------------------------------------------------------------------
# 2) /studies/dates → PagedStudyDates con items: [ { studyDate: ... } ]
# ------------------------------------------------------------------
@router.get(
    '/studies/dates',
    response_model               = PagedStudyDates,
    response_model_exclude_unset = True,
    summary                      = 'List study dates for a patient (paged)',
    description                  = 'Returns the unique study dates (YYYY-MM-DD) for a given patient, paginated',
    responses                    = {**HTTPResponses.search}
)
async def list_study_dates(
    request        : Request,
    query_params   : BasicQueryParams = Depends(BasicQueryParams),
    auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated),
    patient_id     : int              = Query(..., description='Patient ID to filter by'),
):
    opts = query_params.get_dict()
    opts['auth_user_info'] = auth_user_info

    # Expresiones que repiten "to_char(ts, 'YYYY-MM-DD')" en SQLAlchemy
    date_expr = sa.func.to_char(StudyModel.Table.c.ts, 'YYYY-MM-DD').label('study_date')
    # Conteo por partición (por día)
    count_over = sa.func.count().over(partition_by=date_expr).label('count')
    # Hora mínima y máxima en cada partición
    first_time_over = sa.func.to_char(
        sa.func.min(StudyModel.Table.c.ts).over(partition_by=date_expr),
        'HH24:MI:SS'
    ).label('firstTime')
    last_time_over = sa.func.to_char(
        sa.func.max(StudyModel.Table.c.ts).over(partition_by=date_expr),
        'HH24:MI:SS'
    ).label('lastTime')
    # Número de fila ordenado desc por ts dentro de cada partición “día”
    row_number_over = sa.func.row_number().over(
        partition_by=date_expr,
        order_by=StudyModel.Table.c.ts.desc()
    ).label('rn')
    # El step_count de la fila actual
    step_count_col = StudyModel.Table.c.step_count.label('lastStepCount')

    # Subconsulta donde cada fila de “study” tiene:
    #   ‣ study_date (texto 'YYYY-MM-DD')
    #   ‣ count  (cantidad total de filas de ese día)
    #   ‣ firstTime (hora de la fila más antigua de ese día)
    #   ‣ lastTime  (hora de la fila más reciente de ese día)
    #   ‣ lastStepCount (step_count de la fila actual; luego filtraremos para quedarnos con la rn=1)
    #   ‣ rn (1 si es la fila más reciente de ese día, 2 si es la siguiente, etc)
    subq = (
        sa.select([
            date_expr,
            count_over,
            first_time_over,
            last_time_over,
            step_count_col,
            row_number_over
        ])
        .where(StudyModel.Table.c.patient_id == patient_id)
    ).alias('subq')

    # Ahora, de esa subconsulta, nos quedamos solo con row_number = 1 (la fila que representa
    # la última medición de cada día). Esto nos da, por cada día:
    #   study_date, count, firstTime, lastTime, lastStepCount
    stmt = (
        sa.select([
            subq.c.study_date,
            subq.c.count,
            subq.c.firstTime,
            subq.c.lastTime,
            subq.c.lastStepCount,
        ])
        .where(subq.c.rn == 1)
        .order_by(sa.text('study_date DESC'))
        .limit(opts.get('limit'))
        .offset(opts.get('offset') or 0)
    )

    rows = await database_manager.get_db_conn().fetch_all(stmt)

    # Finalmente, mapear cada fila a StudyDateItem
    items = [
        StudyDateItem(
            studyDate = r['study_date'],
            count     = r['count'],
            firstTime = r['firstTime'],
            lastTime  = r['lastTime'],
            lastStepCount = r['lastStepCount']
        )
        for r in rows
    ]

    return {
        'items': items,
        'cursor': None,
    }


# ------------------------------------------------------------------
# Resto de endpoints CRUD para /studies/{...}
# ------------------------------------------------------------------
@router.get(
    '/studies/{study_id}',
    response_model               = Study.FullValidator,
    response_model_exclude_unset = True,
    summary                      = 'Get study',
    description                  = 'Returns a study record based on ID',
    response_description         = 'Study record',
    responses                    = {**HTTPResponses.get}
)
async def get_study(
    study_id       : int                        = Path(..., description='Study ID'),
    fields         : FieldsQueryParam           = Depends(FieldsQueryParam),
    auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    opts = {'auth_user_info': auth_user_info}
    return await braceletCtrlProxy.get(StudyCtrl, study_id, fields.fields, **opts)


@router.post(
    '/studies',
    response_model               = Study.FullValidator,
    response_model_exclude_unset = True,
    summary                      = 'Create study',
    description                  = 'Creates a new study record',
    response_description         = 'Created study record',
    status_code                  = HTTP_201_CREATED,
    responses                    = {**HTTPResponses.post}
)
async def create_study(
    study          : Study.CreateValidator,
    auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    opts = {'auth_user_info': auth_user_info}
    return await braceletCtrlProxy.create(StudyCtrl, study, **opts)


@router.put(
    '/studies/{study_id}',
    summary                      = 'Update study',
    description                  = 'Allows full update of a study record',
    response_description         = 'Empty',
    status_code                  = HTTP_204_NO_CONTENT,
    responses                    = {**HTTPResponses.put},
    response_class               = Response
)
async def update_study(
    study          : Study.UpdateValidator,
    study_id       : int                        = Path(..., description='Study ID'),
    auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    opts = {'auth_user_info': auth_user_info}
    await braceletCtrlProxy.update(StudyCtrl, study_id, study, **opts)


@router.patch(
    '/studies/{study_id}',
    response_model               = Study.FullValidator,
    summary                      = 'Partial update study',
    description                  = 'Allows partial update of a study record',
    response_description         = 'Record updated',
    responses                    = {**HTTPResponses.put}
)
async def patch_study(
    study_in       : Study.MergeValidator,
    study_id       : int                        = Path(..., description='Study ID to update'),
    auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    study_in.id = study_id
    return await braceletCtrlProxy.merge(
        StudyCtrl,
        id             = study_id,
        data           = study_in,
        validate       = False,
        auth_user_info = auth_user_info
    )


@router.delete(
    '/studies/{study_id}',
    summary                      = 'Delete study',
    description                  = 'Allows to delete a study record',
    response_description         = 'Empty',
    status_code                  = HTTP_204_NO_CONTENT,
    responses                    = {**HTTPResponses.delete},
    response_class               = Response
)
async def delete_study(
    study_id       : int                        = Path(..., description='Study ID to delete'),
    auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    opts = {'auth_user_info': auth_user_info}
    await braceletCtrlProxy.delete(StudyCtrl, study_id, **opts)

from typing import Dict, Union, List, Optional
from fastapi import APIRouter, Depends, Path, HTTPException
from pydantic import BaseModel, EmailStr
from starlette.requests import Request
from starlette.status import HTTP_201_CREATED

from fastapi import Query
from collections import OrderedDict

from lib import auth
from routes.common import BasicQueryParams, HTTPResponses
from controllers.bracelet_ctrl_proxy import braceletCtrlProxy
from bracelet_lib.controllers.chats import ChatCtrl
from bracelet_lib.controllers.users import UserAccountCtrl
from bracelet_lib.controllers.message import MessageCtrl
from bracelet_lib.models.chats import Chat
from bracelet_lib.models.users import UserAccount

router = APIRouter()

class ChatSummary(BaseModel):
    chat_id          : int
    other_user_id    : int
    other_first_name : str
    other_last_name  : str
    last_message     : Optional[str]
    last_message_ts  : Optional[str]

class ChatSummaryList(BaseModel):
    items    : List[ChatSummary]
    first    : Optional[str]
    next     : Optional[str]
    previous : Optional[str]

class ChatInit(BaseModel):
    other_user_id : Optional[int] = None
    second_user_id: Optional[int] = None  # Para chats entre dos usuarios específicos (solo admin)
    email         : Optional[EmailStr] = None
    first_name    : Optional[str] = None
    last_name     : Optional[str] = None

class ChatSummaryAnonymous(BaseModel):
    chat_id          : int
    administration   : bool
    last_message     : Optional[str]
    last_message_ts  : Optional[str]

class ChatSummaryAnonymousList(BaseModel):
    items    : List[ChatSummaryAnonymous]
    first    : Optional[str]
    next     : Optional[str]
    previous : Optional[str]

@router.get(
    '/chats/summary',
    response_model               = ChatSummaryList,
    response_model_exclude_unset = True,
    summary                      = 'Resumen de chats (usuario autenticado)',
    description                  = 'Lista los chats en los que participa el usuario autenticado',
    responses                    = {**HTTPResponses.search}
)
async def summary_chats_me(
    request        : Request,
    query_params   : BasicQueryParams           = Depends(BasicQueryParams),
    auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated),
    fts            : str                        = Query(
        None,
        description = 'Text for Full Text Search.',
        example     = 'Justin'
    )
):
    # Debug logging para entender problemas de autenticación
    print(f"DEBUG: Chat summary request - User ID: {auth_user_info.get('user_id')}, Role: {auth_user_info.get('user_role')}")
    
    # 1) Recogemos todos los parámetros de query
    options = query_params.get_dict()
    
    # 2) Extraemos y procesamos los parámetros de ordenamiento
    original_sort_by = options.get('sort_by')
    chat_level_sort = None
    summary_level_sort = []
    
    if original_sort_by:
        # Separamos ordenamientos que se pueden hacer a nivel de Chat vs ChatSummary
        sort_parts = [part.strip() for part in original_sort_by.split(',') if part.strip()]
        chat_sorts = []
        
        for part in sort_parts:
            field, direction = part.split(':')
            field = field.strip()
            direction = direction.strip()
            
            # Campos que existen en el modelo Chat
            if field in ['id', 'user1_id', 'user2_id', 'create_ts', 'update_ts']:
                chat_sorts.append(f"{field}:{direction}")
            # Campos que necesitamos manejar a nivel ChatSummary
            elif field in ['other_first_name', 'other_last_name', 'last_message', 'last_message_ts']:
                summary_level_sort.append((field, direction.lower()))
        
        # Solo pasamos ordenamientos válidos al nivel de Chat
        options['sort_by'] = ','.join(chat_sorts) if chat_sorts else None

    # 3) Configuramos la información de auth para el proxy
    options['auth_user_info']= auth_user_info
    
    # 4) Agregamos el filtro por user_id para que solo devuelva chats del usuario autenticado
    # Combinamos con cualquier extra_args existente y usamos el user_id del usuario autenticado
    existing_extra_args = options.get('extra_args', {})
    existing_extra_args['user_id'] = auth_user_info['user_id']
    options['extra_args'] = existing_extra_args
    
    # Eliminamos user_id de los parámetros de query normales si existe para evitar conflictos
    if 'user_id' in options:
        del options['user_id']

    # 6) Ejecutamos la búsqueda a través del proxy
    search_data = await braceletCtrlProxy.search(
        ChatCtrl,
        request,
        **options
    )


    # 7) Mapeamos cada Chat a ChatSummary
    summaries: List[ChatSummary] = []
    fts_lower = fts.lower() if fts else None
    for chat in search_data.items:
        other_id = chat.user2_id if chat.user1_id == auth_user_info['user_id'] else chat.user1_id
        user = await braceletCtrlProxy.get(
            UserAccountCtrl,
            other_id,
            auth_user_info = auth_user_info
        )
        messages, _ = await MessageCtrl.search(
            extra_args         = {'chat_id': chat.id},
            sort_map           = {'ts': 'desc'},  # Ordenar por timestamp descendente
            reverse_query_sort = False,
            limit              = 1,
            offset             = 0
        )
        last_msg = messages[0] if messages else None  # Tomar el primer elemento que ahora es el más reciente

        # Filtrado por fts (full text search) en nombre o apellido del otro usuario
        if fts_lower:
            nombre = (user.first_name or '').lower()
            apellido = (user.last_name or '').lower()
            if fts_lower not in nombre and fts_lower not in apellido:
                continue

        summaries.append(ChatSummary(
            chat_id          = chat.id,
            other_user_id    = user.id,
            other_first_name = user.first_name,
            other_last_name  = user.last_name,
            last_message     = last_msg.content if last_msg else None,
            last_message_ts  = last_msg.ts.isoformat() if last_msg else None
        ))

    # 8) Aplicamos ordenamiento a nivel de ChatSummary si es necesario
    if summary_level_sort:
        # Implementamos ordenamiento múltiple estable
        for field, direction in reversed(summary_level_sort):  # Aplicamos en orden inverso para ordenamiento estable
            reverse = (direction == 'desc')
            
            if field == 'other_first_name':
                summaries.sort(key=lambda s: (s.other_first_name or '').lower(), reverse=reverse)
            elif field == 'other_last_name':
                summaries.sort(key=lambda s: (s.other_last_name or '').lower(), reverse=reverse)
            elif field == 'last_message':
                summaries.sort(key=lambda s: (s.last_message or '').lower(), reverse=reverse)
            elif field == 'last_message_ts':
                summaries.sort(key=lambda s: s.last_message_ts or '', reverse=reverse)

    # 9) Sustituimos los items y devolvemos
    search_data.items = summaries  # type: ignore
    return search_data

@router.get(
    '/chats/test-auth',
    summary                      = 'Test de autenticación para chats',
    description                  = 'Endpoint simple para verificar autenticación'
)
async def test_chat_auth(
    auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    print(f"DEBUG TEST AUTH: User ID: {auth_user_info.get('user_id')}, Role: {auth_user_info.get('user_role')}")
    return {
        "message": "Authentication successful", 
        "user_id": auth_user_info.get('user_id'),
        "user_role": auth_user_info.get('user_role')
    }

@router.get(
    '/chats/summary/{user_id}',
    response_model               = ChatSummaryList,
    response_model_exclude_unset = True,
    summary                      = 'Resumen de chats (por ID de usuario)',
    description                  = 'Lista los chats en los que participa el usuario indicado',
    responses                    = {**HTTPResponses.search}
)
async def summary_chats_by_user(
    request        : Request,
    user_id        : int                       = Path(..., ge=1),
    query_params   : BasicQueryParams          = Depends(BasicQueryParams),
    auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    # Permisos: sólo admin o el propio usuario
    if auth_user_info['user_id'] != user_id and auth_user_info.get('user_role') != 'admin':
        raise HTTPException(403, detail="No tienes permisos para ver estos chats")
    # Reutilizar la misma lógica que summary_chats_me
    # Construimos un objeto Request "falso" con la misma URL y query params
    return await summary_chats_me(request, query_params, auth_user_info)

@router.post(
    '/chats',
    response_model               = Chat.FullValidator,
    response_model_exclude_unset = True,
    summary                      = 'Iniciar un chat',
    description                  = 'Crea un nuevo chat entre el usuario autenticado y otro usuario',
    status_code                  = HTTP_201_CREATED,
    responses                    = {**HTTPResponses.post}
)
async def initiate_chat(
    payload         : ChatInit,
    auth_user_info  : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    current_id = auth_user_info['user_id']
    current_role = auth_user_info.get('user_role')
    
    # Si se especifica second_user_id, es un chat entre dos usuarios específicos (solo admin)
    if payload.second_user_id:
        if current_role != 'admin':
            raise HTTPException(403, detail="Solo el admin puede crear chats entre otros usuarios")
        
        user1_id = payload.other_user_id
        user2_id = payload.second_user_id
        
        if not user1_id or not user2_id:
            raise HTTPException(400, detail="Debes proporcionar both other_user_id y second_user_id")
        
        if user1_id == user2_id:
            raise HTTPException(400, detail="No se puede crear un chat entre el mismo usuario")
        
        # IMPORTANTE: Ordenar los IDs para evitar duplicados (user1_id siempre menor)
        if user1_id > user2_id:
            user1_id, user2_id = user2_id, user1_id
        
        # Crear chat entre los dos usuarios especificados
        chat_data = Chat.CreateValidator(
            user1_id=user1_id,
            user2_id=user2_id
        )
        return await braceletCtrlProxy.create(
            ChatCtrl,
            chat_data,
            auth_user_info=auth_user_info
        )
    
    # Chat normal: entre el usuario actual y otro usuario
    other_id = payload.other_user_id
    if not other_id:
        if payload.email:
            user = await braceletCtrlProxy.get(
                UserAccountCtrl,
                payload.email,
                field_name      = 'email',
                auth_user_info  = auth_user_info
            )
            other_id = user.id
        elif payload.first_name and payload.last_name:
            users, _ = await UserAccountCtrl.search(
                where_conds=[('first_name', {'eq': payload.first_name}),
                             ('last_name', {'eq': payload.last_name})]
            )
            if not users:
                raise HTTPException(404, detail="Usuario no encontrado")
            if len(users) > 1:
                raise HTTPException(400, detail="Hay varios usuarios con ese nombre")
            other_id = users[0].id
        else:
            raise HTTPException(400, detail="Debes proporcionar other_user_id, email o nombre completo")
    
    if other_id == current_id:
        raise HTTPException(400, detail="No puedes iniciar un chat contigo mismo")
    
    # IMPORTANTE: Ordenar los IDs para evitar duplicados (user1_id siempre menor)
    user1_id, user2_id = (current_id, other_id) if current_id < other_id else (other_id, current_id)
    
    chat_data = Chat.CreateValidator(
        user1_id=user1_id,
        user2_id=user2_id
    )
    return await braceletCtrlProxy.create(
        ChatCtrl,
        chat_data,
        auth_user_info=auth_user_info
    )

@router.get(
    '/chats/summary-anonymous',
    response_model               = ChatSummaryAnonymousList,
    response_model_exclude_unset = True,
    summary                      = 'Resumen anónimo de chats (usuario autenticado)',
    description                  = 'Lista los chats en los que participa el usuario autenticado sin mostrar información de otros participantes',
    responses                    = {**HTTPResponses.search}
)
async def summary_chats_anonymous(
    request        : Request,
    query_params   : BasicQueryParams           = Depends(BasicQueryParams),
    auth_user_info : Dict[str, Union[str, int]] = Depends(auth.check_user_authenticated)
):
    # Debug logging para entender problemas de autenticación
    print(f"DEBUG: Anonymous chat summary request - User ID: {auth_user_info.get('user_id')}, Role: {auth_user_info.get('user_role')}")
    
    # 1) Recogemos todos los parámetros de query
    options = query_params.get_dict()
    
    # 2) Configuramos la información de auth para el proxy
    options['auth_user_info'] = auth_user_info
    
    # 3) Agregamos el filtro por user_id para que solo devuelva chats del usuario autenticado
    existing_extra_args = options.get('extra_args', {})
    existing_extra_args['user_id'] = auth_user_info['user_id']
    options['extra_args'] = existing_extra_args
    
    # Eliminamos user_id de los parámetros de query normales si existe para evitar conflictos
    if 'user_id' in options:
        del options['user_id']

    # 4) Solo permitimos ordenamiento por campos simples del chat
    original_sort_by = options.get('sort_by')
    if original_sort_by:
        # Filtrar solo campos válidos para este endpoint
        valid_fields = ['id', 'create_ts', 'update_ts', 'administration']
        sort_parts = [part.strip() for part in original_sort_by.split(',') if part.strip()]
        valid_sorts = []
        
        for part in sort_parts:
            field, direction = part.split(':')
            field = field.strip()
            if field in valid_fields:
                valid_sorts.append(f"{field}:{direction}")
        
        options['sort_by'] = ','.join(valid_sorts) if valid_sorts else None

    try:
        # 5) Ejecutamos la búsqueda a través del proxy
        search_data = await braceletCtrlProxy.search(
            ChatCtrl,
            request,
            **options
        )

        # 6) Mapeamos cada Chat a ChatSummaryAnonymous (sin información de usuarios)
        summaries: List[ChatSummaryAnonymous] = []
        
        for chat in search_data.items:
            # Obtener el último mensaje sin necesidad de información del otro usuario
            messages, _ = await MessageCtrl.search(
                extra_args         = {'chat_id': chat.id},
                sort_map           = {'ts': 'desc'},
                reverse_query_sort = False,
                limit              = 1,
                offset             = 0
            )
            last_msg = messages[0] if messages else None

            summaries.append(ChatSummaryAnonymous(
                chat_id          = chat.id,
                administration   = chat.administration or False,  # Usar el campo booleano que acabamos de crear
                last_message     = last_msg.content if last_msg else None,
                last_message_ts  = last_msg.ts.isoformat() if last_msg else None
            ))

        # 7) Sustituimos los items y devolvemos
        search_data.items = summaries  # type: ignore
        return search_data
        
    except Exception as e:
        print(f"ERROR in anonymous chat summary: {e}")
        # En caso de error, devolver lista vacía
        return ChatSummaryAnonymousList(
            items=[],
            first=None,
            next=None,
            previous=None
        )

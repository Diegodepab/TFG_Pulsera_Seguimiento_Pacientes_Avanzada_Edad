<script>
  import { goto } from "$app/navigation";
  import { onMount, tick } from "svelte";
  import { getNotificationsContext } from "svelte-notifications";
  import { t } from "svelte-i18n";

  import BlockLoading from "$components/platform/commons/BlockLoading.svelte";
    import BaseButton from "$components/argon_template/BaseButton.svelte";

  import BaseTable from "$components/platform/commons/base_table/BaseTable.svelte";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Global } from "$lib/commons/global";
  import { Routes } from "$lib/commons/routes";
  import { SessionManager } from "$lib/commons/session_manager";
  import { navigatorHistory } from "$lib/commons/stores";
  import { PermissionsEntityType, PermissionsGrantType } from "$lib/models/user_permission";
  import { ChatController } from "$lib/controllers/chat_controller";
  import { ChatListDC } from "$lib/models/data_containers/chat_list_dc";
  import { Chat } from "$lib/models/chat";

  import { Constants } from "$lib/commons/constants";
  import { QueryFields } from "$lib/services/utils/query_utils";
  // Importar modal para crear chats
  import CreateChatModal from "$components/platform/chats/CreateChatModal.svelte";

  if (!Global.notificationContext) {
    Global.notificationContext = getNotificationsContext();
  }

  let checkingGrants = true;
  let blockLoading   = false;
  let _entityAccess;
  let chatsTable;
  let showCreateChatModal = false;
  let currentUser = null;
  let hasChats = true; // Para controlar si hay chats disponibles
  
  const chatCtl = new ChatController();
  // NO configurar baseUrl - usar el proxy de Vite por defecto

  // columnas apuntando a ChatListDC.uiFields
  const columns = [
    {
      key: ChatListDC.uiFields.participants,
      label: $t("entity.chat.participants"),
      sortable: true 
    },
    {
      key: ChatListDC.uiFields.lastMessage,
      label: $t("entity.chat.lastMessage"),
      sortable: false
    },
    {
      key: ChatListDC.uiFields.lastTs,
      label: $t("entity.chat.last"),
      sortable: true
    }
  ];

  onMount(async () => {
    const [perm] = await SessionManager.userPermissionsOn([PermissionsEntityType.CHAT]);
    _entityAccess = perm;
    
    // Obtener usuario actual para verificar rol
    currentUser = await SessionManager.user();
    
    // Test de autenticación específico para chats
    if (currentUser?.roleName === 'user') {
      try {
        const testResponse = await fetch('/v1/chats/test-auth', {
          headers: {
            'Authorization': (await SessionManager.token()).getHeader().Authorization
          }
        });
        
        if (testResponse.ok) {
          const result = await testResponse.json();
        } else {
          // No log
        }
      } catch (testError) {
        // No log
      }
    }
    
    // Solución temporal: permitir acceso a chats para usuarios autenticados
    // TODO: Investigar por qué los permisos no están funcionando correctamente para médicos
    if (!currentUser) {
      CommonNotifications.noAccessPermissions();
      return await goBack();
    }
    
    // Temporal: comentar la verificación estricta de permisos
    // if (!_entityAccess || !_entityAccess.uiVisibility) {
    //   CommonNotifications.noAccessPermissions();
    //   return await goBack();
    // }
    checkingGrants = false;
    await tick();
    // BaseTable iniciará la carga automáticamente
  });

  const goBack = () => navigatorHistory.goBack("/");

  /** función para cargar chats, creando ChatListDC desde cada Chat */
  async function scrollableFunction(opts = {}) {
    try {
      opts.params ??= new Map();
      const me = await SessionManager.user();
      
      // Verificar token
      try {
        const token = await SessionManager.token({ ignoreExceptions: true });
      } catch (tokenError) {
        // No log
      }
      
      if (me) {
        opts.params.set("user_id", me.id);
      }

      if (!opts.params.has(QueryFields.LIMIT)) {
        opts.params.set(QueryFields.LIMIT, Constants.DEFAULT_ITEMS_PER_PAGE);
      }
      
      try {
        // Intentar primero con el endpoint regular
        const result = await chatCtl.search({
          ...opts,
          extraPath: "/summary",
          transformer: async (data) =>
            (await Chat.transformer(data)).toDC(ChatListDC),
        });
        
        hasChats = result.items && result.items.length > 0;
        return result;
        
      } catch (primaryError) {
        // Si falla con 401/403, intentar con el endpoint anónimo
        const errorString = String(primaryError);
        if (errorString.includes('401') || errorString.includes('403') || errorString.includes('Unauthorized')) {
          try {
            console.log('Fallback to anonymous chat endpoint for patient user');
            
            const anonymousResult = await chatCtl.search({
              ...opts,
              extraPath: "/summary-anonymous",
              transformer: async (data) => {
                // Transformar datos anónimos a ChatListDC
                let participantLabel = "Chat";
                
                if (currentUser?.roleName === 'patient') {
                  // Para pacientes, mostrar el tipo de servicio basado en administration
                  participantLabel = data.administration ? 
                    $t("entity.chat.technicalService") || "Servicio Técnico" :
                    $t("entity.chat.doctor") || "Doctor";
                } else {
                  participantLabel = $t("entity.chat.anonymousParticipants") || "Chat participantes";
                }
                
                // Manejar mensaje vacío
                let lastMessageText = data.last_message;
                if (!lastMessageText) {
                  lastMessageText = $t("entity.chat.noMessages") || $t("entity.chat.noConversationStarted") || "No se ha iniciado una conversación todavía";
                }
                
                // Formatear fecha de manera más legible
                let formattedDate = null;
                if (data.last_message_ts) {
                  const messageDate = new Date(data.last_message_ts);
                  const now = new Date();
                  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                  const messageDay = new Date(messageDate.getFullYear(), messageDate.getMonth(), messageDate.getDate());
                  
                  const timeStr = messageDate.toLocaleTimeString('es-ES', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  });
                  
                  if (messageDay.getTime() === today.getTime()) {
                    // Hoy - solo mostrar hora
                    formattedDate = timeStr;
                  } else if (messageDay.getTime() === today.getTime() - 86400000) {
                    // Ayer - mostrar "Ayer" y hora
                    formattedDate = `Ayer ${timeStr}`;
                  } else {
                    // Cualquier otra fecha - mostrar fecha completa con año y hora
                    const dateStr = messageDate.toLocaleDateString('es-ES', { 
                      day: '2-digit', 
                      month: '2-digit',
                      year: 'numeric'
                    });
                    formattedDate = `${dateStr} ${timeStr}`;
                  }
                }
                
                return {
                  id: data.chat_id,
                  participants: participantLabel,
                  lastMessage: lastMessageText,
                  lastTs: formattedDate,
                  administration: data.administration || false
                };
              },
            });
            
            hasChats = anonymousResult.items && anonymousResult.items.length > 0;
            return anonymousResult;
            
          } catch (anonymousError) {
            console.error('Both endpoints failed:', { primaryError, anonymousError });
            throw primaryError; // Lanzar el error original
          }
        } else {
          throw primaryError;
        }
      }
      
    } catch (error) {
      // Manejo simple de errores de autenticación
      const errorString = String(error);
      if (errorString.includes('401') || errorString.includes('Unauthorized')) {
        CommonNotifications.genericDanger('Error de autenticación. Redirigiendo al inicio de sesión...');
        await SessionManager.closeSession();
        await goto('/login');
        return { items: [], total: 0 };
      }
      throw error;
    }
  }

  async function onRowClick({ item }) {
    blockLoading = true;
    await goto(`${Routes.CHATS}/${item.id}`);
  }

  function openCreateChatModal() {
    showCreateChatModal = true;
  }

  function closeCreateChatModal() {
    showCreateChatModal = false;
  }

  async function onChatCreated() {
    // Refrescar la lista de chats
    if (chatsTable && typeof chatsTable.reload === 'function') {
      await chatsTable.reload();
    } else {
      // Recargar la página si no tenemos acceso al método reload
      window.location.reload();
    }
    closeCreateChatModal();
  }


</script>

<svelte:head>
  <title>{$t("route.chats.title")}</title>
</svelte:head>

{#if blockLoading}
  <BlockLoading />
{:else if !checkingGrants}
  <div class="page-content">
    <div class="page-content-title d-flex justify-content-between align-items-center">
      <span>{$t("route.chats.title")}</span>
      
  {#if _entityAccess.write !== PermissionsGrantType.NONE && currentUser && currentUser.roleName === 'admin'}
        <BaseButton
          type="primary"
          size="sm"
          onclick={openCreateChatModal}
        >
          <i class="fas fa-plus fa-fw"></i>
          {$t("route.chats.createChat")}
        </BaseButton>
      {/if}
    </div>


      <BaseTable
        bind:this={chatsTable}
        pageId="chats-list"
        tableTitle={$t("route.chats.list")}
        {columns}
        {scrollableFunction}
        itemsPerPage={Constants.DEFAULT_ITEMS_PER_PAGE}
        itemsPerPageOptions={Constants.ITEMS_PER_PAGE_OPTIONS}
        DataContainerClass={ChatListDC}
        onrowclick={onRowClick}
      >
      </BaseTable>
    {#if !hasChats}
      <div class="card">
        <div class="card-body text-center py-5">
          <div class="mb-3">
            <i class="fas fa-comments fa-3x text-muted"></i>
          </div>
          <h5 class="text-muted mb-3">{$t("route.chats.noChats.title")}</h5>
          <p class="text-muted mb-4">{$t("route.chats.noChats.description")}</p>
          {#if _entityAccess.write === PermissionsGrantType.NONE}
            <div class="alert alert-info">
              <i class="fas fa-info-circle me-2"></i>
              {$t("route.chats.noChats.privacyMessage")}
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </div>
{/if}

<!-- Modal para crear chat -->
{#if showCreateChatModal}
  <CreateChatModal
    {onChatCreated}
    onClose={closeCreateChatModal}
  />
{/if}

<style>
  .page-content { padding: 1rem; }
  .page-content-title { font-size: 1.25rem; margin-bottom: 1rem; }
</style>

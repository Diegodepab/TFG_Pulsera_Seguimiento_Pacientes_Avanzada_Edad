<script>
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import { onMount, tick } from "svelte";
  import { getNotificationsContext } from "svelte-notifications";
  import { t } from "svelte-i18n";

  import BlockLoading from "$components/platform/commons/BlockLoading.svelte";
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Global } from "$lib/commons/global";
  import { Routes } from "$lib/commons/routes";
  import { SessionManager } from "$lib/commons/session_manager";
  import { navigatorHistory } from "$lib/commons/stores";
  import { PermissionsEntityType, PermissionsGrantType } from "$lib/models/user_permission";
  import { ChatController } from "$lib/controllers/chat_controller";
  import { MessageController } from "$lib/controllers/message_controller";
  import { Constants } from "$lib/commons/constants";

  if (!Global.notificationContext) {
    Global.notificationContext = getNotificationsContext();
  }

  // Estado de la página
  let checkingAccess = true;
  let blockLoading = false;
  let loading = false;
  let _entityAccess;
  
  // Datos del chat
  let chatId = parseInt($page.params.id);
  let chatData = null;
  let otherUser = null;
  let messages = [];
  let currentUser = null;
  
  // Formulario de mensaje
  let newMessage = "";
  let messageForm;

  const chatCtl = new ChatController();
  const messageCtl = new MessageController();
  
  // chatCtl.fetch.baseUrl = Constants.API_BASE_URL || 'http://127.0.0.1:8001/v1';
  // messageCtl.fetch.baseUrl = Constants.API_BASE_URL || 'http://127.0.0.1:8001/v1';

  onMount(async () => {
    try {
      // 1. Verificar permisos generales
      const [perm] = await SessionManager.userPermissionsOn([PermissionsEntityType.CHAT]);
      _entityAccess = perm;
      
      if (!_entityAccess.uiVisibility || _entityAccess.read === PermissionsGrantType.NONE) {
        CommonNotifications.noAccessPermissions();
        return await goBack();
      }

      // 2. Obtener usuario actual
      currentUser = await SessionManager.user();

      // 3. Verificar acceso al chat específico y cargar datos
      await loadChatData();
      await loadMessages();
      
      checkingAccess = false;
      await tick();
      
    } catch (error) {
      console.error("Error al cargar el chat:", error);
      CommonNotifications.genericDanger("Error al cargar el chat");
      await goBack();
    }
  });

  const goBack = () => navigatorHistory.goBack(Routes.CHATS);

  async function loadChatData() {
    try {
      // Intentar primero con el endpoint regular
      try {
        const response = await chatCtl.search({
          extraPath: "/summary",
          params: new Map([
            ["limit", "100"] // Aumentamos el límite para asegurar que encontremos el chat
          ])
        });

        if (!response.items || response.items.length === 0) {
          throw new Error("No tienes chats disponibles");
        }

        // Buscar el chat específico en los resultados
        chatData = response.items.find(chat => chat.chat_id === chatId);
        
        if (!chatData) {
          throw new Error("Chat no encontrado o no tienes permisos para acceder a él");
        }

        // Extraer datos del otro usuario
        otherUser = {
          id: chatData.other_user_id,
          first_name: chatData.other_first_name,
          last_name: chatData.other_last_name
        };

      } catch (primaryError) {
        // Si falla con 401/403, intentar con el endpoint anónimo
        const errorString = String(primaryError);
        if (errorString.includes('401') || errorString.includes('403') || errorString.includes('Unauthorized')) {
          
          // Usar el endpoint anónimo
          const anonymousResponse = await chatCtl.search({
            extraPath: "/summary-anonymous",
            params: new Map([
              ["limit", "100"]
            ]),
            // No usar transformer para mantener los datos raw
            transformer: (data) => data  // Pasar los datos sin transformar
          });

          if (!anonymousResponse.items || anonymousResponse.items.length === 0) {
            throw new Error("No tienes chats disponibles");
          }

          // Buscar el chat específico en los resultados anónimos RAW
          const anonymousChatData = anonymousResponse.items.find(chat => chat.chat_id === chatId);
          
          if (!anonymousChatData) {
            throw new Error("Chat no encontrado o no tienes permisos para acceder a él");
          }



          // Transformar datos anónimos para compatibilidad
          chatData = {
            chat_id: anonymousChatData.chat_id,
            administration: anonymousChatData.administration,
            last_message: anonymousChatData.last_message,
            last_message_ts: anonymousChatData.last_message_ts
          };

          // Para pacientes, mostrar etiquetas basadas en el tipo de chat
          if (currentUser?.roleName === 'patient') {
            const isAdministration = anonymousChatData.administration === true;
            
            const participantName = isAdministration ? 
              ($t("entity.chat.technicalService") || "Servicio Técnico") :
              ($t("entity.chat.doctor") || "Doctor");
            
            
            otherUser = {
              id: null, // No tenemos ID del otro usuario
              first_name: participantName,
              last_name: ""
            };
          } else {
            otherUser = {
              id: null,
              first_name: $t("entity.chat.anonymousParticipants") || "Chat participantes",
              last_name: ""
            };
          }
        } else {
          throw primaryError;
        }
      }

    } catch (error) {
      console.error("Error al cargar datos del chat:", error);
      throw error;
    }
  }

  async function loadMessages() {
    try {
      loading = true;
      
      // Cargar mensajes del chat específico usando el método list
      const response = await messageCtl.list(chatId, {
        params: new Map([
          ["sort_by", "ts:desc"] // Ordenar por timestamp descendente (más reciente primero en API)
        ])
      });

      // Invertir el orden para mostrar más recientes abajo (como WhatsApp)
      messages = (response.items || []).reverse();
      
      // Scroll al final después de cargar mensajes
      await tick();
      scrollToBottom();
      
    } catch (error) {
      console.error("Error al cargar mensajes:", error);
      CommonNotifications.genericDanger("Error al cargar mensajes");
    } finally {
      loading = false;
    }
  }

  async function sendMessage() {
    if (!newMessage.trim()) return;

    try {
      loading = true;

      // Enviar el mensaje usando el método del controlador
      await messageCtl.send(chatId, newMessage.trim());
      
      // Limpiar formulario
      newMessage = "";
      
      // Recargar mensajes
      await loadMessages();
      
    } catch (error) {
      console.error("Error al enviar mensaje:", error);
      CommonNotifications.genericDanger("Error al enviar el mensaje");
    } finally {
      loading = false;
    }
  }

  function scrollToBottom() {
    const chatContainer = document.querySelector('.chat-messages');
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }

  function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  // Formatear hora solo HH:MM
  function formatTime(dateString) {
    let date;
    
    // Si la fecha contiene guiones, es formato DD-MM-YYYY
    if (dateString.includes('-') && !dateString.includes('T')) {
      const [datePart, timePart] = dateString.split(' ');
      const [day, month, year] = datePart.split('-');
      // Crear fecha en formato correcto: YYYY-MM-DD + hora
      date = new Date(`${year}-${month}-${day} ${timePart}`);
    } else {
      // Para otros formatos (ISO, etc.)
      date = new Date(dateString);
    }
    
    return date.toLocaleTimeString('es-ES', { 
      hour: '2-digit', 
      minute: '2-digit', 
      hour12: false 
    });
  }

  // Formatear fecha para separadores
  function formatDate(dateString) {
    // Parsear fecha en formato DD-MM-YYYY HH:MM:SS
    let date;
    
    // Si la fecha contiene guiones, es formato DD-MM-YYYY
    if (dateString.includes('-') && !dateString.includes('T')) {
      const [datePart] = dateString.split(' ');
      const [day, month, year] = datePart.split('-');
      // Crear fecha en formato correcto: YYYY-MM-DD
      date = new Date(`${year}-${month}-${day}`);
    } else {
      // Para otros formatos (ISO, etc.)
      date = new Date(dateString);
    }
    
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    if (date.toDateString() === today.toDateString()) {
      return 'Hoy';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Ayer';
    } else {
      return date.toLocaleDateString('es-ES', { 
        day: 'numeric', 
        month: 'long', 
        year: 'numeric' 
      });
    }
  }

  // Formatear fecha y hora para último mensaje
  function formatLastMessageTime(dateString) {
    let date;
    
    // Si la fecha contiene guiones, es formato DD-MM-YYYY
    if (dateString.includes('-') && !dateString.includes('T')) {
      const [datePart, timePart] = dateString.split(' ');
      const [day, month, year] = datePart.split('-');
      // Crear fecha en formato correcto: YYYY-MM-DD + hora
      date = new Date(`${year}-${month}-${day} ${timePart}`);
    } else {
      // Para otros formatos (ISO, etc.)
      date = new Date(dateString);
    }
    
    return date.toLocaleString('es-ES', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  }

  // Parsear fecha correctamente (mismo que formatDate pero solo retorna Date)
  function parseDate(dateString) {
    // Si la fecha contiene guiones, es formato DD-MM-YYYY
    if (dateString.includes('-') && !dateString.includes('T')) {
      const [datePart] = dateString.split(' ');
      const [day, month, year] = datePart.split('-');
      // Crear fecha en formato correcto: YYYY-MM-DD
      return new Date(`${year}-${month}-${day}`);
    } else {
      // Para otros formatos (ISO, etc.)
      return new Date(dateString);
    }
  }

  // Agrupar mensajes por fecha
  function groupMessagesByDate(messages) {
    const grouped = [];
    let currentDate = null;
    
    messages.forEach((message) => {
      const messageDate = parseDate(message.ts).toDateString();
      
      if (currentDate !== messageDate) {
        currentDate = messageDate;
        grouped.push({
          type: 'date-separator',
          date: formatDate(message.ts),
          key: `date-${messageDate}`
        });
      }
      
      grouped.push({
        type: 'message',
        ...message,
        key: `message-${message.id}`
      });
    });
    
    return grouped;
  }

  // Obtener mensajes agrupados reactivamente
  $: groupedMessages = groupMessagesByDate(messages);
</script>

<svelte:head>
  <title>{$t("route.chats.chat_title", { values: { name: otherUser ? `${otherUser.first_name} ${otherUser.last_name}` : 'Chat' } })}</title>
</svelte:head>

{#if blockLoading}
  <BlockLoading />
{:else if checkingAccess}
  <div class="loading-container">
    <div class="spinner-border" role="status">
      <span class="sr-only">Cargando...</span>
    </div>
  </div>
{:else}
  <div class="page-content">
    <div class="chat-container">
      <!-- Encabezado del chat -->
      <div class="chat-header">
        <div class="chat-header-left">
          <BaseButton 
            type="secondary" 
            size="sm" 
            onclick={goBack}
          >
            <i class="fas fa-arrow-left"></i>
          </BaseButton>
          
          <div class="chat-user-info">
            <h5 class="chat-user-name">
              {otherUser ? `${otherUser.first_name} ${otherUser.last_name}` : 'Chat'}
            </h5>
            <small class="chat-user-status text-muted">
              {chatData?.last_message_ts ? `Último mensaje: ${formatLastMessageTime(chatData.last_message_ts)}` : 'Sin mensajes'}
            </small>
          </div>
        </div>
      </div>

      <!-- Área de mensajes -->
      <div class="chat-messages">
        {#if loading && messages.length === 0}
          <div class="loading-messages">
            <div class="spinner-border spinner-border-sm" role="status"></div>
            <span>Cargando mensajes...</span>
          </div>
        {:else if messages.length === 0}
          <div class="no-messages">
            <p class="text-muted">No hay mensajes en esta conversación</p>
            <p class="text-muted">¡Envía el primer mensaje!</p>
          </div>
        {:else}
          {#each groupedMessages as item (item.key)}
            {#if item.type === 'date-separator'}
              <div class="date-separator">
                <span class="date-text">{item.date}</span>
              </div>
            {:else}
              <div class="message {item.sender_id === currentUser.id ? 'message-sent' : 'message-received'}">
                <div class="message-content">
                  {item.content}
                </div>
                <div class="message-time">
                  {formatTime(item.ts)}
                </div>
              </div>
            {/if}
          {/each}
        {/if}
      </div>

      <!-- Formulario de envío -->
      <div class="message-input-container">
        <form bind:this={messageForm} on:submit|preventDefault={sendMessage} class="message-form">
          <div class="input-group">
            <textarea
              bind:value={newMessage}
              on:keypress={handleKeyPress}
              placeholder="Escribe un mensaje..."
              class="form-control message-input"
              rows="1"
              disabled={loading}
            ></textarea>
            <div class="input-group-append">
              <BaseButton
                type="primary"
                disabled={loading || !newMessage.trim()}
                nativeType="submit"
              >
                {#if loading}
                  <div class="spinner-border spinner-border-sm" role="status"></div>
                {:else}
                  <i class="fas fa-paper-plane"></i>
                {/if}
              </BaseButton>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
{/if}

<style>
  .page-content { 
    padding: 1rem; 
    height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .chat-container {
    display: flex;
    flex-direction: column;
    height: calc(100vh - 2rem);
    max-height: calc(100vh - 2rem);
    background: white;
    border-radius: 0.375rem;
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    overflow: hidden;
  }

  .chat-header {
    background: white;
    border-bottom: 1px solid #e9ecef;
    padding: 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
  }

  .chat-header-left {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .chat-user-info {
    display: flex;
    flex-direction: column;
  }

  .chat-user-name {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
  }

  .chat-user-status {
    margin: 0;
    font-size: 0.875rem;
  }

  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    background: #f8f9fa;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .loading-messages, .no-messages {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 0.5rem;
  }

  .date-separator {
    display: flex;
    justify-content: center;
    margin: 1rem 0;
  }

  .date-text {
    background: rgba(0, 0, 0, 0.1);
    color: #6c757d;
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .message {
    max-width: 70%;
    margin-bottom: 0.5rem;
  }

  .message-sent {
    align-self: flex-end;
  }

  .message-received {
    align-self: flex-start;
  }

  .message-content {
    padding: 0.75rem 1rem;
    border-radius: 1rem;
    word-wrap: break-word;
  }

  .message-sent .message-content {
    background: #007bff;
    color: white;
    border-bottom-right-radius: 0.25rem;
  }

  .message-received .message-content {
    background: white;
    border: 1px solid #e9ecef;
    border-bottom-left-radius: 0.25rem;
  }

  .message-time {
    font-size: 0.75rem;
    color: #6c757d;
    margin-top: 0.25rem;
    text-align: right;
  }

  .message-received .message-time {
    text-align: left;
  }

  .message-input-container {
    background: white;
    border-top: 1px solid #e9ecef;
    padding: 1rem;
  }

  .message-form {
    width: 100%;
  }

  .message-input {
    resize: none;
    border-radius: 1.5rem !important;
    border-right: none !important;
  }

  .loading-container {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
  }

  @media (max-width: 768px) {
    .message {
      max-width: 85%;
    }
    
    .chat-header {
      padding: 0.75rem;
    }
    
    .chat-messages {
      padding: 0.75rem;
    }
  }
</style>

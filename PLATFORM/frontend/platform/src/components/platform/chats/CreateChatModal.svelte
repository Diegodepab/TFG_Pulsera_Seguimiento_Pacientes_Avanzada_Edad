<script>
  import { t } from "svelte-i18n";
  import { UserController } from "$lib/controllers/user_controller";
  import { ChatController } from "$lib/controllers/chat_controller";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import BlockLoading from "$components/platform/commons/BlockLoading.svelte";
  import { QueryFields, QueryParamsRaw, QueryParamsSort } from "$lib/services/utils/query_utils";
  import { User } from "$lib/models/user";
  import { UserListDC } from "$lib/models/data_containers/user_list_dc";
  import { Constants } from "$lib/commons/constants";

  export let onChatCreated = () => {};
  export let onClose = () => {};

  let isLoading = false;
  let chatType = "personal"; // "personal" or "user"
  let searchQuery = "";
  let searchQuerySecond = "";
  let selectedUser = null;
  let selectedSecondUser = null;
  let users = [];
  let usersSecond = [];
  let isSearching = false;
  let isSearchingSecond = false;
  let searchTimeout = null;
  let searchTimeoutSecond = null;

  const userCtl = new UserController();
  const chatCtl = new ChatController();
  
  // NO configurar host - usar el proxy de Vite por defecto

  async function searchUsers() {
    if (!searchQuery.trim() || searchQuery.length < 2) {
      users = [];
      return;
    }

    isSearching = true;
    try {
      const params = new Map();
      
      // Usar QueryParamsRaw para fts como en PatientForm.svelte
      params.set(QueryFields.RAW, [new QueryParamsRaw({ field: "fts", value: searchQuery.trim() })]);
      params.set(QueryFields.LIMIT, 10);

      const result = await userCtl.search({
        params,
        transformer: async (data) => (await User.fromJson(data)).toDC(UserListDC),
      });

      users = result.items || [];
    } catch (error) {
      console.error("Error searching users:", error);
      CommonNotifications.genericDanger($t("route.chats.create.errorSearchingUsers"));
      users = [];
    } finally {
      isSearching = false;
    }
  }

  async function searchUsersSecond() {
    if (!searchQuerySecond.trim() || searchQuerySecond.length < 2) {
      usersSecond = [];
      return;
    }

    isSearchingSecond = true;
    try {
      const params = new Map();
      
      // Usar QueryParamsRaw para fts como en PatientForm.svelte
      params.set(QueryFields.RAW, [new QueryParamsRaw({ field: "fts", value: searchQuerySecond.trim() })]);
      params.set(QueryFields.LIMIT, 10);

      const result = await userCtl.search({
        params,
        transformer: async (data) => (await User.fromJson(data)).toDC(UserListDC),
      });

      usersSecond = result.items || [];
    } catch (error) {
      console.error("Error searching users:", error);
      CommonNotifications.genericDanger($t("route.chats.create.errorSearchingUsers"));
      usersSecond = [];
    } finally {
      isSearchingSecond = false;
    }
  }

  function onSearchInput() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(searchUsers, 300);
  }

  function onSearchInputSecond() {
    clearTimeout(searchTimeoutSecond);
    searchTimeoutSecond = setTimeout(searchUsersSecond, 300);
  }

  function selectUser(user) {
    selectedUser = user;
    searchQuery = `${user.firstName} ${user.lastName} (${user.email})`;
    users = [];
  }

  function selectSecondUser(user) {
    selectedSecondUser = user;
    searchQuerySecond = `${user.firstName} ${user.lastName} (${user.email})`;
    usersSecond = [];
  }

  function clearSelection() {
    selectedUser = null;
    searchQuery = "";
    users = [];
  }

  function clearSecondSelection() {
    selectedSecondUser = null;
    searchQuerySecond = "";
    usersSecond = [];
  }

  function changeChatType(newType) {
    chatType = newType;
    clearSelection();
    clearSecondSelection();
  }

  async function createPersonalChat() {
    if (!selectedUser) {
      CommonNotifications.genericDanger($t("route.chats.create.selectUser"));
      return;
    }

    isLoading = true;
    try {
      const chatData = {
        other_user_id: selectedUser.id // Chat entre el admin y el usuario seleccionado
      };

      const response = await chatCtl.createChat(chatData);
      
      if (response) {
        CommonNotifications.genericSuccess($t("route.chats.create.success"));
        onChatCreated();
      }
    } catch (error) {
      console.error("Error creating personal chat:", error);
      
      // Manejar específicamente el error 409 (chat ya existe)
      if (error.message?.includes("409") || 
          error.message?.includes("duplicate key") || 
          error.message?.includes("uq_chat_users") ||
          error.message?.includes("ya existe")) {
        CommonNotifications.genericWarning($t("route.chats.create.alreadyExists"));
        // Cerrar el modal ya que el chat existe
        onChatCreated();
      } else {
        CommonNotifications.genericDanger($t("route.chats.create.error"));
      }
    } finally {
      isLoading = false;
    }
  }

  async function createUserChat() {
    if (!selectedUser || !selectedSecondUser) {
      CommonNotifications.genericDanger($t("route.chats.create.selectFirstUser") + " y " + $t("route.chats.create.selectSecondUser"));
      return;
    }

    isLoading = true;
    try {
      const chatData = {
        other_user_id: selectedUser.id,
        second_user_id: selectedSecondUser.id // Chat entre dos usuarios específicos
      };


      const response = await chatCtl.createChat(chatData);
      
      if (response) {
        CommonNotifications.genericSuccess($t("route.chats.create.success"));
        onChatCreated();
      }
    } catch (error) {
      console.error("Error creating chat:", error);
      console.error("Error details:", {
        selectedUser: selectedUser,
        selectedSecondUser: selectedSecondUser,
        errorMessage: error.message
      });
      
      // Manejar específicamente el error 409 (chat ya existe)
      if (error.message?.includes("409") || 
          error.message?.includes("duplicate key") || 
          error.message?.includes("uq_chat_users") ||
          error.message?.includes("ya existe")) {
        
        const warningMessage = `El chat entre ${selectedUser.first_name} ${selectedUser.last_name} y ${selectedSecondUser.first_name} ${selectedSecondUser.last_name} ya existe`;
        CommonNotifications.genericSuccess(warningMessage + '. Puedes encontrarlo en tu lista de chats.');
        
        // Cerrar el modal ya que el chat existe
        setTimeout(() => {
          onChatCreated();
        }, 4000);
      } else {
        CommonNotifications.genericDanger($t("route.chats.create.error") + ': ' + error.message);
      }
    } finally {
      isLoading = false;
    }
  }

  function handleKeydown(event) {
    if (event.key === "Escape") {
      onClose();
    }
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<!-- Modal backdrop completamente opaco -->
<div class="chat-modal-backdrop" on:click={onClose}>
  <!-- Modal content -->
  <div class="chat-modal-container" on:click|stopPropagation>
    <div class="chat-modal-card">
      <!-- Header sólido -->
      <div class="chat-modal-header">
        <h3 class="chat-modal-title">
          <i class="fas fa-comments"></i>
          {$t("route.chats.create.title")}
        </h3>
        <button class="chat-close-btn" on:click={onClose} type="button">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <!-- Body con fondo sólido -->
      <div class="chat-modal-body">
        {#if isLoading}
          <BlockLoading />
        {:else}
          <!-- Selector de tipo de chat -->
          <div class="chat-type-selector">
            <h4 class="section-title">{$t("route.chats.create.chatType")}</h4>
            
            <div class="chat-type-options">
              <button 
                class="chat-type-option {chatType === 'personal' ? 'active' : ''}"
                on:click={() => changeChatType('personal')}
                type="button"
              >
                <i class="fas fa-user"></i>
                <div class="option-content">
                  <div class="option-title">{$t("route.chats.create.personalChat")}</div>
                  <div class="option-desc">{$t("route.chats.create.personalChatDesc")}</div>
                </div>
              </button>

              <button 
                class="chat-type-option {chatType === 'user' ? 'active' : ''}"
                on:click={() => changeChatType('user')}
                type="button"
              >
                <i class="fas fa-users"></i>
                <div class="option-content">
                  <div class="option-title">{$t("route.chats.create.userChat")}</div>
                  <div class="option-desc">{$t("route.chats.create.userChatDesc")}</div>
                </div>
              </button>
            </div>
          </div>

          <!-- Formulario según tipo de chat -->
          {#if chatType === "personal"}
            <!-- Chat entre admin y otro usuario -->
            <div class="user-search-section">
              <label class="form-label">
                {$t("route.chats.create.searchUser")}
              </label>
              <div class="input-container">
                <input
                  type="text"
                  class="form-input solid-input"
                  bind:value={searchQuery}
                  on:input={onSearchInput}
                  placeholder={$t("route.chats.create.searchPlaceholder")}
                  disabled={isLoading}
                />
                
                {#if isSearching}
                  <div class="input-spinner">
                    <div class="spinner"></div>
                  </div>
                {/if}

                {#if selectedUser}
                  <button
                    type="button"
                    class="clear-btn"
                    on:click={clearSelection}
                    title={$t("route.chats.create.clearSelection")}
                  >
                    <i class="fas fa-times"></i>
                  </button>
                {/if}
              </div>

              <!-- Resultados de búsqueda usuario -->
              {#if users.length > 0 && !selectedUser}
                <div class="search-results solid-results">
                  {#each users as user}
                    <button
                      type="button"
                      class="user-option solid-option"
                      on:click={() => selectUser(user)}
                    >
                      <div class="user-info">
                        <div class="user-name">{user.firstName} {user.lastName}</div>
                        <div class="user-email">{user.email}</div>
                        <span class="user-role">{user.roleName}</span>
                      </div>
                    </button>
                  {/each}
                </div>
              {/if}

              {#if searchQuery.length >= 2 && users.length === 0 && !isSearching && !selectedUser}
                <div class="no-results solid-text">
                  {$t("route.chats.create.noUsersFound")}
                </div>
              {/if}

              {#if selectedUser}
                <div class="selected-user solid-selected">
                  <i class="fas fa-check-circle"></i>
                  {$t("route.chats.create.selectedUser", { 
                    values: { 
                      name: `${selectedUser.firstName} ${selectedUser.lastName}`,
                      email: selectedUser.email 
                    }
                  })}
                </div>
              {/if}
            </div>
          {:else}
            <!-- Chat entre dos usuarios específicos -->
            <!-- Primer usuario -->
            <div class="user-search-section">
              <label class="form-label">
                {$t("route.chats.create.searchFirstUser")}
              </label>
              <div class="input-container">
                <input
                  type="text"
                  class="form-input solid-input"
                  bind:value={searchQuery}
                  on:input={onSearchInput}
                  placeholder={$t("route.chats.create.searchPlaceholder")}
                  disabled={isLoading}
                />
                
                {#if isSearching}
                  <div class="input-spinner">
                    <div class="spinner"></div>
                  </div>
                {/if}

                {#if selectedUser}
                  <button
                    type="button"
                    class="clear-btn"
                    on:click={clearSelection}
                    title={$t("route.chats.create.clearSelection")}
                  >
                    <i class="fas fa-times"></i>
                  </button>
                {/if}
              </div>

              <!-- Resultados de búsqueda primer usuario -->
              {#if users.length > 0 && !selectedUser}
                <div class="search-results solid-results">
                  {#each users as user}
                    <button
                      type="button"
                      class="user-option solid-option"
                      on:click={() => selectUser(user)}
                    >
                      <div class="user-info">
                        <div class="user-name">{user.firstName} {user.lastName}</div>
                        <div class="user-email">{user.email}</div>
                        <span class="user-role">{user.roleName}</span>
                      </div>
                    </button>
                  {/each}
                </div>
              {/if}

              {#if searchQuery.length >= 2 && users.length === 0 && !isSearching && !selectedUser}
                <div class="no-results solid-text">
                  {$t("route.chats.create.noUsersFound")}
                </div>
              {/if}

              {#if selectedUser}
                <div class="selected-user solid-selected">
                  <i class="fas fa-check-circle"></i>
                  {$t("route.chats.create.selectedFirstUser", { 
                    values: { 
                      name: `${selectedUser.firstName} ${selectedUser.lastName}`,
                      email: selectedUser.email 
                    }
                  })}
                </div>
              {/if}
            </div>

            <!-- Segundo usuario (obligatorio para chat entre usuarios) -->
            <div class="user-search-section">
              <label class="form-label">
                {$t("route.chats.create.searchSecondUser")}
              </label>
              <div class="input-container">
                <input
                  type="text"
                  class="form-input solid-input"
                  bind:value={searchQuerySecond}
                  on:input={onSearchInputSecond}
                  placeholder={$t("route.chats.create.searchPlaceholder")}
                  disabled={isLoading}
                />
                
                {#if isSearchingSecond}
                  <div class="input-spinner">
                    <div class="spinner"></div>
                  </div>
                {/if}

                {#if selectedSecondUser}
                  <button
                    type="button"
                    class="clear-btn"
                    on:click={clearSecondSelection}
                    title={$t("route.chats.create.clearSelection")}
                  >
                    <i class="fas fa-times"></i>
                  </button>
                {/if}
              </div>

              <!-- Resultados de búsqueda segundo usuario -->
              {#if usersSecond.length > 0 && !selectedSecondUser}
                <div class="search-results solid-results">
                  {#each usersSecond as user}
                    <button
                      type="button"
                      class="user-option solid-option"
                      on:click={() => selectSecondUser(user)}
                    >
                      <div class="user-info">
                        <div class="user-name">{user.firstName} {user.lastName}</div>
                        <div class="user-email">{user.email}</div>
                        <span class="user-role">{user.roleName}</span>
                      </div>
                    </button>
                  {/each}
                </div>
              {/if}

              {#if searchQuerySecond.length >= 2 && usersSecond.length === 0 && !isSearchingSecond && !selectedSecondUser}
                <div class="no-results solid-text">
                  {$t("route.chats.create.noUsersFound")}
                </div>
              {/if}

              {#if selectedSecondUser}
                <div class="selected-user solid-selected">
                  <i class="fas fa-check-circle"></i>
                  {$t("route.chats.create.selectedSecondUser", { 
                    values: { 
                      name: `${selectedSecondUser.firstName} ${selectedSecondUser.lastName}`,
                      email: selectedSecondUser.email 
                    }
                  })}
                </div>
              {/if}
            </div>
          {/if}
        {/if}
      </div>

      <!-- Footer sólido -->
      <div class="chat-modal-footer">
        <BaseButton
          type="secondary"
          onclick={onClose}
          disabled={isLoading}
        >
          {$t("common.button.cancel")}
        </BaseButton>
        
        {#if chatType === "personal"}
          <BaseButton
            type="primary"
            onclick={createPersonalChat}
            disabled={!selectedUser || isLoading}
          >
            {#if isLoading}
              <span class="btn-spinner"></span>
            {/if}
            {$t("route.chats.create.createPersonal")}
          </BaseButton>
        {:else}
          <BaseButton
            type="primary"
            onclick={createUserChat}
            disabled={!selectedUser || !selectedSecondUser || isLoading}
          >
            {#if isLoading}
              <span class="btn-spinner"></span>
            {/if}
            {$t("route.chats.create.createBetweenUsers")}
          </BaseButton>
        {/if}
      </div>
    </div>
  </div>
</div>

<style>
  /* Backdrop completamente sólido y opaco */
  .chat-modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.85); /* Más opaco para mayor contraste */
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000; /* Z-index más alto */
    padding: 1rem;
    backdrop-filter: blur(3px); /* Efecto de desenfoque para mayor separación */
  }

  .chat-modal-container {
    max-width: 600px;
    width: 100%;
    max-height: 95vh;
    overflow-y: auto;
  }

  /* Modal card completamente sólido */
  .chat-modal-card {
    background: #ffffff; /* Fondo blanco sólido */
    border-radius: 12px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5); /* Sombra más pronunciada */
    overflow: hidden;
    border: 2px solid #e9ecef; /* Borde para definir mejor */
  }

  /* Header con fondo sólido y contraste */
  .chat-modal-header {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    padding: 1.5rem 2rem;
    border-bottom: 2px solid #dee2e6;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .chat-modal-title {
    margin: 0;
    font-size: 1.4rem;
    font-weight: 700;
    color: #212529; /* Color negro sólido */
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .chat-modal-title i {
    color: #007bff;
    font-size: 1.2rem;
  }

  .chat-close-btn {
    background: #dc3545;
    border: none;
    color: white;
    cursor: pointer;
    padding: 0.5rem;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    transition: all 0.2s;
    font-size: 1.1rem;
  }

  .chat-close-btn:hover {
    background: #c82333;
    transform: scale(1.05);
  }

  /* Body con fondo sólido */
  .chat-modal-body {
    padding: 2rem;
    background: #ffffff;
    color: #212529;
  }

  /* Selector de tipo de chat */
  .chat-type-selector {
    margin-bottom: 2rem;
  }

  .section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #212529;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #007bff;
  }

  .chat-type-options {
    display: grid;
    gap: 1rem;
    grid-template-columns: 1fr;
  }

  .chat-type-option {
    background: #f8f9fa;
    border: 2px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
    cursor: pointer;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    gap: 1rem;
    text-align: left;
  }

  .chat-type-option:hover {
    background: #e9ecef;
    border-color: #007bff;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 123, 255, 0.2);
  }

  .chat-type-option.active {
    background: #007bff;
    border-color: #007bff;
    color: white;
    box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
  }

  .chat-type-option i {
    font-size: 1.5rem;
    color: #007bff;
    min-width: 30px;
  }

  .chat-type-option.active i {
    color: white;
  }

  .option-content {
    flex: 1;
  }

  .option-title {
    font-weight: 600;
    font-size: 1rem;
    margin-bottom: 0.3rem;
    color: #212529;
  }

  .chat-type-option.active .option-title {
    color: white;
  }

  .option-desc {
    font-size: 0.9rem;
    color: #6c757d;
  }

  .chat-type-option.active .option-desc {
    color: rgba(255, 255, 255, 0.9);
  }

  /* Secciones de búsqueda de usuarios */
  .user-search-section {
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
    border: 1px solid #dee2e6;
  }

  .form-label {
    display: block;
    margin-bottom: 0.75rem;
    font-weight: 600;
    color: #212529; /* Color negro sólido */
    font-size: 1rem;
  }

  .optional-text {
    color: #6c757d;
    font-weight: 400;
    font-size: 0.9rem;
  }

  .input-container {
    position: relative;
    margin-bottom: 1rem;
  }

  /* Input sólido */
  .solid-input {
    width: 100%;
    padding: 1rem;
    border: 2px solid #ced4da;
    border-radius: 8px;
    font-size: 1rem;
    line-height: 1.5;
    color: #212529; /* Texto negro sólido */
    background: #ffffff; /* Fondo blanco sólido */
    transition: all 0.2s;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .solid-input:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 0.25rem rgba(0, 123, 255, 0.25);
    background: #ffffff;
  }

  .input-spinner {
    position: absolute;
    top: 50%;
    right: 1rem;
    transform: translateY(-50%);
  }

  .spinner {
    width: 20px;
    height: 20px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #007bff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .clear-btn {
    position: absolute;
    top: 50%;
    right: 1rem;
    transform: translateY(-50%);
    background: #dc3545;
    border: none;
    color: white;
    font-size: 1rem;
    cursor: pointer;
    padding: 0.5rem;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    transition: all 0.2s;
  }

  .clear-btn:hover {
    background: #c82333;
    transform: translateY(-50%) scale(1.1);
  }

  /* Resultados de búsqueda sólidos */
  .solid-results {
    background: #ffffff;
    border: 2px solid #ced4da;
    border-radius: 8px;
    max-height: 200px;
    overflow-y: auto;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  }

  .solid-option {
    width: 100%;
    padding: 1rem;
    border: none;
    background: #ffffff;
    text-align: left;
    cursor: pointer;
    border-bottom: 1px solid #f8f9fa;
    transition: background 0.2s;
  }

  .solid-option:hover {
    background: #f8f9fa;
  }

  .solid-option:last-child {
    border-bottom: none;
  }

  .user-info {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
  }

  .user-name {
    font-weight: 600;
    color: #212529;
    font-size: 1rem;
  }

  .user-email {
    color: #6c757d;
    font-size: 0.9rem;
  }

  .user-role {
    background: #007bff;
    color: white;
    padding: 0.3rem 0.7rem;
    border-radius: 15px;
    font-size: 0.8rem;
    font-weight: 500;
    display: inline-block;
    margin-top: 0.3rem;
  }

  .solid-text {
    color: #6c757d;
    font-style: italic;
    padding: 1rem;
    text-align: center;
    background: #f8f9fa;
    border-radius: 6px;
    margin-top: 0.5rem;
  }

  /* Usuario seleccionado sólido */
  .solid-selected {
    background: #d4edda;
    color: #155724;
    padding: 1rem;
    border-radius: 8px;
    border: 2px solid #c3e6cb;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-top: 1rem;
    font-weight: 500;
  }

  .solid-selected i {
    color: #28a745;
    font-size: 1.2rem;
  }

  /* Footer sólido */
  .chat-modal-footer {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    padding: 1.5rem 2rem;
    border-top: 2px solid #dee2e6;
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
  }

  .btn-spinner {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid transparent;
    border-top: 2px solid currentColor;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-right: 0.5rem;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .chat-modal-container {
      margin: 0.5rem;
      max-width: none;
    }
    
    .chat-modal-header,
    .chat-modal-body,
    .chat-modal-footer {
      padding: 1rem;
    }
    
    .chat-type-options {
      grid-template-columns: 1fr;
    }
  }
</style>

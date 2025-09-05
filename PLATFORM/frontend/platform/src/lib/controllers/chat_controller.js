// src/lib/controllers/chat_controller.js
import { Constants } from "$lib/commons/constants";
import { BaseController } from "$lib/controllers/base_controller";
import { ChatFetch } from "$lib/services/fetch/chat_fetch";
import { QueryFields, QueryParamsEmbed } from "$lib/services/utils/query_utils";
import { SessionManager } from "$lib/commons/session_manager";
import { Chat } from "$lib/models/chat";
import { ChatListDC } from "$lib/models/data_containers/chat_list_dc";
import { QueryEncoder } from "$lib/services/utils/query_encoder";

export class ChatController extends BaseController {
  fetch;

  constructor() {
    super();
    this.fetch = new ChatFetch();
  }

  /**
   * Crea un nuevo chat entre usuarios
   * @param {Object} chatData - Datos del chat a crear
   * @returns {Promise<Object>} - Chat creado
   */
  async createChat(chatData) {
    await this.fetch.oauthHeader();
    
    // Usar URL relativa para aprovechar el proxy de Vite
    const url = `/v1/chats`;    
    const response = await this.fetch.doFetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...this.fetch.headers
      },
      body: JSON.stringify(chatData)
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    return await response.json();
  }
}

import { BaseDC } from "$lib/models/data_containers/base_dc";
import { Chat } from "$lib/models/chat";
import { QueryParamsSort } from "$lib/services/utils/query_utils";

/** @typedef {import("$lib/models/chat").Chat} Chat */

/**
 * Contenedor de datos para la lista de chats.
 * Convierte un Chat en propiedades UI: participantes, último mensaje y fecha.
 */
export class ChatListDC extends BaseDC {
  static uiFields = {
    id:           "id",
    participants: "participants",
    lastMessage:  "lastMessage",
    lastTs:       "lastTs",
  };

  /** @type {number} */
  id;
  /** @type {string} */
  participants;
  /** @type {string} */
  lastMessage;
  /** @type {string} */
  lastTs;

  /**
   * @param {Chat} chat
   */
  constructor(chat) {
    super();
    this.id = chat.chat_id;
    this.participants = `${chat.other_first_name} ${chat.other_last_name}`;
    this.lastMessage = chat.last_message || '(sin mensajes)';
    // formatear fecha ISO a local
    this.lastTs = chat.last_message_ts
      ? new Date(chat.last_message_ts).toLocaleString()
      : '';
  }

  /**
   * Parámetros de ordenación según UI field.
   */
  static getSortParamFromUiField(field, sort) {
    const map = new Map([
      [this.uiFields.id,           [Chat.apiFields.chat_id]],
      [this.uiFields.participants, [Chat.apiFields.other_first_name, Chat.apiFields.other_last_name]],
      [this.uiFields.lastMessage,  [Chat.apiFields.last_message]],
      [this.uiFields.lastTs,       [Chat.apiFields.last_message_ts]]
    ]);
    const apiFields = map.get(field) || [];
    return apiFields.map(f => new QueryParamsSort({ field: f, sort }));
  }
}

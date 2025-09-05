import { BaseModel } from "$lib/models/base_model";
import { User } from "$lib/models/user";

class ApiFields {
  /** @type {string} @readonly */
  static chat_id = "chat_id";
  /** @type {string} @readonly */
  static other_user_id = "other_user_id";
  /** @type {string} @readonly */
  static other_first_name = "other_first_name";
  /** @type {string} @readonly */
  static other_last_name = "other_last_name";
  /** @type {string} @readonly */
  static last_message = "last_message";
  /** @type {string} @readonly */
  static last_message_ts = "last_message_ts";
}

/**
 * Representa un chat resumido para la lista.
 * Incluye información del otro usuario y del último mensaje.
 */
export class Chat extends BaseModel {
  /** Referencia a campos de la API */
  static apiFields = ApiFields;

  /** @type {number} */
  chat_id;
  /** @type {number} */
  other_user_id;
  /** @type {string} */
  other_first_name;
  /** @type {string} */
  other_last_name;
  /** @type {string} */
  last_message;
  /** @type {string} */
  last_message_ts;

  /** Constructor a partir de JSON crudo de la API */
  constructor(data = {}) {
    super();
    this.chat_id = data[ApiFields.chat_id];
    this.other_user_id = data[ApiFields.other_user_id];
    this.other_first_name = data[ApiFields.other_first_name];
    this.other_last_name = data[ApiFields.other_last_name];
    this.last_message = data[ApiFields.last_message];
    this.last_message_ts = data[ApiFields.last_message_ts];
  }

  /**
   * Convierte JSON en instancia de Chat.
   * @param {Object} data JSON raw
   * @returns {Promise<Chat>}
   */
  static async fromJson(data) {
    return new Chat(data);
  }

  /**
   * Transformer para DataContainer.
   * @param {Object} data JSON raw
   * @returns {Promise<Chat>}
   */
  static transformer = async (data) => Chat.fromJson(data);

  /**
   * Convierte a JSON para envíos al servidor.
   */
  toDict() {
    return {
      [ApiFields.chat_id]: this.chat_id,
      [ApiFields.other_user_id]: this.other_user_id,
    };
  }
}

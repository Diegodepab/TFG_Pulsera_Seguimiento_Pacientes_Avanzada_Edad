import { BaseController } from "$lib/controllers/base_controller";
import { MessageFetch } from "$lib/services/fetch/message_fetch";
import { QueryFields, QueryParamsQ, QueryComparativeOperations } from "$lib/services/utils/query_utils";
import { Constants } from "$lib/commons/constants";
import { SessionManager } from "$lib/commons/session_manager";
import { Message } from "$lib/models/message";
import { MessageListDC } from "$lib/models/data_containers/message_list_dc";

export class MessageController extends BaseController {
  /** @type {MessageFetch} */
  fetch;

  constructor() {
    super();
    this.fetch = new MessageFetch();
  }

  /** Carga mensajes de un chat (orden ascendente por ts) */
  async list(chatId, opts = {}) {
    opts.params ??= new Map();
    await this.fetch.oauthHeader();

    // filtramos por chat_id usando QueryParamsQ
    const chatFilter = new QueryParamsQ({
      field: "chat_id",
      operation: QueryComparativeOperations.EQ,
      value: chatId
    });
    opts.params.set(QueryFields.Q, [chatFilter]);
    
    // límite generoso
    opts.params.set(QueryFields.LIMIT, Constants.DEFAULT_ITEMS_PER_PAGE.value);

    return this.fetch.search({
      ...opts,
      transformer: async (raw) => {
        const msg = await Message.transformer(raw);
        return msg.toDC(MessageListDC);
      },
    });
  }

  /** Envía un nuevo mensaje */
  async send(chatId, content) {
    await this.fetch.oauthHeader();
    
    // Obtener el usuario actual para el sender_id
    const currentUser = await SessionManager.user();
    
    // Crear timestamp sin zona horaria (formato ISO sin 'Z')
    const now = new Date();
    const timestamp = now.getFullYear() + '-' +
      String(now.getMonth() + 1).padStart(2, '0') + '-' +
      String(now.getDate()).padStart(2, '0') + 'T' +
      String(now.getHours()).padStart(2, '0') + ':' +
      String(now.getMinutes()).padStart(2, '0') + ':' +
      String(now.getSeconds()).padStart(2, '0') + '.' +
      String(now.getMilliseconds()).padStart(3, '0');
    
    const messageData = {
      chat_id: chatId,
      sender_id: currentUser.id,
      content,
      ts: timestamp,
    };
    
    return this.fetch.post(messageData);
  }
}

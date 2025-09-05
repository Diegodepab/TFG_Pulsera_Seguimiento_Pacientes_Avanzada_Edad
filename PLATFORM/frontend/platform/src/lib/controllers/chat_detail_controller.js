import { BaseController } from "$lib/controllers/base_controller";
import { MessageFetch } from "$lib/services/fetch/message_fetch";
import { QueryFields, QueryParamsQ } from "$lib/services/utils/query_utils";
import { Constants } from "$lib/commons/constants";
import { SessionManager } from "$lib/commons/session_manager";

class ChatDetailController extends BaseController {
  /** @type MessageFetch */
  fetch;

  constructor() {
    super();
    this.fetch = new MessageFetch();
  }

  /**
   * Carga los mensajes de un chat dado.
   * @param {number} chatId
   * @param {{ params?: Map<QueryFields, unknown> }} opts
   */
  async loadMessages(chatId, opts = {}) {
    opts.params ??= new Map();
    await this.fetch.oauthHeader();
    opts.params.set(QueryFields.Q, [
      new QueryParamsQ({ field: "chat_id", operation: QueryComparativeOperations.EQ, value: chatId })
    ]);
    if (!opts.params.has(QueryFields.LIMIT)) {
      opts.params.set(QueryFields.LIMIT, Constants.DEFAULT_ITEMS_PER_PAGE);
    }
    const result = await super.search({ ...opts, transformer: data => data });
    return result.items;
  }

  /** Envía un mensaje nuevo */
  async sendMessage(chatId, content) {
    await this.fetch.oauthHeader();
    const me = await SessionManager.userInfo();
    return super.create({ chat_id: chatId, sender_id: me.id, content, ts: new Date().toISOString() });
  }
}

export { ChatDetailController };
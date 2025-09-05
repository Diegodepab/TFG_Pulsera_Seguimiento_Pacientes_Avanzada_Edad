import { SessionManager } from "$lib/commons/session_manager";
import { Chat } from "$lib/models/chat";
import { Fetch } from "$lib/services/fetch/fetch";

class ChatFetch extends Fetch {
  /** @type string */
  path = "/chats";
  /** @type string */
  entity = "chat";
  /** @type ModelTransformer */
  transformer = Chat.transformer;

  constructor() {
    super();
    this.headers = super.headers ?? {};
  }

  /** @returns Promise<void> */
  oauthHeader = async () => {
    const authHeader = (await SessionManager.token()).getHeader();
    Object.entries(authHeader).forEach(([ key, value ]) => {
      this.headers[key] = value;
    });
  };
}

export { ChatFetch };

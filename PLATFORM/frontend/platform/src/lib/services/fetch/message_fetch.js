import { SessionManager } from "$lib/commons/session_manager";
import { Message } from "$lib/models/message";
import { Fetch } from "$lib/services/fetch/fetch";

class MessageFetch extends Fetch {
  /** @type string */
  path = "/messages";
  /** @type string */
  entity = "message";
  /** @type ModelTransformer */
  transformer = Message.transformer;

  constructor() {
    super();
    this.headers = super.headers ?? {};
  }

  /** @returns Promise<void> */
  oauthHeader = async () => {
    const authHeader = (await SessionManager.token()).getHeader();
    Object.entries(authHeader).forEach(([key, value]) => {
      this.headers[key] = value;
    });
  };
}

export { MessageFetch };
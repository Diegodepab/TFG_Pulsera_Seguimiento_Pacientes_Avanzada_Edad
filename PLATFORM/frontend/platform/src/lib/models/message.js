// src/lib/models/message.js
import { BaseModel } from "$lib/models/base_model";
import { User } from "$lib/models/user";
import { DateUtils } from "$lib/commons/utils";

class ApiFields {
  id       = "id";
  chatId   = "chat_id";
  senderId = "sender_id";
  content  = "content";
  ts       = "ts";
}

class ApiEmbeds {
  chat   = "chat";
  sender = "sender";
}

export class Message extends BaseModel {
  static apiFields = new ApiFields();
  static apiEmbeds = new ApiEmbeds();

  id;
  chat_id;
  sender_id;
  content;
  ts;
  chat;
  sender;

  constructor(data) {
    super();
    this.id        = data[Message.apiFields.id];
    this.chat_id   = data[Message.apiFields.chatId];
    this.sender_id = data[Message.apiFields.senderId];
    this.content   = data[Message.apiFields.content];
    this.ts        = data[Message.apiFields.ts];
  }

  /** Carga embeds */
  static async fromJson(data) {
    const msg = new Message(data);
    if (data[Message.apiEmbeds.sender]) {
      msg.sender = await User.fromJson(data[Message.apiEmbeds.sender]);
    }
    return msg;
  }

  /** ModelTransformer */
  static transformer = async (data) => Message.fromJson(data);

  toDict(opts) {
    const d = {};
    [
      [Message.apiFields.chatId,   this.chat_id],
      [Message.apiFields.senderId, this.sender_id],
      [Message.apiFields.content,  this.content],
      [Message.apiFields.ts,       this.ts],
    ].forEach(([k, v]) => {
      if (v != null) d[k] = v;
    });
    return d;
  }
}

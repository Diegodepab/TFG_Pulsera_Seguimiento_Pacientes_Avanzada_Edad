import { BaseDC } from "$lib/models/data_containers/base_dc";
import { DateUtils } from "$lib/commons/utils";

/** @typedef {import("$lib/models/message").Message} Message */

class UiFields {
  id       = "id";
  sender   = "sender";
  sender_id = "sender_id";
  content  = "content";
  ts       = "ts";
  mapUiApi = new Map([
    ["id",        { api: ["id"] }],
    ["sender",    { api: [] }],
    ["sender_id", { api: ["sender_id"] }],
    ["content",   { api: ["content"] }],
    ["ts",        { api: ["ts"] }],
  ]);
}

class MessageListDC extends BaseDC {
  static uiFields = new UiFields();

  /** @type number */
  id;
  /** @type string */
  sender;
  /** @type number */
  sender_id;
  /** @type string */
  content;
  /** @type string */
  ts;

  /**
   * @param {Message} msg
   */
  constructor(msg) {
    super();
    this.id      = msg.id;
    this.sender  = msg.sender?.fullName ?? "";
    this.sender_id = msg.sender_id;
    this.content = msg.content;
    // Formatear la fecha y hora
    const momentDate = DateUtils.momentOrNull(msg.ts);
    this.ts      = momentDate ? `${DateUtils.toDate(momentDate)} ${DateUtils.toTime(momentDate)}` : "";
  }

  static getSortParamFromUiField(field, sort) {
    return MessageListDC.uiFields.mapUiApi
      .get(field)
      .api.map(apiField => new QueryParamsSort({ field: apiField, sort }));
  }
}

export { MessageListDC };
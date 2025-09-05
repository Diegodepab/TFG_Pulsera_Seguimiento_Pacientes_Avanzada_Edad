import { SessionManager } from "$lib/commons/session_manager";
import { Instrument } from "$lib/models/instrument";
import { Fetch } from "$lib/services/fetch/fetch";

class InstrumentFetch extends Fetch {
  /** @type string */
  path = "/instruments";
  /** @type string */
  entity = "instrument";
  /** @type ModelTransformer */
  transformer = Instrument.transformer;

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

export { InstrumentFetch };

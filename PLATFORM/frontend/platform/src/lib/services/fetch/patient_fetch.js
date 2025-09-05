import { SessionManager } from "$lib/commons/session_manager";
import { Patient } from "$lib/models/patient";
import { Fetch } from "$lib/services/fetch/fetch";

class PatientFetch extends Fetch {
  /** @type string */
  path = "/patients";
  /** @type string */
  entity = "patient";
  /** @type ModelTransformer */
  transformer = Patient.transformer;

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

export { PatientFetch };

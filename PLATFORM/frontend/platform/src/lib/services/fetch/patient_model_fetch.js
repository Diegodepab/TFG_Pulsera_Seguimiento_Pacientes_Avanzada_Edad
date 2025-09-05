import { SessionManager } from "$lib/commons/session_manager";
import { PatientModel } from "$lib/models/patient_model";
import { Fetch } from "$lib/services/fetch/fetch";

class PatientModelFetch extends Fetch {
  /** @type string */
  path = "/patient-models";
  /** @type string */
  entity = "patient-model";
  /** @type ModelTransformer */
  transformer = PatientModel.transformer;

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

export { PatientModelFetch };

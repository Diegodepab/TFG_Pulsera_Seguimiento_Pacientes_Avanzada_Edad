import { SessionManager } from "$lib/commons/session_manager";
import { PatientPathology } from "$lib/models/patient_pathology";
import { Fetch } from "$lib/services/fetch/fetch";

class PatientPathologyFetch extends Fetch {
  /** @type string */
  path = "/patient-pathologies";
  /** @type string */
  entity = "patient-pathologies";
  /** @type ModelTransformer */
  transformer = PatientPathology.transformer;

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

export { PatientPathologyFetch };
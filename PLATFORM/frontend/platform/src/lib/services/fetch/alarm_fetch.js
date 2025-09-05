import { Fetch } from "$lib/services/fetch/fetch";
import { Alarm } from "$lib/models/alarm";

import { SessionManager } from "$lib/commons/session_manager";


class AlarmFetch extends Fetch {
  path        = "/alarms";
  entity      = "alarms";
  transformer = Alarm.transformer; // Así Fetch sabe cómo transformar cada ítem de JSON a Alarm

  constructor() {
    super();
    this.headers = super.headers ?? {};
  }

  /** @returns {Promise<void>} Inyecta el header OAuth en this.headers */
  oauthHeader = async () => {
    const authHeader = (await SessionManager.token()).getHeader();
    Object.entries(authHeader).forEach(([key, value]) => {
      this.headers[key] = value;
    });
  };


  /**
   * Opcional: si queremos un método específico “searchByPatient” con paginación,
   * pero podríamos usar directamente el método genérico `search` de BaseController
   * usando params={ patient_id: <...> }.
   *
   * Si lo quieres, déjalo así; si no, basta con usar la búsqueda genérica:
   *   new AlarmController().search({ params: new Map([[QueryFields.Q, [ ... ]]]) })
   */
  async searchByPatient(patientId, offset = null, limit = null) {
    await this.oauthHeader();
    const params = new URLSearchParams({ patient_id: String(patientId) });
    if (offset) params.set("offset", offset);
    if (limit)  params.set("limit", String(limit));
    const url = `${this.host}${this.path}?${params.toString()}`;
    const text = await this.getUrl(url);
    return JSON.parse(text);
  }
}

export { AlarmFetch };
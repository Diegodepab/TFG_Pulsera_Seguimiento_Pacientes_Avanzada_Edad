import { BaseController } from "$lib/controllers/base_controller";
import { StudyFetch } from "$lib/services/fetch/study_fetch";

class StudyController extends BaseController {
  /** @type {StudyFetch} */
  fetch;

  constructor() {
    super();
    this.fetch = new StudyFetch();
  }

  /**
   * List unique study dates for a given patient.
   * @param {number} patientId - The patient ID to filter by.
   * @returns {Promise<string[]>} Array of dates in "YYYY-MM-DD" format.
   */
  listStudyDates = async (patientId, cursor = null) => {
    // 1) Nos aseguramos de inyectar el header OAuth en this.fetch.headers
    await this.fetch.oauthHeader();
    // 2) Construimos la URL completa para getUrl (incluye host)
    const qp = new URLSearchParams({ patient_id: String(patientId) });
    if (cursor) qp.set("cursor", cursor);
    const url = `${this.fetch.host}${this.fetch.path}/dates?${qp.toString()}`;
    // 3) Hacemos la petición (ya con headers) y parseamos JSON
    const text = await this.fetch.getUrl(url);
    return JSON.parse(text);
  };
}

export { StudyController };

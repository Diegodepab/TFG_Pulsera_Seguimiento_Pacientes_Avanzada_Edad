import { BaseController } from "$lib/controllers/base_controller";
import { PatientPathologyMulti } from "$lib/models/patient_pathology_multi";
import { PatientPathologyFetch } from "$lib/services/fetch/patient_pathology_fetch";

class PatientPathologyController extends BaseController {
  /** @type PatientPathologyFetch */
  fetch;

  constructor() {
    super();
    this.fetch = new PatientPathologyFetch();
  }

  /**
   * Links multiple pathologies to the patient
   * @param {number} patientId - Patient id
   * @param {PatientPathology[]} patPathologies
   * @param {Object} [opts]
   * @param {ModelTransformer} [opts.transformer]
   * @returns Promise<unknown>
   */
  multiLinkPathologies = async (patientId, patPathologies, { transformer } = {}) => {
    const _multiData = new PatientPathologyMulti(patientId, patPathologies);
    const _transformer = async (data) => {
      return await Promise.all(data.map(async (item) => (transformer ?? this.fetch.transformer)(item)));
    };

    return (await this.post(_multiData, {
      extraPath: "/multi",
      transformer: _transformer,
    }));
  };
}

export { PatientPathologyController };

import { Constants } from "$lib/commons/constants";
import { BaseController } from "$lib/controllers/base_controller";
import { PatientPathologyController } from "$lib/controllers/patient_pathology_controller";
import { UserChildEntity } from "$lib/controllers/user_controller";
import { BaseSelectListDC } from "$lib/models/data_containers/base_select_list_dc";
import { PatientFetch } from "$lib/services/fetch/patient_fetch";
import { QueryFields } from "$lib/services/utils/query_utils";


class PatientController extends BaseController {
  /** @type {PatientFetch} */
  fetch;

  constructor() {
    super();
    this.fetch = new PatientFetch();
  }

  /**
   * Retrieves gender for a patient.
   * @param {Object} [opts] - Options for retrieving roles.
   * @param {Map<QueryFields, unknown>} [opts.params] - Parameters for the request.
   * @returns Promise<BaseSelectListDC[]> - A promise that resolves with an array of gender types.
   */
  getGenderTypes = async (opts) => {
    opts ??= {};
    opts.params ??= new Map();
    if (!opts.params.has(QueryFields.LIMIT)) {
      opts.params.set(QueryFields.LIMIT, Constants.PAGE_MAX_SIZE);
    }

    return (
      await this.search({
        params: opts.params,
        extraPath: "/gender-types",
        opEntity: UserChildEntity.USER_ROLE,
        transformer: (data) => {
          return new BaseSelectListDC({ value: data["name"] });
        },
      })
    ).items;
  };

  /**
   * Links multiple pathologies to the patient
   * @param {number} patientId - Patient id
   * @param {PatientPathology[]} patPathologies - Patient Pathologies for upload
   * @param {Object} [opts]
   * @param {ModelTransformer} [opts.transformer] - transformer for each result item inside multi response
   * @returns Promise<unknown>
   */
  multiLinkPathologies = async (patientId, patPathologies, { transformer } = {}) => {
    return await (new PatientPathologyController()).multiLinkPathologies(patientId, patPathologies, { transformer });
  };

  /**
   * Obtiene la información del paciente asociada al usuario autenticado
   * @param {Object} options - Opciones de la consulta
   * @returns {Promise<Patient>} - Información del paciente
   */
  async getMyInfo(options = {}) {
    // Usar 'myinfo' sin el prefijo 'patients/' ya que el controlador base ya lo incluye
    const response = await this.fetch.get('myinfo', options);
    return await Patient.transformer(response);
  }
}

export { PatientController };

import { BaseDC } from "$lib/models/data_containers/base_dc";
import { Pathology } from "$lib/models/pathology";
import { Patient } from "$lib/models/patient";
import { PatientPathology } from "$lib/models/patient_pathology";
import { QueryParamsSort } from "$lib/services/utils/query_utils";

/**
 * @typedef {import("moment").Moment} Moment
 */

class UiFields {
  /**
   * @readonly
   * @type string
   */
  id = "id";

  /**
   * @readonly
   * @type string
   */
  patientId = "patientId";

  /**
   * @readonly
   * @type string
   */
  pathologyId = "pathologyId";

  /**
   * @readonly
   * @type string
   */
  detectionDate = "detectionDate";

  /**
   * @readonly
   * @type string
   */
  pathologyName = "pathologyName";

  /**
   * @readonly
   * @type string
   */
  patientCode = "patientCode";

  /**
   * @readonly
   * @type UiApiMapping
   */
  mapUiApi = new Map([
    [ this.id, { api: [ PatientPathology.apiFields.id ] } ],
    [ this.patientId, { api: [ PatientPathology.apiFields.patientId ] } ],
    [ this.pathologyId, { api: [ PatientPathology.apiFields.pathologyId ] } ],
    [ this.detectionDate, { api: [ PatientPathology.apiFields.detectionDate ] } ],

    // embeds
    [ this.pathologyName, { api: [ Pathology.apiFields.name ] } ],
    [ this.patientCode, { api: [ Patient.apiFields.code ] } ],
  ]);
}

class PatientPathologyListDC extends BaseDC {
  /**
   * @type UiFields
   * @readonly
   */
  static uiFields = new UiFields();

  /**
   * @type {number | undefined}
   * @readonly
   */
  id;

  /**
   * @type {number | undefined}
   * @readonly
   */
  patientId;

  /**
   * @type {number | undefined}
   * @readonly
   */
  pathologyId;

  /**
   * @type {Moment | undefined}
   * @readonly
   */
  detectionDate;

  // embeds
  /**
   * @type {string | undefined}
   * @readonly
   */
  pathologyName;

  /**
   * @type {string | undefined}
   * @readonly
   */
  patientCode;

  /**
   * Relates a pathology to a patient.
   * @param {Object} opts - The options for relates the Pathologies with patient.
   * @param {number} [opts.id] - The PatientPathology's identifier.
   * @param {number} [opts.patientId] - Patient ID.
   * @param {number} [opts.pathologyId] - Pathology ID.
   * @param {Moment} [opts.detectionDate] - The PatientPathology's detectionDate.
   * @param {string} [opts.pathology] - The pathology embed.
   * @param {string} [opts.patient] - The patient embed.
   */
  constructor(opts) {
    super({});

    this.id = opts.id;
    this.patientId = opts.patientId;
    this.pathologyId = opts.pathologyId;
    this.detectionDate = opts.detectionDate;
    this.pathologyName = opts?.pathology?.name;
    this.patientCode = opts?.patient?.code;
  }

  /**
   * Gets the sort parameters from a UI field and sort order.
   * @param {string} field - The UI field to sort by.
   * @param {import("$lib/services/utils/query_utils").QuerySortOrder} sort - The sort order (ascending or descending).
   * @returns QueryParamsSort[] - An array of sort parameters.
   */
  static getSortParamFromUiField = (field, sort) => {
    return PatientPathologyListDC.uiFields.mapUiApi
      .get(field)
      .api.map((apiField) => new QueryParamsSort({ field: apiField, sort }));
  };
}

export { PatientPathologyListDC };

import { BaseDC } from "$lib/models/data_containers/base_dc";
import { Patient } from "$lib/models/patient";
import { PatientModel } from "$lib/models/patient_model";
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
  name = "name";

  /**
   * @readonly
   * @type string
   */
  createTs = "createTs";

  /**
   * @readonly
   * @type string
   */
  updateTs = "updateTs";

  // embeds
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
    [ this.id, { api: [ PatientModel.apiFields.id ] } ],
    [ this.patientId, { api: [ PatientModel.apiFields.patientId ] } ],
    [ this.name, { api: [ PatientModel.apiFields.name ] } ],
    [ this.createTs, { api: [ PatientModel.apiFields.createTs ] } ],
    [ this.updateTs, { api: [ PatientModel.apiFields.updateTs ] } ],

    // embeds
    [ this.patientCode, { api: [ Patient.apiFields.code ] } ],
  ]);
}

class PatientModelListDC extends BaseDC {
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
   * @type string
   * @readonly
   */
  name;

  /**
   * @type string
   * @readonly
   */
  data;

  /**
   * @type {Moment | undefined}
   * @readonly
   */
  createTs;

  /**
   * @type {Moment | undefined}
   * @readonly
   */
  updateTs;

  // embeds
  /**
   * @type {string | undefined}
   * @readonly
   */
  patientCode;

  /**
   * Constructs a new PatientModel object with the provided options.
   * @param {Object} opts - The options for creating the PatientModel object.
   * @param {number} [opts.id] - The model's identifier.
   * @param {string} [opts.name] - The model's name.
   * @param {string} [opts.data] - The data of model.
   * @param {Moment} [opts.createTs] - The timestamp when the model was created.
   * @param {Moment} [opts.updateTs] - The timestamp when the model was last updated.
   * @param {string} [opts.patient] - The patient embed.
   */
  constructor(opts) {
    super({});

    this.id = opts.id;
    this.name = opts.name;
    this.data = opts.data;
    this.createTs = opts.createTs;
    this.updateTs = opts.updateTs;
    this.patientCode = opts?.patient?.code;
  }

  /**
   * Gets the sort parameters from a UI field and sort order.
   * @param {string} field - The UI field to sort by.
   * @param {import("$lib/services/utils/query_utils").QuerySortOrder} sort - The sort order (ascending or descending).
   * @returns QueryParamsSort[] - An array of sort parameters.
   */
  static getSortParamFromUiField = (field, sort) => {
    return PatientModelListDC.uiFields.mapUiApi
      .get(field)
      .api.map((apiField) => new QueryParamsSort({ field: apiField, sort }));
  };
}

export { PatientModelListDC };

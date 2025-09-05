import { BaseDC } from "$lib/models/data_containers/base_dc";
import { Pathology } from "$lib/models/pathology";
import { PatientPathology } from "$lib/models/patient_pathology";
import { QueryParamsSort } from "$lib/services/utils/query_utils";

/**
 * @typedef {import("$lib/models/pathology").PathologyStatusType} PathologyStatusType
 * @typedef {import("moment").Moment} Moment
 */
class UiFields {
  /**
   * @type string
   * @readonly
   */
  id = "id";

  /**
   * @type string
   * @readonly
   */
  name = "name";

  /**
   * @type string
   * @readonly
   */
  detectionDate = "detectionDate";

  /**
   * @type string
   * @readonly
   */
  patientPathologies = "patientPathologies";

  /**
   * @readonly
   * @type UiApiMapping
   */
  mapUiApi = new Map([
    [ this.id, { api: [ Pathology.apiFields.id ] } ],
    [ this.name, { api: [ Pathology.apiFields.name ] } ],
    [ this.patientPathologies, { api: [ Pathology.apiEmbeds.patientPathologies ] } ],
    [ this.detectionDate, { api: [ PatientPathology.apiFields.detectionDate ] } ],
  ]);
}

class PathologySuggestionListDC extends BaseDC {
  /**
   * @type UiFields
   * @readonly
   */
  static uiFields = new UiFields();

  /**
   * @type number
   * @readonly
   */
  id;

  /**
   * @type string
   * @readonly
   */
  name;

  // embeds
  /**
   * @type Moment
   * @readonly
   */
  detectionDate;

  /**
   * Constructs a new Pathology object with the provided options.
   * @param {Object} opts - The options for creating the Pathology object.
   * @param {number} [opts.id] - The pathology's id.
   * @param {string} [opts.name] - The pathology's name.
   * @param {string} [opts.patientPathologies] - The pathology's patientPathologies.
   * @param {Moment} [opts.detectionDate] - The detection date.
   */
  constructor(opts) {
    super({});
    this.id = opts.id;
    this.name = opts.name;
    this.patientPathologies = opts.patientPathologies;
    this.detectionDate = opts.detectionDate;
  }

  /**
   * Gets the sort parameters from a UI field and sort order.
   * @param {string} field - The UI field to sort by.
   * @param {import("$lib/services/utils/query_utils").QuerySortOrder} sort - The sort order (ascending or descending).
   * @returns QueryParamsSort[] - An array of sort parameters.
   */
  static getSortParamFromUiField = (field, sort) => {
    return PathologySuggestionListDC.uiFields.mapUiApi
      .get(field)
      .api.map((apiField) => new QueryParamsSort({ field: apiField, sort }));
  };
}

export { PathologySuggestionListDC };

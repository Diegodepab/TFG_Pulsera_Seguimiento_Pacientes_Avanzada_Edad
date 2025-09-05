import { BaseDC } from "$lib/models/data_containers/base_dc";
import { Pathology } from "$lib/models/pathology";
import { QueryParamsSort } from "$lib/services/utils/query_utils";

/**
 * @typedef {import("$lib/models/pathology").PathologyStatusType} PathologyStatusType
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
  name = "name";

  /**
   * @readonly
   * @type string
   */
  updateTs = "updateTs";

  /**
   * @readonly
   * @type UiApiMapping
   */
  mapUiApi = new Map([
    [ this.id, { api: [ Pathology.apiFields.id ] } ],
    [ this.name, { api: [ Pathology.apiFields.name ] } ],
    [ this.updateTs, { api: [ Pathology.apiFields.updateTs ] } ],
  ]);
}

class PathologyListDC extends BaseDC {
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
   * @type {Moment | undefined}
   * @readonly
   */
  updateTs;

  /**
   * Constructs a new Pathology object with the provided options.
   * @param {Object} opts - The options for creating the Pathology object.
   * @param {number} [opts.id] - The pathology's identifier.
   * @param {string} [opts.name] - The pathology's name.
   * @param {Moment} [opts.detectionDate] - Pathology detection date.
   * @param {Moment} [opts.updateTs] - Relation last update ts.
   */
  constructor(opts) {
    super({});

    this.id = opts.id;
    this.name = opts.name;
    this.updateTs = opts.updateTs;
  }

  /**
   * Gets the sort parameters from a UI field and sort order.
   * @param {string} field - The UI field to sort by.
   * @param {import("$lib/services/utils/query_utils").QuerySortOrder} sort - The sort order (ascending or descending).
   * @returns QueryParamsSort[] - An array of sort parameters.
   */
  static getSortParamFromUiField = (field, sort) => {
    return PathologyListDC.uiFields.mapUiApi
      .get(field)
      .api.map((apiField) => new QueryParamsSort({ field: apiField, sort }));
  };
}

export { PathologyListDC };

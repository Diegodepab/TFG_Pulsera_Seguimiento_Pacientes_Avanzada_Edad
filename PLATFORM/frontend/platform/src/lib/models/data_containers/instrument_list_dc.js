import { BaseDC } from "$lib/models/data_containers/base_dc";
import { Instrument } from "$lib/models/instrument";
import { QueryParamsSort } from "$lib/services/utils/query_utils";

/**
 * @typedef {import("$lib/models/instrument").InstrumentStatusType} InstrumentStatusType
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
  model = "model";

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

  /**
   * @readonly
   * @type UiApiMapping
   */
  mapUiApi = new Map([
    [ this.id, { api: [ Instrument.apiFields.id ] } ],
    [ this.name, { api: [ Instrument.apiFields.name ] } ],
    [ this.model, { api: [ Instrument.apiFields.model ] } ],
    [ this.createTs, { api: [ Instrument.apiFields.createTs ] } ],
    [ this.updateTs, { api: [ Instrument.apiFields.updateTs ] } ],
  ]);
}

class InstrumentListDC extends BaseDC {
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
  model;

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

  /**
   * Constructs a new Instrument object with the provided options.
   * @param {Object} opts - The options for creating the Instrument object.
   * @param {number} [opts.id] - The instrument's identifier.
   * @param {string} [opts.name] - The instrument's name.
   * @param {string} [opts.model] - The instrument's model.
   * @param {Moment} [opts.createTs] - The timestamp when the instrument was created.
   * @param {Moment} [opts.updateTs] - The timestamp when the instrument was last updated.
   */
  constructor(opts) {
    super({});

    this.id = opts.id;
    this.name = opts.name;
    this.model = opts.model;
    this.createTs = opts.createTs;
    this.updateTs = opts.updateTs;
  }

  /**
   * Gets the sort parameters from a UI field and sort order.
   * @param {string} field - The UI field to sort by.
   * @param {import("$lib/services/utils/query_utils").QuerySortOrder} sort - The sort order (ascending or descending).
   * @returns QueryParamsSort[] - An array of sort parameters.
   */
  static getSortParamFromUiField = (field, sort) => {
    return InstrumentListDC.uiFields.mapUiApi
      .get(field)
      .api.map((apiField) => new QueryParamsSort({ field: apiField, sort }));
  };
}

export { InstrumentListDC };

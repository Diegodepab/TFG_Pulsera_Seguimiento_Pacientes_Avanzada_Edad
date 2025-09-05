import { BaseDC } from "$lib/models/data_containers/base_dc";

class ModelSuggestionListDC extends BaseDC {
  /** @type number **/
  id;
  /** @type string **/
  patientId;
  /** @type string **/
  name;
  /** @type string **/
  data;

  /**
   * @param {Object} opts - The options for creating the GenericModel object.
   * @param {number} [opts.id] - The Model's identifier.
   * @param {string} [opts.patientId] - Patient relation.
   * @param {string} [opts.name] - The Model's name.
   * @param {string} [opts.data] - The data of Model.
   */
  constructor(opts) {
    super({});

    this.id = opts.id;
    this.patientId = opts.patientId;
    this.name = opts.name;
    this.data = opts.data;
  }
}

export { ModelSuggestionListDC };

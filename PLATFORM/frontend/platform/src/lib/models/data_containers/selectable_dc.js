import { BaseDC } from "$lib/models/data_containers/base_dc";

class SelectableDC extends BaseDC {
  /** @type {string|undefined} */
  id;
  /** @type {string|undefined} */
  name;
  /** @type boolean */
  selected;

  /**
   * Creates an instance of SelectableDC.
   * @param {Object} opts - Options for creating the instance.
   * @param {string} [opts.id] - The ID of the selectable data class.
   * @param {string} [opts.name] - The name of the selectable data class.
   * @param {boolean} [opts.selected] - Indicates if the selectable data class is selected.
   */
  constructor(opts) {
    super({});

    this.id = opts.id;
    this.name = opts.name;
    this.selected = opts.selected;
  }
}

export { SelectableDC };

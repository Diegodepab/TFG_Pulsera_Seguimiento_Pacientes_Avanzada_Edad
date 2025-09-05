import { BaseDC } from "$lib/models/data_containers/base_dc";

class BaseSelectListDC extends BaseDC {
  /**
   * @type unknown
   * NOTE: this DC is used to contain different types of values. That's why the "unknown" type is used
   */
  value;

  /**
   * Constructs a new instance of BaseSelectListDC.
   * @param {Object} opts - Options for initializing the data controller.
   * @param {unknown} [opts.value] - The value associated with the data controller.
   */
  constructor(opts) {
    super({});

    this.value = opts.value;
  }
}

export { BaseSelectListDC };

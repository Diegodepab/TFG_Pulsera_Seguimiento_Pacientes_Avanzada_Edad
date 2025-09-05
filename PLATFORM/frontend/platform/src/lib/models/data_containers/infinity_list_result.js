import { BaseDC } from "$lib/models/data_containers/base_dc";

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
}

class InfinityListResult extends BaseDC {
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
   * @type {string | undefined}
   * @readonly
   */
  name;

  /**
   * Constructs a InfinityListResult instance.
   * @param {number} id - The InfinityListResult's id
   * @param {string} name - The InfinityListResult's name.
   */
  constructor(id, name) {
    super({});

    this.id = id;
    this.name = name;
  }

  /**
   * Creates a InfinityListResult instance from SearchResults.
   * @param {Array<T>} data - It is an array of a generic type.
   * @returns Promise<InfinityListResult[]> - A promise that resolves to a InfinityListResult instance.
   */
  static fromJson = async (data) => {
    return await Promise.all(data.map((item) => new InfinityListResult(
      item[InfinityListResult.uiFields.id],
      item[InfinityListResult.uiFields.name],
    )));
  };
}

export { InfinityListResult };

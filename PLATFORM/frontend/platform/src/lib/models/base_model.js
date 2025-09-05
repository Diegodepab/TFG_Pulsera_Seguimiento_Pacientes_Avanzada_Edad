/**
 * @typedef {import("$lib/models/data_containers/base_dc").BaseDC} BaseDC
 */

class ApiFields {
}

class ApiEmbeds {
}

class BaseModel {
  /**
   * @type ApiFields
   * @readonly
   */
  static apiFields = new ApiFields();
  /**
   * @type ApiEmbeds
   * @readonly
   */
  static apiEmbeds = new ApiEmbeds();

  /**
   * Creates a BaseModel or BaseDC instance from JSON data.
   * @param {Json} data - The JSON data.
   * @returns {Promise<BaseModel | BaseDC>} - A promise that resolves to a BaseModel or BaseDC instance.
   */
  static fromJson = async (data) => {
    return new BaseModel();
  };

  /**
   * Gets the value of an own property from an object if it exists, or returns null.
   * Similar to Object.prototype.hasOwnProperty but returns the value or null.
   *
   * @static
   * @param {Object} obj - The object to check for the property
   * @param {string} propertyName - The name of the property to retrieve
   * @return {*|null} - The value of the property if it exists, or null if it doesn't
   */
  static getOwnPropertyValue = (obj, propertyName) => {
    if (obj == null) {
      return null;
    }

    if (Object.prototype.hasOwnProperty.call(obj, propertyName)) {
      return obj[propertyName];
    }

    return null;
  };

  /**
   * Transforms JSON data into an instance of a specified type.
   * @template {BaseModel} T - The type of the instance to transform to.
   * @param {Json} data - The JSON data to transform.
   * @returns Promise<T> - The transformed instance.
   */
  static transformer = async (data) => await BaseModel.fromJson(data);

  /**
   * Creates a copy of the given BaseModel object.
   * @param {BaseModel} obj - The BaseModel object to copy.
   * @returns Promise<BaseModel> - A promise that resolves to a copy of the BaseModel object.
   */
  static copy = async (obj) => {
    return new BaseModel();
  };

  /**
   * Converts the OAuth instance to a dictionary representation.
   * @param {toDictModel} [opts] - Optional parameters.
   * @returns Json - The dictionary representation of the OAuth instance.
   */
  toDict = (opts) => {
    return {};
  };

  /**
   * Creates a BaseModel instance from JSON data.
   * @param {Json} data - The JSON data representing the BaseModel.
   * @returns Promise<BaseModel> - The BaseModel instance created from the JSON data.
   */
  fromJson = async (data) => undefined;

  /**
   * @template {BaseDC} T
   * @param {T} t
   * @returns T
   */
  toDC = (t) => {
    return new t(this);
  };

  toString() {
    return JSON.stringify(this);
  }
}


export { BaseModel };

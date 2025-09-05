import { QueryComparativeOperations, QueryParamsQ, QueryParamsSort } from "$lib/services/utils/query_utils";

/** @typedef {import("$lib/services/utils/query_utils").QuerySortOrder} QuerySortOrder */

/**
 * @typedef {Map<string, { api: string[] }>} UiApiMapping
 */

class BaseDC {
  /**
   * Constructs a new instance of BaseDC.
   * @param {unknown} opts - Options for initializing the data controller.
   */
  constructor(opts) {
  }

  /**
   * Generates sort parameters from the UI field and sort order.
   * @static
   * @param {string} field - The field to sort by.
   * @param {QuerySortOrder} sort - The sort order.
   * @returns QueryParamsSort[] - An array of sort parameters.
   */
  static getSortParamFromUiField = (field, sort) => {
    return [ new QueryParamsSort({ field, sort }) ];
  };

  /**
   * Generates query filters from UI field, value, and optional operation.
   * @static
   * @param {string} field - The field to filter by.
   * @param {(string | number)[]} value - The filter value(s).
   * @param {QueryComparativeOperations} [operation] - The comparative operation.
   * @returns QueryParamsQ[] - An array of query filters.
   */
  static getQFiltersFromUiField = (field, value, operation) => {
    operation ??= value.length > 1 ? QueryComparativeOperations.IN : QueryComparativeOperations.EQ;
    return [ new QueryParamsQ({ field, operation, value }) ];
  };

  /**
   * Gets the value of an own property from this instance if it exists, or returns null.
   * Instance method version of the static getOwnPropertyValue.
   *
   * @param {string} propertyName - The name of the property to retrieve
   * @return {*|null} - The value of the property if it exists, or null if it doesn't
   */
  getOwnPropertyValue(propertyName) {
    if (Object.prototype.hasOwnProperty.call(this, propertyName)) {
      return this[propertyName];
    }

    return null;
  }
}

/**
 * Gets the value of an own property from this instance if it exists, or returns null.
 * Instance method version of the static getOwnPropertyValue.
 *
 * @param {string} propertyName - The name of the property to retrieve
 * @return {*|null} - The value of the property if it exists, or null if it doesn't
 */


export { BaseDC };

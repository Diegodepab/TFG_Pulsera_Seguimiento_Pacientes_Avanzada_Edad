/**
 * @readonly
 * @enum string
 */
const BaseTableColFilterSelectionType = {
  SINGLE: "single",
  MULTI: "multi",
};

/**
 * Enum representing sort types.
 * @readonly
 * @enum {number}
 */
const BaseTableColSortType = {
  ASC: 0,
  DESC: 1,
  UN_SORT: 2,
};

/**
 * @typedef {Object} BaseTableColDefinition
 * @property {string} key - The key for the column.
 * @property {string} label - The label for the column.
 * @property {string} [width] - The width of the column (optional).
 * @property {boolean} [sortable] - Indicates if the column is sortable (optional).
 * @property {(item: ?) => string} [tdStyler] - Function to style the table cell (optional).
 * @property {(itemValue: ?) => string} [valueFormatter] - Function to format the value of the item (optional).
 * @property {(item: ?) => string} [customValue] - Function to provide custom value for the item (optional).
 * @property {boolean} [widgetColumn] - Indicates if the column is a widget column (optional).
 * @property {BaseTableColFilterSetting} [filterSettings] - Filter settings for the column (optional).
 */

/**
 * Represents settings for column filtering in a base table.
 * @typedef {Object} BaseTableColFilterSetting
 * @property {BaseTableColFilterSelectionType} selectionType - The selection type for column filtering.
 * @property {BaseTableColFilterScrollableFunction} scrollableFunction - The scrollable function for column filtering.
 * @property {boolean} [searchable] - Optional flag indicating if column is searchable.
 */

/**
 * Represents a function for scrolling through a base table.
 * @typedef {Function} BaseTableScrollableFunction
 * @param {Object} [opts] - Options for scrolling.
 * @param {string} [opts.page] - The page to scroll to.
 * @param {Map<QueryFields, ?>} [opts.params] - Additional parameters for scrolling.
 * @returns {Promise<SearchResults<BaseModel | BaseDC>>} - A promise that resolves with search results.
 */

/**
 * Represents a function for filtering and scrolling through a base table column.
 * @typedef {Function} BaseTableColFilterScrollableFunction
 * @param {string} [filter] - The filter to apply.
 * @returns {Promise<SearchResults<BaseModel | BaseDC> | SelectableDC[]>} - A promise that resolves with search results
 *   or an array of selectable DCs.
 */

/**
 * Represents a map for sorting columns in a base table.
 * @typedef {Map<string, BaseTableColSortType>} ColumnsSortMap
 */

/**
 * Represents a map for filtering columns in a base table with query parameters.
 * @typedef {Map<string, (string | number)[]>} ColumnsQFilterMap
 */

/**
 * Represents the data context for loading data.
 * @typedef {Object} LoadDataContext
 * @property {string} ftsText - The full-text search text.
 * @property {ColumnsSortMap} columnsSortMap - The map for sorting columns.
 * @property {ColumnsQFilterMap} columnsQFilterMap - The map for filtering columns with query parameters.
 * @property {string} [paginationPage] - The pagination page.
 */

export { BaseTableColSortType, BaseTableColFilterSelectionType };

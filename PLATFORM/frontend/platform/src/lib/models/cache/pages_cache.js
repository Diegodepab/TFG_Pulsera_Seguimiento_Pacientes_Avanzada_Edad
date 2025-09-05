/**
 * @typedef {import("$components/platform/commons/base_table/base_table_utils").LoadDataContext} LoadDataContext
 */

/**
 * Represents a cache for pages.
 * @typedef {Object} PageCache
 * @property {LoadDataContext} [loadDataContext] - The data context for loading data.
 * @property {Record<string, unknown>} - Additional properties for the cache.
 */

class PagesCache {
  /**
   * @private
   * @type {Map<string, PageCache>}
   */
  _cache = new Map();

  /** @returns {Map<string, PageCache>} */
  get cache() {
    return this._cache;
  }

  /** @param {Map<string, PageCache>} value */
  set cache(value) {
    this._cache = value;
  }
}

export { PagesCache };

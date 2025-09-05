import { Fetch } from "$lib/services/fetch/fetch";

class BaseController {
  /** @type {Fetch} */
  fetch;

  constructor() {
    this.fetch = new Fetch();
  }

  /**
   * Searches for data of type T.
   * @template {BaseModel | BaseDC} T - The type of data to search for, which extends BaseModel or BaseDC.
   * @param {Object} [opts] - Options for the search.
   * @param {string} [opts.page] - The page to search on.
   * @param {string} [opts.customPath] - A custom path for the search.
   * @param {string} [opts.extraPath] - An extra path for the search.
   * @param {Map<QueryFields, unknown>} [opts.params] - Parameters for the search.
   * @param {string} [opts.opEntity] - The operation entity for the search.
   * @param {ModelTransformer} [opts.transformer] - A transformer function for the search results.
   * @returns Promise<SearchResults<T>> - A promise that resolves with the search results of type T.
   */
  search = (opts) => this.fetch.search(opts);

  /**
   * Retrieves data of type T by ID.
   * @template {BaseModel | BaseDC} T - The type of data to retrieve, which extends BaseModel or BaseDC.
   * @param {string | number} id - The ID of the data to retrieve.
   * @param {Object} [opts] - Options for the retrieval.
   * @param {Map<QueryFields, unknown>} [opts.params] - Parameters for the retrieval.
   * @param {string} [opts.customPath] - A custom path for the retrieval.
   * @param {string} [opts.extraPath] - An extra path for the retrieval.
   * @param {string} [opts.opEntity] - The operation entity for the retrieval.
   * @param {ModelTransformer} [opts.transformer] - A transformer function for the retrieval result.
   * @returns Promise<T> - A promise that resolves with the retrieved data of type T.
   */
  get = (id, opts) => this.fetch.get(id, opts);

  /**
   * Posts data of type T.
   * @template {BaseModel | BaseDC} T - The type of data to post, which extends BaseModel or BaseDC.
   * @param {BaseModel} model - The model data to post.
   * @param {Object} [opts] - Options for the post request.
   * @param {string} [opts.customPath] - A custom path for the post request.
   * @param {string} [opts.extraPath] - An extra path for the post request.
   * @param {string} [opts.opEntity] - The operation entity for the post request.
   * @param {ModelTransformer} [opts.transformer] - A transformer function for the post request.
   * @param {Record<string, string>} [opts.headers] - Additional headers for the post request.
   * @returns {Promise<T | boolean>} - A promise that resolves with the posted data of type T, or a boolean indicating
   *   success.
   */
  post = (model, opts) => {

    return this.fetch.post(model.toDict(), opts);
  };

  /**
   * Updates data of type T by ID.
   * @template {BaseModel | BaseDC} T - The type of data to update, which extends BaseModel or BaseDC.
   * @param {string | number} id - The ID of the data to update.
   * @param {BaseModel} model - The model data to update.
   * @param {Object} [opts] - Options for the update request.
   * @param {string} [opts.customPath] - A custom path for the update request.
   * @param {string} [opts.extraPath] - An extra path for the update request.
   * @param {Map<QueryFields, unknown>} [opts.params] - Parameters for the update request.
   * @param {string} [opts.opEntity] - The operation entity for the update request.
   * @param {ModelTransformer} [opts.transformer] - A transformer function for the update request.
   * @param {Record<string, string>} [opts.headers] - Additional headers for the update request.
   * @returns {Promise<T | boolean>} - A promise that resolves with the updated data of type T, or a boolean indicating
   *   success.
   */
  put = (id, model, opts) => {
    return this.fetch.put(id, model.toDict({ ignoreEmbeds: true, ignoreNullValues: false }), opts);
  };

  /**
   * Partially updates data of type T by ID.
   * @template {BaseModel | BaseDC} T - The type of data to partially update, which extends BaseModel or BaseDC.
   * @param {string | number} id - The ID of the data to partially update.
   * @param {BaseModel} model - The model data to use for the partial update.
   * @param {Object} [opts] - Options for the partial update request.
   * @param {string} [opts.customPath] - A custom path for the partial update request.
   * @param {string} [opts.extraPath] - An extra path for the partial update request.
   * @param {Map<QueryFields, unknown>} [opts.params] - Parameters for the partial update request.
   * @param {string} [opts.opEntity] - The operation entity for the partial update request.
   * @param {ModelTransformer} [opts.transformer] - A transformer function for the partial update request.
   * @param {Record<string, string>} [opts.headers] - Additional headers for the partial update request.
   * @returns {Promise<T | boolean>} - A promise that resolves with the partially updated data of type T, or a boolean
   *   indicating success.
   */
  patch = (id, model, opts) => {
    return this.fetch.patch(id, model.toDict({ ignoreEmbeds: true, ignoreNullValues: false }), opts);
  };

  /**
   * Deletes data by ID.
   * @param {string | number} id - The ID of the data to delete.
   * @param {Object} [opts] - Options for the delete request.
   * @param {string} [opts.customPath] - A custom path for the delete request.
   * @param {string} [opts.extraPath] - An extra path for the delete request.
   * @param {string} [opts.opEntity] - The operation entity for the delete request.
   * @param {Record<string, string>} [opts.headers] - Additional headers for the delete request.
   * @returns Promise<boolean> - A promise that resolves with a boolean indicating if the deletion was successful.
   */
  delete = (id, opts) => this.fetch.delete(id, opts);
}

export { BaseController };

import { BaseController } from "$lib/controllers/base_controller";
import { GrantType, Oauth } from "$lib/models/oauth";
import { OauthFetch } from "$lib/services/fetch/oauth_fetch";

/**
 * @typedef {import("$lib/models/base_model").BaseModel} BaseModel
 * @typedef {import("$lib/models/oauth_token").OauthToken} OauthToken
 * @typedef {import("$lib/models/search_results").SearchResults} SearchResults
 * @typedef {import("$lib/services/utils/query_utils").QueryFields} QueryFields
 * @typedef {import("$lib/models/data_containers/base_dc").BaseDC} BaseDC
 */

// noinspection JSUnusedLocalSymbols
class OauthController extends BaseController {
  /**
   * Instance of the OauthFetch class to perform OAuth requests.
   * @type {OauthFetch}
   */
  fetch;

  constructor() {
    super();
    this.fetch = new OauthFetch();
  }

  /**
   * Obtains an OAuth token using a username and password.
   * @param {string} username - The username.
   * @param {string} password - The password.
   * @param {Object} [opts] - Additional options.
   * @param {ScopeType} [opts.scope] - The scope of the token.
   * @returns Promise<OauthToken> - A promise that resolves with the OAuth token.
   */
  getToken = (username, password, opts) => {
    opts ??= {};
    const data = new Oauth(GrantType.PASSWORD, { username, password, ...opts }).toDict();
    return this.fetch.getToken(data);
  };

  /**
   * Refreshes an OAuth token using a refresh token.
   * @param {string} refreshToken - The refresh token.
   * @returns Promise<OauthToken> - A promise that resolves with the new OAuth token.
   */
  refreshToken = (refreshToken) => {
    const data = new Oauth(GrantType.REFRESH_TOKEN, { refreshToken }).toDict();
    return this.fetch.getToken(data);
  };

  /**
   * Verifies if an OAuth token is valid.
   * @param {string} token - The token to verify
   * @returns Promise<boolean> - A promise that resolves with a boolean value indicating whether the token is valid.
   */
  checkToken = (token) => this.fetch.checkToken(token);
  /**
   * Revoke an oauth token.
   * @param {string} token - The Oauth token to revoke.
   * @returns Promise<boolean> - A promise that resolves with a boolean value indicating whether the revocation was
   *   successful.
   */
  revokeToken = (token) => this.fetch.revokeToken(token);

  /**
   * Performs a search using the specified parameters.
   * @template T - The type of model expected in the search results.
   * @param {Object|null} [opts] - Options for the search.
   * @param {string} [opts.page] - Page number for pagination.
   * @param {string[]} [opts.filters] - Filters to apply to the search.
   * @param {ModelTransformer} [opts.transformer] - Optional model transformation function.
   * @returns Promise<SearchResults<T>> - A promise that resolves with the search results.
   * @throws Error Throws an error.
   */
  search = (opts) => {
    throw new Error("Not implemented");
  };

  /**
   * Retrieves a specific model by its identifier.
   * @template T - The type of model expected to be retrieved.
   * @param {string|number} id - The identifier of the model.
   * @param {Object|null} [opts] - Options for retrieving the model.
   * @param {string[]} [opts.filters] - Filters to apply to the search.
   * @param {ModelTransformer} [opts.transformer] - Optional model transformation function.
   * @returns Promise<T> - A promise that resolves with the retrieved model.
   * @throws Error Throws an error.
   */
  get = (id, opts) => {
    throw new Error("Not implemented");
  };

  /**
   * Publishes a new model.
   * @template T - The type of model expected to be published.
   * @param {BaseModel} model - The model to publish.
   * @param {Object|null} [opts] - Options for publishing the model.
   * @param {string} [opts.customPath] - Custom path for publishing.
   * @param {string} [opts.extraPath] - Extra path for publishing.
   * @param {ModelTransformer} [opts.transformer] - Optional model transformation function.
   * @param {Record<string, string>} [opts.headers] - Additional headers for the request.
   * @returns {Promise<T|boolean>} - A promise that resolves with the published model or a boolean value.
   * @throws Error Throws an error.
   */
  post = (model, opts) => {
    throw new Error("Not implemented");
  };

  /**
   * Updates a model with the specified identifier.
   * @template T - The type of model expected to be updated.
   * @param {string|number} id - The identifier of the model to update.
   * @param {BaseModel} model - The model data to update.
   * @param {Object|null} [opts] - Options for updating the model.
   * @param {string} [opts.customPath] - Custom path for the update operation.
   * @param {string} [opts.extraPath] - Extra path for the update operation.
   * @param {Map<QueryFields, unknown>} [opts.params] - Additional parameters for the request.
   * @param {ModelTransformer} [opts.transformer] - Optional model transformation function.
   * @param {Json} [opts.headers] - Additional headers for the request.
   * @returns {Promise<T|boolean>} - A promise that resolves with the updated model or a boolean value.
   * @throws Error - Throws an error.
   */
  put = (id, model, opts) => {
    throw new Error("Not implemented");
  };

  /**
   * Partially updates a model with the specified identifier.
   * @template T - The type of model expected to be partially updated.
   * @param {string|number} id - The identifier of the model to partially update.
   * @param {BaseModel} model - The model data to use for the partial update.
   * @param {Object|null} [opts] - Options for the partial update operation.
   * @param {string} [opts.customPath] - Custom path for the partial update operation.
   * @param {string} [opts.extraPath] - Extra path for the partial update operation.
   * @param {Map<QueryFields, unknown>} [opts.params] - Additional parameters for the request.
   * @param {ModelTransformer} [opts.transformer] - Optional model transformation function.
   * @param {Json} [opts.headers] - Additional headers for the request.
   * @returns {Promise<T|boolean>} - A promise that resolves with the partially updated model or a boolean value.
   * @throws Error - Throws an error.
   */
  patch = (id, model, opts) => {
    throw new Error("Not implemented");
  };

  /**
   * Deletes a model with the specified identifier.
   * @param {string|number} id - The identifier of the model to delete.
   * @param {Object|null} [opts] - Options for the delete operation.
   * @param {string} [opts.customPath] - Custom path for the delete operation.
   * @param {Json} [opts.headers] - Additional headers for the request.
   * @returns Promise<boolean> - A promise that resolves with a boolean value indicating the success of the deletion.
   * @throws Error - Throws an error.
   */
    // eslint-disable-next-line no-unused-vars
  delete = (id, opts) => {
    throw new Error("Not implemented");
  };
}

export { OauthController };

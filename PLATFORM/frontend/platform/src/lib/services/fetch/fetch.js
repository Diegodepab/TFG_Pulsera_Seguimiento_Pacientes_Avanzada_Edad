import { Constants } from "$lib/commons/constants";
import { Global } from "$lib/commons/global";
import { BaseModel } from "$lib/models/base_model";
import { SearchResults } from "$lib/models/search_results";
import { ExceptionFetch } from "$lib/services/fetch/exception_fetch";
import { QueryEncoder } from "$lib/services/utils/query_encoder";
import { QueryFields } from "$lib/services/utils/query_utils";

class Fetch {
  /** @type string */
  host;
  /** @type string */
  path;
  /** @type string */
  entity;
  /** @type {Record<string,string>} */
  headers;
  /** @type ModelTransformer */
  transformer = BaseModel.transformer;

  constructor() {
    this.host = Global.apiUrl;
    this.headers = {};
  }

  /**
   * Retrieves OAuth headers.
   * @returns Promise<void> - A promise that resolves when the OAuth headers are retrieved.
   */
  oauthHeader = async () => null;

  /**
   * Performs a search operation.
   * @param {any} url - The URL to check.
   * @returns {boolean} -  Returns true if the URL is an OAuth URL, false otherwise.
   */
    _isOAuthUrl(url) {
    try {
      const u = new URL(url, this.host);
      return u.pathname.endsWith("/oauth/token");
    } catch {
      return false;
    }
  }


    /**
   * Performs a search operation.
   * @param {any} url - The URL to check.
   * @returns {string} -  Returns the normalized URL if it is valid, otherwise returns the original URL.
   */
   normalizeUrl(url) {
    try {
      const u = new URL(url);
      if (u.host === "host.docker.internal:8001") {
        // Conserva sólo path + search
        return u.pathname + u.search;
      }
      return url;
    } catch {
      return url;
    }
  }

   /**
   * Envía la petición, aplicando reglas de normalización
   * @param {string|Request} input
   * @param {RequestInit} init
   */
  async doFetch(input, init = {}) {
    let url = typeof input === "string" ? input : input.url;
    const isOAuth = this._isOAuthUrl(url);

    // Si no es OAuth, normalizamos host.docker.internal
    if (!isOAuth) {
      url = this.normalizeUrl(url);
      // Si arranca con /v1, lo anteponemos al origen de this.host
      if (url.startsWith("/v1")) {
        const origin = new URL(this.host).origin;
        url = origin + url;
      }
    }

    // Cabeceras
    const headers = { ...(init.headers || {}) };

    if (isOAuth) {
      // Para OAuth: content-type x-www-form-urlencoded
      headers["Content-Type"] = "application/x-www-form-urlencoded";
    } else {
      // Para el resto, usamos JSON si no se ha configurado otra cosa
      if (!headers["Content-Type"]) {
        headers["Content-Type"] = "application/json";
      }
      // Añadimos también cualquier header global (p.ej. token Bearer)
      Object.assign(headers, this.headers);
    }

    const response = await fetch(url, {
      ...init,
      headers
    });

    return response;
  }

  /**
   * Performs a search operation.
   * @template {BaseModel | BaseDC} T
   * @param {Object} opts - Options for the search operation.
   * @param {string} [opts.customPath] - Custom path for the search operation.
   * @param {string} [opts.extraPath] - Additional path for the search operation.
   * @param {Map<QueryFields, unknown>} [opts.params] - Parameters for the search operation.
   * @param {string} [opts.opEntity] - Entity associated with the operation.
   * @param {string} [opts.page] - Page number for pagination.
   * @param {ModelTransformer} [opts.transformer] - Transformer function for transforming models.
   * @param {Record<string, string>} [opts.headers] - Headers to be included in the search request.
   * @returns Promise<SearchResults<T>> - A promise that resolves to the search results.
   * @throws ExceptionFetch - Throws an exception if operation failed.
   */
  async search(opts) {
    await this.oauthHeader();
    opts ??= {};

    if (opts.page != null) {
      const data = await this.getUrl(opts.page);
      if (!data) return SearchResults.empty();
      return SearchResults.fromJson(JSON.parse(data), opts.transformer ?? this.transformer);
    }

    let url = `${this.host}${opts.customPath ?? this.path}${opts.extraPath || ""}`;
    opts.params ??= new Map();
    if (!opts.params.has(QueryFields.LIMIT)) {
      opts.params.set(QueryFields.LIMIT, Constants.PAGE_SIZE);
    }
    if (opts.params.size) {
      url = QueryEncoder.encodeQuery({ params: opts.params, path: url });
    }

    const res = await this.doFetch(url, { method: "GET" });
    if (res.status === 200) {
      return SearchResults.fromJson(await res.json(), opts.transformer ?? this.transformer);
    }
    throw await ExceptionFetch.fromResponse(res, { entity: opts.opEntity ?? this.entity });
  }

  /**
   * Retrieves a single entity by its ID.
   * @template {BaseModel | BaseDC} T
   * @param {string|number} id - The ID of the entity to retrieve.
   * @param {Object} [opts] - Options for the retrieval operation.
   * @param {string} [opts.customPath] - Custom path for the retrieval operation.
   * @param {string} [opts.extraPath] - Additional path for the retrieval operation.
   * @param {Map<QueryFields, unknown>} [opts.params] - Parameters for the retrieval operation.
   * @param {string} [opts.opEntity] - The entity associated with the retrieval operation.
   * @param {ModelTransformer} [opts.transformer] - The transformer function for transforming models.
   * @param {Record<string, string>} [opts.headers] - Headers to be included in the retrieval request.
   * @returns Promise<T> - A promise that resolves to the retrieved entity.
   * @throws ExceptionFetch - Throws an exception if operation failed.
   */
  async get(id, opts) {
    await this.oauthHeader();
    opts ??= {};

    let url = `${this.host}${opts.customPath ?? this.path}/${id}${opts.extraPath || ""}`;
    if (opts.params?.size) {
      url = QueryEncoder.encodeQuery({ params: opts.params, path: url });
    }

    const res = await this.doFetch(url, { method: "GET" });
    if (res.status === 200) {
      return (opts.transformer ?? this.transformer)(await res.json());
    }
    throw await ExceptionFetch.fromResponse(res, { entity: opts.opEntity ?? this.entity });
  }

  /**
   * Sends a POST request to create a new entity.
   * @template {BaseModel | BaseDC} T
   * @param {Json|string} data - The data to be sent in the request body.
   * @param {Object} [opts] - Options for the POST request.
   * @param {string} [opts.customPath] - Custom path for the POST request.
   * @param {string} [opts.extraPath] - Additional path for the POST request.
   * @param {Map<QueryFields, unknown>} [opts.params] - Parameters for the POST request.
   * @param {string} [opts.opEntity] - The entity associated with the POST request.
   * @param {ModelTransformer} [opts.transformer] - The transformer function for transforming models.
   * @param {Record<string, string>} [opts.headers] - Headers to be included in the POST request.
   * @returns {Promise<T | boolean>} - A promise that resolves to the created entity or a boolean value indicating success.
   * @throws ExceptionFetch - Throws an exception if operation failed.
   */
  async post(data, opts) {
    await this.oauthHeader();
    opts ??= {};

    let url = `${this.host}${opts.customPath ?? this.path}${opts.extraPath || ""}`;
    if (opts.params?.size) {
      url = QueryEncoder.encodeQuery({ params: opts.params, path: url });
    }

    const body = this._isOAuthUrl(url)
      ? (typeof data === "string" ? data : new URLSearchParams(data).toString())
      : (typeof data === "string" ? data : JSON.stringify(data));

    const res = await this.doFetch(url, { method: "POST", body });
    if ([200, 201].includes(res.status)) {
      return (opts.transformer ?? this.transformer)(await res.json());
    }
    if (res.status === 204) {
      return true;
    }
    throw await ExceptionFetch.fromResponse(res, { entity: opts.opEntity ?? this.entity });
  }

  /**
   * Sends a PUT request to update an entity by its ID.
   * @template {BaseModel | BaseDC} T
   * @param {string|number} id - The ID of the entity to update.
   * @param {Json|string} data - The data to be sent in the request body for updating the entity.
   * @param {Object} [opts] - Options for the PUT request.
   * @param {string} [opts.customPath] - Custom path for the PUT request.
   * @param {string} [opts.extraPath] - Additional path for the PUT request.
   * @param {Map<QueryFields, unknown>} [opts.params] - Parameters for the PUT request.
   * @param {string} [opts.opEntity] - The entity associated with the PUT request.
   * @param {ModelTransformer} [opts.transformer] - The transformer function for transforming models.
   * @param {Record<string, string>} [opts.headers] - Headers to be included in the PUT request.
   * @returns {Promise<T|boolean>} - A promise that resolves to the updated entity or a boolean value indicating success.
   * @throws ExceptionFetch - Throws an exception if operation failed.
   */
  async put(id, data, opts) {
    await this.oauthHeader();
    opts ??= {};

    let url = `${this.host}${opts.customPath ?? this.path}/${id}${opts.extraPath || ""}`;
    if (opts.params?.size) {
      url = QueryEncoder.encodeQuery({ params: opts.params, path: url });
    }

    const body = typeof data === "string" ? data : JSON.stringify(data);
    const res = await this.doFetch(url, { method: "PUT", body });
    if ([200, 201].includes(res.status)) {
      return (opts.transformer ?? this.transformer)(await res.json());
    }
    if (res.status === 204) {
      return true;
    }
    throw await ExceptionFetch.fromResponse(res, { entity: opts.opEntity ?? this.entity });
  }

  /**
   * Sends a PATCH request to partially update an entity by its ID.
   * @template {BaseModel | BaseDC} T
   * @param {string|number} id - The ID of the entity to partially update.
   * @param {Json|string} data - The data to be sent in the request body for partial update.
   * @param {Object} [opts] - Options for the PATCH request.
   * @param {string} [opts.customPath] - Custom path for the PATCH request.
   * @param {string} [opts.extraPath] - Additional path for the PATCH request.
   * @param {Map<QueryFields, unknown>} [opts.params] - Parameters for the PATCH request.
   * @param {string} [opts.opEntity] - The entity associated with the PATCH request.
   * @param {ModelTransformer} [opts.transformer] - The transformer function for transforming models.
   * @param {Record<string, string>} [opts.headers] - Headers to be included in the PATCH request.
   * @returns {Promise<T|boolean>} - A promise that resolves to the partially updated entity or a boolean value
   *   indicating success.
   * @throws ExceptionFetch - Throws an exception if operation failed.
   */
  async patch(id, data, opts) {
    await this.oauthHeader();
    opts ??= {};

    let url = `${this.host}${opts.customPath ?? this.path}/${id}${opts.extraPath || ""}`;
    if (opts.params?.size) {
      url = QueryEncoder.encodeQuery({ params: opts.params, path: url });
    }

    const body = typeof data === "string" ? data : JSON.stringify(data);
    const res = await this.doFetch(url, { method: "PATCH", body });
    if ([200, 201].includes(res.status)) {
      return (opts.transformer ?? this.transformer)(await res.json());
    }
    if (res.status === 204) {
      return true;
    }
    throw await ExceptionFetch.fromResponse(res, { entity: opts.opEntity ?? this.entity });
  }

  /**
   * Sends a DELETE request to delete an entity by its ID.
   * @param {string|number} id - The ID of the entity to delete.
   * @param {Object} [opts] - Options for the DELETE request.
   * @param {string} [opts.customPath] - Custom path for the DELETE request.
   * @param {string} [opts.extraPath] - Additional path for the DELETE request.
   * @param {string} [opts.opEntity] - The entity associated with the DELETE request.
   * @param {Record<string, string>} [opts.headers] - Headers to be included in the DELETE request.
   * @returns Promise<boolean> - A promise that resolves to a boolean value indicating success.
   * @throws ExceptionFetch - Throws an exception if operation failed.
   */
  async delete(id, opts) {
    await this.oauthHeader();
    opts ??= {};

    const url = `${this.host}${opts.customPath ?? this.path}/${id}${opts.extraPath || ""}`;
    const res = await this.doFetch(url, { method: "DELETE" });
    if ([200, 204].includes(res.status)) {
      return true;
    }
    throw await ExceptionFetch.fromResponse(res, { entity: opts.opEntity ?? this.entity });
  }

  /**
   * @protected
   * Sends a GET request to the specified URL.
   * @param {any} rawUrl - The URL to send the GET request to.
   * @returns {Promise<string|void>} - A promise that resolves to the response text or void if the request fails.
   * @throws ExceptionFetch - Throws an exception if operation failed.
   */
  async getUrl(rawUrl) {
    // En getUrl permitimos siempre la URL tal cual (p.ej. páginas paginadas)
    const res = await this.doFetch(rawUrl, { method: "GET" });
    if (res.status === 200) return await res.text();
    throw await ExceptionFetch.fromResponse(res, { entity: this.entity });
  }
}


export { Fetch };

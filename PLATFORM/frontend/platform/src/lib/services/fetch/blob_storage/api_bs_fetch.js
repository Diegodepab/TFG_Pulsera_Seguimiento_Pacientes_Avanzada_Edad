import { Global } from "$lib/commons/global";
import { SessionManager } from "$lib/commons/session_manager";
import { ApiBlobStorageUtils } from "$lib/services/fetch/blob_storage/api_bs_utils";
import { ExceptionFetch } from "$lib/services/fetch/exception_fetch";

/**
 * Class for handling API requests related to blob storage.
 */
class ApiBlobStorageFetch {
  /** @type string - The base URL for the API. */
  host;

  /** @type string - The entity type for the API. */
  entity = "blob_storage";

  /** @type {Record<string, string>} - The headers for API requests. */
  headers;

  /**
   * Creates an instance of ApiBlobStorageFetch.
   */
  constructor() {
    this.host = Global.apiUrl;
    this.headers = {};
  }

  /**
   * Sets the OAuth header for authentication.
   * @returns Promise<void> - A promise that resolves when the header is set.
   */
  oauthHeader = async () => {
    const authHeader = (await SessionManager.token()).getHeader();
    Object.entries(authHeader).forEach(([ key, value ]) => {
      this.headers[key] = value;
    });
  };

  /**
   * Fetches a signed URL for a specific blob.
   * @param {string|number} id - The ID of the blob.
   * @param {string} rootPath - The root path for the signed URL.
   * @param {Object} [opts] - Optional parameters.
   * @param {string} [opts.opEntity] - The operation entity (optional).
   * @param {Record<string, string>} [opts.headers] - Additional headers (optional).
   * @returns Promise<GetSignedUrlResponse> - A promise that resolves to the signed URL response.
   * @throws {ExceptionFetch} If the request fails.
   */
  get = async (id, rootPath, opts) => {
    await this.oauthHeader();

    /** @type string */
    const _path = `${ this.host }${ rootPath }/${ id }/bs-signed-url`;

    /** @type Response */
    const response = await fetch(_path, {
      method: "GET",
      headers: this._addHeaders(opts?.headers),
    });

    if (response.status === 200) {
      return {
        displayUrl: (await response.json())["display_url"],
      };
    }
    throw await ExceptionFetch.fromResponse(response, { entity: opts?.opEntity ?? this.entity });
  };

  /**
   * Posts data to get signed URLs for uploading files.
   * @param {PostSignedUrlRequest | PostSignedUrlRequest[]} data - The request data.
   * @param {string} rootPath - The root path for the signed URL.
   * @param {Object} [opts] - Optional parameters.
   * @param {string} [opts.opEntity] - The operation entity (optional).
   * @param {Record<string, string>} [opts.headers] - Additional headers (optional).
   * @param {function(Json): T} [opts.transformer] - A transformer function for the response (optional).
   * @returns {Promise<T = PostSignedUrlResponse>} - A promise that resolves to the signed URL response.
   * @throws ExceptionFetch - If the request fails.
   */
  post = async (data, rootPath, opts) => {
    await this.oauthHeader();

    /** @type string */
    const _path = `${ this.host }${ rootPath }/bs-signed-url`;

    this.headers["Content-Type"] = "application/json";

    const _requestTransformer = "length" in data
      ? ApiBlobStorageUtils.jsonToMultiRequestPayload
      : ApiBlobStorageUtils.jsonToRequestPayload;

    /** @type string */
    const body = JSON.stringify(_requestTransformer(data, { isPost: true }));

    /** @type Response */
    const response = await fetch(_path, {
      method: "POST",
      body: body,
      headers: this._addHeaders(opts?.headers),
    });

    if ([ 200, 201 ].includes(response.status)) {
      if (opts?.transformer) return opts.transformer(await response.json());
      return ApiBlobStorageUtils.responseToSignedUrlResponse(await response.json(), { isPost: true });
    }

    throw await ExceptionFetch.fromResponse(response, { entity: opts?.opEntity ?? this.entity });
  };

  /**
   * Updates a signed URL for a specific blob.
   * @param {string|number} id - The ID of the blob.
   * @param {PutSignedUrlRequest} data - The data to update.
   * @param {string} rootPath - The root path for the signed URL.
   * @param {Object} [opts] - Optional parameters.
   * @param {string} [opts.opEntity] - The operation entity (optional).
   * @param {Record<string, string>} [opts.headers] - Additional headers (optional).
   * @param {function(Json): unknown} [opts.transformer] - A transformer function for the response (optional).
   * @returns Promise<PutSignedUrlResponse> - A promise that resolves to the updated signed URL response.
   * @throws ExceptionFetch - If the request fails.
   */
  put = async (id, data, rootPath, opts) => {
    await this.oauthHeader();

    /** @type string */
    const _path = `${ this.host }${ rootPath }/${ id }/bs-signed-url`;

    this.headers["Content-Type"] = "application/json";

    /** @type string */
    const body = JSON.stringify(ApiBlobStorageUtils.jsonToRequestPayload(data));
    /** @type Response */
    const response = await fetch(_path, {
      method: "PUT",
      body: body,
      headers: this._addHeaders(opts?.headers),
    });

    if ([ 200, 201 ].includes(response.status)) {
      if (opts?.transformer) return opts.transformer(await response.json());
      return ApiBlobStorageUtils.responseToSignedUrlResponse(await response.json());
    }

    throw await ExceptionFetch.fromResponse(response, { entity: opts?.opEntity ?? this.entity });
  };

  /**
   * Deletes a resource identified by the given ID from the specified root path.
   *
   * @template T
   * @param {string | number} id - The ID of the resource to delete.
   * @param {string} rootPath - The root path for the delete request.
   * @param {{
   *   data?: Json | string,
   *   opEntity?: string,
   *   headers?: Record<string, string>,
   *   transformer?: (response: Json) => T
   * }} [opts] - Optional parameters for the delete operation.
   * @returns Promise<T> - A promise that resolves to the transformed response.
   * @throws ExceptionFetch - Throws an error if the response status is not 200.
   */
  delete = async (id, rootPath, opts) => {
    await this.oauthHeader();

    opts ??= {};
    const _path = `${ this.host }${ rootPath }${ id ? `/${ id }` : "" }/bs-signed-url`;

    this.headers ??= {};
    this.headers["Content-Type"] = "application/json";

    /** @type {string | undefined} */
    let body;
    if (opts.data) body = typeof opts.data === "string" ? opts.data : JSON.stringify(opts.data);

    /** @type Response */
    const response = await fetch(_path, {
      method: "DELETE",
      body: body,
      headers: this._addHeaders(opts?.headers),
    });

    if ([ 200 ].includes(response.status)) {
      if ([ 200 ].includes(response.status)) return {
        deleteUrl: (await response.json())["delete_url"],
      };
    }

    throw await ExceptionFetch.fromResponse(response, { entity: opts?.opEntity ?? this.entity });
  };

  /**
   * @protected
   * Adds additional headers to the existing headers.
   * @param {Json} [headers] - Optional headers to add.
   * @returns {Record<string, string>} - The combined headers.
   */
  _addHeaders = (headers) => {
    /** @type {Record<string, string>} */
    const _headers = this.headers ?? {};
    if (headers != null) Object.entries(headers).forEach(([ key, value ]) => (
      _headers[key] = value
    ));

    return _headers;
  };
}

export { ApiBlobStorageFetch };

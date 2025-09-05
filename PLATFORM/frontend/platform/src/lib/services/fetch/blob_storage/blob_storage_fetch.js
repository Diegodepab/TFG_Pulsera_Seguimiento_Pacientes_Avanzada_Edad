import { ExceptionFetch } from "$lib/services/fetch/exception_fetch";

/**
 * Class for handling blob storage fetch operations.
 */
class BlobStorageFetch {
  /**
   * Converts a string of headers into an object.
   * @private
   * @param {string} strHeaders - The string representation of headers.
   * @returns {Record<string, string>} - An object mapping header names to values.
   */
  _strHeadersToObject = (strHeaders) => {
    const headersParts = strHeaders.replace(/"/gm, "").split("\r\n");
    return headersParts.reduce((sum, current) => {
      const parts = current.split(":");
      const key = parts[0].trim();
      if (key) sum[key] = parts[1].trim();
      return sum;
    }, {});
  };

  /**
   * Uploads a blob to the specified URL.
   * @param {string} url - The URL to upload the blob to.
   * @param {Object} [opts] - Optional parameters for the upload.
   * @param {Blob} [opts.blob] - Optional blob for the upload.
   * @param {BlobProgress} [opts.onUpload] - Optional callback to execute while uploading.
   * @returns Promise<Response> - A promise that resolves to the response of the upload.
   */
  upload = async (url, { blob, onUpload } = {}) => {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      xhr.onload = () => {
        const response = new Response(xhr.response, {
          headers: this._strHeadersToObject(xhr.getAllResponseHeaders()),
          status: xhr.status,
          statusText: xhr.statusText,
        });

        if (response.status === 200) return resolve(response);
        reject(response);
      };

      xhr.onerror = reject;

      if (onUpload) {
        xhr.upload.onprogress = (event) => {
          return onUpload(event.loaded, event.total);
        };
      }

      xhr.open("PUT", url);
      xhr.send(blob ?? null);
    });
  };

  /**
   * Makes a request to the specified URL with the given method.
   * @param {string} url - The URL to send the request to.
   * @param {"POST" | "DELETE"} method - The HTTP method to use for the request.
   * @param {Object} [opts] - Optional parameters for the request.
   * @param {string} [opts.entity="blob_storage"] - Optional entity for request.
   * @param {string | undefined} [opts.data] - Media to request.
   * @returns Promise<Response> - A promise that resolves to the response of the request.
   * @throws Error - Throws an error if the response status is not 200 or 204.
   */
  request = async (url, method, { data, entity } = {}) => {
    /** @type Response */
    const response = await fetch(url, { method, body: data });

    if ([ 200, 204 ].includes(response.status)) return response;

    entity ??= "blob_storage";
    throw await ExceptionFetch.fromResponse(response, { entity });
  };
}

export { BlobStorageFetch };

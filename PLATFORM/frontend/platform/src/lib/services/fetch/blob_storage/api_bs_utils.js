import { BlobStorageUtils } from "$lib/services/fetch/blob_storage/blob_storage_utils";

/**
 * Abstract class for utility functions related to Blob Storage API.
 * @abstract
 */
class ApiBlobStorageUtils {
  /**
   * Prepares a POST request for uploading a file.
   * @param {File} file - The file to be uploaded.
   * @param {Object} [opts] - Optional parameters.
   * @param {number | string} [opts.reservedId] - Identifier to use for the uploaded register.
   * @returns PostSignedUrlRequest - The prepared request object.
   */
  static preparePostRequest = (file, { reservedId } = {}) => {
    if (file.size <= BlobStorageUtils.CHUNK_SIZE) return { id: reservedId, filename: file.name, numParts: 1 };

    return {
      id: reservedId,
      filename: file.name,
      numParts: Math.ceil(file.size / BlobStorageUtils.CHUNK_SIZE),
    };
  };

  /**
   * Prepares a PUT request for uploading a file.
   * @param {File} file - The file to be uploaded.
   * @returns PutSignedUrlRequest - The prepared request object.
   */
  static preparePutRequest = (file) => {
    if (file.size <= BlobStorageUtils.CHUNK_SIZE) return { filename: file.name, numParts: 1 };

    return {
      filename: file.name,
      numParts: Math.ceil(file.size / BlobStorageUtils.CHUNK_SIZE),
    };
  };

  /**
   * Converts JSON data to a request payload.
   * @param {Json} data - The data to convert.
   * @param {Object} [opts] - Optional parameters.
   * @param {boolean} [opts.isPost=false] - Whether the operation is a post or not.
   * @returns Json - The converted request payload.
   */
  static jsonToRequestPayload = (data, { isPost } = {}) => {
    const result = {
      filename: data["filename"],
      num_parts: data["numParts"],
    };

    // 'put' operation doesn't need to declare its 'id'
    if (isPost) Object.assign(result, { id: data["id"] });
    return result;
  };

  /**
   * Converts an array of JSON data to an array of request payloads.
   * @param {Json[]} data - The array of data to convert.
   * @param {Object} [opts] - Optional parameters.
   * @param {boolean} [opts.isPost=false] - Whether the operation is a post or not.
   * @returns Json[] - The array of converted request payloads.
   */
  static jsonToMultiRequestPayload = (data, opts) => {
    return data.map((f) => this.jsonToRequestPayload(f, opts));
  };

  /**
   * Converts JSON response data to a signed URL response.
   * @param {Json} data - The response data to convert.
   * @param {Object} [opts] - Optional parameters.
   * @param {boolean} [opts.isPost=false] - Whether the operation is a post or not.
   * @returns UploadResponse - The converted upload response.
   */
  static responseToSignedUrlResponse = (data, { isPost } = {}) => {
    const result = {
      uploadId: data["upload_id"],
      urls: data["urls"],
      displayUrl: data["display_url"],
      deleteUrl: data["delete_url"],
      completeUrl: data["complete_url"],
      abortUrl: data["abort_url"],
    };

    if (isPost) Object.assign(result, { reservedId: data["reserved_id"], filename: data["filename"] });
    return result;
  };

  /**
   * Converts an array of JSON response data to an array of signed URL responses.
   * @param {Json[]} data - The array of response data to convert.
   * @param {Object} [opts] - Optional parameters.
   * @param {boolean} [opts.isPost=false] - Whether the operation is a post or not.
   * @returns UploadResponse[] - The array of converted upload responses.
   */
  static responseToMultiSignedUrlResponse = (data, opts) => {
    return data.map((d) => this.responseToSignedUrlResponse(d, opts));
  };
}

export { ApiBlobStorageUtils };

import { ApiBlobStorageFetch } from "$lib/services/fetch/blob_storage/api_bs_fetch";
import { ApiBlobStorageUtils } from "$lib/services/fetch/blob_storage/api_bs_utils";

/**
 * Class for managing blob storage operations through API calls.
 */
class ApiBlobStorageController {
  /** @type {ApiBlobStorageFetch} The fetch utility for API calls. */
  fetch;

  /**
   * Creates an instance of ApiBlobStorageController.
   */
  constructor() {
    this.fetch = new ApiBlobStorageFetch();
  }

  /**
   * Fetches a signed URL for a specific blob.
   * @param {number} id - The ID of the blob.
   * @param {string} rootPath - The root path for the signed URL.
   * @param {Object} [opts] - Optional parameters.
   * @param {string} [opts.opEntity] - The operation entity (optional).
   * @returns Promise<GetSignedUrlResponse> - A promise that resolves to the signed URL response.
   */
  getSignedUrl = async (id, rootPath, opts) => {
    return this.fetch.get(id, rootPath, opts);
  };

  /**
   * Fetches a signed URL for uploading a single file.
   * @param {File} file - The file to upload.
   * @param {string} rootPath - The root path for the signed URL.
   * @param {Object} [opts] - Optional parameters.
   * @param {string} [opts.opEntity] - The operation entity (optional).
   * @param {number|string} [opts.reservedId] - An optional reserved ID.
   * @returns Promise<PostSignedUrlResponse> - A promise that resolves to the signed URL response.
   */
  getPostSignedUrl = async (file, rootPath, opts) => {
    const dataRequest = ApiBlobStorageUtils.preparePostRequest(file, { reservedId: opts?.reservedId });
    return this.fetch.post(dataRequest, rootPath, opts);
  };

  /**
   * Asynchronously fetches multiple signed URLs for uploading files to a Blob Storage service.
   * @param {FilePostMultipleRequest[]} files - An array of objects representing the files to upload.
   * @param {string} rootPath - The root path for the signed URLs.
   * @param {Object} [opts] - Optional configuration options.
   * @param {string} [opts.opEntity] - The entity type for the uploaded file (optional).
   * @param {number|string} [opts.reservedId] - Reserved ID for specified files (optional).
   * @returns Promise<PostSignedUrlResponse[]> - A promise that resolves to an array of `PostSignedUrlResponse` objects.
   * @throws Error - If an error occurs during the request.
   */
  getMultiPostSignedUrl = async (files, rootPath, opts) => {
    /** @type {PostSignedUrlRequest[]} */
    const dataRequest = [];
    files.forEach((f) => {
      const postReq = ApiBlobStorageUtils.preparePostRequest(f.file, { reservedId: f.reservedId ?? opts?.reservedId });
      dataRequest.push(postReq);
    });

    return this.fetch.post(dataRequest, rootPath, {
      ...opts,
      transformer: (d) => ApiBlobStorageUtils.responseToMultiSignedUrlResponse(d, { isPost: true }),
    });
  };

  /**
   * Fetches a signed URL for uploading a file using PUT method.
   * @param {number} id - The ID of the blob.
   * @param {File} file - The file to upload.
   * @param {string} rootPath - The root path for the signed URL.
   * @param {Object} [opts] - Optional parameters.
   * @param {string} [opts.opEntity] - The operation entity (optional).
   * @returns Promise<PostSignedUrlResponse> - A promise that resolves to the signed URL response.
   */
  getPutSignedUrl = async (id, file, rootPath, opts) => {
    /** @type {PutSignedUrlRequest} */
    const dataRequest = ApiBlobStorageUtils.preparePutRequest(file);
    return this.fetch.put(id, dataRequest, rootPath, opts);
  };

  /**
   * Fetches a signed URL for deleting a blob.
   * @param {number|string} id - The ID of the blob to delete.
   * @param {string} rootPath - The root path for the signed URL.
   * @param {Object} [opts] - Optional parameters.
   * @param {string} [opts.opEntity] - The operation entity (optional).
   * @param {Json} [opts.data] - Additional data for the request (optional).
   * @returns Promise<DeleteSignedUrlResponse> - A promise that resolves to the delete signed URL response.
   */
  getDeleteSignedUrl = async (id, rootPath, opts) => {
    return this.fetch.delete(id, rootPath, opts);
  };

  /**
   * Fetches multiple signed URLs for deleting blobs.
   * @param {FileDeleteMultipleRequest[]} files - An array of objects representing the files to delete.
   * @param {string} rootPath - The root path for the signed URLs.
   * @param {Object} [opts] - Optional parameters.
   * @param {string} [opts.opEntity] - The operation entity (optional).
   * @returns Promise<DeleteSignedUrlResponse[]> - A promise that resolves to an array of delete signed URL responses.
   */
  getMultiDeleteSignedUrl = async (files, rootPath, opts) => {
    return this.fetch.delete("", rootPath, {
      ...opts,
      transformer: (d) => {
        return d.map((e) => {
          return {
            deleteUrl: e["delete_url"],
            filename: e["filename"],
            id: e["id"],
          };
        });
      },
      data: files,
    });
  };
}

export { ApiBlobStorageController };

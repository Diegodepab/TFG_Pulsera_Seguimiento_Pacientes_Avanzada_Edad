import { PlatformException } from "$lib/exceptions/platform_exception";
import { BlobUploadTask } from "$lib/models/blob_storage/blob_upload_task";
import { BlobUploadWorker } from "$lib/models/blob_storage/blob_upload_worker";
import { BlobStorageFetch } from "$lib/services/fetch/blob_storage/blob_storage_fetch";
import { BlobStorageUtils } from "$lib/services/fetch/blob_storage/blob_storage_utils";

/**
 * Class for managing blob storage operations, including file uploads.
 */
class BlobStorageController {
  /** @type {BlobStorageFetch} The fetch utility for API calls. */
  fetch;

  /**
   * Creates an instance of BlobStorageController.
   */
  constructor() {
    this.fetch = new BlobStorageFetch();
  }

  /**
   * Uploads a file to blob storage using a signed URL.
   * @param {UploadResponse} signedArgs - The signed URL response containing upload URLs.
   * @param {File} file - The file to upload.
   * @param {Object} [opts] - Optional parameters.
   * @param {BlobProgress} [opts.onUpload] - Callback for upload progress.
   * @returns Promise<BlobStorageResponse> - A promise that resolves to the blob storage response.
   */
  upload = async (signedArgs, file, opts) => {
    if (signedArgs.urls.length > 1) return this._fileMultipartUpload(signedArgs, file, opts);
    return this._fileSimpleUpload(signedArgs, file, opts);
  };

  /**
   * Uploads a file using a simple upload method (single URL).
   * @private
   * @param {UploadResponse} signedArgs - The signed URL response containing the upload URL.
   * @param {File} file - The file to upload.
   * @param {Object} [opts] - Optional parameters.
   * @param {BlobProgress} [opts.onUpload] - Callback for upload progress.
   * @returns Promise<BlobStorageResponse> - A promise that resolves to the blob storage response.
   * @throws Error - If an error occurs during the upload.
   */
  _fileSimpleUpload = async (signedArgs, file, opts) => {
    try {
      const response = await this.fetch.upload(signedArgs.urls.at(0), {
        blob: file.slice(0, file.size),
        onUpload: opts?.onUpload,
      });

      const _url = new URL(signedArgs.urls.at(0));

      return {
        extra: {
          etag: response.headers.get("etag") ?? undefined,
        },
        blobUrl: `${ _url.origin }${ _url.pathname }`,
      };

    } catch (e) {
      throw PlatformException.errorOnSimpleFileUpload({
        fromError: e,
        extraArgs: { multipart: false, rejected: true },
      });
    }
  };

  /**
   * Uploads file parts for multipart uploads.
   * @private
   * @param {string[]} partsUrl - The URLs for the parts to upload.
   * @param {File} file - The file to upload.
   * @param {Object} [opts] - Optional parameters.
   * @param {BlobProgress} [opts.onUpload] - Callback for upload progress.
   * @returns Promise<Response> - A promise that resolves to the response from the upload.
   */
  _uploadParts = async (partsUrl, file, opts) => {
    const parts = BlobStorageUtils.blobPartsFromUrls(partsUrl, file);

    /** @type {BlobProgress} */
    let onUpload;
    if (opts?.onUpload) {
      onUpload = () => {
        opts.onUpload(
          parts.reduce((sum, part) => sum + (part.uploadedBytes ?? 0), 0),
          file.size,
        );
      };
    }

    const tasks = parts.map((part) => new BlobUploadTask(part, { onUpload }));
    const workers = [ ...Array(Math.min(BlobStorageUtils.WORKERS, parts.length)).keys() ]
      .map((wId) => new BlobUploadWorker(wId, tasks).start());

    await Promise.all(workers);

    const failedParts = parts.filter((task) => task.etag == null);
    const init = /** @type ResponseInit */ { headers: { "Content-Type": "application/json" } };
    if (!failedParts.length) return new Response(
      BlobStorageUtils.blobPartsToResponseBody(parts),
      { ...init, status: 202, statusText: "Accepted" },
    );

    // Some part has failed
    return new Response(
      BlobStorageUtils.blobPartsToResponseBody(failedParts),
      { ...init, status: 422, statusText: "Unprocessable Entity" },
    );
  };

  /**
   * Uploads a file using a multipart upload method.
   * @private
   * @param {UploadResponse} signedArgs - The signed URL response containing upload URLs.
   * @param {File} file - The file to upload.
   * @param {Object} [opts] - Optional parameters.
   * @param {BlobProgress} [opts.onUpload] - Callback for upload progress.
   * @returns Promise<BlobStorageResponse> - A promise that resolves to the blob storage response.
   * @throws PlatformException - If an error occurs during the multipart upload.
   */
  _fileMultipartUpload = async (signedArgs, file, opts) => {
    const response = await this._uploadParts(signedArgs.urls, file, opts);
    const _url = new URL(signedArgs.completeUrl);

    const parts = await response.json();
    if (response.status === 202) {
      try {
        await this.fetch.request(signedArgs.completeUrl, "POST", {
          data: BlobStorageUtils.partsToXml(parts),
        });
      } catch (e) {
        // Error on completing the upload for the file
        throw PlatformException.errorOnMultipartFileUpload({
          fromError: e,
          extraArgs: { multipart: true, completed: false },
        });
      }

      return {
        blobUrl: `${ _url.origin }${ _url.pathname }`,
        parts: parts,
      };
    }

    // response.status === 422
    const extraArgs = { multipart: true, completed: false, aborted: true };
    /** @type {Error | undefined} */
    let fromError;
    try {
      await this.fetch.request(signedArgs.abortUrl, "POST");
    } catch (e) { // Error on aborting the upload for the file
      fromError = e;
      extraArgs.aborted = false;
    }

    throw PlatformException.errorOnMultipartFileUpload({ fromError, extraArgs });
  };

  /**
   * Deletes a resource at the specified URL.
   * @param {string} url - The URL of the resource to delete.
   * @returns Promise<void> - A promise that resolves when the deletion is complete.
   * @throws PlatformException - Throws an error if the deletion fails, wrapped in a PlatformException.
   */
  delete = async (url) => {
    try {
      await this.fetch.request(url, "DELETE");
    } catch (e) {
      throw PlatformException.deleteFileToBlobStorage({ fromError: e });
    }
  };
}

export { BlobStorageController };

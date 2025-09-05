import { BaseController } from "$lib/controllers/base_controller";
import { ApiBlobStorageController } from "$lib/controllers/blob_storage/api_bs_controller";
import { InstrumentFetch } from "$lib/services/fetch/instrument_fetch";

class InstrumentController extends BaseController {
  /** @type {InstrumentFetch} */
  fetch;

  constructor() {
    super();
    this.fetch = new InstrumentFetch();
  }

  /**
   * Initializes the API Blob Storage Controller if it is not already initialized.
   * @private
   * @returns void
   */
  _initApiBSController = () => {
    if (this.apiBSController != null) return;
    this.apiBSController = new ApiBlobStorageController();
  };

  /**
   * Returns the path for blob storage.
   * @private
   * @returns string - The blob path.
   */
  _blobPath = () => "/instruments";

  /**
   * Retrieves a signed URL for the specified ID.
   * @param {number} id - The ID of the resource for which to get the signed URL.
   * @returns Promise<GetSignedUrlResponse> - A promise that resolves to the signed URL response.
   */
  getSignedUrl = (id) => {
    this._initApiBSController();
    return this.apiBSController.getSignedUrl(id, this._blobPath());
  };

  /**
   * Retrieves a post-signed URL for uploading a file.
   * @param {File} file - The file to upload.
   * @param {{ reservedId: number }} [opts] - Optional parameters including a reserved ID.
   * @returns Promise<PostSignedUrlResponse> - A promise that resolves to the post-signed URL response.
   */
  getPostSignedUrl = async (file, opts) => {
    this._initApiBSController();
    return this.apiBSController.getPostSignedUrl(file, this._blobPath(), { reservedId: opts?.reservedId });
  };

  /**
   * Retrieves a put-signed URL for uploading a file associated with a specific ID.
   * @param {number} id - The ID of the resource for which to get the put-signed URL.
   * @param {File} file - The file to upload.
   * @returns Promise<PutSignedUrlResponse> - A promise that resolves to the put-signed URL response.
   */
  getPutSignedUrl = async (id, file) => {
    this._initApiBSController();
    return this.apiBSController.getPutSignedUrl(id, file, this._blobPath());
  };

  /**
   * Retrieves a delete-signed URL for a specified ID.
   * @param {number} id - The ID of the resource for which to get the delete-signed URL.
   * @returns Promise<DeleteSignedUrlResponse> - A promise that resolves to the delete-signed URL response.
   */
  getDeleteSignedUrl = async (id) => {
    this._initApiBSController();
    return this.apiBSController.getDeleteSignedUrl(id, this._blobPath());
  };

}

export { InstrumentController };

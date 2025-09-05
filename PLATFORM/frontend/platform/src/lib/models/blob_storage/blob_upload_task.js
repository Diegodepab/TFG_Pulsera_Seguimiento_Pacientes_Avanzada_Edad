import { BlobStorageFetch } from "$lib/services/fetch/blob_storage/blob_storage_fetch";

/**
 * Exception class for handling errors during blob upload tasks.
 * @extends {Error}
 */
class BlobUploadTaskException extends Error {
  /** @type {BlobUploadTask} */
  task;

  /** @type {Response} */
  response;

  /**
   * Creates an instance of BlobUploadTaskException.
   * @param {string} message - The error message.
   * @param {BlobUploadTask} task - The associated blob upload task.
   * @param {Response} response - The response from the upload attempt.
   */
  constructor(message, task, response) {
    super(message);
    this.task = task;
    this.response = response;
  }
}

/**
 * Class representing a blob upload task.
 */
class BlobUploadTask {
  /** @type {BlobPart} */
  part;

  /** @type {BlobProgress} */
  onUpload;

  /** @type {BlobStorageFetch} */
  blobFetch;

  /**
   * @readonly
   * @private
   * @type number
   */
  MAX_ATTEMPTS = 5;

  /**
   * @private
   * @type number
   * */
  currentAttempt = 0;

  /**
   * Creates an instance of BlobUploadTask.
   * @param {BlobPart} part - The part of the blob to upload.
   * @param {{ onUpload?: BlobProgress }} [opts] - Optional parameters.
   */
  constructor(part, opts) {
    this.part = part;
    this.onUpload = opts?.onUpload;
    this.part.uploadedBytes = 0;
    this.blobFetch = new BlobStorageFetch();
  }

  /**
   * Runs the upload task.
   * @returns Promise<void> - A promise that resolves when the upload is complete.
   */
  run = async () => {
    try {
      const response = await this.blobFetch.upload(this.part.url, {
        blob: this.part.chunk,
        onUpload: (loaded, total) => {
          this.part.uploadedBytes = loaded;
          if (this.onUpload) this.onUpload(loaded, total);
        },
      });

      if (response.status !== 200) {
        throw new BlobUploadTaskException("An error has occurred while uploading", this, response);
      }

      this.part.etag = response.headers.get("etag") ?? undefined;
    } catch (e) {
      this.part.uploadedBytes = 0;
      if (this.currentAttempt >= this.MAX_ATTEMPTS) return;

      await new Promise((r) => setTimeout(r, 10));
      this.currentAttempt++;
      await this.run();
    }
  };
}

export { BlobUploadTask, BlobUploadTaskException };

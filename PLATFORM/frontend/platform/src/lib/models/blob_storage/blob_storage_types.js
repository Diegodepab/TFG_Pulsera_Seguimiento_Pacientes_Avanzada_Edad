/**
 * Represents a part of a blob during upload.
 * @typedef {Object} BlobPart
 * @property {number} partNumber - The part number of the blob.
 * @property {string} [etag] - The entity tag for the blob part (optional).
 * @property {Blob} [chunk] - The blob chunk (optional).
 * @property {string} url - The URL of the blob part.
 * @property {number} [uploadedBytes] - The number of bytes uploaded (optional).
 */

/**
 * Callback type for blob upload progress.
 * @callback BlobProgress
 * @param {number} loaded - The number of bytes loaded.
 * @param {number} total - The total number of bytes to be loaded.
 */

/**
 * Represents the response from a blob storage operation.
 * @typedef {Object} BlobStorageResponse
 * @property {string} blobUrl - The URL of the blob.
 * @property {BlobPart[]} [parts] - An array of blob parts (optional).
 * @property {Object} [extra] - Additional information.
 * @property {string} [extra.etag] - The entity tag for the blob (optional).
 */

/**
 * Context for blob storage exceptions.
 * @typedef {BlobStorageUploadExceptionCtx | BlobStorageMultiUploadExceptionCtx | BlobStorageDeleteExceptionCtx} BlobStorageExceptionCtx
 */

/**
 * Context for upload exceptions in blob storage.
 * @typedef {Object} BlobStorageUploadExceptionCtx
 * @property {string} path - The path where the upload occurred.
 * @property {string[]} [filenames] - The names of the files being uploaded.
 * @property {string[]} [newFilenames] - The new names assigned to the uploaded files.
 */

/**
 * Context for multi-upload exceptions in blob storage.
 * @typedef {Object} BlobStorageMultiUploadExceptionCtx
 * @property {string} path - The path where the uploads occurred.
 * @property {Object[]} errors - An array of errors encountered during the upload.
 * @property {string} [errors.filename] - The original filename (optional).
 * @property {string} [errors.newFilename] - The new filename assigned.
 * @property {Error} [errors.fromError] - The error that occurred.
 */

/**
 * Context for delete exceptions in blob storage.
 * @typedef {Object} BlobStorageDeleteExceptionCtx
 * @property {string} path - The path where the deletion occurred.
 * @property {string[]} filenames - The names of the files being deleted.
 */

/**
 * Context for multi-delete exceptions in blob storage.
 * @typedef {Object} BlobStorageMultiDeleteExceptionCtx
 * @property {string} path - The path where the deletions occurred.
 * @property {Object[]} errors - An array of errors encountered during the deletion.
 * @property {string} [errors.filename] - The original filename (optional).
 * @property {string} errors.newFilename - The new filename assigned.
 * @property {Error} errors.fromError - The error that occurred.
 */

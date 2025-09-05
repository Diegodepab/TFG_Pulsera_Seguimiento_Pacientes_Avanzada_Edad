// BlobStorage helper types

/**
 * Enum for blob operations.
 * @enum string
 */
const BlobOperation = {
  /** Remove operation */
  REMOVE: "remove",
  /** Upload operation */
  UPLOAD: "upload",
  /** Replace operation */
  REPLACE: "replace",
};

/**
 * Enum for resource types.
 * @enum string
 */
const ResourceType = {
  /** Blob storage resource type */
  BLOB_STORAGE: "blob_storage",
  /** Local storage resource type */
  LOCAL_STORAGE: "local_storage",
};

/**
 * Represents a resource stored in blob storage.
 * @typedef {Object} BlobStorageResource
 * @property {ResourceType.BLOB_STORAGE} type - The type of resource.
 * @property {string|number} dir - The directory of the resource.
 * @property {string} filename - The name of the file.
 * @property {string} bsUri - The URI of the blob storage.
 * @property {string} displayUrl - The URL to display the resource.
 * @property {string} [deleteUrl] - The URL to delete the resource.
 * @property {Object} [previousLocalResource] - Reference to a previous local resource.
 * @property {string} previousLocalResource.displayUrl - The display URL of the previous local resource.
 */

/**
 * Represents a resource stored in local storage.
 * @typedef {Object} LocalStorageResource
 * @property {ResourceType.LOCAL_STORAGE} type - The type of resource.
 * @property {string|number} dir - The directory of the resource.
 * @property {string} filename - The name of the file.
 * @property {string} displayUrl - The URL to display the resource.
 * @property {File} file - The file object.
 */

/**
 * Represents a blob resource, which can be either local or blob storage.
 * @typedef {LocalStorageResource | BlobStorageResource} BlobResource
 */

/**
 * Represents a blob resource that can be operated on.
 * @typedef {BlobResource & { operation?: BlobOperation }} OperableBlobResource
 */

/**
 * Represents a request to post multiple files.
 * @typedef {Object} FilePostMultipleRequest
 * @property {string|number} [reservedId] - An optional reserved ID.
 * @property {File} file - The file to be posted.
 */

/**
 * Represents a request to delete multiple files.
 * @typedef {Object} FileDeleteMultipleRequest
 * @property {string} id - The ID of the file to delete.
 * @property {string} filename - The name of the file to delete.
 */

/**
 * Represents a request to post a signed URL.
 * @typedef {Object} PostSignedUrlRequest
 * @property {string} filename - The name of the file.
 * @property {number} numParts - The number of parts for the upload.
 * @property {number|string} [id] - An optional ID.
 */

/**
 * Represents a request to put a signed URL.
 * @typedef {Object} PutSignedUrlRequest
 * @property {string} filename - The name of the file.
 * @property {number} numParts - The number of parts for the upload.
 */

/**
 * Represents the response from getting a signed URL.
 * @typedef {Object} GetSignedUrlResponse
 * @property {string} displayUrl - The display URL of the resource.
 */

/**
 * Represents the response from posting a signed URL.
 * @typedef {Object} PostSignedUrlResponse
 * @property {number|string} [reservedId] - An optional reserved ID.
 * @property {string} filename - The name of the file.
 * @property {string} [uploadId] - The upload ID.
 * @property {string[]} urls - The signed URLs for the upload.
 * @property {string} displayUrl - The display URL of the resource.
 * @property {string} deleteUrl - The URL to delete the resource.
 * @property {string} [completeUrl] - The URL to complete the upload.
 * @property {string} [abortUrl] - The URL to abort the upload.
 */

/**
 * Represents the response from putting a signed URL.
 * @typedef {Object} PutSignedUrlResponse
 * @property {string} [uploadId] - The upload ID.
 * @property {string[]} urls - The signed URLs for the upload.
 * @property {string} displayUrl - The display URL of the resource.
 * @property {string} deleteUrl - The URL to delete the resource.
 * @property {string} [completeUrl] - The URL to complete the upload.
 * @property {string} [abortUrl] - The URL to abort the upload.
 */

/**
 * Represents the response from an upload operation.
 * @typedef {PostSignedUrlResponse | PutSignedUrlResponse} UploadResponse
 */

/**
 * Represents the response from deleting a signed URL.
 * @typedef {Object} DeleteSignedUrlResponse
 * @property {string} deleteUrl - The URL to delete the resource.
 * @property {string} filename - The name of the file.
 * @property {string} id - The ID of the resource.
 */

export { ResourceType, BlobOperation };

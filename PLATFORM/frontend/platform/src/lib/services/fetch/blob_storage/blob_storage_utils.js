/**
 * Abstract class for utility functions related to Blob Storage operations.
 * @abstract
 */
class BlobStorageUtils {
  /**
   * @readonly
   * {number} Number of concurrent workers for uploads.
   */
  static WORKERS = 4;

  /**
   * @readonly
   * {number} Size of each chunk in bytes (5 MB).
   */
  static CHUNK_SIZE = (
    1024 * 1024
  ) * 5;

  /**
   * Creates an array of BlobPart objects from an array of URLs and a file.
   * @param {string[]} urls - The array of URLs for the blob parts.
   * @param {File} file - The file to be sliced into parts.
   * @returns BlobPart[] - An array of BlobPart objects.
   */
  static blobPartsFromUrls = (urls, file) => {
    return urls.map((url, index) => {
      const partNumber = index + 1;
      return {
        partNumber: partNumber,
        url,
        chunk: file.slice(
          BlobStorageUtils.CHUNK_SIZE * index,
          Math.min(BlobStorageUtils.CHUNK_SIZE * partNumber, file.size),
        ),
      };
    });
  };

  /**
   * Converts an array of BlobPart objects to a JSON string for the response body.
   * @param {BlobPart[]} parts - The array of BlobPart objects.
   * @returns string - The JSON string representation of the parts.
   */
  static blobPartsToResponseBody = (parts) => {
    return JSON.stringify(
      parts.map((part) =>
        Object.keys(part).reduce((acc, key) => {
          if (![ "etag", "partNumber" ].includes(key)) return acc;
          return { ...acc, [key]: part[key] };
        }, {}),
      ),
    );
  };

  /**
   * Converts an array of BlobPart objects to an XML string for multipart upload completion.
   * @param {BlobPart[]} parts - The array of BlobPart objects.
   * @returns string - The XML string representation of the parts.
   */
  static partsToXml = (parts) => {
    /** @type string[] */
    const partsSettings = parts.map((part) => {
      return `<Part><PartNumber>${ part.partNumber }</PartNumber><ETag>${ part.etag }</ETag></Part>`;
    });

    return `<CompleteMultipartUpload>${ partsSettings.join("\n") }</CompleteMultipartUpload>`;
  };
}

export { BlobStorageUtils };

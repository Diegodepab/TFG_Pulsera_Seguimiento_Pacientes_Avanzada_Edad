/**
 * Enum representing use mode of files for Dropzone.
 * @enum string
 */
const DropzoneFileUseMode = {
  STANDALONE: "standalone",
  EXTERNAL: "external",
};

/**
 * Enum representing types of files for Dropzone.
 * @enum string
 */
const DropzoneFileType = {
  model: "model",
  video: "video",
  image: "image",
};

/**
 * Represents a file in the blob storage.
 * @typedef {Object} BlobFile
 * @property {number} id - The unique identifier for the file.
 * @property {string} name - The name of the file.
 * @property {string} url - The URL to access the file.
 * @property {string} displayUrl - The URL for displaying the file.
 * @property {string} [deleteUrl] - The optional URL to delete the file.
 * @property {boolean} [original] - Indicates if this is the original file.
 */

/**
 * Represents the upload progress data.
 * @typedef {Object} UploadProgressData
 * @property {boolean | undefined} uploading - Indicates if the upload is in progress.
 * @property {number} progress - The current progress percentage of the upload (0 to 100).
 */

/** @abstract */
class DropzoneUploadFileUtils {
  static MODEL_FILE_TYPES = [ ".gltf", ".glb" ];
  static VIDEO_FILE_TYPES = [ ".avi", ".mp4", ".webm" ];
  static IMAGE_FILE_TYPES = [ ".png", ".jpg", ".gif", ".jpeg", ".svg", ".webp" ];

  static FILE_FORBIDDEN_CHARS = [ "#", "?", "&", "/", "\\" ];

  /**
   * Obtain the file extension.
   * @param {string} name - File name.
   * @returns string - Extension.
   * @static
   */
  static getFileExtension(name) {
    return `.${ name.split(".").at(-1) }`;
  }

  /**
   * Obtain the file from its name.
   * @param {string} name - File name.
   * @returns string - File type.
   * @static
   */
  static getFileTypeByName(name) {
    const extension = this.getFileExtension(name);
    if (this.MODEL_FILE_TYPES.includes(extension)) return DropzoneFileType.model;
    else if (this.VIDEO_FILE_TYPES.includes(extension)) return DropzoneFileType.video;
    else return DropzoneFileType.image;
  }

  /**
   * @static
   * Gets file types from a dropzone file type.
   * @param {DropzoneFileType} type - Dropzone file type.
   * @returns string[] - The allowed files.
   */
  static getFileTypes(type) {
    switch (type) {
      case DropzoneFileType.video:
        return this.VIDEO_FILE_TYPES;

      case DropzoneFileType.model:
        return this.MODEL_FILE_TYPES;

      case DropzoneFileType.image:
        return this.IMAGE_FILE_TYPES;
    }
  }

  /**
   * @static
   * Verify if the file contains forbidden characters.
   * @param {string} name - File name.
   * @returns boolean
   */
  static hasForbiddenChars(name) {
    return this.FILE_FORBIDDEN_CHARS.some((c) => name.indexOf(c) >= 0);
  }

  /**
   * @static
   * Improve the unit size given.
   * @param {number} kb - The number of kilobytes.
   * @returns string
   */
  static improveSizeUnit = (kb) => {
    if (!kb) return "0 bytes";

    let bytes = kb * 1024;
    const units = [ "bytes", "KB", "MB", "GB", "TB" ];
    let i = 0;
    while (bytes >= 1024) {
      bytes /= 1024;
      i++;
    }

    return `${ bytes.toFixed(2) } ${ units[i] }`;
  };

  /**
   * @static
   * Build HTML Input File.
   * @param {Object} opts - Options for build input file.
   * @param {() => unknown} opts.onInput - onInput function.
   * @param {boolean} opts.multiple - multiple boolean.
   * @param {string} opts.accept - accept.
   * @returns HTMLInputElement
   */
  static buildInputFile(opts) {
    /** @type HTMLInputElement */
    const inputFile = document.createElement("input");
    inputFile.type = "file";
    inputFile.accept = opts.accept;
    inputFile.multiple = opts.multiple;
    inputFile.oninput = opts.onInput;

    return inputFile;
  }
}

export { DropzoneFileUseMode, DropzoneFileType, DropzoneUploadFileUtils };

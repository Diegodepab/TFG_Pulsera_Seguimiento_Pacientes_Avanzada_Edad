import { Exception } from "$lib/exceptions/exception";
import { ExceptionBlobStorage, ExceptionPlatformCodes } from "$lib/exceptions/exception_codes";
import { ExceptionManager } from "$lib/exceptions/exception_manager";
import { ExceptionMessages } from "$lib/exceptions/exception_messages";

/**
 * Abstract class representing platform-specific exceptions.
 * @abstract
 */
class PlatformException {

  /**
   * Creates an exception for no available media devices.
   * @readonly
   * @returns Exception - The exception instance.
   */
  static noAvailableMediaDevices = () => {
    return new Exception(
      "No available media devices",
      "Any media device found connected in the computer", {
        code: ExceptionPlatformCodes.noAvailableMediaDevices,
        entity: "session",
      },
    );
  };

  /**
   * Creates an exception for no available video devices.
   * @readonly
   * @returns Exception - The exception instance.
   */
  static noAvailableVideoDevices = () => {
    return new Exception(
      "No available video devices",
      "Any video device found connected in the computer", {
        code: ExceptionPlatformCodes.noAvailableVideoDevices,
        entity: "session",
      },
    );
  };

  /**
   * Creates an exception for no available audio output devices.
   * @readonly
   * @returns Exception - The exception instance.
   */
  static noAvailableAudioOutputDevices = () => {
    return new Exception(
      "No available audio devices",
      "Any audio device found connected in the computer", {
        code: ExceptionPlatformCodes.noAvailableAudioOutputDevices,
        entity: "session",
      },
    );
  };

  /**
   * Creates an exception for errors during user media devices checks.
   * @readonly
   * @param {Object} [opts] - Optional parameters.
   * @param {Exception} [opts.fromError] - The original error that caused this exception.
   * @returns Exception - The exception instance.
   */
  static userMediaDevicesCheckException = (opts) => {
    return new Exception(
      "Error on request user media devices",
      "A problem occurs during user media devices checks", {
        code: ExceptionPlatformCodes.errorOnGetUserMediaDevices,
        entity: "session",
        fromError: opts?.fromError,
      },
    );
  };

  /* *
  * Player + Driven Playback Exceptions
  * */

  /**
   * Creates an exception for unknown source on player.
   * @readonly
   * @param {Object} [opts] - Optional parameters.
   * @param {Record<string, unknown>} [opts.extraArgs] - Additional arguments for the exception.
   * @returns Exception - The exception instance.
   */
  static unknownSourceOnPlayer = (opts) => {
    return new Exception(
      "Source was missing into player",
      "An unknown source was not possible to mount during playback", {
        code: ExceptionPlatformCodes.unknownPlaybackSource,
        entity: "player",
        extraArgs: opts?.extraArgs,
      },
    );
  };

  /**
   * Creates an exception for failure to create or update a CaseItemView.
   * @readonly
   * @param {"create" | "update"} type - The type of operation.
   * @param {Object} [opts] - Optional parameters.
   * @param {Record<string, unknown>} [opts.extraArgs] - Additional arguments for the exception.
   * @returns Exception - The exception instance.
   */
  static failCreateOrUpdateCaseItemView = (type, opts) => {
    return new Exception(
      `Cannot ${ type } CaseItemView`,
      `An error occurs while CaseItemView was ${ type }d`, {
        code: ExceptionPlatformCodes.failedCaseItemViewCreateOrUpdate,
        entity: "player",
        extraArgs: opts?.extraArgs,
      },
    );
  };

  /* *
   * Blob Storage Exceptions
   * */

  /**
   * Creates an exception for errors during single file upload.
   * @readonly
   * @param {Object} [opts] - Optional parameters.
   * @param {Error} [opts.fromError] - The original error that caused this exception.
   * @param {Record<string, unknown>} opts.extraArgs - Additional arguments for the exception.
   * @returns Exception - The exception instance.
   */
  static errorOnSimpleFileUpload = (opts) => new Exception(
    "Error during single file upload",
    "A problem occurs during a single file upload.", {
      code: ExceptionBlobStorage.abortedMultipartFileUpload,
      entity: "blob_storage",
      fromError: opts?.fromError,
      extraArgs: opts?.extraArgs,
    },
  );

  /**
   * Creates an exception for errors during multipart file upload.
   * @readonly
   * @param {Object} [opts] - Optional parameters.
   * @param {Error} [opts.fromError] - The original error that caused this exception.
   * @param {Record<string, unknown>} opts.extraArgs - Additional arguments for the exception.
   * @returns Exception - The exception instance.
   */
  static errorOnMultipartFileUpload = (opts) => new Exception(
    "Error during multipart file upload",
    "A problem occurs during a multipart file upload.", {
      code: ExceptionBlobStorage.abortedMultipartFileUpload,
      entity: "blob_storage",
      fromError: opts?.fromError,
      extraArgs: opts?.extraArgs,
    },
  );

  /**
   * Creates an exception for errors when uploading a file to blob storage.
   * @readonly
   * @param {Object} [opts] - Optional parameters.
   * @param {Error} [opts.fromError] - The original error that caused this exception.
   * @param {Record<string, unknown>} [opts.extraArgs] - Additional arguments for the exception.
   * @returns Exception - The exception instance.
   */
  static uploadFileToBlobStorage = (opts) => {
    return new Exception(
      "Error on upload new file to blob storage",
      "A problem occurs while a file was uploaded to Blob Storage", {
        code: ExceptionBlobStorage.errorOnFileUpload,
        entity: "blob_storage",
        fromError: opts?.fromError,
        extraArgs: opts?.extraArgs,
      },
    );
  };

  /**
   * Creates an exception for errors when getting a delete URL for a file.
   * @readonly
   * @param {Object} opts - Parameters for the exception.
   * @param {Error} opts.fromError - The original error that caused this exception.
   * @param {Record<string, unknown>} [opts.extraArgs] - Additional arguments for the exception.
   * @returns Exception - The exception instance.
   */
  static errorOnGetDeleteUrl = (opts) => {
    return new Exception(
      "Error on get delete url from file",
      "A problem occurs during the request of file deletion.", {
        code: ExceptionBlobStorage.errorOnGetDeleteUrl,
        entity: "blob_storage",
        fromError: opts.fromError,
        extraArgs: opts.extraArgs,
      },
    );
  };

  /**
   * Creates an exception for errors when removing a file from blob storage.
   * @readonly
   * @param {Object} [opts] - Optional parameters.
   * @param {Error} opts.fromError - The original error that caused this exception.
   * @param {Record<string, unknown>} [opts.extraArgs] - Additional arguments for the exception.
   * @returns Exception - The exception instance.
   */
  static deleteFileToBlobStorage = (opts) => {
    return new Exception(
      "Error on remove file to blob storage",
      "A problem occurs while a file was removed from Blob Storage", {
        code: ExceptionBlobStorage.errorOnFileDeletion,
        entity: "blob_storage",
        fromError: opts?.fromError,
        extraArgs: opts?.extraArgs,
      },
    );
  };

  /**
   * Notifies about an error and manages the exception action.
   * @readonly
   * @param {Error} error - The error to notify about.
   * @param {Object} [opts] - Optional parameters.
   * @param {boolean} [opts.ignoreUiNotifications] - Whether to ignore UI notifications.
   * @returns Promise<void> - A promise that resolves when the notification is managed.
   */
  static notifyError = async (error, opts) => {
    const exceptionAction = ExceptionMessages.getExceptionAction(error, {
      ignoreNotification: opts?.ignoreUiNotifications,
    });

    await ExceptionManager.manage(exceptionAction);
  };
}

export { PlatformException };

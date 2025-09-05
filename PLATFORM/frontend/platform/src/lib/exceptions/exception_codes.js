/**
 * Abstract class representing platform-specific exception codes.
 * @abstract
 */
class ExceptionPlatformCodes {

  /**
   * @readonly
   * @type number
   */
  static noAvailableMediaDevices = 9000001;

  /**
   * @readonly
   * @type number
   */
  static noAvailableVideoDevices = 9000002;

  /**
   * @readonly
   * @type number
   */
  static noAvailableAudioOutputDevices = 9000003;

  /**
   * Array of exception codes related to room session issues.
   * @readonly
   * @type {number[]}
   */
  static roomSessionExceptions = [
    ExceptionPlatformCodes.noAvailableMediaDevices,
    ExceptionPlatformCodes.noAvailableVideoDevices,
    ExceptionPlatformCodes.noAvailableAudioOutputDevices,
  ];

  /**
   * @readonly
   * @type number
   */
  static errorOnGetUserMediaDevices = 9000004;

  /**
   * Array of exception codes related to device request issues.
   * @readonly
   * @type {number[]}
   */
  static requestDevicesExceptions = [
    ExceptionPlatformCodes.errorOnGetUserMediaDevices,
  ];

  /**
   * @readonly
   * @type number
   */
  static unknownPlaybackSource = 9000010;

  /**
   * @readonly
   * @type number
   */
  static failedCaseItemViewCreateOrUpdate = 9000011;

  /**
   * Array of exception codes related to playback issues.
   * @readonly
   * @type {number[]}
   */
  static playbackExceptions = [
    ExceptionPlatformCodes.unknownPlaybackSource,
    ExceptionPlatformCodes.failedCaseItemViewCreateOrUpdate,
  ];

  /**
   * @readonly
   * @type number
   */
  static enterImmersiveFailed = 9000030;

  /**
   * @readonly
   * @type number
   */
  static enter3DFailed = 9000031;

  /**
   * Array of exception codes related to layout issues.
   * @readonly
   * @type {number[]}
   */
  static layoutExceptions = [
    ExceptionPlatformCodes.enterImmersiveFailed,
    ExceptionPlatformCodes.enter3DFailed,
  ];
}

/**
 * Abstract class representing exceptions related to Blob Storage.
 * @abstract
 */
class ExceptionBlobStorage {
  // blob upload related
  /**
   * Code for wrong simple file upload exception.
   * @type number
   * @readonly
   */
  static get wrongSimpleFileUpload() {
    return 9000101;
  }

  /**
   * Code for aborted multipart file upload exception.
   * @type number
   * @readonly
   */
  static get abortedMultipartFileUpload() {
    return 9000102;
  }

  /**
   * Code for aborted multipart file upload exception.
   * @type number
   * @readonly
   */
  static get errorOnFileUpload() {
    return 9000103;
  }

  /**
   * Array containing blob storage upload related exceptions.
   * @type {Array<number>}
   * @readonly
   */
  static get blobStorageExceptions() {
    return [
      ExceptionBlobStorage.wrongSimpleFileUpload,
      ExceptionBlobStorage.abortedMultipartFileUpload,
      ExceptionBlobStorage.errorOnFileUpload,
    ];
  }

  // blob removement related
  /**
   * Code for error on file deletion exception.
   * @type number
   * @readonly
   */
  static get errorOnFileDeletion() {
    return 9000104;
  }

  /**
   * Array containing blob storage deletion related exceptions.
   * @type {Array<number>}
   * @readonly
   */
  static get blobDeleteExceptions() {
    return [ ExceptionBlobStorage.errorOnFileDeletion ];
  }
}

/**
 * Abstract class representing UI context exception codes.
 * @abstract
 */
class ExceptionUiCtxCodes {
  // login related
  /**
   * Code for login failed exception.
   * @type number
   * @readonly
   */
  static get loginFailed() {
    return 100400;
  }

  /**
   * Code for invalid credentials exception during login.
   * @type number
   * @readonly
   */
  static get loginInvalidCredentials() {
    return 100401;
  }

  /**
   * Array containing login related exceptions.
   * @type {Array<number>}
   * @readonly
   */
  static get loginExceptions() {
    return [
      ExceptionUiCtxCodes.loginFailed,
      ExceptionUiCtxCodes.loginInvalidCredentials,
    ];
  }

  /**
   * Code for reset password not found email exception.
   * @type number
   * @readonly
   */
  // password related
  static get resetPasswordNotFoundEmail() {
    return 300404;
  }

  /**
   * Code for old password not matched exception.
   * @type number
   * @readonly
   */
  static get oldPasswordNotMatched() {
    return 400422;
  }

  /**
   * Array containing password related exceptions.
   * @type {Array<number>}
   * @readonly
   */
  static get passwordRelatedExceptions() {
    return [
      ExceptionUiCtxCodes.resetPasswordNotFoundEmail,
      ExceptionUiCtxCodes.oldPasswordNotMatched,
    ];
  }

  // auth exceptions
  /**
   * Code for expired session exception.
   * @type number
   * @readonly
   */
  static get expiredSession() {
    return 100402;
  }

  /**
   * Array containing user authentication related exceptions.
   * @type {Array<number>}
   * @readonly
   */
  static get userAuthExceptions() {
    return [ ExceptionUiCtxCodes.expiredSession ];
  }

  // websocket related
  /**
   * Code for not enough permissions exception in websocket.
   * @type number
   * @readonly
   */
  static get wsNotEnoughPermissions() {
    return 700401;
  }

  /**
   * Code for resource not found exception in websocket.
   * @type number
   * @readonly
   */
  static get wsResourceNotFound() {
    return 700404;
  }

  /**
   * Array containing websocket related exceptions.
   * @type {Array<number>}
   * @readonly
   */
  static get wsExceptions() {
    return [
      ExceptionUiCtxCodes.wsNotEnoughPermissions,
      ExceptionUiCtxCodes.wsResourceNotFound,
    ];
  }
}

/**
 * Abstract class representing API context exception codes.
 * @abstract
 */
class ExceptionApiCtxCodes {
  /**
   * Code for duplicated user email exception.
   * @type number
   * @readonly
   */
  static get userEmailDuplicated() {
    return 1000;
  }

  /**
   * Code for already activated user exception.
   * @type number
   * @readonly
   */
  static get userAlreadyActivated() {
    return 1001;
  }

  /**
   * Code for invalid user status name exception.
   * @type number
   * @readonly
   */
  static get userInvalidStatusName() {
    return 1003;
  }

  /**
   * Array containing user related exceptions.
   * @type {Array<number>}
   * @readonly
   */

  static get userExceptions() {
    return [
      ExceptionApiCtxCodes.userEmailDuplicated,
      ExceptionApiCtxCodes.userAlreadyActivated,
      ExceptionApiCtxCodes.userInvalidStatusName,
    ];
  }

  // login related
  /**
   * Code for invalid credentials exception during login.
   * @type number
   * @readonly
   */
  static get loginInvalidCredentials() {
    return 1004;
  }

  /**
   * Code for invalid credentials when user is blocked exception during login.
   * @type number
   * @readonly
   */
  static get loginInvalidCredentialsUserBlocked() {
    return 1005;
  }

  /**
   * Array containing login related exceptions.
   * @type {Array<number>}
   * @readonly
   */
  static get loginExceptions() {
    return [
      ExceptionApiCtxCodes.loginInvalidCredentials,
      ExceptionApiCtxCodes.loginInvalidCredentialsUserBlocked,
    ];
  }

  /**
   * Code for duplicated patient codes exception.
   * @type number
   * @readonly
   */
  static get patientcodeDuplicated() {
    return 2000;
  }

  /**
   * Array containing patient related exceptions.
   * @type {Array<number>}
   * @readonly
   */
  static get patientExceptions() {
    return [
      ExceptionApiCtxCodes.patientcodeDuplicated,
    ];
  }
}

export {
  ExceptionPlatformCodes,
  ExceptionBlobStorage,
  ExceptionUiCtxCodes,
  ExceptionApiCtxCodes,
};

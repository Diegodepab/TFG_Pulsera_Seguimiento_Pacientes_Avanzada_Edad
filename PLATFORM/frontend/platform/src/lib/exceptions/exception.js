import { ExceptionUiCtxCodes } from "$lib/exceptions/exception_codes";

class Exception extends Error {

  /** @type string */
  title;
  /** @type {number | undefined} */
  code;
  /** @type {Error | undefined} */
  fromError;
  /** @type string */
  entity;
  /** @type { Record<string, ?>} */
  extraArgs;

  /**
   * Creates an instance of Exception.
   * @param {string} title - The title of the exception.
   * @param {string} message - The message describing the exception.
   * @param {Object} [opts] - Optional options for the exception.
   * @param {number} [opts.code] - Optional code associated with the exception.
   * @param {Error} [opts.fromError] - Optional Error object from which this exception originates.
   * @param {string} [opts.entity] - Optional entity related to the exception.
   * @param {Record<string, unknown>} [opts.extraArgs] - Additional arguments or data associated with the exception.
   */
  constructor(title, message, opts) {
    super(message);
    this.title = title;
    this.code = opts?.code;
    this.fromError = opts?.fromError;
    this.entity = opts?.entity;
    this.extraArgs = opts?.extraArgs;
  }

  /// This is a modifier property to get more specific context of error
  /**
   * Optional UI context information associated with the exception.
   * @type {UiCtxException=}
   * @private
   */
  _uiCtx;

  /**
   * Gets the UI context information associated with the exception.
   * @type {UiCtxException | undefined}
   */
  get uiCtx() {
    return this._uiCtx;
  }

  /**
   * Sets the UI context information associated with the exception.
   * @param {UiCtxException | undefined} value - The UI context information to set.
   */
  set uiCtx(value) {
    this._uiCtx = value;
  }

  // This is a modifier property to get more specific context of error
  /**
   * Optional API context information associated with the exception.
   * @type {ApiCtxException=}
   * @private
   */
  _apiCtx;

  /**
   * Gets the UI context information associated with the exception.
   * @type {ApiCtxException | undefined}
   */
  get apiCtx() {
    return this._apiCtx;
  }

  /**
   * Gets the UI context information associated with the exception.
   * @param {ApiCtxException | undefined} value
   */
  set apiCtx(value) {
    this._apiCtx = value;
  }

  static invalidToken = () =>
    new Exception("Token", "Invalid token", {
      code: ExceptionUiCtxCodes.loginInvalidCredentials,
      entity: "oauth",
    });
}

export { Exception };

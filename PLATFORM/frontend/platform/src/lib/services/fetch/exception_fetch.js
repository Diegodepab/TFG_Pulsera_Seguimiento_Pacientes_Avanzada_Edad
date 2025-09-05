import { Utils } from "$lib/commons/utils";
import { Exception } from "$lib/exceptions/exception";

class ExceptionFetch extends Exception {
  /**
   * Creates an instance of ExceptionFetch.
   * @param {string} title - The title of the exception.
   * @param {string} message - The error message.
   * @param {Object} [opts] - Additional options for the exception.
   * @param {number} [opts.code] - The error code.
   * @param {Error} [opts.fromError] - The original error object.
   * @param {string} [opts.entity] - The entity associated with the exception.
   */
  constructor(title, message, opts) {
    super(title, message, opts);
  }

  /**
   * @static
   * Creates an instance of ExceptionFetch based on an existing Exception.
   * @param {Exception} error - The original Exception object.
   * @returns ExceptionFetch - An instance of ExceptionFetch.
   */
  static fromException = (error) => {
    return new ExceptionFetch(error.title, error.message, {
      code: error.code,
      fromError: error.fromError,
      entity: error.entity,
    });
  };

  /**
   * @static
   * Creates an instance of ExceptionFetch based on a fetch Response object.
   * @param {Response} response - The fetch Response object.
   * @param {Object} [opts] - Additional options for creating the exception.
   * @param {string} [opts.entity] - The entity associated with the exception.
   * @returns Promise<ExceptionFetch> - A promise that resolves to an instance of ExceptionFetch.
   */
  static fromResponse = async (response, opts) => {
    /** @type number */
    const code = response.status;
    /** @type string */
    const title = response.statusText;
    /** @type string */
    const message = response.statusText;

    /** @type {ExceptionFetch} */
    const exception = new ExceptionFetch(title, message, {
      code,
      entity: opts?.entity,
    });

    try {
      const json = await response.json();
      if (json) {
        exception.apiCtx = {
          code: json.code,
          type: json.type,
          message: json.msg ?? json.detail?.toString(),
          loc: json.loc,
          extra: json.extra,
        };
      }
    } catch (e) {
      Utils.logging("error", e);
    }

    return exception;
  };
}

export { ExceptionFetch };

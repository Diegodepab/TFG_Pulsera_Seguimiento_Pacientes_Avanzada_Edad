import { CommonAlerts } from "$components/platform/utils/common_alerts";
import { CommonNotifications } from "$components/platform/utils/common_notifications";
import { Global } from "$lib/commons/global";

import { SessionManager } from "$lib/commons/session_manager";
import { Exception } from "$lib/exceptions/exception";
import { ExceptionAction, ExceptionActionLevel } from "$lib/exceptions/exception_action";
import { ExceptionApiCtxCodes, ExceptionBlobStorage, ExceptionUiCtxCodes } from "$lib/exceptions/exception_codes";
import { t } from "svelte-i18n";
import Swal from "sweetalert2/dist/sweetalert2";

class ExceptionMessages {
  /**
   * Get an exception action based on the provided error.
   * @static
   * @param {Error} error - The error object.
   * @param {Object} [opts] - Options.
   * @param {boolean} [opts.ignoreNotification] - Whether to ignore notifications.
   * @returns ExceptionAction - The exception action.
   */
  static getExceptionAction(error, opts) {
    let errorKey;
    let errorExtraArgs;
    let customDefaultErrorKey;
    /**
     * @type ExceptionActionShowMessageFunction
     * @param {ExceptionActionShowMessageArgs} opts - The options for displaying the message.
     * @returns Promise<void> - A promise indicating the completion of displaying the message.
     */
    let showMessage = async (opts) =>
      await Swal.fire({
        title: opts.title,
        html: opts.content,
        icon: opts.icon ?? "warning",
        heightAuto: false,
        buttonsStyling: false,
        allowOutsideClick: false,
        customClass: {
          confirmButton: "btn btn-warning",
        },
      });

    /**
     * Arguments for displaying a message in an exception action.
     * @type ExceptionActionShowMessageArgs
     */
    const showMessageKArgs = {};

    /**
     * Function to manage an exception action.
     * @type ExceptionOnManageFunction
     */
    let onManage;

    // ignored errors
    if (error?.message.includes("The play()")) {
      console.warn(error);
      return new ExceptionAction(error, "", "", {
        report: false,
        level: ExceptionActionLevel.INFO,
        showMessage: undefined,
        showMessageKArgs: {},
        onManage: undefined,
      });
    }

    errorKey = "exception.common.unknown";

    if (error instanceof Exception) {
      /** @type {Exception} */
      const exception = error;
      /** @type number */
      const code = exception.code;
      /** @type string */
      const entity = exception.entity;

      errorKey = `exception.common.${ code }.${ entity ?? "generic" }`;
      customDefaultErrorKey = `exception.common.${ code }.default`;

      if (ExceptionBlobStorage.blobStorageExceptions.includes(code)) {
        if (Global.notificationContext != null) {
          /** @returns Promise<void> */
          showMessage = async () => {
            await CommonAlerts.uploadBlobStorageAdvice();
          };
        }
      } else if (ExceptionBlobStorage.blobDeleteExceptions.includes(code)) {
        showMessage = undefined;
      } else if (
        ExceptionUiCtxCodes.loginExceptions.includes(exception.uiCtx?.code) ||
        ExceptionUiCtxCodes.passwordRelatedExceptions.includes(exception.uiCtx?.code)
      ) {
        errorKey = `exception.uiCtx.${ exception.uiCtx.code }`;
        if (Global.notificationContext != null) {
          /**
           * @param {ExceptionActionShowMessageArgs} opts - The options for displaying the message.
           * @returns Promise<void> - A Promise that resolves when the message is displayed.
           */
          showMessage = async (opts) => {
            CommonNotifications.genericDanger(opts.content ?? opts.title);
          };
        }
      } else if (ExceptionApiCtxCodes.loginExceptions.includes(exception.apiCtx?.code)) {
        showMessage = undefined;
      } else if (ExceptionApiCtxCodes.userExceptions.includes(exception.apiCtx?.code)) {
        errorKey = `exception.apiCtx.${ exception.apiCtx.code }`;
      } else if (ExceptionApiCtxCodes.patientExceptions.includes(exception.apiCtx?.code)) {
        errorKey = `exception.apiCtx.${ exception.apiCtx.code }`;

        if (Global.notificationContext != null) {
          /**
           * @param {ExceptionActionShowMessageArgs} opts - The options for displaying the message.
           * @returns Promise<void> - A Promise that resolves when the message is displayed.
           */
          showMessage = async (opts) => {
            CommonNotifications.genericDanger(opts.content ?? opts.title);
          };
        }
      } else if (
        ExceptionUiCtxCodes.wsExceptions.find((code) => code === exception.uiCtx?.code)
      ) {
        errorKey = `exception.ws.${ exception.apiCtx.code ?? exception.uiCtx.code }`;
      } else if (code === 401 || ExceptionUiCtxCodes.userAuthExceptions.includes(exception.uiCtx?.code)) {
        showMessage = undefined;
        onManage = ExceptionMessages.__goToLogin;
      }
    } else {
      if (import.meta.env.DEV) {
        console.warn("This error is not controlled by us. Take the info about it and tell anyone", error.name);
      }

      // this code omits the error in case the error is not controlled previously
      opts ??= {};
      opts.ignoreNotification = true;
    }

    // used to resolve the translations tValue('key', { args })
    /**
     * Retrieves the value associated with a key.
     *
     * @param {string} key - The key to look up in the value table.
     * @param {Record<string, unknown>} [args] - Additional arguments (optional).
     * @returns string - The value corresponding to the specified key.
     */
    let tValue = (key, args) => {
    };
    const unsubscribe = t.subscribe((value) => tValue = value);

    /** @type string */
    let title;
    /** @type string */
    let content;
    try {
      title = tValue(`${ errorKey }.title`, {
        values: errorExtraArgs?.title,
        default: tValue(`${ customDefaultErrorKey }.title`, {
          default: tValue(`exception.common.unknown.title`),
        }),
      });

      content = tValue(`${ errorKey }.content`, {
        values: errorExtraArgs?.content,
        default: tValue(`${ customDefaultErrorKey }.content`, {
          default: tValue(`exception.common.unknown.content`),
        }),
      });
    } catch (e) {
      // this try-catch pretends to fix the "Cannot format without set the first locale" exception.
      // although tValue is defined, error is thrown when access to tValue method without init the locales
      title = "Unknown error";
      content = "An unexpected error has occurred, please reload your page. If your problem persist contact to the support team.";
    }

    Object.entries(showMessageKArgs).forEach(([ k, v ]) => showMessageKArgs[k] = tValue(v));
    unsubscribe();

    if (opts?.ignoreNotification) showMessage = undefined;

    return new ExceptionAction(error, title, content, {
      report: true,
      level: ExceptionActionLevel.ERROR,
      showMessage,
      showMessageKArgs: { title, content, ...showMessageKArgs },
      onManage,
    });
  };

  /**
   * Static method to navigate to the login page.
   * @returns Promise<void> - A Promise that resolves when navigation to the login page is completed.
   * @private
   */
  static __goToLogin = async () => {
    await SessionManager.closeSession();
    // await goto('/login', { replaceState: true });
    location.replace("/");
  };
}

export { ExceptionMessages };

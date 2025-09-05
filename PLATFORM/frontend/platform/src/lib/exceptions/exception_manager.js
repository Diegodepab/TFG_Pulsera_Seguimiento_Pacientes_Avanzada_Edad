import { Constants } from "$lib/commons/constants";
import { Utils } from "$lib/commons/utils";
import { Exception } from "$lib/exceptions/exception";
import * as Sentry from "@sentry/browser";
import { Integrations } from "@sentry/tracing";

/**
 * @typedef {import("./exception_action").ExceptionAction} ExceptionAction
 * @typedef {import("@sentry/browser").BrowserOptions} BrowserOptions
 */

class _ExceptionManager {
  /**
   * Initializes the exception manager with optional configurations.
   * @public
   * @param {Object} [options] - Configuration options.
   * @param {BrowserOptions} [options.sentryOptions] - Sentry configuration options.
   * @returns void
   */
  init = (options) => {
    // Sentry initialization
    Sentry.init({
      dsn: options?.sentryOptions?.dsn ?? "https://ea55f3d4524e495bbf9b1d44cd906dbb@o435580.ingest.sentry.io/6106466",
      release: options?.sentryOptions?.release ?? `${ Constants.appName }@${ Constants.appRelease }`,
      // tunnel: options?.sentryOptions?.tunnel ?? '/sentry',  // this is needed to avoid ad-blockers,
      integrations: options?.sentryOptions?.integrations ?? [ new Integrations.BrowserTracing() ],///Que es eso
      tracesSampleRate: options?.sentryOptions?.tracesSampleRate ?? 0,
      attachStacktrace: options?.sentryOptions?.attachStacktrace ?? true,
    });
  };

  /**
   * Manages the exception action by reporting errors and executing optional actions.
   * @public
   * @param {ExceptionAction} action - The exception action to manage.
   * @returns Promise<void>
   */
  manage = async (action) => {
    if (!action.report) {
      Utils.logging("log", "Platform Exception", `Error: ${ action.error }`, `Action: ${ action }`);
    } else {
      try {
        this._reportError(action);
      } catch (e) {
        Utils.logging(
          "error",
          "An error occurred while trying to report some error via Sentry:",
          ` -Error: ${ e }`,
          ` -First Error: ${ action.error }`,
        );
      }
    }

    if (action.showMessage != null) await action.showMessage(action.showMessageKArgs);
    if (action.onManage != null) await action.onManage();
  };

  /**
   * Reports the error to the error tracking system (e.g., Sentry) and logs additional information.
   * @private
   * @param {ExceptionAction} action - The exception action to report.
   * @returns void
   */
  _reportError = (action) => {
    /** @type {Record<string, unknown> | undefined} */
    let extraArgs;
    if (action.error instanceof Exception && Object.keys(action.error.extraArgs ?? {}).length) {
      extraArgs = action.error && action.error.extraArgs;
    }

    /**
     * Executes a function within a Sentry scope, allowing additional context to be attached to captured errors.
     * @param {Sentry.ScopeCallback} callback - The function to execute within the Sentry scope.
     * @returns void
     */
    Sentry.withScope((scope) => {
      scope.setLevel(Utils.exceptionLevelToSentrySeverity(action.level));

      // include extraArgs to Sentry
      if (action.error instanceof Exception && action.error.extraArgs) {
        scope.setContext("extraArgs", action.error.extraArgs);
      }

      Sentry.captureException(action.error);
    });

    if (import.meta.env.DEV && extraArgs) Utils.logging("error", extraArgs);
    Utils.logging("error", action.error);
  };
}

export const ExceptionManager = new _ExceptionManager();

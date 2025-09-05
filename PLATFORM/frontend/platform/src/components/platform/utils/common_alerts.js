import { DropzoneFileType } from "$components/platform/uploadFile/dropzone_upload_file_utils";
import { i18nGender } from "$lib/commons/ui_utils";
import { t } from "svelte-i18n";
import Swal from "sweetalert2/dist/sweetalert2";

class CommonAlerts {
  /**
   * Generates a confirmation for deleting or disabling an entity.
   * @static
   * @async
   * @param {Object} [opts] - Options for the advice.
   * @param {string} [opts.title] - Title for the advice.
   * @param {string} [opts.content] - Satisfied message of the advice.
   * @param {string} [opts.confirmButtonText="OK"] - The text of the confirmation button.
   * @returns Promise<boolean> - A promise indicating if the action was confirmed.
   */
  static async genericHighImportanceInfo({ title, content, confirmButtonText } = {}) {
    return await Swal.fire({
      title,
      text: content,
      buttonsStyling: false,
      customClass: {
        confirmButton: "btn btn-info",
      },
      allowOutsideClick: false,
      icon: "info",
      showCancelButton: false,
      confirmButtonText: confirmButtonText ?? "OK",
    });
  }

  /**
   * Provides advice for uploading to Blob Storage.
   * @static
   * @async
   * @param {Object} [opts] - Options for the advice.
   * @param {string} [opts.title] - Title for the advice.
   * @param {string} [opts.content] - Satisfied message of the advice.
   * @param {string} [opts.confirmButtonText="OK"] - The text of the confirmation button.
   * @returns Promise<SweetAlertResult> - A promise with the result of the advice.
   */
  static async genericConfirmation({ title, content, confirmButtonText } = {}) {
    return await Swal.fire({
      title,
      text: content,
      icon: "warning",
      heightAuto: false,
      buttonsStyling: false,
      allowOutsideClick: false,
      customClass: {
        confirmButton: "btn btn-danger",
        cancelButton: "btn btn-secondary",
      },
      confirmButtonText: confirmButtonText ?? "OK",
      showCancelButton: true,
      cancelButtonText: CommonAlerts.getText("common.button.cancel"),
    });
  }

  // TODO: Check gender translations
  /**
   * Generates a confirmation for deleting or disabling an entity.
   * @static
   * @async
   * @param {string} entity - The entity to delete or disable.
   * @param {Object} [opts] - Options for the confirmation.
   * @param {boolean} [opts.isDisable=false] - Indicates if it should be disabled instead of deleted.
   * @param {i18nGender} [opts.gender="female"] - The gender of the entity (default is female).
   * @returns Promise<boolean> - A promise indicating if the action was confirmed.
   */
  static async deleteOrDisableConfirmation(entity, { isDisable, gender } = {}) {
    const action = isDisable ? "disable" : "delete";
    gender ??= i18nGender.FEMALE; // most of the entities are female referenced
    const result = await CommonAlerts.genericConfirmation({
      title: CommonAlerts.getText("alert.common.confirmation.title"),
      content: CommonAlerts.getText(`alert.common.${ action }.content`, {
        values: { entity: entity.toLowerCase(), gender: gender.valueOf() },
      }),
      confirmButtonText: CommonAlerts.getText(`alert.common.button.confirm-${ action }`, {
        values: { entity: entity.toLowerCase(), gender: gender.valueOf() },
      }),
    });

    return !!result?.value;
  };

  /**
   * Provides an advice for uploading to Blob Storage.
   * @static
   * @async
   * @param {Object} [opts] - Options for the advice.
   * @param {string} [opts.text] - The text of the advice.
   * @param {DropzoneFileType} [opts.type] - The file type (default is video).
   * @param {boolean} [opts.asDelete] - Indicates if it's a deletion action.
   * @param {string} [opts.confirmButtonText] - The text of the confirmation button.
   * @returns Promise<SweetAlertResult> - A promise with the result of the advice.
   */
  static async uploadBlobStorageAdvice(opts) {
    if (opts == null) {
      opts = {};
    }
    const action = opts.asDelete ? "delete" : "upload";
    if (opts.type == null) {
      opts.type = DropzoneFileType.video;
    }
    if (opts.text == null) {
      opts.text = CommonAlerts.getText(`alert.upload-file-warning.content.${ action }.${ opts.type }`);
    }

    return await Swal.fire({
      titleText: CommonAlerts.getText(`alert.upload-file-warning.title.${ action }`),
      text: opts.text,
      icon: "warning",
      heightAuto: false,
      buttonsStyling: false,
      allowOutsideClick: false,
      customClass: {
        confirmButton: "btn btn-warning",
      },
      confirmButtonText: opts.confirmButtonText ?? "OK",
    });
  };

  /**
   * Gets translated text for a given key.
   * @private
   * @param {string} key - The translation key.
   * @param {Record<string, unknown>} [opts] - Options for the translation.
   * @returns string - The translated text.
   */
  static getText(key, opts) {
    let tValue; // used to resolve the translations tValue('key')
    const unsubscribe = t.subscribe((value) => tValue = value);
    const value = tValue(key, opts);
    unsubscribe();
    return value;
  };

  // todo. review in the future to check if its works
  // static getText(key, opts) => get(t)(key, opts);
}

export { CommonAlerts };

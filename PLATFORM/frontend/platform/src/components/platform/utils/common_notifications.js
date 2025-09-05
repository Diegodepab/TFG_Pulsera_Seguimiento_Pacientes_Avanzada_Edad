import { Global } from "$lib/commons/global";
import { t } from "svelte-i18n";
import { v4 as uuidv4 } from "uuid";

/**
 * Abstract class for generating common notifications.
 * @abstract
 */
class CommonNotifications {
  /**
   * Generates a notification with a danger type.
   * @static
   * @param {string} message - The message for the notification.
   * @return {void}
   */
  static genericDanger(message) {
    Global.notificationContext.addNotification({
      id: uuidv4(),
      text: message,
      position: "top-right",
      notifyClassNames: "top right",
      type: "danger",
      removeAfter: 3000,
      icon: "fas fa-triangle-exclamation",
    });
  };

  /**
   * Generates a notification with a warning type.
   * @static
   * @param {string} message - The message for the notification.
   * @return {void}
   */
  static genericWarning(message) {
    Global.notificationContext.addNotification({
      id: uuidv4(),
      text: message,
      position: "top-right",
      notifyClassNames: "top right",
      type: "warning",
      removeAfter: 3000,
      icon: "fas fa-circle-info",
    });
  };

  /**
   * Generates a notification with a success type.
   * @static
   * @param {string} message - The message for the notification.
   * @return {void}
   */
  static genericSuccess(message) {
    Global.notificationContext.addNotification({
      id: uuidv4(),
      text: message,
      position: "top-right",
      notifyClassNames: "top right",
      type: "success",
      removeAfter: 3000,
      icon: "fas fa-check",
    });
  };

  /**
   * Provides a notification for no access permissions.
   * @static
   * @return {void}
   */
  static noAccessPermissions() {
    CommonNotifications.genericWarning(
      CommonNotifications.getText("notification.entity.permission.no-access"),
    );
  };

  /**
   * Generates a notification for a validation error.
   * @static
   * @return {void}
   */
  static validationError() {
    CommonNotifications.genericDanger(
      CommonNotifications.getText("notification.common.validation-error"),
    );
  };

  /**
   * Gets translated text for a given key.
   * @private
   * @param {string} key - The translation key.
   * @return {string} The translated text.
   */
  static getText(key) {
    let tValue; // used to resolve the translations tValue('key')
    const unsubscribe = t.subscribe((value) => tValue = value);
    const value = tValue(key);
    unsubscribe();
    return value;
  };
}

export { CommonNotifications };

import { BaseController } from "$lib/controllers/base_controller";
import { PasswordFetch } from "$lib/services/fetch/password_fetch";

class PasswordController extends BaseController {
  /** @type {PasswordFetch} */
  fetch;

  constructor() {
    super();
    this.fetch = new PasswordFetch();
  }

  /**
   * Resets the password for the given email.
   * @param {string} email - The email for which the password will be reset.
   * @returns Promise<boolean> - A promise that resolves with a boolean indicating if the password reset was successful.
   */
  reset = (email) => this.fetch.reset(email);

  /**
   * Saves the password using the provided token.
   * @param {string} token - The token used for password reset.
   * @param {string} password - The new password to save.
   * @returns Promise<void> - A promise that resolves when the password is successfully saved.
   */
  savePassword = (token, password) => this.fetch.savePassword(token, password);
}

export { PasswordController };

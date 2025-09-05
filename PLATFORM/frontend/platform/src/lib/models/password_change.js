import { BaseModel } from "$lib/models/base_model";

class ApiFields {
  /**
   * @type string
   * @readonly
   */
  oldPassword = "old_password";

  /**
   * @type string
   * @readonly
   */
  newPassword = "new_password";
}

class PasswordChange extends BaseModel {
  /**
   * @type ApiFields
   * @readonly
   */
  static apiFields = new ApiFields();
  /** @type string */
  oldPassword;
  /** @type string */
  newPassword;

  /**
   * Creates an instance of PasswordChangeRequest.
   * @param {string} oldPassword - The old password.
   * @param {string} newPassword - The new password.
   */
  constructor(oldPassword, newPassword) {
    super();

    this.oldPassword = oldPassword;
    this.newPassword = newPassword;
  }

  /**
   * Creates an empty PasswordChange instance.
   * @returns PasswordChange - An empty PasswordChange instance.
   */
  static empty = () => new PasswordChange(null, null);

  /**
   * Converts the PasswordChange instance to a dictionary.
   * @returns Json - A dictionary representation of the PasswordChange instance.
   */
  toDict = (_) => {
    return {
      [PasswordChange.apiFields.oldPassword]: this.oldPassword,
      [PasswordChange.apiFields.newPassword]: this.newPassword,
    };
  };
}

export { PasswordChange };

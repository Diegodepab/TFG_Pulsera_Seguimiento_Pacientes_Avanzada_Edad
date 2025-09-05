import { User } from "$lib/models/user";
import { ExceptionFetch } from "$lib/services/fetch/exception_fetch";
import { Fetch } from "$lib/services/fetch/fetch";
import { QueryEncoder } from "$lib/services/utils/query_encoder";
import { QueryFields, QueryParamsRaw } from "$lib/services/utils/query_utils";

class PasswordFetch extends Fetch {
  /** @type string */
  path = "/password";
  /** @type string */
  entity = "password";

  constructor() {
    super();
  }

  /**
   * Resets the password for the specified email.
   * @param {string} email - The email for which the password will be reset.
   * @returns Promise<boolean> - A promise that resolves with a boolean indicating if the password reset request was
   *   successful.
   */
  reset = async (email) => {
    /** @type {Map<QueryFields, unknown>} */
    const params = new Map();

    params.set(QueryFields.RAW, [
      new QueryParamsRaw({
        field: User.apiFields.email,
        value: email.trim(),
      }),
    ]);

    return await this.passwordRequest("reset", params);
  };

  /**
   * Saves the provided password using the provided token.
   * @param {string} token - The token used for password reset.
   * @param {string} password - The new password to save.
   * @returns Promise<void> - A promise that resolves when the password is successfully saved.
   */
  savePassword = async (token, password) => {
    /** @type {Map<QueryFields, unknown>} */
    const params = new Map();
    params.set(QueryFields.RAW, [
      new QueryParamsRaw({
        field: "token",
        value: token.trim(),
      }),
    ]);

    await this.post({ password: password }, { extraPath: "/edit", params });
  };

  /**
   * Makes a password request with the provided extra path and parameters.
   * @private
   * @param {string} extraPath - The extra path for the password request.
   * @param {Map<QueryFields, unknown>} params - The parameters for the password request.
   * @returns Promise<boolean> - A promise that resolves with a boolean indicating the success of the password request.
   * @throws {ExceptionFetch} If the request fails.
   */
  passwordRequest = async (extraPath, params) => {
    /** @type string */
    let _path = `${ this.host }${ this.path }/${ extraPath }`;
    _path = QueryEncoder.encodeQuery({ params, path: _path });

    /** @type {Response} */
    const response = await fetch(_path, { method: "GET" });

    if (response.status === 204) return true;
    throw await ExceptionFetch.fromResponse(response, { entity: "email" });
  };
}

export { PasswordFetch };

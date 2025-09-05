import { SessionManager } from "$lib/commons/session_manager";
import { OauthToken } from "$lib/models/oauth_token";
import { User } from "$lib/models/user";
import { ExceptionFetch } from "$lib/services/fetch/exception_fetch";
import { Fetch } from "$lib/services/fetch/fetch";

class UserFetch extends Fetch {
  /** @type string */
  path = "/users";
  /** @type string */
  entity = "user";
  /** @type ModelTransformer */
  transformer = User.transformer;

  constructor() {
    super();
    this.headers = super.headers ?? {};
  }

  /** @returns Promise<void> */
  oauthHeader = async () => {
    const authHeader = (await SessionManager.token()).getHeader();
    Object.entries(authHeader).forEach(([ key, value ]) => {
      this.headers[key] = value;
    });
  };

  /**
   * Activates a user account using the provided access token and data.
   * @param {string} accessToken - The access token.
   * @param {Json} data - The data for activation.
   * @returns Promise<boolean> - A promise that resolves with a boolean indicating if the activation was successful.
   * @throws ExceptionFetch - Request fails.
   */
  activate = async (accessToken, data) => {
    /** @type {OauthToken} */
    const token = new OauthToken(accessToken, null, null, null);
    /** @type string */
    const _path = `${ this.host }${ this.path }/${ token.userId }/activate`;

    const headers = {
      "Content-Type": "application/json",
      ...token.getHeader(),
    };

    /** @type string */
    const body = typeof data === "string" ? data : JSON.stringify(data);
    const response = await fetch(_path, {
      method: "POST",
      body: body,
      headers,
    });

    if (response.status === 200) return true; // activated user
    throw await ExceptionFetch.fromResponse(response, { entity: this.entity });
  };

  /**
   * Deletes a user account using the provided options.
   * @param {Object} [opts] - Options for deleting the account.
   * @param {number|string} [opts.userId] - The ID of the user to delete.
   * @param {string} [opts.accessToken] - The access token.
   * @returns Promise<boolean> - A promise that resolves with a boolean indicating if the deletion was successful.
   * @throws {ExceptionFetch} If the request fails.
   */
  // deleteAccount = async (opts) => {
  //   /** @type {OauthToken} */
  //   let token;
  //   let headers;
  //
  //   if (opts?.accessToken) {
  //     token = new OauthToken(opts.accessToken, null, null, null);
  //     headers = { ...token.getHeader() };
  //   } else {
  //     await this.oauthHeader();
  //     headers = this._addHeaders();
  //   }
  //
  //   /** @type {string|number} */
  //   const id = token?.userId ?? opts.userId;
  //   const _path = `${ this.host }${ this.path }/${ id }/delete-account`;
  //
  //   const response = await fetch(_path, { method: "POST", headers });
  //
  //   if (response.status === 200) return true; // disabled user
  //   throw await ExceptionFetch.fromResponse(response, { entity: this.entity });
  // };
}

export { UserFetch };

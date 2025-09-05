import { Constants } from "$lib/commons/constants";
import { Utils } from "$lib/commons/utils";
import { OauthController } from "$lib/controllers/oauth_controller";
import { Exception } from "$lib/exceptions/exception";
import { ExceptionUiCtxCodes } from "$lib/exceptions/exception_codes";
import { OauthToken } from "$lib/models/oauth_token";
import { User } from "$lib/models/user";
import { UserPermission } from "$lib/models/user_permission";
import { QueryComparativeOperations, QueryFields, QueryParamsQ } from "$lib/services/utils/query_utils";
import moment from "moment";

class _SessionManager {
  constructor() {
    /**
     * User object associated with the session.
     * @private
     * @type {User|null}
     */
    this._user = null;

    /**
     * Authentication token.
     * @private
     * @type {OauthToken|null}
     */
    this._token = null;

    /**
     * @private
     * @type {OauthController|null}
     */
    this._oauthCtl = null;

    /**
     * @private
     * User controller instance.
     */
    this._userCtl = null;
  }

  /** @returns number - ID of the User */
  userId = () => this._token?.userId;

  /** @returns UserRoleType - Rol of the User. */
  userRole = () => this._token?.userRole;

  /**
   * @param {Object} [opts]
   * @param {boolean} [opts.ignoreNotValidTokenError]
   * @param {boolean} [opts.ignoreExceptions]
   * @returns Promise<OauthToken>
   * @throws Exception - Throws an error if token is not valid.
   */
  token = async (opts) => {
    let valid;

    try {
      valid = await this._isValid();
    } catch (e) {
      this._cleanTokenFromLocalStorage();
      if (!opts?.ignoreExceptions) throw e;
      return null;
    }

    if (!valid && !opts?.ignoreNotValidTokenError && !opts?.ignoreExceptions) {
      this._cleanTokenFromLocalStorage();
      throw Exception.invalidToken();
    }

    return this._token;
  };

  /**
   * Gets the basic authorization value.
   * @returns string - The basic authorization value.
   */
  getBasis = () => {
    return `Basic ${ btoa(`${ Constants.APP_ID }:${ Constants.APP_IDK }`) }`;
  };

  /**
   * Initializes the session.
   * @returns Promise<void> - A promise indicating the initialization completion.
   */
  init = async () => {
    this._oauthCtl ??= new OauthController();
    if (this._userCtl == null) {
      const { UserController } = await import("$lib/controllers/user_controller");
      this._userCtl ??= new UserController();
    }
  };

  /**
   * Saves the new token in the session and session Storage.
   * @param {OauthToken} token - The token to be saved.
   * @returns Promise<void> - A promise indicating the completion of the token saving process.
   */
  saveToken = async (token) => {
    this._user = null;
    this._token = token;

    window.sessionStorage.removeItem("token");
    window.localStorage.setItem("token", JSON.stringify(token.toDict()));
  };

  /**
   * Closes the user session.
   * @returns Promise<void> - A promise indicating the completion of the session closure.
   */
  closeSession = async () => {
    this._token ??= await this._loadFromStorage();

    if (this._token == null || moment().isAfter(moment.unix(this._token.tokenExpirationDate))) {
      return this._cleanTokenFromLocalStorage();
    }

    try {
      await this._oauthCtl.revokeToken(this._token.accessToken);
    } catch (e) {
      Utils.logging(e);
    }

    return this._cleanTokenFromLocalStorage();
  };

  /**
   * Retrieves the user information.
   * @returns Promise<User> - A promise containing the user information.
   * @throws Exception - Throws an error if the user not found.
   */
  user = async () => {
    if (this._user == null || this._user.id != this.userId()) {
      try {
        this._user = await this._userCtl.get(this.userId());
      } catch (e) {
        if (!(e instanceof Exception)) throw e;

        e.uiCtx = {
          code: e.code === 404 ? ExceptionUiCtxCodes.loginInvalidCredentials : ExceptionUiCtxCodes.expiredSession,
        };
        throw e;
      }
    }

    return this._user;
  };

  /**
   * Retrieves the user permissions.
   * @param {Object} [opts] - Additional options.
   * @param {Map<QueryFields, unknown>} [opts.params] - Parameters for the query.
   * @returns Promise<UserPermission[]> - A promise containing the user permissions.
   */
  userPermissions = async ({ params } = {}) => {
    return await this._userCtl.getPermissions({ params });
  };

  /**
   * Retrieves the user permissions for specific entities.
   * @param {PermissionsEntityType[]} entities - The entities to check permissions for.
   * @returns Promise<UserPermission[]> - A promise containing the user permissions for the specified entities.
   */
  userPermissionsOn = (entities) => {
    /**
     * Parameters for a permission query.
     * @type {Map<QueryFields, unknown>}
     */
    const params = new Map();
    params.set(QueryFields.Q, [
      new QueryParamsQ({
        field: UserPermission.apiFields.entityName,
        operation: QueryComparativeOperations.IN,
        value: entities,
      }),
    ]);
    return SessionManager.userPermissions({ params });
  };

  /**
   * Check if session is valid
   *
   *   - If this.token is null, try to load from localStorage
   *   - If this.token is valid but about to expire (4 hours) automatically send a refreshToken request to API
   *   - If this.token is expired or refresh is invalid, clean session and localStorage.
   *   @private
   *   @returns Promise<boolean> - A promise indicating whether the token is valid.
   */
  _isValid = async () => {
    this._token ??= await this._loadFromStorage();

    if (this._token == null) {
      this._cleanTokenFromLocalStorage();
      return false;
    }

    // renew
    if (moment().isSameOrAfter(moment.unix(this._token.tokenExpirationDate).subtract(30, "seconds"))) {
      const newToken = await this._oauthCtl.refreshToken(this._token.refreshToken);
      if (newToken == null) {
        this._cleanTokenFromLocalStorage();
        return false;
      }

      await this.saveToken(newToken);
    }

    return true;
  };

  /**
   * Clean session
   * @private
   * @returns void
   */
  _cleanTokenFromLocalStorage = () => {
    window.localStorage.removeItem("token");
    this._token = null;
    this._user = null;
  };

  /**
   * Loads the token from local storage.
   * @private
   * @returns Promise<OauthToken> - A promise containing the loaded OAuth token.
   */
  _loadFromStorage = async () => {
    const strToken = window.sessionStorage.getItem("token") || window.localStorage.getItem("token");

    if (strToken == null) {
      this._token = null;
      return null;
    }

    return await OauthToken.fromJson(JSON.parse(strToken));
  };
}

/**
 * The session manager instance.
 * @type {_SessionManager}
 */

export const SessionManager = new _SessionManager();

import { Constants } from "$lib/commons/constants";
import { BaseController } from "$lib/controllers/base_controller";
import { BaseSelectListDC } from "$lib/models/data_containers/base_select_list_dc";
import { UserPermission } from "$lib/models/user_permission";
import { UserFetch } from "$lib/services/fetch/user_fetch";
import { QueryFields } from "$lib/services/utils/query_utils";

/**
 * @typedef {import("$lib/models/user").UserRoleType} UserRoleType
 * @typedef {import("$lib/models/user").User} User
 * @typedef {import("$lib/models/password_change").PasswordChange} PasswordChange
 */

/**
 * @readonly
 * @enum string
 */
const UserChildEntity = {
  PERMISSION: "permission",
  USER_ROLE: "user_role",
};

class UserController extends BaseController {
  /** @type {UserFetch} */
  fetch;

  constructor() {
    super();
    this.fetch = new UserFetch();
  }

  /**
   * Changes the password for a user.
   * @param {number} id - The ID of the user.
   * @param {PasswordChange} model - The password change request model.
   * @returns Promise<boolean> - A promise that resolves with a boolean indicating if the password was changed
   *   successfully.
   */
  changePassword = (id, model) => {
    return this.put(id, model, { extraPath: "/password" });
  };

  /**
   * Retrieves permissions for a user.
   * @param {Object} [opts] - Options for retrieving permissions.
   * @param {Map<QueryFields, unknown>} [opts.params] - Parameters for the request.
   * @returns Promise<UserPermission[]> - A promise that resolves with an array of user permissions.
   */
  getPermissions = async ({ params } = {}) => {
    params ??= new Map();
    if (!params.has(QueryFields.LIMIT)) params.set(QueryFields.LIMIT, Constants.PAGE_MAX_SIZE);

    return (await this.search({
      params,
      transformer: UserPermission.transformer,
      customPath: "/permissions",
      opEntity: UserChildEntity.PERMISSION,
    })).items;
  };

  /**
   * Retrieves roles for a user.
   * @param {Object} [opts] - Options for retrieving roles.
   * @param {Map<QueryFields, unknown>} [opts.params] - Parameters for the request.
   * @returns Promise<BaseSelectListDC[]> - A promise that resolves with an array of user roles.
   */
  getUserRoles = async ({ params } = {}) => {
    params ??= new Map();
    if (!params.has(QueryFields.LIMIT)) params.set(QueryFields.LIMIT, Constants.PAGE_MAX_SIZE);

    return (await this.search({
      params,
      extraPath: "/allowed-roles",
      opEntity: UserChildEntity.USER_ROLE,
      transformer: (data) => new BaseSelectListDC({ value: data["name"] }),
    })).items;
  };

  /**
   * Activates a user account using the provided token and user data.
   * @param {string} token - The activation token.
   * @param {User} user - The user object.
   * @returns Promise<boolean> - A promise that resolves with a boolean indicating if the activation was successful.
   */
  activate = (token, user) => this.fetch.activate(token, user.toDict());

  /**
   * Deletes or anonymizes a user account.
   * If userId is not provided, the current user's ID will be used.
   * @param {number} [userId] - The ID of the user to delete.
   * @returns Promise<boolean> - A promise that resolves with a boolean indicating if the deletion was successful.
   */
  // deleteAccount = (userId) => {
  //   return this.fetch.deleteAccount({ userId: userId ?? SessionManager.userId() });
  // };

  /**
   * Cancels the user registration using the provided access token.
   * @param {string} accessToken - The access token.
   * @returns Promise<boolean> - A promise that resolves with a boolean indicating if the cancellation was successful.
   */
  cancelRegister = (accessToken) => this.fetch.deleteAccount({ accessToken });
}

export { UserController, UserChildEntity };

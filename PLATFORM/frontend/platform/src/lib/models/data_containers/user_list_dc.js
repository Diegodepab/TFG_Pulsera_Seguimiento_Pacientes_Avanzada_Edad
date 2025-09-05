import { BaseDC } from "$lib/models/data_containers/base_dc";
import { User } from "$lib/models/user";
import { QueryParamsSort } from "$lib/services/utils/query_utils";

/**
 * @typedef {import("$lib/models/user").UserStatusType} UserStatusType
 * @typedef {import("moment").Moment} Moment
 */

class UiFields {
  /**
   * @readonly
   * @type string
   */
  id = "id";
  /**
   * @readonly
   * @type string
   */
  email = "email";
  /**
   * @readonly
   * @type string
   */
  firstName = "firstName";
  /**
   * @readonly
   * @type string
   */
  lastName = "lastName";
  /**
   * @readonly
   * @type string
   */
  fullName = "fullName";
  /**
   * @readonly
   * @type string
   */
  roleName = "roleName";
  /**
   * @readonly
   * @type string
   */
  phone = "phone";
  /**
   * @readonly
   * @type string
   */
  statusName = "statusName";
  /**
   * @readonly
   * @type string
   */
  createTs = "createTs";
  /**
   * @readonly
   * @type string
   */
  updateTs = "updateTs";

  /**
   * @readonly
   * @type UiApiMapping
   */
  mapUiApi = new Map([
    [ this.id, { api: [ User.apiFields.id ] } ],
    [ this.email, { api: [ User.apiFields.email ] } ],
    [ this.firstName, { api: [ User.apiFields.firstName ] } ],
    [ this.lastName, { api: [ User.apiFields.lastName ] } ],
    [ this.fullName, { api: [ User.apiFields.firstName, User.apiFields.lastName ] } ],
    [ this.roleName, { api: [ User.apiFields.roleName ] } ],
    [ this.phone, { api: [ User.apiFields.phone ] } ],
    [ this.statusName, { api: [ User.apiFields.statusName ] } ],
    [ this.createTs, { api: [ User.apiFields.createTs ] } ],
    [ this.updateTs, { api: [ User.apiFields.updateTs ] } ],
  ]);
}

class UserListDC extends BaseDC {
  /**
   * @type {UiFields}
   * @readonly
   */
  static uiFields = new UiFields();

  /**
   * @type {number | undefined}
   * @readonly
   */
  id;

  /**
   * @type string
   * @readonly
   */
  email;

  /**
   * @type string
   * @readonly
   */
  firstName;

  /**
   * @type string
   * @readonly
   */
  lastName;

  /**
   * @type string
   * @readonly
   */
  roleName;

  /**
   * @type string
   * @readonly
   */
  phone;

  /**
   * @type UserStatusType
   * @readonly
   */
  statusName;

  /**
   * @type {Moment | undefined}
   * @readonly
   */
  createTs;

  /**
   * @type {Moment | undefined}
   * @readonly
   */
  updateTs;

  /**
   * Constructs a new User object with the provided options.
   * @param {Object} opts - The options for creating the User object.
   * @param {number} [opts.id] - The user's identifier.
   * @param {string} [opts.email] - The user's email address.
   * @param {string} [opts.firstName] - The user's first name.
   * @param {string} [opts.lastName] - The user's last name.
   * @param {string} [opts.roleName] - The user's role name.
   * @param {string} [opts.phone] - The user's phone number.
   * @param {UserStatusType} [opts.statusName] - The user's status.
   * @param {Moment} [opts.createTs] - The timestamp when the user was created.
   * @param {Moment} [opts.updateTs] - The timestamp when the user was last updated.
   */
  constructor(opts) {
    super({});

    this.id = opts.id;
    this.email = opts.email;
    this.firstName = opts.firstName;
    this.lastName = opts.lastName;
    this.roleName = opts.roleName;
    this.phone = opts.phone;
    this.statusName = opts.statusName;
    this.createTs = opts.createTs;
    this.updateTs = opts.updateTs;
  }

  /** @returns string */
  get fullName() {
    return [ this.firstName, this.lastName ].join(" ");
  }

  /**
   * Gets the sort parameters from a UI field and sort order.
   * @param {string} field - The UI field to sort by.
   * @param {import("$lib/services/utils/query_utils").QuerySortOrder} sort - The sort order (ascending or descending).
   * @returns QueryParamsSort[] - An array of sort parameters.
   */
  static getSortParamFromUiField = (field, sort) => {
    return UserListDC.uiFields.mapUiApi
      .get(field)
      .api.map((apiField) => new QueryParamsSort({ field: apiField, sort }));
  };
}

export { UserListDC };

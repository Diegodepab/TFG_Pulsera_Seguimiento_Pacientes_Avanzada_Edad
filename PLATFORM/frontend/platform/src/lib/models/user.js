import { DateUtils } from "$lib/commons/utils";
import { BaseModel } from "$lib/models/base_model";
import { Patient } from "$lib/models/patient";
import moment from "moment";

/**
 * Enum representing user role types.
 * @readonly
 * @enum string
 */
const UserRoleType = {
  ADMIN: "admin",
  USER: "user",
};

/**
 * Enum representing user status types.
 * @readonly
 * @enum string
 */
const UserStatusType = {
  ACTIVE: "active",
  PENDING: "pending",
  INACTIVE: "inactive",
};

class ApiFields {
  /**
   * @type string
   * @readonly
   */
  id = "id";

  /**
   * @type string
   * @readonly
   */
  email = "email";

  /**
   * @type string
   * @readonly
   */
  password = "password";

  /**
   * @type string
   * @readonly
   */
  roleName = "user_role_name";

  /**
   * @type string
   * @readonly
   */
  statusName = "user_status_name";

  /**
   * @type string
   * @readonly
   */
  firstName = "first_name";

  /**
   * @type string
   * @readonly
   */
  lastName = "last_name";

  /**
   * @type string
   * @readonly
   */
  phone = "phone";

  /**
   * @type string
   * @readonly
   */
  approvalTocTs = "approval_toc_ts";

  /**
   * @type string
   * @readonly
   */
  blockedTs = "blocked_ts";

  /**
   * @type string
   * @readonly
   */
  createTs = "create_ts";

  /**
   * @type string
   * @readonly
   */
  updateTs = "update_ts";
}

class ApiEmbeds {
  /**
   * @type string
   * @readonly
   */
  patients = "patients";
}


class User extends BaseModel {
  /**
   * @type ApiFields
   * @readonly
   */
  static apiFields = new ApiFields();
  /**
   * @type ApiEmbeds
   * @readonly
   */
  static apiEmbeds = new ApiEmbeds();

  /** @type {number|undefined} */
  id;
  /**  @type string */
  email;
  /** @type {string|undefined} */
  password;
  /**  @type {UserRoleType|null} */
  roleName;
  /** @type {UserStatusType} */
  statusName;
  /** @type string */
  firstName;
  /** @type string */
  lastName;
  /** @type string */
  phone;
  /** @type {Moment|undefined} */
  approvalTocTs;
  /** @type {Moment|undefined} */
  blockedTs;
  /** @type {Moment|undefined} */
  createTs;
  /** @type {Moment|undefined} */
  updateTs;

  // embeds
  /** @type {Patient[]|undefined} */
  patients;

  /**
   * Constructs a user instance.
   * @param {string} email - The user's email.
   * @param {UserRoleType} roleName - The user's role name.
   * @param {UserStatusType} statusName - The user's status name.
   * @param {string} firstName - The user's first name.
   * @param {string} lastName - The user's last name.
   * @param {string} phone - The user's phone number.
   * @param {Object} [opts] - Optional parameters.
   * @param {number|undefined} [opts.id] - The user's ID.
   * @param {string|undefined} [opts.password] - The user's password.
   * @param {Moment|undefined} [opts.approvalTocTs] - The timestamp for approval TOC.
   * @param {Moment|undefined} [opts.blockedTs] - The timestamp when the user was blocked.
   * @param {Moment|undefined} [opts.createTs] - The timestamp when the user was created.
   * @param {Moment|undefined} [opts.updateTs] - The timestamp when the user was last updated.
   */
  constructor(
    email,
    roleName,
    statusName,
    firstName,
    lastName,
    phone,
    opts,
  ) {
    super();

    this.id = opts?.id;
    this.email = email;
    this.roleName = roleName;
    this.statusName = statusName;
    this.password = opts?.password;
    this.firstName = firstName;
    this.lastName = lastName;
    this.phone = phone;
    this.approvalTocTs = opts?.approvalTocTs;
    this.blockedTs = opts?.blockedTs;
    this.createTs = opts?.createTs;
    this.updateTs = opts?.updateTs;

  }

  /**
   * Gets the full name by combining firstName and name
   * @returns string - The combined full name
   **/
  get fullName() {
    return [ this.firstName, this.lastName ].join(" ");
  }

  /**
   * Creates a User instance from JSON data.
   * @param {Json} data - The JSON data representing the user.
   * @returns Promise<User> - A promise that resolves to a User instance.
   */
  static fromJson = async (data) => {
    const user = new User(
      data[User.apiFields.email],
      data[User.apiFields.roleName],
      data[User.apiFields.statusName],
      data[User.apiFields.firstName],
      data[User.apiFields.lastName],
      data[User.apiFields.phone],
      {
        id: data[User.apiFields.id],
        password: data[User.apiFields.password],
        approvalTocTs: DateUtils.momentOrNull(data[User.apiFields.approvalTocTs]),
        blockedTs: DateUtils.momentOrNull(data[User.apiFields.blockedTs]),
        createTs: moment(data[User.apiFields.createTs]),
        updateTs: moment(data[User.apiFields.updateTs]),
      },
    );

    if (Object.keys(data[User.apiEmbeds.patients] ?? {}).length) {
      user.patients = await Promise.all(data[User.apiEmbeds.patients].map((item) => Patient.fromJson(item)));
    }

    return user;
  };

  /**
   * Transforms JSON data into an instance of a specified type.
   * @template {User} T - The type of the instance to transform to.
   * @param {Json} data - The JSON data to transform.
   * @returns Promise<User> - The transformed instance.
   */
  static transformer = async (data) => await User.fromJson(data);

  /** @returns User */
  static empty = () => new User(null, null, null, null, null, null, null);

  /** @returns User */
  static undef = () => new User(undefined, undefined, undefined, undefined, undefined, undefined);

  /**
   * Creates a copy of the given user object.
   * @param {User} obj - The user object to copy.
   * @param {Object} [opts] - Optional parameters.
   * @param {boolean} [opts.ignoreEmbeds] - Whether to ignore embedded objects.
   * @returns User - A promise that resolves to a copy of the user object.
   */
  static copy = async (obj, opts) => {
    const newObj = new User(obj.email, obj.roleName, obj.statusName, obj.firstName, obj.lastName, obj.phone, {
      id: obj.id,
      password: obj.password,
      approvalTocTs: obj.approvalTocTs,
      blockedTs: obj.blockedTs,
      createTs: obj.createTs,
      updateTs: obj.updateTs,
    });

    //embeds
    if (!opts?.ignoreEmbeds) {
      // No embeds
    }

    return newObj;
  };

  /**
   * Converts the OAuth instance to a dictionary representation.
   * @param {toDictModel} [opts] - Optional parameters.
   * @returns Json - The dictionary representation of the OAuth instance.
   */
  toDict = (opts) => {
    /** @type Json */
    const dict = {};

    [
      [ User.apiFields.id, this.id ],
      [ User.apiFields.email, this.email ],
      [ User.apiFields.roleName, this.roleName ],
      [ User.apiFields.statusName, this.statusName ],
      [ User.apiFields.firstName, this.firstName ],
      [ User.apiFields.lastName, this.lastName ],
      [ User.apiFields.phone, this.phone ],
      [ User.apiFields.password, this.password ],
      [ User.apiFields.approvalTocTs, DateUtils.utcTimestampOrNull(this.approvalTocTs) ],
      [ User.apiFields.createTs, DateUtils.utcTimestampOrNull(this.createTs) ],
      [ User.apiFields.updateTs, DateUtils.utcTimestampOrNull(this.updateTs) ],
    ].forEach(([ first, second ]) => {
      if (second !== undefined && (second !== null || !opts?.includeNullValues)) {
        dict[first] = second;
      }
    });

    if (!opts?.ignoreEmbeds) {
      // No embeds
    }

    return dict;
  };
}

export { User, UserRoleType, UserStatusType };

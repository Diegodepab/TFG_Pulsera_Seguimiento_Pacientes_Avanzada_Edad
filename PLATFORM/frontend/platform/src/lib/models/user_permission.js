import { BaseModel } from "$lib/models/base_model";

/**
 * Enum representing permissions grant types.
 * @readonly
 * @enum string
 */
const PermissionsGrantType = {
  ALL: "all",
  OWN: "own",
  NONE: "none",
};

/**
 * Enum representing permissions entity types.
 * @readonly
 * @enum string
 */
const PermissionsEntityType = {
  ENTITY: "entity",
  PERMISSION_GRANT: "permission_grant",
  USER: "user_account",
  USER_ROLE: "user_role",
  PATIENT: "patient",
  INSTRUMENT: "instrument",
  PATHOLOGY: "pathology",
  PATIENT_MODEL: "patient_model",
  STUDY: "study", 
  ALARM: "alarms",
  CHAT: "chat",
  MESSAGE: "message",
};

class ApiFields {
  /** @type string
   * @readonly
   */
  entityName = "entity_name";
  /**
   * @type string
   * @readonly
   */
  read = "read";
  /**
   * @type string
   * @readonly
   */
  write = "write";
  /**
   * @type string
   * @readonly
   */
  del = "delete";
  /**
   * @type string
   * @readonly
   */
  uiVisibility = "ui_visibility";
}

class UserPermission extends BaseModel {
  /**
   * @type ApiFields @readonly  */
  static apiFields = new ApiFields();

  /** @type {PermissionsEntityType} */
  entityName;
  /** @type {PermissionsGrantType} */
  read;
  /** @type {PermissionsGrantType} */
  write;
  /** @type {PermissionsGrantType} */
  del;
  /** @type boolean */
  uiVisibility;

  /**
   * Constructs a UserPermission instance.
   * @param {PermissionsEntityType} entityName - The name of the entity.
   * @param {PermissionsGrantType} read - The permission type for read operations.
   * @param {PermissionsGrantType} write - The permission type for write operations.
   * @param {PermissionsGrantType} del - The permission type for delete operations.
   * @param {boolean} uiVisibility - Whether the entity is visible in the UI.
   */
  constructor(
    entityName,
    read,
    write,
    del,
    uiVisibility,
  ) {
    super();
    this.entityName = entityName;
    this.read = read;
    this.write = write;
    this.del = del;
    this.uiVisibility = uiVisibility;
  }

  /**
   * Creates a UserPermission instance from JSON data.
   * @param {Json} data - The JSON data representing the user permission.
   * @returns Promise<UserPermission> - A promise that resolves to a UserPermission instance.
   */
  static fromJson = async (data) => {
    return new UserPermission(
      data[UserPermission.apiFields.entityName],
      data[UserPermission.apiFields.read],
      data[UserPermission.apiFields.write],
      data[UserPermission.apiFields.del],
      data[UserPermission.apiFields.uiVisibility],
    );
  };

  /**
   * Transforms JSON data into an instance of a specified type.
   * @template T - The type of the instance to transform to.
   * @param {Json} data - The JSON data to transform.
   * @returns Promise<UserPermission> - The transformed instance.
   */
  static transformer = async (data) => await UserPermission.fromJson(data);

  /** @returns UserPermission */
  static empty = () => new UserPermission(null, null, null, null, null);

  /**
   * Creates a copy of the given user permission object.
   * @param {UserPermission} obj - The user permission object to copy.
   * @returns Promise<UserPermission> - A promise that resolves to a copy of the user permission object.
   */
  static copy = async (obj) => {
    return new UserPermission(obj.entityName, obj.read, obj.write, obj.del, obj.uiVisibility);
  };

  /**
   * Converts the UserPermission instance to a dictionary representation.
   * @param {toDictModel} [opts] - Optional parameters.
   * @returns Json - The dictionary representation of the UserPermission instance.
   */
  toDict = (opts) => {
    /** @type Json */
    const dict = {};

    dict[UserPermission.apiFields.entityName] = this.entityName;
    dict[UserPermission.apiFields.read] = this.read;
    dict[UserPermission.apiFields.write] = this.write;
    dict[UserPermission.apiFields.del] = this.del;
    dict[UserPermission.apiFields.uiVisibility] = this.uiVisibility;

    return dict;
  };
}

export { UserPermission, PermissionsGrantType, PermissionsEntityType };

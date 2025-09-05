import { GenderType } from "$lib/models/patient";
import { UserRoleType, UserStatusType } from "$lib/models/user";

/**
 * Enum to display different genders with svelte-i18n based on plural method
 * @readonly
 * @enum string
 */
const i18nGender = {
  MALE: "male",
  FEMALE: "female",
};


/** @abstract */
class UIBaseEntityIcons {
  /** @type string */
  static user = "fa-users";              // alt(s): 'fa-user-md'
  /** @type string */
  static patient = "fa-users-medical";
  /** @type string */
  static instrument = "fa-scalpel";
  /** @type string */
  static pathology = "fa-heart-pulse";
  /** @type string */
  static alarms = "fa-bell";
}

/** @abstract */
class UiPillClassTranslate {
  /**
   * Determines the CSS class for the user role pill based on the user role type.
   * @param {UserRoleType} userRole - The user role type.
   * @returns string - The CSS class for the user role pill.
   */
  static userRolePillClass = (userRole) => {
    switch (userRole) {
      case UserRoleType.ADMIN:
        return "badge-danger";
      case UserRoleType.USER:
        return "badge-primary";
      default:
        return "badge-light";
    }
  };

  /**
   * Determines the CSS class for the user status pill based on the user status type.
   * @param {UserStatusType} userStatus - The user status type.
   * @returns string - The CSS class for the user status pill.
   */
  static userStatusPillClass = (userStatus) => {
    switch (userStatus) {
      case UserStatusType.ACTIVE:
        return "bg-success";
      case UserStatusType.INACTIVE:
        return "bg-warning";
      case UserStatusType.PENDING:
        return "bg-light";
      default:
        return "bg-light";
    }
  };

  static patientGenderPillClass = (type) => {
    switch (type) {
      case GenderType.MALE:
        return "badge-blue";
      case GenderType.FEMALE:
        return "badge-pink";
      default:
        return "badge-light";
    }
  };
}

export { UiPillClassTranslate, i18nGender, UIBaseEntityIcons };

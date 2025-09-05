import { BaseDC } from "$lib/models/data_containers/base_dc";
import { Patient } from "$lib/models/patient";
import { User } from "$lib/models/user";
import { QueryParamsSort } from "$lib/services/utils/query_utils";

/**
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
  code = "code";

  /**
   * @readonly
   * @type string
   */
  gender = "gender";

  /**
   * @readonly
   * @type string
   */
  weight = "weight";

  /**
   * @readonly
   * @type string
   */
  birthDate = "birthDate";

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
   * @type string
   */
  ownerFullName = "ownerFullName";

  /**
   * @readonly
   * @type UiApiMapping
   */
  mapUiApi = new Map([
    [ this.id, { api: [ Patient.apiFields.id ] } ],
    [ this.code, { api: [ Patient.apiFields.code ] } ],
    [ this.gender, { api: [ Patient.apiFields.gender ] } ],
    [ this.weight, { api: [ Patient.apiFields.weight ] } ],
    [ this.birthDate, { api: [ Patient.apiFields.birthDate ] } ],
    [ this.createTs, { api: [ Patient.apiFields.createTs ] } ],
    [ this.updateTs, { api: [ Patient.apiFields.updateTs ] } ],
    // embeds // TODO: update when embed sort enabled
    [ this.ownerFullName, { api: [ User.apiFields.firstName, User.apiFields.lastName ] } ],
  ]);
}

class PatientListDC extends BaseDC {
  /** @type UiFields
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
  code;

  /**
   * @type number
   * @readonly
   */
  gender;

  /**
   * @type number
   * @readonly
   */
  weight;

  /**
   * @type {Moment | undefined}
   * @readonly
   */
  birthDate;

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

  // embeds
  /**
   * @type {string | undefined}
   * @readonly
   */
  ownerFullName;

  /**
   * Constructs a new Patient object with the provided options.
   * @param {Object} opts - The options for creating the Patient object.
   * @param {number} [opts.id] - The patient's identifier.
   * @param {string} [opts.code] - The patient's code.
   * @param {number} [opts.gender] - The patient's gender.
   * @param {number} [opts.weight] - The patient's weight.
   * @param {Moment} [opts.birthDate] - The patient's birth date.
   * @param {User} [opts.ownerUser] - The user (doctor) the this patient.
   * @param {string} [opts.ownerFullName] - The relation with owner or doctor.
   * @param {Moment} [opts.createTs] - The timestamp when the patient was created.
   * @param {Moment} [opts.updateTs] - The timestamp when the patient was last updated.
   */
  constructor(opts) {
    super({});

    this.id = opts.id;
    this.code = opts.code;
    this.gender = opts.gender;
    this.weight = opts.weight;
    this.birthDate = opts.birthDate;
    this.createTs = opts.createTs;
    this.updateTs = opts.updateTs;

    this.ownerFullName = opts.ownerUser?.fullName;
  }

  /**
   * Gets the sort parameters from a UI field and sort order.
   * @param {string} field - The UI field to sort by.
   * @param {import("$lib/services/utils/query_utils").QuerySortOrder} sort - The sort order (ascending or descending).
   * @returns QueryParamsSort[] - An array of sort parameters.
   */
  static getSortParamFromUiField = (field, sort) => {
    return PatientListDC.uiFields.mapUiApi
      .get(field)
      .api.map((apiField) => new QueryParamsSort({ field: apiField, sort }));
  };
}

export { PatientListDC };

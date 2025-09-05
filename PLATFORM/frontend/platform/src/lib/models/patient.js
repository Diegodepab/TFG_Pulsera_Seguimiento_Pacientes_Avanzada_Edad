import { DateUtils } from "$lib/commons/utils";
import { BaseModel } from "$lib/models/base_model";
import { Pathology } from "$lib/models/pathology";
import { PatientModel } from "$lib/models/patient_model";
import { PatientPathology } from "$lib/models/patient_pathology";
import { User } from "$lib/models/user";
import moment from "moment";

/**
 * Enum representing gender types.
 * @readonly
 * @enum string
 */
const GenderType = {
  MALE: "male",
  FEMALE: "female",
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
  code = "code";

  /**
   * @type string
   * @readonly
   */
  gender = "gender";

  /**
   * @type string
   * @readonly
   */
  weight = "weight";

  /**
   * @type string
   * @readonly
   */
  birthDate = "birth_date";

  /**
   * @type string
   * @readonly
   */
  ownerUserId = "owner_user_id";

  /**
   * @type string
   * @readonly
   */
  patientUserId = "patient_user_id";

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

  /**
   * @type string
   * @readonly
   */
  detectionDate = "detection_date";
}

class ApiEmbeds {
  /**
   * @type string
   * @readonly
   */
  pathologies = "pathologies";

  /**
   * @type string
   * @readonly
   */
  ownerUser = "owner_user";

  /**
   * @type string
   * @readonly
   */
  patientPathologies = "patient_pathologies";

  /**
   * @type string
   * @readonly
   */
  patientModels = "patient_models";
}

class Patient extends BaseModel {
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

  /** @type string */
  code;

  /** @type {GenderType} */
  gender;

  /** @type number */
  weight;

  /** @type {Moment|undefined} */
  birthDate;

  /** @type {number|undefined} */
  ownerUserId;

  /** @type {Moment|undefined} */
  createTs;

  /** @type {Moment|undefined} */
  updateTs;

  // embeds
  /** @type {Pathology[]|undefined} */
  pathologies;

  /** @type {User|undefined} */
  ownerUser;

  /** @type {PatientPathology[]|undefined} */
  patientPathologies;

  /** @type {PatientModel[]|undefined} */
  patientModels;

  // Embed from LinkedPatients
  /** @type {Moment|undefined} */
  detectionDate;

  /**
   * Constructs a patient instance.
   * @param {string} code - The patient's code.
   * @param {GenderType} gender - The patient's gender.
   * @param {number} weight - The patient's weight.
   * @param {Moment} birthDate - The patient's birth date.
   * @param {number|undefined} ownerUserId - The relation with user (doctor).
   * @param {Object} [opts] - Optional parameters.
   * @param {number|undefined} [opts.id] - The patient's ID.
   * @param {Moment|undefined} [opts.createTs] - The timestamp when the patient was created.
   * @param {Moment|undefined} [opts.updateTs] - The timestamp when the patient was last updated.
   * @param {Moment|undefined} [opts.detectionDate] - The detectionDate from PatientPathology.
   */
  constructor(code, gender, weight, birthDate, ownerUserId, opts) {
    super();

    this.id = opts?.id;
    this.code = code;
    this.gender = gender;
    this.weight = weight;
    this.birthDate = birthDate;
    this.ownerUserId = ownerUserId;
    this.createTs = opts?.createTs;
    this.updateTs = opts?.updateTs;
    this.detectionDate = opts?.detectionDate;
  }

  /**
   * Creates a Patient instance from JSON data.
   * @param {Json} data - The JSON data representing the patient.
   * @returns Promise<Patient> - A promise that resolves to a Patient instance.
   */
  static fromJson = async (data) => {
    /** @type Patient */
    const patient = new Patient(
      data[Patient.apiFields.code],
      data[Patient.apiFields.gender],
      data[Patient.apiFields.weight],
      DateUtils.momentOrNull(data[Patient.apiFields.birthDate]),
      data[Patient.apiFields.ownerUserId],
      {
        id: data[Patient.apiFields.id],
        createTs: moment(data[Patient.apiFields.createTs]),
        updateTs: moment(data[Patient.apiFields.updateTs]),
        detectionDate: moment(data[Patient.apiFields.detectionDate]),
      },
    );

    if (Object.keys(data[Patient.apiEmbeds.pathologies] ?? {}).length) {
      patient.pathologies = (await Promise.all(data[Patient.apiEmbeds.pathologies].map((item) => Pathology.fromJson(item))));
    }

    if (Object.keys(data[Patient.apiEmbeds.patientPathologies] ?? {}).length) {
      patient.patientPathologies = (await Promise.all(data[Patient.apiEmbeds.patientPathologies].map((item) => PatientPathology.fromJson(item))));
    }

    if (Object.keys(data[Patient.apiEmbeds.patientModels] ?? {}).length) {
      patient.patientModels = (await Promise.all(data[Patient.apiEmbeds.patientModels].map((item) => PatientModel.fromJson(item))));
    }

    if (Object.keys(data[Patient.apiEmbeds.ownerUser] ?? {}).length) {
      patient.ownerUser = await User.fromJson(data[Patient.apiEmbeds.ownerUser]);
    }

    return patient;
  };

  /**
   * Transforms JSON data into an instance of a specified type.
   * @template {Patient} T - The type of the instance to transform to.
   * @param {Json} data - The JSON data to transform.
   * @returns Promise<Patient> - The transformed instance.
   */
  static transformer = async (data) => await Patient.fromJson(data);

  /** @returns Patient */
  static empty = () => new Patient(null, null, null, null, null);

  /** @returns Patient */
  static undef = () => new Patient(undefined, undefined, undefined, undefined, undefined);

  /**
   * Creates a copy of the given patient object.
   * @param {Patient} obj - The patient object to copy.
   * @param {Object} [opts] - Optional parameters.
   * @param {boolean} [opts.ignoreEmbeds] - Whether to ignore embedded objects.
   * @returns Patient - A promise that resolves to a copy of the patient object.
   */
  static copy = async (obj, opts) => {
    const newObj = new Patient(obj.code, obj.gender, obj.weight, obj.birthDate, {
      id: obj.id,
      createTs: obj.createTs,
      updateTs: obj.updateTs,
      detectionDate: obj.detectionDate,
    });

    // embeds
    if (!opts?.ignoreEmbeds) {
      if (obj.pathologies) {
        newObj.pathologies = await Promise.all(obj.pathologies.map((item) => Pathology.copy(item, opts)));
      }

      if (obj.patientPathologies) {
        newObj.patientPathologies = await Promise.all(obj.patientPathologies.map((item) => PatientPathology.copy(item, opts)));
      }

      if (obj.patientModels) {
        newObj.patientModels = await Promise.all(obj.patientModels.map((item) => PatientModel.copy(item, opts)));
      }

      if (obj.ownerUser) {
        newObj.ownerUser = await User.copy(obj.ownerUser, opts);
      }

      return newObj;
    }
  };

  /**
   * Converts the Patient instance to a dictionary representation.
   * @param {toDictModel} [opts] - Optional parameters.
   * @returns Json - The dictionary representation of the Patient instance.
   */
  toDict = (opts) => {
    /** @type Json */
    const dict = {};

    [
      [ Patient.apiFields.id, this.id ],
      [ Patient.apiFields.code, this.code ],
      [ Patient.apiFields.gender, this.gender ],
      [ Patient.apiFields.weight, this.weight ],
      [ Patient.apiFields.birthDate, DateUtils.toDate(this.birthDate, { format: "YYYY-MM-DD" }) ],
      [ Patient.apiFields.ownerUserId, this.ownerUserId ],
      [ Patient.apiFields.createTs, DateUtils.utcTimestampOrNull(this.createTs) ],
      [ Patient.apiFields.updateTs, DateUtils.utcTimestampOrNull(this.updateTs) ],
    ].forEach(([ first, second ]) => {
      if (second !== undefined && (second !== null || !opts?.includeNullValues)) {
        dict[first] = second;
      }
    });

    if (!opts?.ignoreEmbeds) {
      [
        [ Patient.apiEmbeds.pathologies, this.pathologies?.map((item) => item.toDict(opts)) ],
        [ Patient.apiEmbeds.patientPathologies, this.patientPathologies?.map((item) => item.toDict(opts)) ],
        [ Patient.apiEmbeds.patientModels, this.patientModels?.map((item) => item.toDict(opts)) ],
        [ Patient.apiEmbeds.ownerUser, this.ownerUser?.toDict(opts) ],
      ].forEach(([ first, second ]) => {
        if (second !== undefined) dict[first] = second;
      });
    }

    return dict;
  };
}

export { Patient, GenderType };

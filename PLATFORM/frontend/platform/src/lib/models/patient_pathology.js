import { BaseModel } from "$lib/models/base_model";
import { Pathology } from "$lib/models/pathology";
import { Patient } from "$lib/models/patient";
import moment from "moment";

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
  patientId = "patient_id";

  /**
   * @type string
   * @readonly
   */
  pathologyId = "pathology_id";

  /**
   * @type string
   * @readonly
   */
  detectionDate = "detection_date";

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
  patient = "patient";

  /**
   * @type string
   * @readonly
   */
  pathology = "pathology";
}

class PatientPathology extends BaseModel {
  /**
   *  @type ApiFields
   * @readonly
   */
  static apiFields = new ApiFields();

  /**
   * @type {ApiEmbeds}
   * @readonly
   */
  static apiEmbeds = new ApiEmbeds();

  /**
   * @type {number|undefined}
   */
  id;

  /**
   * @type number
   */
  patientId;

  /**
   * @type number
   */
  pathologyId;

  /**
   * @type {Moment}
   */
  detectionDate;

  /**
   * @type {Moment|undefined}
   */
  createTs;

  /**
   * @type {Moment|undefined}
   */
  updateTs;

  /**
   * @type {Patient|undefined}
   */
  patient;

  /**
   * @type {Pathology|undefined}
   */
  pathology;

  /**
   * Constructs a PatientPathology instance.
   * @param {number} patientId - The ID of the patient.
   * @param {number} pathologyId - The ID of the pathology.
   * @param {Moment} detectionDate - The date of the pathology diagnosis.
   * @param {Object} [opts] - Optional parameters.
   * @param {number|undefined} [opts.id] - The record ID.
   * @param {Moment|undefined} [opts.createTs] - The creation timestamp.
   * @param {Moment|undefined} [opts.updateTs] - The update timestamp.
   */
  constructor(patientId, pathologyId, detectionDate, opts) {
    super();
    this.id = opts?.id;
    this.patientId = patientId;
    this.pathologyId = pathologyId;
    this.detectionDate = detectionDate;
    this.createTs = opts?.createTs;
    this.updateTs = opts?.updateTs;
  }

  /**
   * Creates a PatientPathology instance from JSON data.
   * @param {Json} data - The JSON data representing the patient pathology record.
   * @returns Promise<PatientPathology> - A promise that resolves to a PatientPathology instance.
   */
  static fromJson = async (data) => {
    /** @type PatientPathology */
    const patientPathology = new PatientPathology(
      data[PatientPathology.apiFields.patientId],
      data[PatientPathology.apiFields.pathologyId],
      moment(data[PatientPathology.apiFields.detectionDate]),
      {
        id: data[PatientPathology.apiFields.id],
        createTs: moment(data[PatientPathology.apiFields.createTs]),
        updateTs: moment(data[PatientPathology.apiFields.updateTs]),
      },
    );

    if (Object.keys(data[PatientPathology.apiEmbeds.patient] ?? {}).length) {
      patientPathology.patient = await Patient.fromJson(data[PatientPathology.apiEmbeds.patient]);
    }

    if (Object.keys(data[PatientPathology.apiEmbeds.pathology] ?? {}).length) {
      patientPathology.pathology = await Pathology.fromJson(data[PatientPathology.apiEmbeds.pathology]);
    }

    return patientPathology;
  };

  /**
   * Transforms JSON data into an instance of a specified type.
   * @template {Instrument} T - The type of the instance to transform to.
   * @param {Json} data - The JSON data to transform.
   * @returns Promise<PatientPathology> - The transformed instance.
   */
  static transformer = async (data) => await PatientPathology.fromJson(data);

  /** @returns PatientPathology */
  static empty = () => new PatientPathology(null, null, null, null);

  /** @returns PatientPathology */
  static undef = () => new PatientPathology(undefined, undefined, undefined, undefined);

  /**
   * Creates a copy of the given patient pathology object.
   * @param {PatientPathology} obj - The patient pathology object to copy.
   * @param {Object} [opts] - Optional parameters.
   * @param {boolean} [opts.ignoreEmbeds] - Whether to ignore embedded objects.
   * @returns Promise<PatientPathology> - A promise that resolves to a copy of the patient pathology object.
   */
  static copy = async (obj, opts) => {
    const newObj = new PatientPathology(
      obj.patientId,
      obj.pathologyId,
      obj.detectionDate,
      {
        id: obj.id,
        createTs: obj.createTs,
        updateTs: obj.updateTs,
      },
    );

    // Copy embeds if present and not ignored
    if (!opts?.ignoreEmbeds) {
      if (obj.patient) {
        newObj.patient = await Patient.copy(obj.patient, opts);
      }
      if (obj.pathology) {
        newObj.pathology = await Pathology.copy(obj.pathology, opts);
      }
    }

    return newObj;
  };

  /**
   * Converts the PatientPathology instance to a dictionary representation.
   * @param {toDictModel} [opts] - Optional parameters.
   * @returns Json - The dictionary representation of the PatientPathology instance.
   */
  toDict = (opts) => {
    /** @type Json */
    const dict = {};

    [
      [ PatientPathology.apiFields.id, this.id ],
      [ PatientPathology.apiFields.patientId, this.patientId ],
      [ PatientPathology.apiFields.pathologyId, this.pathologyId ],
      [ PatientPathology.apiFields.detectionDate, this.detectionDate ],
      [ PatientPathology.apiFields.createTs, this.createTs?.utc().toISOString(true) ],
      [ PatientPathology.apiFields.updateTs, this.updateTs?.utc().toISOString(true) ],
    ].forEach(([ field, value ]) => {
      if (value !== undefined && (value !== null || !opts?.includeNullValues)) {
        dict[field] = value;
      }
    });

    // Include embedded objects if present and not ignored
    if (!opts?.ignoreEmbeds) {
      [
        [ PatientPathology.apiEmbeds.patient, this.patient?.toDict(opts) ],
        [ PatientPathology.apiEmbeds.pathology, this.pathology?.toDict(opts) ],
      ].forEach(([ field, value ]) => {
        if (value !== undefined) dict[field] = value;
      });
    }

    return dict;
  };
}

export { PatientPathology };

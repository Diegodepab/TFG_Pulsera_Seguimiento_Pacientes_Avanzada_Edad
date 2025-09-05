import { BaseModel } from "$lib/models/base_model";
import { Patient } from "$lib/models/patient";
import moment from "moment";

class ApiFields {
  /** @type {string} @readonly */
  id = "id";
  /** @type {string} @readonly */
  patientId = "patient_id";
  /** @type {string} @readonly */
  stepCount = "step_count";
  /** @type {string} @readonly */
  bpm = "bpm";
  /** @type {string} @readonly */
  spo2 = "spo2";
  /** @type {string} @readonly */
  ts = "ts";
  /** @type {string} @readonly */
  createTs = "create_ts";
  /** @type {string} @readonly */
  updateTs = "update_ts";
}

class ApiEmbeds {
  /** @type {string} @readonly */
  patient = "patient";
}

/**
 * Represents a study record for a patient, with measurements and timestamps.
 * @extends BaseModel
 */
class Study extends BaseModel {
  /** @type {ApiFields} @readonly */
  static apiFields = new ApiFields();
  /** @type {ApiEmbeds} @readonly */
  static apiEmbeds = new ApiEmbeds();

  /** @type {number|undefined} */ id;
  /** @type {number} */ patientId;
  /** @type {number} */ stepCount;
  /** @type {number} */ bpm;
  /** @type {number|undefined} */ spo2;
  /** @type {moment.Moment} */ ts;
  /** @type {moment.Moment|undefined} */ createTs;
  /** @type {moment.Moment|undefined} */ updateTs;
  /** @type {Patient|undefined} */ patient;

  /**
   * @param {number} patientId
   * @param {number} stepCount
   * @param {number} bpm
   * @param {moment.Moment} ts
   * @param {Object} [opts]
   * @param {number} [opts.spo2]
   * @param {number} [opts.id]
   * @param {moment.Moment} [opts.createTs]
   * @param {moment.Moment} [opts.updateTs]
   */
  constructor(patientId, stepCount, bpm, ts, opts) {
    super();
    this.id = opts?.id;
    this.patientId = patientId;
    this.stepCount = stepCount;
    this.step_count = stepCount; // Alias para compatibilidad
    this.bpm = bpm; // CORREGIDO: era bmp, ahora es bpm
    this.spo2 = opts?.spo2;
    this.ts = ts;
    this.createTs = opts?.createTs;
    this.updateTs = opts?.updateTs;
  }

  /**
   * Converts JSON data into a Study instance.
   * @param {Object} data
   * @returns {Promise<Study>}
   */
  static fromJson = async (data) => {
    const fields = Study.apiFields;

    const study = new Study(
      Number(data[fields.patientId]),
      Number(data[fields.stepCount]),
      Number(data[fields.bpm]),
      moment(data[fields.ts]),
      {
        id: Number(data[fields.id]),
        spo2: Number(data[fields.spo2]),
        createTs: data[fields.createTs] ? moment(data[fields.createTs]) : undefined,
        updateTs: data[fields.updateTs] ? moment(data[fields.updateTs]) : undefined,
      }
    );
    
    
    const embedKey = Study.apiEmbeds.patient;
    if (data[embedKey]) {
      study.patient = await Patient.fromJson(data[embedKey]);
    }
    return study;
  };

  /**
   * Transformer for API data.
   * @param {Object} data
   * @returns {Promise<Study>}
   */
  static transformer = async (data) => Study.fromJson(data);

  /** @returns {Study} */
  static empty = () => new Study(null, null, null, null, {});
  /** @returns {Study} */
  static undef = () => new Study(undefined, undefined, undefined, undefined, {});

  /**
   * Deep copy of a Study object.
   * @param {Study} obj
   * @param {Object} [opts]
   * @param {boolean} [opts.ignoreEmbeds]
   * @returns {Promise<Study>}
   */
  static copy = async (obj, opts) => {
    const newObj = new Study(
      obj.patientId,
      obj.stepCount,
      obj.bpm,
      obj.ts,
      {
        id: obj.id,
        spo2: obj.spo2,
        createTs: obj.createTs,
        updateTs: obj.updateTs,
      }
    );
    if (!opts?.ignoreEmbeds && obj.patient) {
      newObj.patient = await Patient.copy(obj.patient, opts);
    }
    return newObj;
  };

  /**
   * Serializes the Study instance to a plain object.
   * @param {Object} [opts]
   * @param {boolean} [opts.includeNullValues]
   * @param {boolean} [opts.ignoreEmbeds]
   * @returns {Object}
   */
  toDict = (opts) => {
    const dict = {};
    const fields = Study.apiFields;
    [
      [fields.id, this.id],
      [fields.patientId, this.patientId],
      [fields.stepCount, this.stepCount],
      [fields.bpm, this.bpm],
      [fields.spo2, this.spo2],
      [fields.ts, this.ts?.utc().toISOString(true)],
      [fields.createTs, this.createTs?.utc().toISOString(true)],
      [fields.updateTs, this.updateTs?.utc().toISOString(true)],
    ].forEach(([key, value]) => {
      if (value !== undefined && (value !== null || !opts?.includeNullValues)) {
        dict[key] = value;
      }
    });
    if (!opts?.ignoreEmbeds && this.patient) {
      dict[Study.apiEmbeds.patient] = this.patient.toDict(opts);
    }
    return dict;
  };

  toString = () => {
    return `Study{id: ${this.id}, patientId: ${this.patientId}, stepCount: ${this.stepCount}, bpm: ${this.bpm}, spo2: ${this.spo2}, ts: ${this.ts}}`;
  };

  static resourceName = () => "studies";
  static resourceDisplayName = () => "Study";

  static searchFields = [
    Study.apiFields.id,
    Study.apiFields.patientId,
    Study.apiFields.stepCount,
    Study.apiFields.bpm,
    Study.apiFields.spo2,
    Study.apiFields.ts,
  ];

  static sortFields = [
    Study.apiFields.id,
    Study.apiFields.patientId,
    Study.apiFields.stepCount,
    Study.apiFields.bpm,
    Study.apiFields.spo2,
    Study.apiFields.ts,
    Study.apiFields.createTs,
    Study.apiFields.updateTs,
  ];

  static defaultSortField = () => Study.apiFields.ts;
  static defaultSortDirection = () => "desc";

  static embedFields = [
    {
      fieldName: "patient",
      model: Patient,
      keyField: Study.apiFields.patientId,
      embeddedKeyField: Patient.apiFields.id,
    },
  ];
}

export { Study };

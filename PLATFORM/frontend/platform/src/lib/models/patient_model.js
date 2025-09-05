import { BaseModel } from "$lib/models/base_model";
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
  name = "name";

  /**
   * @type string
   * @readonly
   */
  patientId = "patient_id";

  /**
   * @type string
   * @readonly
   */
  filename = "filename";

  /**
   * @type string
   * @readonly
   */
  url = "url";

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
  blobDisplayUrl = "blob_display_url";
}

class ApiEmbeds {
  /**
   * @type string
   * @readonly
   */
  patient = "patient";
}

class ApiRaw {
  /**
   * @type string
   * @readonly
   */
  addBlobDisplayUrl = "add_blob_display_url";
}

class PatientModel extends BaseModel {
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
   * @type ApiRaw
   * @readonly
   */
  static apiRaw = new ApiRaw();

  /** @type {number|undefined} */
  id;

  /** @type string */
  name;

  /** @type {number|undefined} */
  patientId;

  /** @type string */
  filename;

  /** @type string */
  url;

  /** @type {Moment|undefined} */
  createTs;

  /** @type {Moment|undefined} */
  updateTs;

  /** @type {Patient} */
  patient;

  /** @type string */
  blobDisplayUrl;

  /**
   * Constructs a PatientModel instance.
   * @param {string} name - The model name.
   * @param {string} filename - The instrument filename.
   * @param {string} url - The instrument url for blob.
   * @param {Object} [opts] - Optional parameters.
   * @param {Object} [opts] - Optional parameters.
   * @param {number|undefined} [opts.id] - The model ID.
   * @param {number|undefined} [opts.patientId] - The ID of the patient associated with this model.
   * @param {Moment|undefined} [opts.createTs] - The timestamp when the model was created.
   * @param {Moment|undefined} [opts.updateTs] - The timestamp when the model was last updated.
   * @param {string} [opts.blobDisplayUrl] - The instrument display url for blob.
   */
  constructor(name, filename, url, opts) {
    super();
    this.id = opts?.id;
    this.name = name;
    this.patientId = opts?.patientId;
    this.filename = filename;
    this.url = url;
    this.createTs = opts?.createTs;
    this.updateTs = opts?.updateTs;
    this.blobDisplayUrl = opts?.blobDisplayUrl;
  }

  /**
   * Creates an PatientModel instance from JSON data.
   * @param {Json} data - The JSON data representing the model.
   * @returns Promise<PatientModel> - A promise that resolves to an PatientModel instance.
   */
  static fromJson = async (data) => {
    /** @type PatientModel */
    const model = new PatientModel(
      data[PatientModel.apiFields.name],
      data[PatientModel.apiFields.filename],
      data[PatientModel.apiFields.url],
      {
        id: data[PatientModel.apiFields.id],
        patientId: data[PatientModel.apiFields.patientId],
        createTs: moment(data[PatientModel.apiFields.createTs]),
        updateTs: moment(data[PatientModel.apiFields.updateTs]),
        blobDisplayUrl: data[PatientModel.apiFields.blobDisplayUrl],
      },
    );

    if (Object.keys(data[PatientModel.apiEmbeds.patient] ?? {}).length) {
      model.patient = await Patient.fromJson(data[PatientModel.apiEmbeds.patient]);
    }

    return model;
  };

  /**
   * Transforms JSON data into an instance of a specified type.
   * @template {Instrument} T - The type of the instance to transform to.
   * @param {Json} data - The JSON data to transform.
   * @returns Promise<PatientModel> - The transformed instance.
   */
  static transformer = async (data) => await PatientModel.fromJson(data);

  /** @returns PatientModel */
  static empty = () => new PatientModel(null, null, null);

  /** @returns PatientModel */
  static undef = () => new PatientModel(undefined, undefined, undefined);

  /**
   * Creates a copy of the given model object.
   * @param {PatientModel} obj - The model object to copy.
   * @param {Object} [opts] - Optional parameters.
   * @param {boolean} [opts.ignoreEmbeds] - Whether to ignore embedded objects.
   * @returns PatientModel - A promise that resolves to a copy of the model object.
   */
  static copy = async (obj, opts) => {
    const newObj = new PatientModel(obj.name, obj.filename, obj.url, {
      id: obj.id,
      patientId: obj.patientId,
      createTs: obj.createTs,
      updateTs: obj.updateTs,
      blobDisplayUrl: obj.blobDisplayUrl,
    });

    // embeds
    if (!opts?.ignoreEmbeds) {
      if (obj.patient) {
        newObj.patient = await Patient.copy(obj.patient, opts);
      }
    }

    return newObj;
  };

  /**
   * Converts the PatientModel instance to a dictionary representation.
   * @param {toDictModel} [opts] - Optional parameters.
   * @returns Json - The dictionary representation of the PatientModel instance.
   */
  toDict = (opts) => {
    /** @type Json */
    const dict = {};

    [
      [ PatientModel.apiFields.id, this.id ],
      [ PatientModel.apiFields.name, this.name ],
      [ PatientModel.apiFields.patientId, this.patientId ],
      [ PatientModel.apiFields.filename, this.filename ],
      [ PatientModel.apiFields.url, this.url ],
      [ PatientModel.apiFields.createTs, this.createTs?.utc().toISOString(true) ],
      [ PatientModel.apiFields.updateTs, this.updateTs?.utc().toISOString(true) ],
    ].forEach(([ first, second ]) => {
      if (second !== undefined && (
        second !== null || !opts?.includeNullValues
      )) {
        dict[first] = second;
      }
    });

    if (!opts?.ignoreEmbeds) {
      [
        [ PatientModel.apiEmbeds.patient, this.patient?.toDict(opts) ],
      ].forEach(([ first, second ]) => {
        if (second !== undefined) dict[first] = second;
      });
    }

    return dict;
  };
}

export { PatientModel };

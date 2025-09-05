import { BaseModel } from "$lib/models/base_model";
import { Patient } from "$lib/models/patient";
import { PatientPathology } from "$lib/models/patient_pathology";
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
  patients = "patients";

  /**
   * @type string
   * @readonly
   */
  patientPathologies = "patient_pathologies";
}

class Pathology extends BaseModel {
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
  name;
  /** @type {Moment|undefined} */
  createTs;
  /** @type {Moment|undefined} */
  updateTs;

  // embed
  /** @type {Patient[]|undefined} */
  patients;

  /** @type {PatientPathology[]|undefined} */
  patientPathologies;

  /**
   * Constructs a pathology instance.
   * @param {string} name - The pathology name.
   * @param {Object} [opts] - Optional parameters.
   * @param {number|undefined} [opts.id] - The pathology ID.
   * @param {Moment|undefined} [opts.createTs] - The timestamp when the pathology was created.
   * @param {Moment|undefined} [opts.updateTs] - The timestamp when the pathology was last updated.
   */
  constructor(name, opts) {
    super();

    this.id = opts?.id;
    this.name = name;
    this.createTs = opts?.createTs;
    this.updateTs = opts?.updateTs;
  }

  /**
   * Creates a Pathology instance from JSON data.
   * @param {Json} data - The JSON data representing the pathology.
   * @returns Promise<Pathology> - A promise that resolves to a Pathology instance.
   */
  static fromJson = async (data) => {
    /** @type {Pathology} */
    const pathology = new Pathology(
      data[Pathology.apiFields.name],
      {
        id: data[Pathology.apiFields.id],
        createTs: moment(data[Pathology.apiFields.createTs]),
        updateTs: moment(data[Pathology.apiFields.updateTs]),
      },
    );

    if (Object.keys(data[Pathology.apiEmbeds.patients] ?? {}).length) {
      pathology.patients = (await Promise.all(data[Pathology.apiEmbeds.patients].map((item) => Patient.fromJson(item))));
    }

    if (Object.keys(data[Pathology.apiEmbeds.patientPathologies] ?? {}).length) {
      pathology.patientPathologies = (await Promise.all(data[Pathology.apiEmbeds.patientPathologies].map((item) => PatientPathology.fromJson(item))));
    }

    return pathology;
  };

  /**
   * Transforms JSON data into an instance of a specified type.
   * @template {Instrument} T - The type of the instance to transform to.
   * @param {Json} data - The JSON data to transform.
   * @returns Promise<Pathology> - The transformed instance.
   */
  static transformer = async (data) => await Pathology.fromJson(data);

  /** @returns Pathology */
  static empty = () => new Pathology(null, null);

  /** @returns Pathology */
  static undef = () => new Pathology(undefined, undefined);

  /**
   * Creates a copy of the given pathology object.
   * @param {Pathology} obj - The pathology object to copy.
   * @param {Object} [opts] - Optional parameters.
   * @param {boolean} [opts.ignoreEmbeds] - Whether to ignore embedded objects.
   * @returns Pathology - A promise that resolves to a copy of the pathology object.
   */
  static copy = async (obj, opts) => {
    const newObj = new Pathology(obj.name, {
      id: obj.id,
      createTs: obj.createTs,
      updateTs: obj.updateTs,
    });

    // embeds
    if (!opts?.ignoreEmbeds) {
      if (obj.patients) {
        newObj.patients = await Promise.all(obj.patients.map((item) => Patient.copy(item, opts)));
      }

      if (obj.patientPathologies) {
        newObj.patientPathologies = await Promise.all(obj.patientPathologies.map((item) => PatientPathology.copy(item, opts)));
      }
    }

    return newObj;
  };

  /**
   * Converts the Pathology instance to a dictionary representation.
   * @param {toDictModel} [opts] - Optional parameters.
   * @returns Json - The dictionary representation of the Pathology instance.
   */
  toDict = (opts) => {
    /** @type Json */
    const dict = {};

    [
      [ Pathology.apiFields.id, this.id ],
      [ Pathology.apiFields.name, this.name ],
      [ Pathology.apiFields.createTs, this.createTs?.utc().toISOString(true) ],
      [ Pathology.apiFields.updateTs, this.updateTs?.utc().toISOString(true) ],
    ].forEach(([ first, second ]) => {
      if (second !== undefined && (second !== null || !opts?.includeNullValues)) {
        dict[first] = second;
      }
    });

    if (!opts?.ignoreEmbeds) {
      [
        [ Pathology.apiEmbeds.patients, this.patients?.map((item) => item.toDict(opts)) ],
        [ Pathology.apiEmbeds.patientPathologies, this.patients?.map((item) => item.toDict(opts)) ],
      ].forEach(([ first, second ]) => {
        if (second !== undefined) dict[first] = second;
      });
    }

    return dict;
  };
}

export { Pathology };

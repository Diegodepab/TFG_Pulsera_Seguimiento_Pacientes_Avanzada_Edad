import { BaseModel } from "$lib/models/base_model";
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
  filename = "filename";

  /**
   * @type string
   * @readonly
   */
  model = "model";

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
  // Define any embedded objects here if needed
}

class ApiRaw {
  /**
   * @type string
   * @readonly
   */
  addBlobDisplayUrl = "add_blob_display_url";
}

class Instrument extends BaseModel {
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
  /**
   * @type ApiRaw
   * @readonly
   */
  static apiRaw = new ApiRaw();

  /** @type {number|undefined} */
  id;
  /** @type string */
  name;
  /** @type string */
  filename;
  /** @type string */
  model;
  /** @type string */
  url;
  /** @type {Moment|undefined} */
  createTs;
  /** @type {Moment|undefined} */
  updateTs;
  /** @type string */
  blobDisplayUrl;

  /**
   * Constructs an instrument instance.
   * @param {string} name - The instrument name.
   * @param {string} filename - The instrument filename.
   * @param {string} model - The instrument model.
   * @param {string} url - The instrument url for blob.
   * @param {Object} [opts] - Optional parameters.
   * @param {number|undefined} [opts.id] - The instrument ID.
   * @param {Moment|undefined} [opts.createTs] - The timestamp when the instrument was created.
   * @param {Moment|undefined} [opts.updateTs] - The timestamp when the instrument was last updated.
   * @param {string} [opts.blobDisplayUrl] - The instrument display url for blob.
   */
  constructor(name, filename, model, url, opts) {
    super();

    this.id = opts?.id;
    this.name = name;
    this.filename = filename;
    this.model = model;
    this.url = url;
    this.createTs = opts?.createTs;
    this.updateTs = opts?.updateTs;
    this.blobDisplayUrl = opts?.blobDisplayUrl;
  }

  /**
   * Creates an Instrument instance from JSON data.
   * @param {Json} data - The JSON data representing the instrument.
   * @returns Promise<Instrument> - A promise that resolves to an Instrument instance.
   */
  static fromJson = async (data) => {
    return new Instrument(
      data[Instrument.apiFields.name],
      data[Instrument.apiFields.filename],
      data[Instrument.apiFields.model],
      data[Instrument.apiFields.url],
      {
        id: data[Instrument.apiFields.id],
        createTs: moment(data[Instrument.apiFields.createTs]),
        updateTs: moment(data[Instrument.apiFields.updateTs]),
        blobDisplayUrl: data[Instrument.apiFields.blobDisplayUrl],
      },
    );
  };

  /**
   * Transforms JSON data into an instance of a specified type.
   * @template {Instrument} T - The type of the instance to transform to.
   * @param {Json} data - The JSON data to transform.
   * @returns Promise<Instrument> - The transformed instance.
   */
  static transformer = async (data) => await Instrument.fromJson(data);

  /** @returns Instrument */
  static empty = () => new Instrument(null, null, null, null, null);

  /** @returns Instrument */
  static undef = () => new Instrument(undefined, undefined, undefined, undefined, undefined);

  /**
   * Creates a copy of the given instrument object.
   * @param {Instrument} obj - The instrument object to copy.
   * @param {Object} [opts] - Optional parameters.
   * @param {boolean} [opts.ignoreEmbeds] - Whether to ignore embedded objects.
   * @returns Instrument - A promise that resolves to a copy of the instrument object.
   */
  static copy = async (obj, opts) => {
    const newObj = new Instrument(obj.name, obj.filename, obj.model, obj.url, {
      id: obj.id,
      createTs: obj.createTs,
      updateTs: obj.updateTs,
      blobDisplayUrl: obj.blobDisplayUrl,
    });

    // embeds
    if (!opts?.ignoreEmbeds) {
      // Handle embeds if necessary
    }

    return newObj;
  };

  /**
   * Converts the Instrument instance to a dictionary representation.
   * @param {toDictModel} [opts] - Optional parameters.
   * @returns Json - The dictionary representation of the Instrument instance.
   */
  toDict = (opts) => {
    /** @type Json */
    const dict = {};

    [
      [ Instrument.apiFields.id, this.id ],
      [ Instrument.apiFields.name, this.name ],
      [ Instrument.apiFields.filename, this.filename ],
      [ Instrument.apiFields.model, this.model ],
      [ Instrument.apiFields.url, this.url ],
      [ Instrument.apiFields.createTs, this.createTs?.utc().toISOString(true) ],
      [ Instrument.apiFields.updateTs, this.updateTs?.utc().toISOString(true) ],
    ].forEach(([ first, second ]) => {
      if (second !== undefined && (second !== null || !opts?.includeNullValues)) {
        dict[first] = second;
      }
    });

    if (!opts?.ignoreEmbeds) {
      // Handle embeds if necessary
    }

    return dict;
  };
}

export { Instrument };

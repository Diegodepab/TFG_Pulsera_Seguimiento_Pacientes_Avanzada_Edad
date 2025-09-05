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
  // Embeds
}

class ApiRaw {
  /**
   * @type string
   * @readonly
   */
  addBlobDisplayUrl = "add_blob_display_url";
}

class GenericModel extends BaseModel {
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
  url;

  /** @type {Moment|undefined} */
  createTs;

  /** @type {Moment|undefined} */
  updateTs;

  /** @type string */
  blobDisplayUrl;

  /**
   * Constructs a GenericsModel instance.
   * @param {string} name - The model name.
   * @param {string} filename - The instrument filename.
   * @param {string} url - The instrument url for blob.
   * @param {Object} [opts] - Optional parameters.
   * @param {Object} [opts] - Optional parameters.
   * @param {number|undefined} [opts.id] - The model ID.
   * @param {Moment|undefined} [opts.createTs] - The timestamp when the model was created.
   * @param {Moment|undefined} [opts.updateTs] - The timestamp when the model was last updated.
   * @param {string} [opts.blobDisplayUrl] - The instrument display url for blob.
   */
  constructor(name, filename, url, opts) {
    super();
    this.id = opts?.id;
    this.name = name;
    this.filename = filename;
    this.url = url;
    this.createTs = opts?.createTs;
    this.updateTs = opts?.updateTs;
    this.blobDisplayUrl = opts?.blobDisplayUrl;
  }

  /**
   * Creates an GenericModel instance from JSON data.
   * @param {Json} data - The JSON data representing the model.
   * @returns Promise<GenericModel> - A promise that resolves to an GenericsModel instance.
   */
  static fromJson = async (data) => {
    return new GenericModel(
      data[GenericModel.apiFields.name],
      data[GenericModel.apiFields.filename],
      data[GenericModel.apiFields.url],
      {
        id: data[GenericsModel.apiFields.id],
        createTs: moment(data[GenericModel.apiFields.createTs]),
        updateTs: moment(data[GenericModel.apiFields.updateTs]),
        blobDisplayUrl: data[GenericModel.apiFields.blobDisplayUrl],
      },
    );
  };

  /**
   * Transforms JSON data into an instance of a specified type.
   * @template {Instrument} T - The type of the instance to transform to.
   * @param {Json} data - The JSON data to transform.
   * @returns Promise<GenericsModel> - The transformed instance.
   */
  static transformer = async (data) => await GenericModel.fromJson(data);

  /** @returns GenericModel */
  static empty = () => new GenericModel(null, null, null);

  /** @returns GenericModel */
  static undef = () => new GenericModel(undefined, undefined, undefined);

  /**
   * Creates a copy of the given model object.
   * @param {GenericModel} obj - The model object to copy.
   * @param {Object} [opts] - Optional parameters.
   * @param {boolean} [opts.ignoreEmbeds] - Whether to ignore embedded objects.
   * @returns Promise<GenericModel>
   */
  static copy = async (obj, opts) => {
    const newObj = new GenericModel(obj.name, obj.filename, obj.url, {
      id: obj.id,
      createTs: obj.createTs,
      updateTs: obj.updateTs,
      blobDisplayUrl: obj.blobDisplayUrl,
    });

    // embeds
    if (!opts?.ignoreEmbeds) {
      // embeds
    }

    return newObj;
  };

  /**
   * Converts the GenericModel instance to a dictionary representation.
   * @param {toDictModel} [opts] - Optional parameters.
   * @returns Json - The dictionary representation of the GenericModel instance.
   */
  toDict = (opts) => {
    /** @type Json */
    const dict = {};

    [
      [ GenericModel.apiFields.id, this.id ],
      [ GenericModel.apiFields.name, this.name ],
      [ GenericModel.apiFields.filename, this.filename ],
      [ GenericModel.apiFields.url, this.url ],
      [ GenericModel.apiFields.createTs, this.createTs?.utc().toISOString(true) ],
      [ GenericModel.apiFields.updateTs, this.updateTs?.utc().toISOString(true) ],
    ].forEach(([ first, second ]) => {
      if (second !== undefined && (second !== null || !opts?.includeNullValues)) {
        dict[first] = second;
      }
    });

    if (!opts?.ignoreEmbeds) {
      // embeds
    }

    return dict;
  };
}

export { GenericModel };

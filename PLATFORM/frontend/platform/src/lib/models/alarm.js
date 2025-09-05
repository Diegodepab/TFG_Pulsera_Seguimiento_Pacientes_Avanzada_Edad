import { BaseModel } from "$lib/models/base_model";
import moment from "moment";

class ApiFields {
  /** @readonly @type {string} */ id        = "id";
  /** @readonly @type {string} */ patientId = "patient_id";
  /** @readonly @type {string} */ alarmType = "alarm_type";
  /** @readonly @type {string} */ ts        = "ts";
  /** @readonly @type {string} */ isUrgent  = "is_urgent";
  /** @readonly @type {string} */ createTs  = "create_ts";
  /** @readonly @type {string} */ updateTs  = "update_ts";
}

class ApiEmbeds {
  // Si más adelante queremos “embed” del paciente, podríamos poner:
  // /** @readonly @type {string} */ patient = "patient";
  // Pero por ahora no lo necesitamos.
}

class Alarm extends BaseModel {
  /** @type {ApiFields} @readonly */
  static apiFields = new ApiFields();

  /** @type {ApiEmbeds} @readonly */
  static apiEmbeds = new ApiEmbeds();

  /** @type {number|undefined} */  id;
  /** @type {number} */           patientId;
  /** @type {string} */           alarmType;
  /** @type {moment.Moment} */    ts;
  /** @type {boolean} */          isUrgent;
  /** @type {moment.Moment|undefined} */ createTs;
  /** @type {moment.Moment|undefined} */ updateTs;
  // Si más adelante hacemos embed:  /** @type {Patient|undefined} */ patient;

  /**
   * @param {number}       patientId
   * @param {string}       alarmType
   * @param {moment.Moment} ts
   * @param {boolean}      isUrgent
   * @param {Object} [opts]
   * @param {number} [opts.id]
   * @param {moment.Moment} [opts.createTs]
   * @param {moment.Moment} [opts.updateTs]
   */
  constructor(patientId, alarmType, ts, isUrgent, opts = {}) {
    super();
    this.id        = opts.id;
    this.patientId = patientId;
    this.alarmType = alarmType;
    this.ts        = ts;
    this.isUrgent  = isUrgent;
    this.createTs  = opts.createTs;
    this.updateTs  = opts.updateTs;
  }

  /**
   * Convierte un objeto JSON de la API a una instancia de Alarm.
   * @param {Object} data
   * @returns {Promise<Alarm>}
   */
  static fromJson = async (data) => {
    const f = Alarm.apiFields;
    const alarm = new Alarm(
      data[f.patientId],
      data[f.alarmType],
      moment(data[f.ts]),
      data[f.isUrgent],
      {
        id: data[f.id],
        createTs: moment(data[f.createTs]),
        updateTs: moment(data[f.updateTs]),
      }
    );
    // Si tuviéramos embed “patient”, se haría algo parecido a:
    // if (data[Alarm.apiEmbeds.patient]) {
    //   alarm.patient = await Patient.fromJson(data[Alarm.apiEmbeds.patient]);
    // }
    return alarm;
  };

  /**
   * Transformer que se usa en el fetch para mapear cada item.
   * @param {Object} data
   * @returns {Promise<Alarm>}
   */
  static transformer = async (data) => Alarm.fromJson(data);

  /** @returns {Alarm} Instancia “vacía” (útil para formularios) */
  static empty = () => new Alarm(undefined, undefined, undefined, false, {});

  /**
   * Serializa a un objeto plano para enviar a la API (p. ej. en creaciones/actualizaciones).
   * @param {Object} [opts]
   * @param {boolean} [opts.includeNullValues]
   * @param {boolean} [opts.ignoreEmbeds]
   * @returns {Object}
   */
  toDict = (opts = {}) => {
    const dict = {};
    const f = Alarm.apiFields;
    [
      [f.id,         this.id],
      [f.patientId,  this.patientId],
      [f.alarmType,  this.alarmType],
      [f.ts,         this.ts?.utc().toISOString(true)],
      [f.isUrgent,   this.isUrgent],
      [f.createTs,   this.createTs?.utc().toISOString(true)],
      [f.updateTs,   this.updateTs?.utc().toISOString(true)],
    ].forEach(([key, value]) => {
      if (value !== undefined && (value !== null || !opts.includeNullValues)) {
        dict[key] = value;
      }
    });
    // Si hubiera embeds: 
    // if (!opts.ignoreEmbeds && this.patient) {
    //   dict[Alarm.apiEmbeds.patient] = this.patient.toDict(opts);
    // }
    return dict;
  };
}

export { Alarm };
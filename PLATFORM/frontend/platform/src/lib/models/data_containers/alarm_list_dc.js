import { BaseDC } from "$lib/models/data_containers/base_dc";
import { Alarm } from "$lib/models/alarm";
import { QueryParamsSort } from "$lib/services/utils/query_utils";

class UiFields {
  /** @readonly @type {string} */ alarmType = "alarmType";
  /** @readonly @type {string} */ ts        = "ts";
  /** @readonly @type {string} */ isUrgent  = "isUrgent";

  /**
   * Mapa de campo UI → campo(s) API para ordenar.
   * Sólo permitimos orden por “ts” en la UI.
   * @type {Map<string, {api: string[]}>}
   */
  mapUiApi = new Map([
    [ this.ts, { api: [ Alarm.apiFields.ts ] } ],
    // No necesitamos mapear “alarmType” ni “isUrgent” para ordenar.
  ]);
}

class AlarmListDC extends BaseDC {
  /** @type {UiFields} @readonly */
  static uiFields = new UiFields();

  /** @type {number|undefined} */  id;
  /** @type {number} */           patientId;
  /** @type {string} */           alarmType;
  /** @type {string} */           ts;        // Lo dejamos como string ISO, la tabla formateará.
  /** @type {boolean} */          isUrgent;

  /**
   * @param {{
   *   id: number,
   *   patient_id: number,
   *   alarm_type: string,
   *   ts: string,
   *   is_urgent: boolean
   * }} opts
   */
  constructor(opts) {
    super({});
    this.id         = opts.id;
    this.patientId  = opts.patient_id;
    this.alarmType  = opts.alarm_type;
    this.ts         = opts.ts;
    this.isUrgent   = opts.is_urgent;
  }

  /**
   * Crea un DC a partir del objeto JSON crudo.
   * @param {Object} data
   * @returns {AlarmListDC}
   */
  static fromJson(data) {
    return new AlarmListDC({
      id: data[Alarm.apiFields.id],
      patient_id: data[Alarm.apiFields.patientId],
      alarm_type: data[Alarm.apiFields.alarmType],
      ts: data[Alarm.apiFields.ts],
      is_urgent: data[Alarm.apiFields.isUrgent],
    });
  }

  /**
   * Mapea un campo de orden UI a QueryParamsSort[]
   * @param {string} field
   * @param {import("$lib/services/utils/query_utils").QuerySortOrder} sort
   */
  static getSortParamFromUiField(field, sort) {
    const entry = AlarmListDC.uiFields.mapUiApi.get(field);
    if (!entry) return [];
    return entry.api.map(apiField => new QueryParamsSort({ field: apiField, sort }));
  }
}

export { AlarmListDC };
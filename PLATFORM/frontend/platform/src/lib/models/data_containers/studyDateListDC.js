import { BaseDC } from "$lib/models/data_containers/base_dc";
import { Study } from "$lib/models/study";
import { QueryParamsSort } from "$lib/services/utils/query_utils";

class UiFields {
  /** @readonly @type string */
  studyDate = "studyDate";

  /** @readonly @type string */
  count = "count";

  /** @readonly @type string */
  firstTime = "firstTime";

  /** @readonly @type string */
  lastTime = "lastTime";

  /** @readonly @type string */
  lastStepCount = "lastStepCount";

  /** @readonly @type Map<string, {api:string[]}> */
  mapUiApi = new Map([
    // Solo mantenemos sorting para studyDate (mapea a ts en la API)
    [ this.studyDate, { api: [ Study.apiFields.ts ] } ],
    // NO incluimos count, firstTime, lastTime ni lastStepCount, 
    // ya que no existe un campo directo en la API para ordenar por ellos.
  ]);
}

class StudyDateListDC extends BaseDC {
  /** @type UiFields @readonly */
  static uiFields = new UiFields();

  /** @type {string} @readonly */
  studyDate;

  /** @type {number} @readonly */
  count;

  /** @type {string} @readonly */
  firstTime;

  /** @type {string} @readonly */
  lastTime;

  /** @type {number} @readonly */
  lastStepCount;

  /**
   * @param {{
   *   studyDate: string,
   *   count: number,
   *   firstTime: string,
   *   lastTime: string,
   *   lastStepCount: number
   * }} opts
   */
  constructor(opts) {
    super({});
    this.studyDate      = opts.studyDate;
    this.count          = opts.count;
    this.firstTime      = opts.firstTime;
    this.lastTime       = opts.lastTime;
    this.lastStepCount  = opts.lastStepCount;
  }

  /**
   * Sorting by studyDate (mapea a ts en API si se solicita).
   * No hay sorting por count/firstTime/lastTime/lastStepCount
   * porque son campos agregados.
   * @param {string} field
   * @param {import("$lib/services/utils/query_utils").QuerySortOrder} sort
   * @returns {QueryParamsSort[]}
   */
  static getSortParamFromUiField(field, sort) {
    const entry = StudyDateListDC.uiFields.mapUiApi.get(field);
    if (!entry) return [];
    return entry.api.map(apiField => new QueryParamsSort({ field: apiField, sort }));
  }
}

export { StudyDateListDC };

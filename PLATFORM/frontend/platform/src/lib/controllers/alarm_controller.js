import { BaseController } from "$lib/controllers/base_controller";
import { AlarmFetch }       from "$lib/services/fetch/alarm_fetch";
import { Alarm }            from "$lib/models/alarm";

class AlarmController extends BaseController {
  /** @type {AlarmFetch} */
  fetch;

  constructor() {
    super();
    this.fetch = new AlarmFetch();
  }

  /**
   * Busca alarmas paginadas para un paciente, devuelve el JSON ya transformado.
   * Si quieres un método especializado, podrías llamar internamente a:
   *   return this.search({ params: new Map([[ QueryFields.Q, [ ... ] ]]) });
   *
   * Pero para la tabla, haremos directamente:
   *   new AlarmController().search({...})
   *
   * Si quisieras, podrías definir un helper:
   * 
   * async listByPatient(patientId, offset = null, limit = null) {
   *   return await this.search({
   *     params: new Map([
   *       [
   *         QueryFields.Q,
   *         [ new QueryParamsQ({ field: Alarm.apiFields.patientId, operation: QueryComparativeOperations.EQ, value: patientId }) ]
   *       ]
   *     ]),
   *     limit,
   *     offset,
   *     // Aquí no necesitamos transformer, porque BaseController.search ya aplicará Alarm.transformer
   *   });
   * }
   */
}

export { AlarmController };
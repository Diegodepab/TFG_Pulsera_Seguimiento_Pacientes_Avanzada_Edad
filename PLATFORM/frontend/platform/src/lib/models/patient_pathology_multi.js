import { DateUtils } from "$lib/commons/utils";
import { BaseModel } from "$lib/models/base_model";
import { PatientPathology } from "$lib/models/patient_pathology";

class ApiFields {
  /**
   * @type string
   * @readonly
   */
  patientId = "patient_id";

  /**
   * @type string
   * @readonly
   */
  pathologies = "pathologies";
}

class PatientPathologyMulti extends BaseModel {
  /**
   *  @type ApiFields
   * @readonly
   */
  static apiFields = new ApiFields();

  /** @type number */
  patientId;

  /** @type PatientPathology[] */
  pathologies;

  /**
   * Constructs a PatientPathology instance.
   * @param {number} patientId - The ID of the patient.
   * @param {PatientPathology[]} pathologies - List of pathologies
   */
  constructor(patientId, pathologies) {
    super();
    this.patientId = patientId;
    this.pathologies = pathologies;
  }

  /** @returns PatientPathologyMulti */
  static empty = () => new PatientPathologyMulti(null, null);

  /**
   * Converts the PatientPathology instance to a dictionary representation.
   * @param {toDictModel} [opts] - Optional parameters.
   * @returns Json - The dictionary representation of the PatientPathology instance.
   */
  toDict = (opts) => {
    /** @type Json */
    const dict = {};

    [
      [ PatientPathologyMulti.apiFields.patientId, this.patientId ],
      [ PatientPathologyMulti.apiFields.pathologies, this.pathologies.map((p) => {
        // FORMAT PATIENT-PATHOLOGIES TO MULTI-LINK ENDPOINT INPUT FORMAT
        return {
          id: p.pathologyId,
          [PatientPathology.apiFields.detectionDate]: DateUtils.toDate(p.detectionDate, { format: "YYYY-MM-DD" }) };
      }) ],
    ].forEach(([ field, value ]) => {
      if (value !== undefined && (value !== null || !opts?.includeNullValues)) {
        dict[field] = value;
      }
    });

    return dict;
  };
}

export { PatientPathologyMulti };

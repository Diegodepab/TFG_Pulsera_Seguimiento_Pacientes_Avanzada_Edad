import { SessionManager } from "$lib/commons/session_manager";
import { Study }         from "$lib/models/study";
import { Fetch }         from "$lib/services/fetch/fetch";

class StudyFetch extends Fetch {
  path        = "/studies";
  entity      = "studies";
  transformer = Study.transformer;

  constructor() {
    super();
    this.headers = super.headers ?? {};
  }

  /** @returns Promise<void> */
  oauthHeader = async () => {
    const authHeader = (await SessionManager.token()).getHeader();
    Object.entries(authHeader).forEach(([ key, value ]) => {
      this.headers[key] = value;
    });
  };
}
export { StudyFetch };
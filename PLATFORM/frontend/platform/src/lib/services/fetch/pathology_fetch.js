import { SessionManager } from "$lib/commons/session_manager";
import { Pathology } from "$lib/models/pathology";
import { Fetch } from "$lib/services/fetch/fetch";

class PathologyFetch extends Fetch {
  /** @type string */
  path = "/pathologies";
  /** @type string */
  entity = "pathology";
  /** @type ModelTransformer */
  transformer = Pathology.transformer;

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

export { PathologyFetch };

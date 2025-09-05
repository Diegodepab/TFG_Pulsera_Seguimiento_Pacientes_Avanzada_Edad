import { BaseController } from "$lib/controllers/base_controller";
import { PathologyFetch } from "$lib/services/fetch/pathology_fetch";

class PathologyController extends BaseController {
  /** @type {PathologyFetch} */
  fetch;

  constructor() {
    super();
    this.fetch = new PathologyFetch();
  }
}

export { PathologyController };

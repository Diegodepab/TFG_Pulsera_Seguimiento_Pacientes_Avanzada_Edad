import { BaseSelectListDC } from "$lib/models/data_containers/base_select_list_dc";

class Constants {
  /** @type string */
  static appName = "app-name";
  /** @type string */
  static appRelease = "0.0.1";
  /** @type number */
  static PAGE_SIZE = 50;
  /** @type number */
  static PAGE_MAX_SIZE = 500;
  /** @type number */
  static WS_TIMEOUT_ATTEMPTS = 5000;  // in ms
  /** @type number */
  static WS_MAX_ATTEMPTS = 48;
  /** @type string */
  static APP_ID = "bracelet-platform";
  /** @type string */
  static APP_IDK = "007ed2a3e6b139642ed22a280f4589c39e1a269afdbb2a801158152cb8f3f690";

  /** @type number */
  static LOGIN_MIN_ATTEMPTS_LEFT_SHOW_MESSAGE = 3;

  /** @type {BaseSelectListDC[]} */
  static ITEMS_PER_PAGE_OPTIONS = [
    new BaseSelectListDC({ value: 25 }),
    new BaseSelectListDC({ value: 50 }),
    new BaseSelectListDC({ value: 75 }),
    new BaseSelectListDC({ value: 100 }),
  ];

  /** @type {BaseSelectListDC} */
  static DEFAULT_ITEMS_PER_PAGE = Constants.ITEMS_PER_PAGE_OPTIONS.at(0);
}

export { Constants };

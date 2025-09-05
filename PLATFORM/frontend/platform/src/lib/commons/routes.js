/**
 * Enum representing routes.
 * @readonly
 * @enum string
 */
const Routes = {
  LOGIN: "/login",
  MY_PROFILE: "/my-profile",
  USERS: "/users",
  INSTRUMENTS: "/instruments",
  PATIENTS: "/patients",
  PATHOLOGIES: "/pathologies",
  PATIENT_MODELS: "/patient-models",
  STUDIES:  "/studies",
  CHATS:    "/chats",
  MESSAGES: "/messages",
  ALARMS:   "/alarm",
  
};

/** @abstract */
class RouteGroup {
  /** @type {(string|RegExp)[]} */
  static notAuthRoutes = [
    "/docs",
    "/terms-and-conditions/es",
    "/terms-and-conditions/en",
    "/about-us",
    "/password/reset",
    "/password/edit",
    "/register",
  ];

  /** @type {(string|RegExp)[]} */
  static notNavbarRoutes = [
    "/login",
    ...RouteGroup.notAuthRoutes,
  ];

  // static guestAccessRoutes: (string | RegExp)[] = [...RouteGroup.roomSessionRoutes];

  /** @type {(string|RegExp)[]} */
  static showNoAuthFooterRoutes = [
    "/login",
    //...RouteGroup.notAuthRoutes.filter((route) => route != Routes.VR)
  ];
}

/** @abstract */
class RouteUtils {
  /**
   * Determines the route based on the entity.
   * @param {Object} opts - Options for determining the route.
   * @param {string} opts.entity - The entity for which to determine the route.
   * @param {string} [opts.extraPath] - Extra path to be appended to the route (optional).
   * @returns string - The determined route.
   */
  static routeByEntity = (opts) => {
    /** @type string */
    let baseRoute;
    switch (opts.entity) {
      case "login":
        baseRoute = Routes.LOGIN;
        break;

      case "user":
      case "user_account":
        baseRoute = Routes.USERS;
        break;

      case "instrument":
        baseRoute = Routes.INSTRUMENTS;
        break;

      case "patient":
        baseRoute = Routes.PATIENTS;
        break;

      case "pathology":
        baseRoute = Routes.PATHOLOGIES;
        break;

      case "patient_model":
        baseRoute = Routes.PATIENT_MODELS;
        break;
        
      case "alarms":
        baseRoute = Routes.ALARMS;
        break;

      case "chat":
        baseRoute = Routes.CHATS;
        break;
    }
    

    if (baseRoute == null) return;
    return [ baseRoute, opts.extraPath ].join("");
  };
}

export { Routes, RouteGroup, RouteUtils };

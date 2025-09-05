import { Routes, RouteUtils } from "$lib/commons/routes";
import { SessionManager } from "$lib/commons/session_manager";
import { UIBaseEntityIcons } from "$lib/commons/ui_utils";
import { PermissionsEntityType, PermissionsGrantType, UserPermission } from "$lib/models/user_permission";
import {
  QueryComparativeOperations,
  QueryFields,
  QueryLogicOperations,
  QueryParamsQ,
} from "$lib/services/utils/query_utils";

/**
 * Represents an action entity in the navigation system.
 * @typedef {Object} ActionEntity
 * @property {string} route - The destination path of the action
 * @property {string} labelKey - The key to internationalization labeling
 * @property {string} icon - The name of the icon to display
 * @property {Object} [divider] - Optional divider configuration
 * @property {boolean} [divider.prepend] - If a divider is to be added before the element
 * @property {boolean} [divider.append] - If a divider is to be added after the element
 */

/**
 * Represents the actions available in the navigation bar
 * @typedef {Object} NavbarActions
 * @property {ActionEntity[]} main - List of actions for the main menu
 * @property {ActionEntity[]} profile - List of actions for the profile menu
 */

/**
 * Represents a route in the navbar with associated action.
 * @typedef {Object} NavbarRoute
 * @property {Routes | PermissionsEntityType} id - The ID of the route.
 * @property {boolean} checkGrants - Indicates if access grants should be checked for this route.
 * @property {PermissionsEntityType[]} grants - Indicates the different grants which give access for this route (one of them).
 * @property {() => boolean} visible - Function to determine if the route is visible.
 * @property {ActionEntity} action - The action associated with the route.
 */

/** @abstract */
class NavbarUtils {
  // NOTE: The order for this list is important because navbar will draw routes using it
  /**
   * Array containing the main actions available in the navbar.
   * @type {(PermissionsEntityType | Routes)[]}
   * @private
     /***/
  static mainActions = [
    PermissionsEntityType.PATIENT,
    PermissionsEntityType.PATHOLOGY,
    PermissionsEntityType.CHAT,
    PermissionsEntityType.ALARM, 
    // PermissionsEntityType.INSTRUMENT,
  ];

  /**
   * Array containing the main actions available in the navbar.
   * @type {PermissionsEntityType[]}
   * @private
   */
  static profileActions = [
    PermissionsEntityType.USER,
  ];

  /**
   * Array containing the main actions available in the navbar.
   * @type {NavbarRoute[]}
   * @private
   * @readonly
   */
  static navbarActions = [
    {
      id: PermissionsEntityType.USER,
      checkGrants: true,
      grants: [ PermissionsEntityType.USER ],
      visible: () => true,
      action: {
        route: RouteUtils.routeByEntity({ entity: PermissionsEntityType.USER }),
        icon: `fas ${ UIBaseEntityIcons.user }`,
        labelKey: "component.navbar.menu.section.user_account",
      },
    },
    {
      id: PermissionsEntityType.PATIENT,
      checkGrants: true,
      grants: [ PermissionsEntityType.PATIENT ],
      visible: () => true,
      action: {
        route: RouteUtils.routeByEntity({ entity: PermissionsEntityType.PATIENT }),
        icon: `fas ${ UIBaseEntityIcons.patient }`,
        labelKey: "component.navbar.menu.section.patient",
      },
    },
    {
      id: PermissionsEntityType.PATHOLOGY,
      checkGrants: true,
      grants: [ PermissionsEntityType.PATHOLOGY ],
      visible: () => true,
      action: {
        route: RouteUtils.routeByEntity({ entity: PermissionsEntityType.PATHOLOGY }),
        icon: `fas ${ UIBaseEntityIcons.pathology }`,
        labelKey: "component.navbar.menu.section.pathology",
      },
    },/*
    {
      id: PermissionsEntityType.INSTRUMENT,
      checkGrants: true,
      grants: [ PermissionsEntityType.INSTRUMENT ],
      visible: () => true,
      action: {
        route: RouteUtils.routeByEntity({ entity: PermissionsEntityType.INSTRUMENT }),
        icon: `fas ${ UIBaseEntityIcons.instrument }`,
        labelKey: "component.navbar.menu.section.instrument",
      },
    },*/
    {
      id: PermissionsEntityType.CHAT,
      checkGrants: true,
      grants: [PermissionsEntityType.CHAT],
      visible: () => true,
      action: {
        route: RouteUtils.routeByEntity({ entity: PermissionsEntityType.CHAT }),
        icon: `fas fa-comments`,
        labelKey: "component.navbar.menu.section.chat",
      },
    },
    {
      id: PermissionsEntityType.ALARM,
      checkGrants: true,
      grants: [PermissionsEntityType.ALARM],
      visible: () => true,
      action: {
        route: RouteUtils.routeByEntity({ entity: PermissionsEntityType.ALARM }),
        icon: `fas ${ UIBaseEntityIcons.alarms }`,
        labelKey: "component.navbar.menu.section.alarms",
      },
    },

  ];

  /**
   * Requests permissions for navbar routes asynchronously.
   * @returns Promise<NavbarRoute[]> - A promise that resolves with an array of navbar routes.
   * @private
   */
  static _requestActionsPermissions = async () => {
    // Obtener información del usuario actual
    const currentUser = await SessionManager.user();
    const userRole = currentUser?.roleName;

    // Para pacientes, usar lógica simplificada sin depender del sistema de permisos backend
    if (userRole === "patient") {
      return [
        {
          id: PermissionsEntityType.PATIENT,
          checkGrants: false,
          grants: [],
          visible: () => true,
          action: {
            route: "/myinfo",
            icon: `fas ${UIBaseEntityIcons.patient}`,
            labelKey: "component.navbar.menu.section.my_patient_info",
          },
        },
        {
          id: PermissionsEntityType.CHAT,
          checkGrants: false,
          grants: [],
          visible: () => true,
          action: {
            route: RouteUtils.routeByEntity({ entity: PermissionsEntityType.CHAT }),
            icon: `fas fa-comments`,
            labelKey: "component.navbar.menu.section.chat",
          },
        }, /*
        {
          id: PermissionsEntityType.INSTRUMENT,
          checkGrants: false,
          grants: [],
          visible: () => true,
          action: {
            route: RouteUtils.routeByEntity({ entity: PermissionsEntityType.INSTRUMENT }),
            icon: `fas ${UIBaseEntityIcons.instrument}`,
            labelKey: "component.navbar.menu.section.instrument",
          },
        } */
      ];
    }

    /** @type {Map<QueryFields, unknown>} */
    const params = new Map();
    params.set(QueryFields.Q, [
      new QueryParamsQ({
        field: UserPermission.apiFields.entityName,
        operation: QueryComparativeOperations.IN,
        value: this.navbarActions
          .filter((aux) => aux.checkGrants && !!aux.grants?.length && aux.visible())
          .reduce((acc, item) => {
            acc.push(...item.grants);
            return acc;
          }, []),
      }),
      QueryLogicOperations.AND,
      new QueryParamsQ({
        field: UserPermission.apiFields.read,
        operation: QueryComparativeOperations.NE,
        value: PermissionsGrantType.NONE,
      }),
    ]);

    // check permissions for required entities
    /** @type PermissionsEntityType[] */
    const entitiesAccess = (await SessionManager.userPermissions({ params }))
        ?.filter((permission) => permission.uiVisibility)
        ?.map((permission) => permission.entityName);

    const filteredActions = this.navbarActions.map((navAction) => {
      // Crear una copia del navAction para evitar mutaciones
      const actionCopy = { ...navAction, action: { ...navAction.action } };
      
      // Aplicar lógica de roles específica
      if (actionCopy.id === PermissionsEntityType.USER) {
        // USERS solo visible para admin
        const shouldShow = userRole === "admin" && actionCopy.visible() && (
          !actionCopy.checkGrants
          || entitiesAccess.findIndex((permission) => actionCopy.grants.includes(permission)) !== -1
        );
        return shouldShow ? actionCopy : null;
      }
      
      if (actionCopy.id === PermissionsEntityType.PATIENT) {
        // PATIENT visible para admin y user (doctor) - pacientes ya manejados arriba
        const hasRoleAccess = (userRole === "admin" || userRole === "user");
        const isVisible = actionCopy.visible();
        const hasPermission = !actionCopy.checkGrants || entitiesAccess.findIndex((permission) => actionCopy.grants.includes(permission)) !== -1;
        
        return (hasRoleAccess && isVisible && hasPermission) ? actionCopy : null;
      }
      
      if (actionCopy.id === PermissionsEntityType.PATHOLOGY) {
        // PATHOLOGY solo para admin y user (doctor)
        const hasRoleAccess = (userRole === "admin" || userRole === "user");
        const isVisible = actionCopy.visible();
        const hasPermission = !actionCopy.checkGrants || entitiesAccess.findIndex((permission) => actionCopy.grants.includes(permission)) !== -1;
        
        return (hasRoleAccess && isVisible && hasPermission) ? actionCopy : null;
      }
      
      if (actionCopy.id === PermissionsEntityType.ALARM) {
        // ALARM para admin y user (doctor) - pacientes ya manejados arriba
        const hasRoleAccess = (userRole === "admin" || userRole === "user");
        const isVisible = actionCopy.visible();
        const hasPermission = !actionCopy.checkGrants || entitiesAccess.findIndex((permission) => actionCopy.grants.includes(permission)) !== -1;
        
        return (hasRoleAccess && isVisible && hasPermission) ? actionCopy : null;
      }
      /*
      if (actionCopy.id === PermissionsEntityType.INSTRUMENT) {
        // INSTRUMENT solo para admin y user (doctor)
        const hasRoleAccess = (userRole === "admin" || userRole === "user");
        const isVisible = actionCopy.visible();
        const hasPermission = !actionCopy.checkGrants || entitiesAccess.findIndex((permission) => actionCopy.grants.includes(permission)) !== -1;
        
        return (hasRoleAccess && isVisible && hasPermission) ? actionCopy : null;
      }
      */
      if (actionCopy.id === PermissionsEntityType.CHAT) {
        // CHAT para todos los roles - pacientes ya manejados arriba
        const hasRoleAccess = (userRole === "admin" || userRole === "user");
        const isVisible = actionCopy.visible();
        const hasPermission = !actionCopy.checkGrants || entitiesAccess.findIndex((permission) => actionCopy.grants.includes(permission)) !== -1;
        
        return (hasRoleAccess && isVisible && hasPermission) ? actionCopy : null;
      }

      // Para el resto de entidades, usar la lógica normal
      const shouldShow = actionCopy.visible() && (
        !actionCopy.checkGrants
        || entitiesAccess.findIndex((permission) => actionCopy.grants.includes(permission)) !== -1
      );
      
      return shouldShow ? actionCopy : null;
    }).filter(action => action !== null);

    return filteredActions;
  };

  /**
   * Filters and sorts permissions by group.
   * @param {NavbarRoute[]} permissions - The permissions to filter and sort.
   * @param {string[]} group - The group of permissions to include.
   * @returns ActionEntity[] - An array of action entities corresponding to the filtered and sorted permissions.
   * @private
   */
  static _permissionsByGroup = (permissions, group) => {
    const filterPerms = permissions
      .filter((e) => group.includes(e.id))
      .sort((a1, a2) => group.indexOf(a1.id) - group.indexOf(a2.id));
    return filterPerms.map((a) => a.action);
  };

  /**
   * Requests navbar permissions asynchronously and organizes them into main and profile actions.
   * @returns Promise<NavbarActions> - A promise that resolves with an object containing main and profile actions.
   */
  static requestNavbarPermissions = async () => {
    const navbarActions = await this._requestActionsPermissions();

    return {
      main: this._permissionsByGroup(navbarActions, this.mainActions),
      profile: this._permissionsByGroup(navbarActions, this.profileActions),
    };
  };
}

export { NavbarUtils };

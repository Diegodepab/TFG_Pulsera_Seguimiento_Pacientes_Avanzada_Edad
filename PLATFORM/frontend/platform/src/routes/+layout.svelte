<script>
  import { goto } from "$app/navigation";
  import { navigating, page } from "$app/state";
  import BaseNav from "$components/argon_template/Navbar/BaseNav.svelte";
  import "/static/font/open_sans/stylesheet.css";
  import "/static/css/argon_global.css";
  import "/static/css/global.css";
  import "@fortawesome/fontawesome-pro/css/all.min.css";
  import CustomNotification from "$components/argon_template/NotificationPlugin/CustomNotification.svelte";
  import MainNavbarMenuActions from "$components/platform/navbar/MainNavbarMenuActions.svelte";
  import NotAuthFooter from "$components/platform/NotAuthFooter.svelte";
  import { Global } from "$lib/commons/global";
  import { RouteGroup, Routes } from "$lib/commons/routes";
  import { SessionManager } from "$lib/commons/session_manager";
  import { navigatorHistory, userLogged } from "$lib/commons/stores";
  import { Utils } from "$lib/commons/utils";
  import { ExceptionManager } from "$lib/exceptions/exception_manager";
  import { ExceptionMessages } from "$lib/exceptions/exception_messages";
  import { onMount } from "svelte";
  import { getLocaleFromNavigator, init, isLoading as loadingT, register } from "svelte-i18n";
  import Notifications from "svelte-notifications";

  /**
   * @typedef {Object} LayoutProps
   * @property {Snippet} [children]
   */

  /** @type LayoutProps */
  let { children } = $props();

  if (import.meta.env.DEV) {
    // window['__PLATFORM_DEV_MODE'] = true;
    // window['__WRTC_DEV_MODE'] = true;
    // window['__LAYOUT_DEV_MODE'] = true;
  }

  register("en", () => import("/static/lang/en.json"));
  register("es", () => import("/static/lang/es.json"));

  init({
    fallbackLocale: "en",
    initialLocale: getLocaleFromNavigator(),
  });

  //const port = import.meta.env.DEV ? '8443' : null;
  Global.init({
    host: new URL(page.url.origin),
    apiVersion: "/v1",
    wsPath: "/ws",
    signalingWsPrePath: "/signaling",
    //apiPort: port
  });

  // Global exception handler
  ExceptionManager.init();
  onunhandledrejection = async (ev) => {
    ev.preventDefault();
    await ExceptionManager.manage(ExceptionMessages.getExceptionAction(ev.reason));
  };

  onerror = async function (event, source, lineno, colno, error) {
    Utils.logging("error", event, source, lineno, colno, error);
    //await exceptionManager.manage(ExceptionMessages.getExceptionAction(error));
  };

  /** @type boolean */
  let showNavbar = $derived(!RouteGroup.notNavbarRoutes.some((path) => page.url.pathname.match(path)));

  /** @type boolean */
  let showNoAuthFooter = $derived(RouteGroup.showNoAuthFooterRoutes.some((path) => page.url.pathname.match(path)));


  $effect(() => {
    if (!navigatorHistory.isCurrentPath(page.url)) {
      if (page.url.pathname === "/") navigatorHistory.reset();
      navigatorHistory.push(page.url);
    }
  });

  $effect(() => {
    if (navigating?.type === "popstate") {
      if (navigatorHistory.isPrevPath(navigating.to.url)) navigatorHistory.pop();
    }
  });

  /** @type boolean */
  let loading = $state(true);

  /** @type OnMount */
  onMount(async () => {
    await SessionManager.init();

    if (RouteGroup.notAuthRoutes.some((path) => page.url.pathname.match(path))) {
      try {
        await SessionManager.closeSession();
      } finally {
        loading = false;
      }
    } else {
      const token = await SessionManager.token({ ignoreNotValidTokenError: true });
      if (token == null) {
        await goto(/** @type string */ Routes.LOGIN, { replaceState: true });
      } else {
        userLogged.set(await SessionManager.user());
        let user = await SessionManager.user();
      }

      loading = false;
    }
  });

  /** @returns Promise<void> */
  const logout = async () => {
    await SessionManager.closeSession();
    await goto(Routes.LOGIN);
  };
</script>

<Notifications item={CustomNotification}>
  <div class="main-content">
    {#if loading || $loadingT}
      <div></div>
    {:else}
      {#if showNavbar}
        <BaseNav
            containerClasses="container-fluid"
            topClasses="navbar-top border-bottom navbar-expand bg-navbar-custom-primary navbar-dark p-3"
            menuClasses="navbar-collapse collapse"
            position="top"
            show
        >

          {#snippet brandSnippet()}
            <div>
              <a class="logo-title text-light navbar-logo-title" href="/">
                <img alt="bracelet Logo" src="/imgs/logos/logo.png" width="35"/>
              </a>
            </div>
          {/snippet}

          <div class="d-flex ml-auto justify-content-end">
            <MainNavbarMenuActions onlogout={logout}/>
          </div>
        </BaseNav>
      {/if}
      {@render children?.()}
    {/if}
  </div>

  {#if showNoAuthFooter}
    <NotAuthFooter/>
  {/if}

</Notifications>

<script>
  import BaseDropdown from "$components/argon_template/BaseDropdown.svelte";
  import MainNavbarProfile from "$components/platform/navbar/MainNavbarProfile.svelte";
  import MainNavbarProfileMenuActions from "$components/platform/navbar/MainNavbarProfileMenuActions.svelte";
  import { NavbarUtils } from "$components/platform/navbar/navbar_utils";
  import { Routes } from "$lib/commons/routes";
  import { userLogged } from "$lib/commons/stores";
  import { onMount } from "svelte";
  import { t, locale } from "svelte-i18n";

  /**
   * @typedef {Object} MainNavbarMenuProps
   * @property {() => void} [onlogout]
   */

  /** @type MainNavbarMenuProps */
  let {
    /** @type {() => void} */ onlogout,
  } = $props();

  /** @type NavbarActions */
  let navbarActions = $state();

  /** @boolean */
  let isDark = $state(true);

  let currentLang = $state('es'); // idioma por defecto

  onMount(async () => {
    // Carga de rutas
    navbarActions = await NavbarUtils.requestNavbarPermissions();
    
    // Tema inicial
    isDark = localStorage.getItem('theme') === 'dark';
    document.documentElement.classList.toggle('dark-mode', isDark);

    // Idioma inicial
    const savedLang = localStorage.getItem('lang');
    if (savedLang) {
      currentLang = savedLang;
      locale.set(currentLang);
    }
  });

  function toggleTheme() {
    isDark = !isDark;
    document.documentElement.classList.toggle('dark-mode', isDark);
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }

  function toggleLang() {
    currentLang = currentLang === 'es' ? 'en' : 'es';
    locale.set(currentLang);
    localStorage.setItem('lang', currentLang);
  }
</script>




<!-- Vista de escritorio -->
<ul class="navbar-nav ml-auto align-items-center d-none d-sm-flex">
  {#each navbarActions?.main ?? [] as action}
    <li class="nav-item">
      <a class="nav-link nav-link-icon" href={action.route}>
        <span class="nav-link-inner--text">{$t(action.labelKey)}</span>
      </a>
    </li>
  {/each}

  <MainNavbarProfile allowedActions={navbarActions?.profile} {onlogout}/>
    <!-- Toggle idioma ES/EN -->
  <li class="nav-item">
    <a
      class="nav-link nav-link-icon"
      role="button"
      style="cursor:pointer;"
      onclick={toggleLang}
    >
      <span class="fas fa-language" style="color: #fff;"></span>
      <span class="nav-link-inner--text" style="color: #fff;">{currentLang === 'es' ? 'ES' : 'EN'}</span>
    </a>
  </li>
    <!-- Toggle modo claro/oscuro -->
  <li class="nav-item">
  <label class="theme-switch">
    <input
      type="checkbox"
      class="theme-switch__checkbox"
      onchange={toggleTheme}
    />
    <div class="theme-switch__container">
      <div class="theme-switch__clouds"></div>
      <div class="theme-switch__stars-container">

      </div>
      <div class="theme-switch__circle-container">
        <div class="theme-switch__sun-moon-container">
          <div class="theme-switch__moon">
            <div class="theme-switch__spot"></div>
            <div class="theme-switch__spot"></div>
            <div class="theme-switch__spot"></div>
          </div>
        </div>
      </div>
    </div>
  </label>
</li>
</ul>

<!-- Vista móvil -->
<ul class="align-items-center ml-auto navbar-nav show-from-top d-flex d-sm-none">

  
  <BaseDropdown
      isOpen={false}
      menuClasses="mt-2"
      menuOnRight
      tag="li"
      hasToggle={false}
      tagClasses="nav-item pr-0"
      titleTag="a"
  >
    {#snippet titleSnippet()}
      <div class="nav-link mx-0 d-flex align-items-center">
        <span class="mr-1">{$t('component.navbar.menu.col-xs-title')}</span>
        <span class="fas fa-bars" style="font-size: 1.1rem;"></span>
      </div>
    {/snippet}

    <div class="align-items-center">
      <div class="col mx-2 d-flex justify-content-center align-content-center align-items-center">
        <span class="avatar avatar-sm avatar-light bg-secondary-custom avatar-custom">
          <i class="fas fa-laptop-medical fa-fw"></i>
        </span>
        <div class="col-11 px-0">
          <div class="dropdown-header">
            <span class="m-0">{$userLogged?.fullName}</span>
          </div>
          <div class="dropdown-subheader mb-1 item-overflow">
            <span class="m-0">{$userLogged?.email}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="dropdown-divider"></div>
    <a class="dropdown-item item-overflow" href={Routes.MY_PROFILE}>
      <i class="fas fa-user fa-fw"></i>
      <span>{$t('component.navbar.profile-menu.my-profile')}</span>
    </a>

    <div class="dropdown-divider"></div>

    {#each navbarActions?.profile ?? [] as action}
      <a class="dropdown-item item-overflow" href={action.route}>
        <i class="{action.icon} fa-fw"></i>
        <span>{$t(action.labelKey)}</span>
      </a>

      {#if action?.divider?.append}
        <div class="dropdown-divider"></div>
      {/if}
    {/each}

    <!-- Toggle en móvil si se desea incluir -->
    <div class="dropdown-divider"></div>
    <a class="dropdown-item item-overflow" onclick={toggleTheme}>
      <i class="fas fa-adjust fa-fw"></i>
      <span>{isDark ? $t('component.navbar.theme.light') : $t('component.navbar.theme.dark')}</span>
    </a>
    <!-- Toggle idioma en móvil -->
    <a class="dropdown-item item-overflow" onclick={toggleLang}>
      <i class="fas fa-language fa-fw"></i>
      <span>{currentLang === 'es' ? 'Español' : 'English'}</span>
    </a>

    <MainNavbarProfileMenuActions
        prependDivider={false}
        allowedActions={navbarActions?.main}
        {onlogout}
    />
  </BaseDropdown>
</ul>

<script>
  import BaseDropdown from "$components/argon_template/BaseDropdown.svelte";
  import MainNavbarProfileMenuActions from "$components/platform/navbar/MainNavbarProfileMenuActions.svelte";
  import { Routes } from "$lib/commons/routes";
  import { userLogged } from "$lib/commons/stores";
  import { t } from "svelte-i18n";

  /**
   * @typedef {Object} MainNavbarProfileProps
   * @property {ActionEntity[]} allowedActions
   * @property {() => void} [onlogout]
   */

  /** @type MainNavbarProfileProps */
  let {
    /** @type ActionEntity[] */ allowedActions,
    /** @type {() => void} */ onlogout,
  } = $props();
</script>

<ul class="align-items-end ml-auto navbar-nav show-from-top">
  <BaseDropdown
      isOpen={false}
      menuClasses="mt-2"
      menuOnRight
      tag="li"
      tagClasses="nav-item"
      titleClasses="nav-link pr-0"
      titleTag="a">


    <div class="dropdown-header">
      <span class="m-0">{$userLogged?.fullName}</span>
    </div>

    <div class="dropdown-subheader mb-1">
      <span class="m-0">{$userLogged?.email}</span>
    </div>

    <div class="dropdown-divider"></div>

    <a class="dropdown-item" href={Routes.MY_PROFILE}>
      <i class="fas fa-user fa-fw"></i>
      <span>{$t('component.navbar.profile-menu.my-profile')}</span>
    </a>

    <MainNavbarProfileMenuActions {allowedActions} {onlogout}/>
  </BaseDropdown>
</ul>

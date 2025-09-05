<script>
  import { t } from "svelte-i18n";

  /**
   * @typedef {Object} ProfileMenuActionsProps
   * @property {ActionEntity[]} allowedActions
   * @property {boolean} [prependDivider]
   * @property {() => void} [onlogout]
   */

  /** @type ProfileMenuActionsProps */
  let {
    /** @type {ActionEntity[]} */ allowedActions,
    /** @type boolean */ prependDivider = true,
    /** @type {() => void} */ onlogout,
  } = $props();
</script>

{#if !!allowedActions && prependDivider}
  <div class="dropdown-divider"></div>
{/if}

{#each allowedActions ?? [] as action}
  {#if action.divider?.prepend}
    <div class="dropdown-divider"></div>
  {/if}
  <a class="dropdown-item" href={action.route}>
    <i class="{action.icon} fa-fw"></i>
    <span class="pr-2">{$t(action.labelKey)}</span>
  </a>

  {#if action.divider?.append}
    <div class="dropdown-divider"></div>
  {/if}

{/each}

{#if allowedActions?.length !== 0}
  <div class="dropdown-divider"></div>
{/if}

<a class="dropdown-item item-overflow" onclick={onlogout}>
  <i class="fas fa-door-open fa-fw"></i>
  <span class="pr-2">{$t('component.navbar.profile-menu.logout')}</span>
</a>

<style>
  .dropdown-item {
    padding-right: 2rem !important;
  }
</style>
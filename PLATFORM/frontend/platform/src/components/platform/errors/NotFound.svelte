<script>
  import { goto } from "$app/navigation";
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import { t } from "svelte-i18n";

  /**
   * @typedef {Object} NotFoundProps
   * @property {App.Error | undefined} error
   * @property {number} status - Status code representing the current status.
   */

  /** @type NotFoundProps */
  let {
    /** @type {App.Error | undefined} */ error,
    /** @type number */ status,
  } = $props();
</script>

<svelte:head>
  <title>{$t('route.error.404.title')}</title>
</svelte:head>

<div class="d-flex justify-content-center">
  <div class="page-content p-0 w-100 w-lg-75 text-center">
    <!-- header section -->
    <div class="mx-3 mt-4 font-weight-400 text-primary">
      <div class="text-lg">{$t('route.error.404.content.first')}</div>
      <div class="text-md mt-1">{$t('route.error.404.content.last')}</div>
    </div>

    <hr class="w-50 mt-4 mb-1">

    <!-- footer section -->
    <div class="mx-3 mt-2 mb-4 font-weight-400 text-primary">
      <div class="d-flex justify-content-center">
        <div class="w-100 w-xl-75 d-flex justify-content-around align-items-center flex-column flex-md-row">
          <div class="pb-3 pb-md-0 pr-md-3 text-center text-md-left">{$t('route.error.common.help')}</div>
          <BaseButton onclick={() => goto('/')} outline>
            <span class="btn-inner--text">{$t('route.error.common.button.go-home')}</span>
          </BaseButton>
        </div>
      </div>
    </div>
  </div>
</div>
<script>
  import BaseProgress from "$components/argon_template/BaseProgress.svelte";

  /**
   * @typedef {Object} LoadingContentPageProps
   * @property {string} [classNames] - Additional CSS classes for the container div
   * @property {boolean} [loading=false] - Whether the content is currently loading
   * @property {string} [type='info'] - The type/color of the progress bar (info, success, warning, danger, etc.)
   */

  /** @type LoadingContentPageProps */
  let {
    /** @type string */ classNames = "",
    /** @type boolean */ loading = false,
    /** @type string */ type = "info",
  } = $props();

</script>

<div class={classNames}>
  {#if loading}
    <BaseProgress striped animated {type} height={4} value={100}/>
  {:else}
    <div style="height: 4px; width: 100%"></div>
  {/if}
</div>

<script>
  import { onDestroy, onMount } from "svelte";

  /**
   @typedef {Object} BlockLoadingProps
   @property {number} [width] -Additional CSS classes to apply to the modal header
   @property {number} [height] - Whether clicking outside the modal should close it
   */

  /** @type BlockLoadingProps */
  let {
    /** @type number */ width = 0,
    /** @type number */ height = 0,
  } = $props();


  /** @type onMount */
  onMount(() => {
    document.body.style.overflow = "hidden";
    updateSize();
  });

  /** @type onDestroy */
  onDestroy(() => {
    document.body.style.overflow = "unset";
  });

  /** @return void */
  const updateSize = () => {
    width = document.documentElement.clientWidth;
    height = document.documentElement.clientHeight;
  };

</script>

<svelte:window onresize={updateSize}></svelte:window>

<div class="block-loading" style="width: {width}px; height: {height}px;">
  <i class="fas fa-spinner fa-spin"></i>
</div>

<style>
  .block-loading {
    top: 0;
    left: 0;
    z-index: 10000;
    background: var(--shadow-color-light-transparent);
    position: fixed;
    display: flex;
    justify-content: center;
    align-items: center;
    color: var(--primary-regular-color-light);
  }

  .block-loading i {
    height: 2rem;
    width: 2rem;
    font-size: 2rem;
  }
</style>

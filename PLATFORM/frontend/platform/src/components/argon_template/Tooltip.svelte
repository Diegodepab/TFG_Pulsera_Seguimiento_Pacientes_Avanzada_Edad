<script>
  /**
   * @typedef {Object} TooltipProps
   * @property {string} [tip = ""] - Text content to show in the tooltip
   * @property {boolean} [top = false] - Position the tooltip above the element
   * @property {boolean} [right = false] - Position the tooltip to the right of the element
   * @property {boolean} [bottom = false] - Position the tooltip below the element
   * @property {boolean} [left = false] - Position the tooltip to the left of the element
   * @property {boolean} [active = false] - Force the tooltip to be visible (without hover)
   * @property {string} [color = "#757575"] - Background color of the default tooltip
   * @property {import("svelte").Snippet} [children] - Content that triggers the tooltip on hover
   * @property {import("svelte").Snippet} [customTipSnippet] - Custom tooltip content instead of the default tip
   */

  /** @type TooltipProps */
  let {
    /** @type string */ tip = "",
    /** @type boolean */ top = false,
    /** @type boolean */ right = false,
    /** @type boolean */ bottom = false,
    /** @type boolean */ left = false,
    /** @type boolean */ active = false,
    /** @type string */ color = "#757575",
    /** @type Snippet */ children,
    /** @type Snippet */ customTipSnippet,
  } = $props();

  /** @type string */
  let style = `background-color: ${ color };`;
</script>

<style>
  .tooltip-wrapper {
    position: relative;
    display: inline-block;
  }

  .tooltip {
    position: absolute;
    font-family: inherit;
    display: inline-block;
    white-space: nowrap;
    color: inherit;
    opacity: 0;
    visibility: hidden;
    transition: opacity 150ms, visibility 150ms;
  }

  .default-tip {
    display: inline-block;
    padding: 8px 16px;
    border-radius: 6px;
    color: inherit;
  }

  .tooltip.top {
    left: 50%;
    transform: translate(-50%, -100%);
    margin-top: -8px;
  }

  .tooltip.bottom {
    left: 50%;
    bottom: 0;
    transform: translate(-50%, 100%);
    margin-bottom: -8px;
  }

  .tooltip.left {
    left: 0;
    transform: translateX(-100%);
    margin-left: -8px;
  }

  .tooltip.right {
    right: 0;
    transform: translateX(100%);
    margin-right: -8px;
  }

  .tooltip.active {
    opacity: 1;
    visibility: initial;
  }

  .tooltip-slot:hover + .tooltip {
    opacity: 1;
    visibility: initial;
  }
</style>

<div class="tooltip-wrapper">
  <span class="tooltip-slot">
    {@render children?.()}
  </span>
  <div
      class="tooltip"
      class:active
      class:bottom
      class:left
      class:right
      class:top>
    {#if tip}
      <div class="default-tip" {style}>{tip}</div>
    {:else}
      {@render customTipSnippet?.()}
    {/if}
  </div>
</div>

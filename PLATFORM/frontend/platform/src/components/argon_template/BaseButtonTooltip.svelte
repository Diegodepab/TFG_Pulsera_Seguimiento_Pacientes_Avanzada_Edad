<script>
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import { fade } from "svelte/transition";

  /**
   * @typedef {Object} BaseTooltipProps
   * @property {boolean} [top = false] - Position the tooltip above the button
   * @property {boolean} [bottom = !top] - Position the tooltip below the button
   * @property {boolean} [left = false] - Align the tooltip to the left
   * @property {boolean} [right = !left] - Align the tooltip to the right
   * @property {string} text - Text content to display in the tooltip
   * @property {string} [iconClass = "fa-copy"] - Icon class to display in the button
   * @property {number} [viewingTime = 2000] - Duration in milliseconds to display the tooltip
   * @property {boolean} [showTooltip = $bindable(false)] - Whether the tooltip is visible
   * @property {*} [animationType = fade] - Svelte transition to use for the tooltip
   * @property {import("svelte").Snippet} [buttonSnippet] - Custom button content
   * @property {(event: Event) => void} [onclick = () => null] - Function to execute when the button is clicked
   */

  /** @type BaseTooltipProps */
  let {
    /** @type boolean */ top = false,
    /** @type boolean */ bottom = !top,
    /** @type boolean */ left = false,
    /** @type boolean */ right = !left,
    /** @type string */ text,
    /** @type string */ iconClass = "fa-copy",
    /** @type number */ viewingTime = 2000,
    /** @type boolean */ showTooltip = $bindable(false),
    /** @type * */ animationType = fade,
    /** @type Snippet */ buttonSnippet,
    /** @type {(event: Event) => void} */ onclick = (_) => null,
  } = $props();

  /**
   * @param {Event} event
   * @return {void}
   * */
  const onClick = (event) => {
    showTooltip = true;
    onclick(event);
  };
</script>

<div class="base-button-tp mx-2">
  {#if buttonSnippet}
    {@render buttonSnippet()}
  {:else}
    <BaseButton size="sm" type="primary" onclick={onClick}>
      <i class="fas {iconClass} fa-fw"></i>
    </BaseButton>
  {/if}

  {#if showTooltip}
    <div
        transition:animationType={{ duration: viewingTime }}
        onintroend={() => showTooltip = false}
        class="tp"
        class:top
        class:bottom
        class:left
        class:right
    >
      <strong>{text}</strong>
    </div>
  {/if}
</div>

<style>
  .base-button-tp {
    position: relative;
  }

  .base-button-tp .tp {
    border: 1px black solid;
    position: absolute;
    border-radius: 0.3rem;
    padding: 0.25rem 0.5rem;
    z-index: 1;
  }

  .base-button-tp .tp.top {
    bottom: calc(100% + 0.5rem);
  }

  .base-button-tp .tp.bottom {
    top: calc(100% + 0.5rem);
  }

  .base-button-tp .tp.left {
    left: 0;
  }

  .base-button-tp .tp.right {
    right: 0;
  }

  .base-button-tp .tp.bottom.left:after {
    position: absolute;
    content: "";
    border-bottom: .5em solid;
    border-right: .5em solid transparent;
    border-top: 0;
    border-left: .5em solid transparent;
    top: -0.5em;
    left: 0.5em;
  }

  .base-button-tp .tp.bottom.right:after {
    position: absolute;
    content: "";
    border-bottom: .5em solid;
    border-right: .5em solid transparent;
    border-top: 0;
    border-left: .5em solid transparent;
    top: -0.5em;
    right: 0.5em;
  }

  .base-button-tp .tp.top.left:after {
    position: absolute;
    content: "";
    border-top: .5rem solid;
    border-right: .5rem solid transparent;
    border-bottom: 0;
    border-left: .5rem solid transparent;
    bottom: -0.5rem;
    left: 0.5em;
  }

  .base-button-tp .tp.top.right:after {
    position: absolute;
    content: "";
    border-top: .5rem solid;
    border-right: .5rem solid transparent;
    border-bottom: 0;
    border-left: .5rem solid transparent;
    bottom: -0.5rem;
    right: 0.5em;
  }
</style>

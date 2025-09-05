<script>
  /**
   * @typedef {Object} BaseButtonProps
   * @property {"primary" | "secondary" | "danger" | "success"} [type="primery"] - Button color variant
   * @property {string} [classNames = ""] - Additional CSS classes for the button
   * @property {boolean} [loading = false] - Whether some process of loading is being executed
   * @property {boolean} [round = false] - Whether the button will be rounded
   * @property {boolean} [wide = false] - Whether the button will be displayed wide
   * @property {boolean} [icon = false] - Whether the content will be an icon
   * @property {boolean} [block = false]  - Whether the button will be displayed as block
   * @property {"button" | "input" | "submit" | "reset" | null | undefined} [nativeType = "button"] - HTML button type attribute
   * @property {boolean} [disabled = false]   - Indicates if the button is disabled
   * @property {"xs" | "sm" | "lg" | ""} [size = ""] - Button size
   * @property {boolean} [outline = false] - Whether the button is outline
   * @property {boolean} [link = false] - Whether the button contains a link
   * @property {boolean} [defaultPrevented = false] - Whether the button must prevent its events
   * @property {import("svelte").Snippet} [children] - Content to display inside the button
   * @property {import("svelte").Snippet} [loadingSnippet] - Custom loading indicator
   * @property {(event: Event) => void} [onclick = (event) => null] - Function to execute when button is clicked
   */

  /** @type BaseButtonProps */
  let {
    /** @type {"primary" | "secondary" | "danger" | "success"} */ type = "primary",
    /** @type string */ classNames = "",
    /** @type boolean */ loading = false,
    /** @type boolean */ round = false,
    /** @type boolean */ wide = false,
    /** @type boolean */ icon = false,
    /** @type boolean */ block = false,
    /** @type {"button" | "input" | "submit" | "reset" | null | undefined} */ nativeType = "button",
    /** @type boolean */ disabled = false,
    /** @type {"xs" | "sm" | "lg" | ""} */ size = "",
    /** @type boolean */ outline = false,
    /** @type boolean */ link = false,
    /** @type boolean */ defaultPrevented = false,
    /** @type Snippet */ children,
    /** @type Snippet */ loadingSnippet,
    /** @type {(event: Event) => void} */ onclick = (_) => null,
  } = $props();


  /**
   * @param {Event} event
   * @return {void}
   * */
  const onClick = (event) => {
    if (defaultPrevented) {
      event.stopPropagation();
      event.preventDefault();
    }

    onclick(event);
  };

</script>

<button
    class="btn {size ? `btn-${size}` : ''} {type ? outline ? `btn-outline-${type}` : `btn-${type}` : ''} {classNames}"
    class:btn-block={block}
    class:btn-wd={wide}
    class:btn-link={link}
    class:btn-icon={icon}
    class:btn-fab={icon}
    class:rounded-circle={round}
    disabled={disabled || loading}
    onclick={onClick}
    type={nativeType}
    variant="{outline ? `outline-${type}` : type}"
>
  {#if loadingSnippet}
    {@render loadingSnippet()}
  {:else}
    {#if loading}
      <i class="bi bi-arrow-clockwise spin"></i>
    {/if}
  {/if}

  {@render children?.()}
</button>

<style>
  .base-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .base-button i {
    padding: 0 3px;
  }
</style>

<script>
  /**
   * @typedef {Object} CardProps
   * @property {string} [classNames = ""] - Additional CSS classes for the card
   * @property {string} [headerClasses = ""] - Additional CSS classes for the card header
   * @property {string} [bodyClasses = ""] - Additional CSS classes for the card body
   * @property {string} [footerClasses = ""] - Additional CSS classes for the card footer
   * @property {boolean} [background = false] - Whether to apply the background style
   * @property {string} [gradient = ""] - Background gradient style to apply
   * @property {boolean} [shadow = false] - Whether to apply a shadow to the card
   * @property {string} [shadowSize = ""] - Size of the shadow if enabled
   * @property {"notice" | "mini" | "" | null} [type = null] - Predefined card style variant
   * @property {boolean} [hover = false] - Whether to apply hover lift effect
   * @property {boolean} [imgTop = false] - Whether to show an image at the top of the card
   * @property {boolean} [imgBottom = false] - Whether to show an image at the bottom of the card
   * @property {string} [imgSrc = ""] - Source URL for the card image
   * @property {string} [alt = ""] - Alt text for the card image
   * @property {boolean} [noBody = false] - Whether to omit the card body wrapper
   * @property {import("svelte").Snippet} [children] - Content to display in the card body
   * @property {import("svelte").Snippet} [imageSnippet] - Custom image content
   * @property {import("svelte").Snippet} [headerSnippet] - Content to display in the card header
   * @property {import("svelte").Snippet} [footerSnippet] - Content to display in the card footer
   * @property {(event: Event) => void} [onclosemodal = () => null] - Function for handling modal close
   */

  /** @type CardProps */
  let {
    /** @type string */ classNames = "",
    /** @type string */ headerClasses = "",
    /** @type string */ bodyClasses = "",
    /** @type string */ footerClasses = "",
    /** @type boolean */ background = false,
    /** @type boolean */ shadow = false,
    /** @type boolean */ hover = false,
    /** @type string */ gradient = "",
    /** @type string */ shadowSize = "",
    /** @type {"notice" | "mini" | "" | null} */ type = "",
    /** @type boolean */ imgTop = false,
    /** @type boolean */ imgBottom = false,
    /** @type string */ imgSrc = "",
    /** @type string */ alt = "",
    /** @type boolean */ noBody = false,
    /** @type Snippet */ children,
    /** @type Snippet */ imageSnippet,
    /** @type Snippet */ headerSnippet,
    /** @type Snippet */ footerSnippet,
  } = $props();

</script>

<div
    class="{classNames}
  {gradient !== '' ? `bg-gradient-${gradient}` : ''}
  {type !== '' ? `bg-${type}` : ''}
  {shadowSize !== '' ? `shadow-${shadowSize}` : ''} card card-content"
    class:shadow
    class:bg-candy={background}
    class:card-lift--hover={hover}
>
  {#if imgSrc && (!imgTop || !imgBottom)}
    <img src={imgSrc} alt={alt} class="card-img">
  {/if}

  {#if imgTop && (imageSnippet || imgSrc)}
    {#if imageSnippet}
      {@render imageSnippet()}
    {:else}
      <img {alt} src={imgSrc} class="card-img-top"/>
    {/if}
  {/if}

  {#if headerSnippet}
    <div class="card-header {headerClasses}">
      {@render headerSnippet()}
    </div>
  {/if}

  {#if !noBody}
    <div class="card-body {bodyClasses}">
      {@render children?.()}
    </div>
  {:else}
    {@render children?.()}
  {/if}

  {#if footerSnippet}
    <div class="card-footer {footerClasses}">
      {@render footerSnippet()}
    </div>
  {/if}

  {#if imgBottom && (imageSnippet || imgSrc)}
    {#if imageSnippet}
      {@render imageSnippet()}
    {:else}
      <img {alt} src={imgSrc} class="card-img-bottom"/>
    {/if}
  {/if}
</div>

<style>
  .bg-candy {
    background: #262A33 !important;
  }
</style>

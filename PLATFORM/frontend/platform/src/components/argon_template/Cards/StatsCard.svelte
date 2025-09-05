<script>
  import Card from "$components/argon_template/Cards/Card.svelte";

  /**
   * @typedef {Object} StatsCardProps
   * @property {string} [classNames = ""] - Additional CSS classes for the card
   * @property {"primary"} [type = "primary"] - Color theme for the card and icon
   * @property {string} [icon = ""] - Icon class to display in the card
   * @property {string} [title = ""] - Title text to display in the card
   * @property {string} [subTitle = ""] - Subtitle/value text to display in the card
   * @property {string} [iconClasses = ""] - Additional CSS classes for the icon container
   * @property {import("svelte").Snippet} [children] - Custom content for the main area of the card
   * @property {import("svelte").Snippet} [iconSnippet] - Custom icon content
   * @property {import("svelte").Snippet} [footerSnippet] - Content to display in the card footer
   * @property {(event: Event) => void} [onclosemodal = () => null] - Function for handling modal close
   */

  /** @type StatsCardProps */
  let {
    /** @type string */ classNames = "",
    type = "primary",
    /** @type string */ icon = "",
    /** @type string */ title = "",
    /** @type string */ subTitle = "",
    /** @type string */ iconClasses = "",
    /** @type Snippet */ children,
    /** @type Snippet */ iconSnippet,
    /** @type Snippet */ footerSnippet,
  } = $props();

</script>

<Card classNames="card-stats card {classNames}">
  <div class="row">
    <div class="col">
      {#if children}
        {@render children()}
      {:else}
        {#if title}
          <h5 class="card-title text-uppercase text-muted mb-0">{title}</h5>
        {/if}

        {#if subTitle}
          <span class="h2 font-weight-bold mb-0">{subTitle}</span>
        {/if}
      {/if}
    </div>

    {#if iconSnippet}
      {@render iconSnippet()}
    {:else}
      {#if icon}
        <div class="col-auto">
          <div class="icon icon-shape text-white rounded-circle shadow bg-{type} {iconClasses}">
            <i class={icon}></i>
          </div>
        </div>
      {/if}
    {/if}
  </div>

  {@render footerSnippet?.()}
</Card>

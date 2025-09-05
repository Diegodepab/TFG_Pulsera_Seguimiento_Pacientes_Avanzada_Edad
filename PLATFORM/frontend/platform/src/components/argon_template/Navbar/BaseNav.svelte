<script>
  /**
   * @typedef {Object} BaseNavProps
   * @property {boolean} [show] - Whether the navigation menu is visible
   * @property {boolean} [transparent] - Whether the navbar has a transparent background
   * @property {string} [expand] - Breakpoint at which the navbar expands
   * @property {string} [menuClasses] - Additional CSS classes for the collapsed menu
   * @property {string} [topClasses] - Additional CSS classes for the navbar
   * @property {string} [containerClasses] - Additional CSS classes for the navbar container
   * @property {string} [type] - Color theme of the navbar
   * @property {string} [position] - Position of the navbar (fixed-top, fixed-bottom, etc.)
   * @property {boolean} [hasMenu] - Whether the navbar has a collapsible menu
   * @property {import("svelte").Snippet} [children] - Content to display in the navbar menu
   * @property {import("svelte").Snippet} [brandSnippet] - Custom content for the navbar brand
   * @property {import("svelte").Snippet} [toggleButtonSnippet] - Custom toggle button for the mobile menu
   */

  /** @type BaseNavProps */
  let {
    /** @type boolean */ show = false,
    /** @type boolean */ transparent = false,
    /** @type boolean */ hasMenu = false,
    /** @type string */ expand = "lg",
    /** @type string */ menuClasses = "",
    /** @type string */ topClasses = "",
    /** @type string */ containerClasses = "",
    /** @type string */ type = "",
    /** @type string */ position = "",
    /** @type Snippet */ children,
    /** @type Snippet */ brandSnippet,
    /** @type Snippet */ toggleButtonSnippet,
  } = $props();

  /**
   * Validates a given type against a predefined list of valid types.
   * @param {string} type - The type to validate.
   * @return {string} The validated type, or an empty string if the type is not valid.
   */
  const validator = (type) => [
    "",
    "dark",
    "success",
    "danger",
    "warning",
    "white",
    "primary",
    "light",
    "info",
    "vue",
  ].find((_type) => _type === type) ?? "";

  type = validator(type);

  /** @type string */
  let color = `bg-${ type }`;

  /** @return void */
  const toggleMenu = () => {
    show = !show;
  };

  /** @return void */
  const closeMenu = () => {
    show = false;
  };

</script>

<nav
    class="navbar navbar-expand-{expand} {!position ? `navbar-${position}` : ''} {type ? `navbar-${type}` : ''} {topClasses}"
    class:navbar-transparent={transparent}
>
  <div class={containerClasses}>
    {#if brandSnippet}
      {@render brandSnippet()}
    {/if}

    {#if toggleButtonSnippet}
      {@render toggleButtonSnippet()}
    {:else}
      {#if hasMenu}
        <button
            class="navbar-toggler collapsed"
            type="button"
            onclick={toggleMenu}
            aria-expanded="false"
            aria-label="Toggle navigation">
          <span class="navbar-toggler-bar navbar-kebab"></span>
          <span class="navbar-toggler-bar navbar-kebab"></span>
          <span class="navbar-toggler-bar navbar-kebab"></span>
        </button>
      {/if}
    {/if}

    <button
        aria-controls="nav-text-collapse"
        aria-expanded="false"
        aria-label="Toggle navigation"
        class="navbar-toggler"
        data-target="#nav-text-collapse"
        onclick={toggleMenu}
        type="button"
    >
      <span class="navbar-toggler-icon"></span>
    </button>

    {#if show}
      <div
          id="nav-text-collapse"
          class="navbar-custom-collapse collapse show {menuClasses}"
          class:show
          visible={show}
          onoutclick={closeMenu}
      >
        {#if children}
          {@render children(closeMenu)}
        {/if}
      </div>
    {/if}
  </div>
</nav>

<script>
  import { GeneralActions } from "$components/directives/general_actions";

  /**
   * @typedef {Object} BaseDropdownProps
   * @property {"div" | "li"} [tag = "div"] - HTML element to use as the dropdown container
   * @property {"button" | "a"} [titleTag = "button"] - HTML element to use for the dropdown trigger
   * @property {string} [title = ""] - Text to display in the dropdown button
   * @property {string} [tagClasses = ""] - Additional CSS classes for the dropdown container
   * @property {"down"} [direction = "down"] - Direction in which the dropdown opens
   * @property {string} [icon = ""] - Icon class to display in the dropdown button
   * @property {string} [titleClasses = ""] - Additional CSS classes for the dropdown button
   * @property {string} [menuClasses = ""] - Additional CSS classes for the dropdown menu
   * @property {boolean} [menuOnRight = false] - Whether to align the dropdown menu to the right
   * @property {boolean} [hasToggle = true] - Whether to display the toggle indicator in the button
   * @property {boolean} [isOpen = true] - Whether the dropdown is initially open
   * @property {boolean} [positionFixed = false] - Whether to use fixed positioning for the dropdown menu
   * @property {boolean} [disabled = false] - Whether the dropdown is disabled
   * @property {boolean} [defaultPrevented = false] - Whether to prevent default click behavior
   * @property {import("svelte").Snippet} [children] - Content to display in the dropdown menu
   * @property {import("svelte").Snippet} [elementSnippet] - Custom dropdown trigger element
   * @property {import("svelte").Snippet} [titleSnippet] - Custom content for the dropdown button
   * @property {(event: Event) => void} [toggledropdown = () => null] - Function to execute when dropdown state changes
   */

  /** @type BaseDropdownProps */
  let {
    /** @type {"div" | "li"} */ tag = "div",
    /** @type {"button" | "a"} */ titleTag = "button",
    /** @type string */ title = "",
    /** @type string */ tagClasses = "",
    /** @type {"down"} */ direction = "down",
    /** @type string */ icon = "",
    /** @type string */ titleClasses = "",
    /** @type string */ menuClasses = "",
    /** @type boolean */ menuOnRight = false,
    /** @type boolean */ hasToggle = true,
    /** @type boolean */ isOpen = true,
    /** @type boolean */ positionFixed = false,
    /** @type boolean */ disabled = false,
    /** @type boolean */ defaultPrevented = false,
    /** @type Snippet */ children,
    /** @type Snippet */ elementSnippet,
    /** @type Snippet */ titleSnippet,
    /** @type {(event: Event) => void} */ toggledropdown = (_) => null,
  } = $props();


  /**
   * Reference to the menu element.
   * @type {HTMLElement}
   */
  let menuEl = $state();

  /**
   * Style representing the position of the menu.
   * @type {string | undefined}
   */
  let menuPositionStyle = $derived.by(() => {
    if (isOpen && positionFixed) {
      return getMenuPositionStyle();
    }
  });

  /**
   * @param {Event} event
   * @return void
   */
  const toggleDropdown = (event) => {
    if (defaultPrevented) {
      event.stopPropagation();
      event.preventDefault();
    }

    if (disabled) return;

    isOpen = !isOpen;
    toggledropdown({ isOpen });
  };

  const handleGlobalClick = (event) => {
    if (menuEl && !menuEl.contains(event.target)) {
      closeDropDown(event);
    }
  };

  /**
   * @param {Event} event
   * @return void
   */
  const handleClickOutside = (event) => {
    closeDropDown(event);
  };

  /**
   * @param {Event} event
   */
  const closeDropDown = (event) => {
    if (!isOpen) return;
    isOpen = false;

    toggledropdown({ isOpen });
  };

  /**
   * Calculates the CSS styles for positioning the dropdown menu.
   * @return string - The CSS styles for positioning the dropdown menu.
   */
  const getMenuPositionStyle = () => {
    const viewPortEl = document.documentElement;
    const menuElRect = menuEl.getBoundingClientRect();
    const menuContentElRect = menuEl.querySelector(".dropdown-menu")?.getBoundingClientRect() ?? new DOMRect();

    const styles = [ `--dropdown-menu-right-fixed-position: ${ viewPortEl.clientWidth - menuElRect.right }px;` ];

    (menuElRect.top + menuContentElRect.height + 10 > viewPortEl.clientHeight)
      ? styles.push(`--dropdown-menu-top-fixed-position: ${ menuElRect.top - menuContentElRect.height - 10 }px;`)
      : styles.push(`--dropdown-menu-top-fixed-position: ${ menuElRect.top + menuElRect.height + 5 }px;`);

    return styles.join(" ");
  };

  /** @return void */
  const updateMenuPosition = () => {
    if (isOpen && positionFixed) {
      // menuPositionStyle = getMenuPositionStyle();
    }
  };
</script>

<svelte:window onresize={updateMenuPosition} onscroll={updateMenuPosition} onclick={handleGlobalClick}/>

{#if tag === 'li' && titleTag === 'a'}
  <li
      bind:this={menuEl}
      use:GeneralActions.outClick
      onoutclick={handleClickOutside}
      class="drop{direction} {tagClasses}"
      class:show={isOpen}
      onclick={toggleDropdown}
  >
    {#if elementSnippet}
      {@render elementSnippet()}
    {:else}
      <a
          class="btn-rotate {titleClasses}"
          class:dropdown-toggle={hasToggle}
          aria-expanded={isOpen}
          data-toggle="dropdown"
      >
        {#if titleSnippet}
          {@render titleSnippet()}
        {:else}
          <i class={icon}></i>
          <span>{title}</span>
        {/if}
      </a>
    {/if}

    <ul
        class="dropdown-menu {menuClasses}"
        class:show={isOpen}
        class:fixed={positionFixed}
        class:dropdown-menu-right={menuOnRight}
        style={menuPositionStyle}
    >
      {@render children?.()}
    </ul>
  </li>

{:else}
  <div
      bind:this={menuEl}
      use:GeneralActions.outClick
      onoutclick={handleClickOutside}
      class="drop{direction} {tagClasses}"
      class:show={isOpen}
      onclick={toggleDropdown}
  >
    {#if elementSnippet}
      {@render elementSnippet()}
    {:else}
      <button
          class="btn-rotate {titleClasses}"
          class:dropdown-toggle={hasToggle}
          aria-expanded={isOpen}
          data-toggle="dropdown"
      >
        {#if titleSnippet}
          {@render titleSnippet()}
        {:else}
          <i class={icon}></i>
          {title}
        {/if}
      </button>
    {/if}

    <ul
        class="dropdown-menu {menuClasses}"
        class:show={isOpen}
        class:dropdown-menu-right={menuOnRight}
        class:fixed={positionFixed}
        style={menuPositionStyle}
    >
      {@render children?.()}
    </ul>
  </div>
{/if}

<style>
  .dropdown {
    cursor: pointer;
    user-select: none;
  }

  .btn-rotate:hover {
    cursor: pointer;
  }
</style>

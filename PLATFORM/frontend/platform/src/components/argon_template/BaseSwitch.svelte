<script>
  /**
   * @typedef {Object} BaseSwitchProps
   * @property {boolean} [checked = false] - Whether the check is selected or not
   * @property {boolean} [disabled = false] - Whether the check is disabled or not
   * @property {string} [onType = ""] - Checkbox type when it's ON
   * @property {string} [classNames = ""] - Additional CSS classes for the switch wrapper
   * @property {string} [labelClasses = ""] - Additional CSS classes for the label
   * @property {string} [label = ""] - Label to show with the checkbox
   * @property {string} [labelOn = ""] - Label to show into the checkbox when it's ON
   * @property {string} [labelOff = ""] - Label to show with the checkbox when it's OFF
   * @property {import("svelte").Snippet} [indicatorSnippet] - Custom content to display next to the switch
   * @property {(event: Event) => void} [onclick] - Function to execute when the switch is clicked
   */

  /** @type BaseSwitchProps */
  let {
    /** @type boolean */ checked = false,
    /** @type boolean */ disabled = false,
    /** @type string */ onType = "",
    /** @type string */ classNames = "",
    /** @type string */ labelClasses = "",
    /** @type string */ label = "",
    /** @type string */ labelOn = "",
    /** @type string */ labelOff = "",
    /** @type Snippet */ indicatorSnippet,
    /** @type {(event: Event) => void} */ onclick = (_) => null,
  } = $props();

  /** @type string */
  let toggleType = $derived(!disabled && checked ? onType : "light");

  /**
   * @param {Event} event
   * @return void
   */
  const onClick = (event) => {
    checked = !checked;
    Object.assign(event, { detail: { checked } });
    onclick(event);
  };

</script>

<div class="{classNames}">
  {#if label}
    <div class="mb-2 {labelClasses}">{label}</div>
  {/if}

  <div class="w-auto d-flex align-content-center">
    <label class="custom-toggle custom-toggle-{toggleType}">
      <input
          bind:checked
          {disabled}
          onclick={onClick}
          type="checkbox"
      >
      <span class="custom-toggle-slider rounded-circle"
            data-label-off={labelOff}
            data-label-on={labelOn}></span>
    </label>

    {@render indicatorSnippet?.()}

  </div>
</div>

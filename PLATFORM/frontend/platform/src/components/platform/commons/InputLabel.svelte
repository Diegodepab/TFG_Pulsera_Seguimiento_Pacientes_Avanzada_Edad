<script>
  /**
   * @typedef {Object} InputLabelProps
   * @property {string} [label=''] - The text label for the form field
   * @property {boolean} [required=false] - Whether the field is required, displays an asterisk when true
   * @property {string} [labelClasses=''] - Additional CSS classes for the label container
   * @property {Snippet} [children] - Content to render inside the label container
   */

  /** @type InputLabelProps */
  let {
    /** @type string */ label = "",
    /** @type boolean */ required = false,
    /** @type string */ labelClasses = "",
    /** @type Snippet */ children,
  } = $props();
</script>

<div class="form-control-label {labelClasses}">
  {label}

  {#if required}
    <span class="required-indicator text-warning-darker font-weight-bold">*</span>
  {/if}

  {@render children?.()}
</div>

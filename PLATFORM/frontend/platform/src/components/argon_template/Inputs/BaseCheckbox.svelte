<script>
  import { v1 as uuidv1 } from "uuid";

  /**
   * @typedef {Object} BaseCheckboxProps
   * @property {string} [classNames = ""]
   * @property {string} [inputClasses = ""]
   * @property {string} [labelClasses = ""]
   * @property {string} [label = ""]
   * @property {string} [type = ""]
   * @property {boolean} [inline = true]
   * @property {boolean} [disabled = false]
   * @property {boolean} [required = false]
   * @property {boolean} [checked = false]
   * @property {import("svelte").Snippet} [labelSnippet]
   * @property {(event: Event) => void} [onchecked = () => null]
   */

  /** @type BaseCheckboxProps */
  let {
    /** @type string */ classNames = "",
    /** @type string */ inputClasses = "",
    /** @type string */ labelClasses = "",
    /** @type string */ label = "",
    /** @type string */ type = "",
    /** @type boolean */ inline = true,
    /** @type boolean */ disabled = false,
    /** @type boolean */ required = false,
    /** @type boolean */ checked = false,
    /** @type Snippet */ labelSnippet,
    /** @type {(event: Event) => void} */ onchecked = (_) => null,
  } = $props();

  let id = uuidv1();

  /** @param {Event} event */
  const onClick = (event) => {
    checked = !checked;
    const customEvent = { ...event, detail: { checked } };
    onchecked(customEvent);
  };

</script>

<div
    class="custom-control custom-checkbox {type ? `custom-checkbox-${type}` : ''} {classNames}"
    class:form-check-inline={inline}
    class:disabled
>
  <input
      bind:checked
      class="custom-control-input {inputClasses}"
      {disabled}
      {id}
      onclick={onClick}
      {required}
      type="checkbox"
  />

  <label class="custom-control-label h-auto {labelClasses}" for={id}>
    {#if labelSnippet}
      {@render labelSnippet()}
    {:else}
      {#if inline}
        <span>&nbsp;</span>
      {/if}

      {label ?? ''}
    {/if}
  </label>
</div>

<script>
  import InputLabel from "$components/platform/commons/InputLabel.svelte";
  import { InputValidators } from "$lib/commons/utils";
  import { t } from "svelte-i18n";

  /**
   * @typedef {(value: string) => string | null} _defaultValidator
   * @typedef {{ value: string, defaultValidator?: _defaultValidator }} _validatorParams
   * @typedef {(params: _validatorParams) => string | null} validatorFn
   */

  /**
   * @typedef {Object} BaseInputProps
   * @property {string | null} [id = null] - The ID of the input element.
   * @property {boolean} [required = false] - Whether the input is required.
   * @property {boolean} [group = false] - Whether the input is a group or not.
   * @property {boolean} [alternative = false] - Whether the input should use the alternative styling.
   * @property {string} [label = ""] - The label for the input.
   * @property {string | null} [error = ""] - The error message for the input.
   * @property {string} [successMessage = ""] - The success message for the input.
   * @property {string} [labelClasses = "form-control-label"] - CSS classes for the label.
   * @property {string} [inputClasses = ""] - CSS classes for the input.
   * @property {string} [inputGroupClasses = ""] - CSS classes for the input group.
   * @property {string} [formGroupClasses = ""] - CSS classes for the second div the component.
   * @property {string} [errorClasses = ""] - CSS classes for the error message.
   * @property {string} [value = ""] - The value of the input.
   * @property {string} [type = ""] - The type of the input.
   * @property {string} [appendIcon = ""] - The icon to prepend to the input.
   * @property {string} [prependIcon = ""] - The icon to prepend to the input.
   * @property {string} [rules = ""] - Validation rules for the input.
   * @property {string} [name = ""] - The name of the input.
   * @property {string} [placeholder = ""] - The placeholder text for the input.
   * @property {string} [autocomplete = ""] - The autocomplete attribute for the input.
   * @property {boolean} [updateValueOnInput = false] - Whether to update the value on input.
   * @property {boolean} [readonly = false] - Whether the input is read-only.
   * @property {Object} [inputAttrs = {}] - Additional attributes for the input.
   * @property {boolean} [showAppend = false] - Whether to show the append slot.
   * @property {boolean} [isAppendSlotText = true] - Whether the append slot is text.
   * @property {boolean} [customRequired = false] - Whether the input has custom required validation.
   * @property {validatorFn | null} [validator = null] - The validation function for the input.
   * @property {import("svelte").Snippet} [children]
   * @property {import("svelte").Snippet} [appendSnippet]
   * @property {import("svelte").Snippet} [prependSnippet]
   * @property {import("svelte").Snippet} [labelSnippet]
   * @property {import("svelte").Snippet} [successSnippet]
   * @property {import("svelte").Snippet} [errorSnippet]
   * @property {import("svelte").Snippet} [infoBlockSnippet]
   * @property {(event: Event) => void} [onchange = () => null]
   * @property {(event: Event) => void} [onfocus = () => null]
   * @property {(event: Event) => void} [onblur = () => null]
   */

  /** @type BaseInputProps */
  let {
    /** @type {string | null} */ id = null,
    /** @type boolean */ required = false,
    /** @type boolean */ group = false,
    /** @type boolean */ alternative = false,
    /** @type string */ label = "",
    /** @type {string | null} */ error = "",
    /** @type string */ successMessage = "",
    /** @type string */ labelClasses = "form-control-label",
    /** @type string */ inputClasses = "",
    /** @type string */ inputGroupClasses = "",
    /** @type string */ formGroupClasses = "",
    /** @type string */ errorClasses = "",
    /** @type string */ value = $bindable(""),
    /** @type string */ type = "",
    /** @type string */ appendIcon = "",
    /** @type string */ prependIcon = "",
    /** @type string */ rules = "",
    /** @type string */ name = "",
    /** @type string */ placeholder = "",
    /** @type string */ autocomplete = "",
    /** @type boolean */ updateValueOnInput = false,
    /** @type boolean */ readonly = false,
    /** @type Object */ inputAttrs = {},
    /** @type boolean */ showAppend = true,
    /** @type boolean */ isAppendSlotText = true,
    /** @type boolean */ customRequired = false,
    /** @type {validatorFn | null} */ validator = null,
    /** @type Snippet */ children,
    /** @type Snippet */ appendSnippet,
    /** @type Snippet */ prependSnippet,
    /** @type Snippet */ labelSnippet,
    /** @type Snippet */ successSnippet,
    /** @type Snippet */ errorSnippet,
    /** @type Snippet */ infoBlockSnippet,
    /** @type {(event: Event) => void} */ onchange = () => null,
    /** @type {(event: Event) => void} */ onfocus = () => null,
    /** @type {(event: Event) => void} */ onblur = () => null,
  } = $props();

  /** @type boolean */
  let focused = $state(false);

  /**
   * Default validator function for validating a string value.
   * @param {string} value - The value to validate.
   * @return {string | null} The validated string or null if validation fails.
   */
  const defaultValidator = (value) => {
    return InputValidators.validateRequired(value, $t, { values: { field: name } });
  };

  if (customRequired) {
    required = false;
    validator ??= ({ value, defaultValidator }) => defaultValidator(value);
  }

  /** Defines event listeners. */
  const listeners = () => ({
    input: updateValue,
    focus: onFocus,
    blur: onBlur,
  });

  /** Gives snippet data attributes. */
  const snippetData = () => ({
    focused: focused,
    error: error,
    listeners,
  });

  /**
   * @param {Event} event
   * @return void
   */
  const updateValue = (event) => {
    if (event.type === "input" && !updateValueOnInput) return;
    validate();
    onchange(event);
  };

  /**
   * @param {Event} event
   * @return void
   */
  const onFocus = (event) => {
    focused = true;
    onfocus(event);
  };

  /** @param {Event} event */
  const onBlur = (event) => {
    // NOTE: normally the current 'value' is the same on event.target.value. TEST THIS DEEPLY
    focused = false;
    validate();
    onblur(event);
  };

  /**
   * Validates the value based on the defined validation rules.
   * @return {boolean} - `true` if the validation passes, `false` otherwise.
   */
  export const validate = () => {
    if (!required && !customRequired) return true;

    error = null;
    if (value === "" && required) error = $t("common.form.field.required", { values: { field: name } });
    if (validator) error = validator({ value, defaultValidator }) ?? error;

    return error == null;
  };
</script>

<div {name} {rules}>
  <div class="form-group {formGroupClasses}">
    {#if labelSnippet}
      {@render labelSnippet()}
    {:else}
      {#if label}
        <InputLabel {label} {labelClasses} required={customRequired}/>
      {/if}
    {/if}

    <div
        class="{inputGroupClasses}"
        class:focused={focused}
        class:has-label={!!label}
        class:input-group={!!appendSnippet || !!prependSnippet || !!appendIcon || !!prependIcon || !!group}
        class:input-group-alternative={alternative}
    >
      {#if prependSnippet}
        <div class="input-group-prepend">
          <span class="input-group-text">
            {@render prependSnippet()}
          </span>
        </div>
      {/if}

      {#if prependIcon}
        <div class="input-group-prepend">
          <span class="input-group-text">
            {#if prependSnippet}
              {@render prependSnippet()}
            {:else}
              <i class={prependIcon}></i>
            {/if}
          </span>
        </div>
      {/if}

      {#if children}
        {@render children()}
      {:else}
        <input
            {...inputAttrs}
            {autocomplete}
            class="form-control {inputClasses}"
            {id}
            onblur={onBlur}
            onchange={updateValue}
            onfocus={onFocus}
            oninput={updateValue}
            {placeholder}
            {readonly}
            {required}
            {type}
            bind:value
        />
      {/if}

      {#if showAppend}
        {#if appendIcon}
          <div class="input-group-append">
            <span class:input-group-text={isAppendSlotText}>
              {#if appendSnippet}
                {@render appendSnippet()}
              {:else}
                <i class={appendIcon}></i>
              {/if}
            </span>
          </div>

        {:else if appendSnippet}
          <div class="input-group-append">
            <span class:input-group-text={isAppendSlotText}>{@render appendSnippet()}</span>
          </div>
        {/if}
      {/if}
    </div>

    {#if successSnippet}
      {@render successSnippet()}
    {:else}
      <div class="valid-feedback">
        {#if error === '' && successMessage !== ''}{error}{/if}
      </div>
    {/if}

    {#if errorSnippet}
      {@render errorSnippet()}
    {:else}
      <div class:invalid-feedback={error} class:d-block={error} class="{errorClasses}">
        {#if error}{error}{/if}
      </div>
    {/if}

    {#if infoBlockSnippet}
      {@render infoBlockSnippet()}
    {/if}
  </div>
</div>

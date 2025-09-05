<script>
  import InputLabel from "$components/platform/commons/InputLabel.svelte";
  import { InputValidators } from "$lib/commons/utils";

  import { t } from "svelte-i18n";

  // The svelte-select package does not update for svelte 5 - https://github.com/rob-balfre/svelte-select
import Select from 'svelte-select';
  // import Select from "$components/platform/commons/CustomSelect.svelte";

  /**
   * @typedef {(value: unknown) => string | null} _defaultValidator
   * @typedef {{ value: unknown, defaultValidator?: _defaultValidator }} _validatorParams
   * @typedef {(params: _validatorParams) => string | null} validatorFn
   */

  /**
   * Normalizes events emitted by the Select component.
   * @callback TransformEventFn
   * @param {Event|any} event - The original event to be transformed.
   * @returns {object} The normalized event.
   */

  /**
   * @typedef {Object} BaseSelectProps
   * @property {string} [selectClasses=""] - Additional CSS classes for the Select component.
   * @property {string} [name=""] - Unique name for the select field.
   * @property {string} [placeholder=""] - Placeholder text when no selection is made.
   * @property {boolean} [placeholderAlwaysShow=false] - Whether to always show the placeholder even when a selection is made.
   * @property {string} [label=""] - Label for the select field.
   * @property {string} [labelClasses=""] - Additional CSS classes for the label.
   * @property {string|null} [error=""] - Validation error message.
   * @property {string} [errorClasses=""] - Additional CSS classes for the error message.
   * @property {boolean} [multiple=false] - Allows multiple selections when true.
   * @property {boolean} [clearable=false] - Shows a button to clear the selection when true.
   * @property {boolean} [searchable=true] - Allows searching options when true.
   * @property {boolean} [disabled=false] - Disables the select field when true.
   * @property {boolean} [showChevron=true] - Shows a chevron icon when true.
   * @property {string} [chevronIcon="fas fa-chevron-down"] - Icon class for the chevron.
   * @property {boolean} [required=false] - Marks the field as required for HTML5 validation.
   * @property {boolean} [customRequired=false] - Activates custom validation instead of standard HTML5.
   * @property {unknown} [value=null] - Currently selected value.
   * @property {string} [itemId="id"] - Name of the ID property in the item objects.
   * @property {string} [itemLabel="label"] - Name of the label property in the item objects.
   * @property {unknown[]|null} [items=null] - Array of items to select from.
   * @property {boolean} [loading=false] - Indicates if the component is loading data.
   * @property {boolean} [focused=false] - Indicates if the component has focus.
   * @property {string} [filterText=""] - Current search text.
   * @property {string} [noOptionsMessage=$t('component.select.no-options')] - Message when no options are available.
   * @property {boolean} [hideEmptyState=false] - Hides the empty state when true.
   * @property {string} [description=""] - Description text for the field.
   * @property {string} [descriptionClasses=""] - Additional CSS classes for the description text.
   * @property {Snippet} [appendLabelSnippet] - Snippet to append content after the label.
   * @property {Snippet} [appendSnippet] - Snippet to append content after the field.
   * @property {Snippet} [prependSnippet] - Snippet to prepend content before the field.
   * @property {Snippet} [itemSnippet] - Custom snippet to render each list item.
   * @property {Snippet} [chevronIconSnippet] - Custom snippet for the chevron icon.
   * @property {Snippet} [selectionSnippet] - Custom snippet to render the current selection.
   * @property {Snippet} [emptySnippet] - Custom snippet for when there are no options.
   * @property {((filterText: string) => unknown[])|undefined} [loadOptions=undefined] - Function to dynamically load options based on search text.
   * @property {validatorFn | null} [validator=null] - Custom validation function.
   * @property {(event: Event) => void} [onchange] - Callback for when the selection changes.
   * @property {(event: Event) => void} [onclear] - Callback for when the selection is cleared.
   * @property {(event: Event) => void} [onfocus] - Callback for when the component loses focus.
   * @property {(event: Event) => void} [onerror] - Callback for when an error occurs.
   * @property {TransformEventFn} [transformEvent = normalizeEvent] - Function to transform events before passing them to callbacks.
   */

  /** @type BaseSelectProps */
  let {
    /** @type string */ selectClasses = "",
    /** @type string */ name = "",
    /** @type string */ placeholder = "",
    /** @type boolean */ placeholderAlwaysShow = false,
    /** @type string */ label = "",
    /** @type string */ labelClasses = "",
    /** @type {string|null} */ error = "",
    /** @type string */ errorClasses = "",
    /** @type boolean */ multiple = false,
    /** @type boolean */ clearable = false,
    /** @type boolean */ searchable = true,
    /** @type boolean */ disabled = false,
    /** @type boolean */ showChevron = true,
    /** @type string */ chevronIcon = "fas fa-chevron-down",
    /** @type boolean */ required = false,
    /** @type boolean */ customRequired = false,
    /** @type {unknown} */ value = null,
    /** @type string */ itemId = "id",
    /** @type string */ itemLabel = "label",
    /** @type {unknown[]|null} */ items = null,
    /** @type boolean */ loading = false,
    /** @type boolean */ focused = false,
    /** @type string */ filterText = "",
    /** @type string */ noOptionsMessage = $t("component.select.no-options"),
    /** @type boolean */ hideEmptyState = false,
    /** @type string */ description = "",
    /** @type string */ descriptionClasses = "",
    /** @type Snippet */ appendSnippet,
    /** @type Snippet */ appendLabelSnippet,
    /** @type Snippet */ prependSnippet,
    /** @type Snippet */ itemSnippet,
    /** @type Snippet */ emptySnippet,
    /** @type Snippet */ chevronIconSnippet,
    /** @type Snippet */ selectionSnippet,
    /** @type {((filterText: string) => unknown[])|undefined} */ loadOptions = undefined,
    /** @type {validatorFn | null} */ validator,
    /** @type {(event: Event) => void} */ onchange,
    /** @type {(event: Event) => void} */ onfocus,
    /** @type {(event: Event) => void} */ onclear,
    /** @type {(event: Event) => null} */ onerror,
  } = $props();


  /**
   * Default validator function for validating the current selection.
   * @param {unknown} value - The value to validate.
   * @return {string | null} The validated string or null if validation fails.
   */
  const defaultValidator = (value) => {
    return InputValidators.validateRequired(value, $t, { values: { field: name } });
  };

  $effect(() => {
    if (customRequired) {
      required = false;
      validator ??= ({ value, defaultValidator }) => defaultValidator(value);
    } else {
      error = null;
    }
  });

  /**
   * Validate current selection
   * @return boolean
   */
  export const validate = () => {
    if (!required && !customRequired) return true;

    error = null;
    if (value === "" && required) error = $t("common.form.field.required", { values: { field: name } });
    if (validator) error = validator({ value, defaultValidator }) ?? error;

    return error == null;
  };

  // NOTE: handleClear is required because in other sites it doesn't clean well (e.g. IncrementSelectList comp)
  /** @type Select */
  let _selectEl;

  /** @returns void */
  export const handleClear = () => _selectEl.handleClear();

  /**
   * @param {Event} event
   */
  const onChange = (event) => {
    validate();
    // const normalized = transformEvent(event);
    onchange?.(event);
  };

  /**
   * @param {Event} event
   * @return void
   */
  const onClear = (event) => {
    validate();
    onclear?.(event);
  };

  /**
   * @param {Event} event
   * @return void
   */
  const onFocusOut = (event) => {
    // NOTE: This event is fired before onSelect is done, so validate throw error before validate with value.
    //  This case returns a relatedTarget with the list-item value selected from Select, so we return in that case.
    //  TEST THIS DEEPLY
    event.preventDefault();
    event.stopPropagation();

    if (event.relatedTarget != null) return;
    validate();
    onfocus?.(event);
  };
</script>

<div {name}>
  {#if label !== ''}
    <InputLabel {label} labelClasses="mb-2 {labelClasses}" required={required || customRequired}>
      {#if appendLabelSnippet}
        {@render appendLabelSnippet()}
      {/if}
    </InputLabel>
  {/if}
  <div class={appendSnippet ? 'd-flex justify-content-start' : ''}>
    {#if prependSnippet}
      {@render prependSnippet()}
    {/if}
    <div class="w-100">
      <div onfocusout={onFocusOut}>
        <Select
            bind:filterText={filterText}
            bind:focused
            bind:loading
            bind:this={_selectEl}
            bind:value={value}
            class={selectClasses}
            {clearable}
            {disabled}
            hideEmptyState={loading || hideEmptyState}
            {itemId}
            {items}
            label={itemLabel}
            loadOptions={disabled ? null : loadOptions}
            {multiple}
            onchange={onChange}
            onclear={onClear}
            onerror={onerror}
            onfocusout={onFocusOut}
            {placeholder}
            {placeholderAlwaysShow}
            {searchable}
            showChevron={showChevron && !disabled && !loading && !(value && clearable)}
        >
          {#snippet chevronIconSnippet()}
            <div class="{chevronIcon ?? ''}"></div>
          {/snippet}

          {#snippet selectionSnippet(selection)}
            <span>
              {#if selectionSnippet}
                {@render selectionSnippet(selection)}
              {:else}
                {value[itemLabel] ?? selection?.label}
              {/if}
            </span>
          {/snippet}

          {#snippet itemSnippet(item)}
            <span>
              {#if itemSnippet}
                {@render itemSnippet(item)}
              {:else}
                {item[itemLabel]}
              {/if}
            </span>
          {/snippet}

          {#snippet emptySnippet()}
            <div class="empty">{noOptionsMessage ?? ''}</div>
          {/snippet}
        </Select>
      </div>
    </div>

    {#if appendSnippet}{@render appendSnippet()}{/if}
  </div>

  {#if error}
    <div class="invalid-feedback d-block {errorClasses}">{error}</div>
  {/if}

  {#if description}
    <div class="mt-1 text-xs wrap-overflow {descriptionClasses}">{description}</div>
  {/if}
</div>

<style>
  .empty {
    font-size: 14px !important;
    text-align: center;
    padding: 20px 0;
    color: #78848f;
  }
</style>
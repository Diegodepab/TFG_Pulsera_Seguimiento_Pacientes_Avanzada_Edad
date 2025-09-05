<svelte:options/>
<script>
  import BaseInput from "$components/argon_template/Inputs/BaseInput.svelte";
  import { InputValidators } from "$lib/commons/utils";
  import moment from "moment";
  import { t } from "svelte-i18n";
  import { v1 as uuidv1 } from "uuid";

  /**
   * @typedef {"date" | "datetime-local"} DateInputType
   * @typedef {(value: string) => string | null} _defaultValidator
   * @typedef {{ value: string, defaultValidator?: _defaultValidator }} _validatorParams
   * @typedef {(params: _validatorParams) => string | null} validatorFn
   */

  /**
   * @typedef {Object} BaseDateInputProps
   * @property {DateInputType} [type='date'] - The type of date input (date only or date with time)
   * @property {string} [label=''] - Label text for the input field
   * @property {string} [name=''] - Name attribute for the input field
   * @property {string} [placeholder=''] - Placeholder text for the input
   * @property {string} [inputGroupClasses=''] - Additional CSS classes for the input group container
   * @property {string} [formGroupClasses = ""] - CSS classes for the second div the component.
   * @property {boolean} [setTodayValue=false] - Whether to set the current date as the default value
   * @property {moment.Moment | null} [value=null] - The date value
   * @property {string} [error=''] - Error message to display
   * @property {string} [errorClasses=''] - Additional CSS classes for the error message
   * @property {boolean} [readonly=false] - Whether the input is read-only
   * @property {boolean} [required=false] - Whether the field is required
   * @property {boolean} [customRequired=false] - Enable custom required validation without HTML5 validation
   * @property {string} [id=uuidv1()] - Unique ID for the input element. Default to uuidv1
   * @property {boolean} [updateValueOnInput=true] - Whether to update the value as the user types
   * @property {validatorFn} [validator] - Custom validation function
   * @property {(value: moment.Moment) => void} [onchange] - Callback when value changes, receives `moment.Moment` as parameter
   * @property {(event: Event) => void} [onblur] - Callback when input loses focus
   */

  /** @type BaseDateInputProps */
  let {
    /** @type DateInputType */ type = "date",
    /** @type string */ label = "",
    /** @type string */ name = "",
    /** @type string */ placeholder = "",
    /** @type string */ inputGroupClasses = "",
    /** @type string */ formGroupClasses = "",
    /** @type boolean */ setTodayValue = false,
    /** @type {moment.Moment | null} */ value = $bindable(setTodayValue ? moment() : null),
    /** @type string */ error = $bindable(""),
    /** @type string */ errorClasses = "",
    /** @type boolean */ readonly = false,
    /** @type boolean */ required = $bindable(false),
    /** @type boolean */ customRequired = false,
    /** @type string */ id = uuidv1(),
    /** @type boolean */ updateValueOnInput = true,
    /** @type validatorFn */ validator = $bindable(null),
    /** @type {(value: moment.Moment) => void} */ onchange = () => null,
    /** @type {(event: Event) => void} */ onblur = () => null,
  } = $props();
  /**
   * Format current value to string (if defined)
   * @param {moment.Moment} newValue
   * @param {DateInputType} type
   * @return {string | undefined}
   */
  const _formatValue = (newValue, type) => {
    if (!newValue) return "";
    if (type === "date") return newValue.format("YYYY-MM-DD");
    return newValue.format("YYYY-MM-DDTHH:mm");
  };


  /** @type BaseInput */
  let _baseInput = $state();

  // TODO. test both solutions in the future to use the best option
  // /** @type string */
  // let value_Derivado = $derived(_formatValue(value, type))
  //
  // /** @type string */
  // let _value = $state(value_Derivado);

  /** @type string */
  let _value = $state(_formatValue(value, type));

  $effect(() => {
    _value = _formatValue(value, type);
  });

  /**
   * Default validator function for validating a string value.
   * @param {string} value - The value to validate.
   * @return {string | null} The validated string or null if validation fails.
   */
  const defaultValidator = (value) => {
    if (customRequired) {
      const notEmpty = InputValidators.validateRequired(value, $t, { values: { field: name } });
      if (notEmpty) return notEmpty;
    }

    return InputValidators.validateDate(value, $t, { tArgs: { field: name } });
  };

  if (customRequired) {
    required = false;
    validator ??= ({ value, defaultValidator }) => defaultValidator(value);
  }

  /** Handles change events from the base input */
  const onChange = (event) => {
    _value = event.target.value;
    value = _value ? moment(_value).startOf("day") : null;
    onchange(value);
  };

  /**
   * Validates the input
   * @return boolean -  Whether the input value is valid
   */
  export const validate = () => _baseInput.validate();

</script>
<BaseInput
    bind:error
    bind:this={_baseInput}
    {customRequired}
    {errorClasses}
    {id}
    {inputGroupClasses}
    {formGroupClasses}
    {label}
    {name}
    onblur={onblur}
    onchange={onChange}
    {placeholder}
    {readonly}
    {required}
    {type}
    {updateValueOnInput}
    {validator}
    value={_value}
/>

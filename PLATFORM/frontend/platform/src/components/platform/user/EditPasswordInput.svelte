<script>
  import BaseInput from "$components/argon_template/Inputs/BaseInput.svelte";
  import { t } from "svelte-i18n";


  /**
   * @typedef {Object} EditPasswordInputProps
   * @property {string} [password]
   * @property {string} [repeatPassword]
   * @property {boolean} [showRepeatPasswordField]
   */

  /** @type EditPasswordInputProps */
  let {
    password = $bindable(""),
    repeatPassword = $bindable(""),
    showRepeatPasswordField = false,
  } = $props();

  /** @type boolean */
  let isShowingPassword = $state(false);

  /** @type boolean */
  let isShowingRepeatPassword = $state(false);

  /** @type BaseInput */
  let _newPasswordInput = $state();

  /** @type string */
  const _newPwdField = $t("entity.user.password");

  /** @type BaseInput */
  let _repeatedPasswordInput = $state();

  /** @type string */
  const _repeatedPwdField = $t("route.edit-password.form.label.repeat");

  /** @type {string|null} */
  let notMatchError = $state();

  /** @return boolean */
  const onShowPassword = () => isShowingPassword = !isShowingPassword;

  /** @return boolean */
  const onShowRepeatPassword = () => isShowingRepeatPassword = !isShowingRepeatPassword;

  /** @return boolean */
  const validatePasswordsMatch = () => {
    const inputs = [ _newPasswordInput ];
    if (showRepeatPasswordField) inputs.push(_repeatedPasswordInput);

    const isValid = !inputs.map((input) => input.validate()).includes(false);
    notMatchError = password != repeatPassword ? $t("route.my-profile-edit.password.form.validation.not-match") : null;
    return !notMatchError && isValid;
  };

  /**
   * Handles the blur event for the new passwords input.
   * @type EventCallback
   */
  const onBlurNewPasswords = (event) => {
    validatePasswordsMatch();
  };

  /** @return boolean */
  export const validateForm = () => {
    const inputs = [ _newPasswordInput ];
    if (showRepeatPasswordField) inputs.push(_repeatedPasswordInput);

    return !inputs.map((el) => el.validate()).includes(false) || validatePasswordsMatch();
  };

</script>

<BaseInput
    alternative
    bind:this={_newPasswordInput}
    bind:value={password}
    class="mb-3"
    customRequired
    id="password"
    label={_newPwdField}
    name={_newPwdField}
    onblur={onBlurNewPasswords}
    placeholder={_newPwdField}
    prependIcon="fas fa-unlock-alt"
    type={isShowingPassword ? 'text' : 'password'}
    updateValueOnInput
>
  {#snippet append()}
    <span>
            <i class="fas {isShowingPassword ? 'fa-eye-slash' : 'fa-eye'} pointer" onclick={onShowPassword}></i>
        </span>
  {/snippet}
</BaseInput>

{#if showRepeatPasswordField}
  <BaseInput
      bind:this={_repeatedPasswordInput}
      class="mb-3"
      type={isShowingRepeatPassword ? 'text' : 'password'}
      label={_repeatedPwdField}
      name={_repeatedPwdField}
      customRequired
      placeholder={_repeatedPwdField}
      prependIcon="fas fa-unlock-alt"
      updateValueOnInput
      bind:value={repeatPassword}
      alternative
      error={notMatchError}
      validator={({ value, defaultValidator}) => {
            if (notMatchError != null) return notMatchError;
            return defaultValidator(value);
        }}
      onblur={onBlurNewPasswords}
  >
    {#snippet append()}
            <span>
        <i class="fas {isShowingRepeatPassword ? 'fa-eye-slash' : 'fa-eye'} pointer"
           onclick={onShowRepeatPassword}>
        </i>
      </span>
    {/snippet}
  </BaseInput>
{/if}

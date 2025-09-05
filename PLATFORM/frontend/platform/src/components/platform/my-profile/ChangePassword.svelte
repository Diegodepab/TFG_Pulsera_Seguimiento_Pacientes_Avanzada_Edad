<script>
  import { page } from "$app/state";
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import BaseInput from "$components/argon_template/Inputs/BaseInput.svelte";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Global } from "$lib/commons/global";
  import { SessionManager } from "$lib/commons/session_manager";
  import { UserController } from "$lib/controllers/user_controller";
  import { Exception } from "$lib/exceptions/exception";
  import { ExceptionUiCtxCodes } from "$lib/exceptions/exception_codes";
  import { PasswordChange } from "$lib/models/password_change";
  import { t } from "svelte-i18n";
  import { getNotificationsContext } from "svelte-notifications";
  import { fade } from "svelte/transition";

  /** @type UserController */
  const userController = new UserController();
  if (!Global.notificationContext) Global.notificationContext = getNotificationsContext();

  /** @type string */
  let currentPassword = $state("");
  /** @type string */
  let newPassword = $state("");
  /** @type string */
  let repeatedPassword = $state("");

  /** @type number */
  let userId = $derived(parseInt(page.params.id) || SessionManager.userId());


  /** @type boolean */
  let isShowingCurrentPassword = $state(false);
  /** @type boolean */
  let isShowingNewPassword = $state(false);
  /** @type boolean */
  let isShowingRepeatPassword = $state(false);

  /** @type string */
  let newPasswordError = "";
  /** @type string */
  let repeatPasswordError = "";

  /** @type BaseInput */
  let _currentPasswordInput = $state();
  /** @type string */
  const _currentPwdField = $t("route.my-profile-edit.password.form.label.current");

  /** @type BaseInput */
  let _newPasswordInput = $state();
  /** @type string */
  const _newPwdField = $t("route.my-profile-edit.password.form.label.new");

  /** @type BaseInput */
  let _repeatedPasswordInput = $state();
  /** @type string */
  const _repeatedPwdField = $t("route.my-profile-edit.password.form.label.repeated");
  /** @type {string | null} */
  let notMatchError = $state();

  /**
   * Toggles the visibility of the current password.
   */
  const onShowCurrentPassword = () => isShowingCurrentPassword = !isShowingCurrentPassword;

  /**
   * Toggles the visibility of the new password.
   */
  const onShowNewPassword = () => isShowingNewPassword = !isShowingNewPassword;

  /**
   * Toggles the visibility of the repeated password.
   */
  const onShowRepeatPassword = () => isShowingRepeatPassword = !isShowingRepeatPassword;

  /**
   * Clears the password fields and resets error messages.
   * @param {boolean} [closeMenu] - Whether to close the menu after clearing.
   */
  const clearPasswords = (closeMenu) => {
    currentPassword = "";
    newPassword = "";
    repeatedPassword = "";
    repeatPasswordError = "";
    newPasswordError = "";

    if (closeMenu) isOpen = false;
  };

  /**
   * Changes the user's password.
   * @throws {Exception} Throws an exception if the old password does not match.
   */
  const changePassword = async () => {
    if (!validateForm()) {
      CommonNotifications.validationError();
      return;
    }

    try {
      /** @type {PasswordChange} */
      let passwordChange = new PasswordChange(currentPassword, newPassword);
      const result = await userController.changePassword(userId, passwordChange);

      if (result) {
        CommonNotifications.genericSuccess($t("notification.entity.password.success.edit"));
        clearPasswords();
      }
    } catch (e) {
      if (!(e instanceof Exception)) throw e;
      e.uiCtx = { code: ExceptionUiCtxCodes.oldPasswordNotMatched };
      throw e;
    }
  };

  /** @type boolean */
  let isOpen = $state(false);

  /**
   * Validates that the new password and repeated password match.
   * @returns boolean - True if passwords match and are valid, false otherwise.
   */
  const validatePasswordsMatch = () => {
    const isValid = ![ _newPasswordInput, _repeatedPasswordInput ].map((input) => input.validate()).includes(false);

    notMatchError = null;
    if (newPassword != repeatedPassword) {
      notMatchError = $t("route.my-profile-edit.password.form.validation.not-match");
    }

    return !notMatchError && isValid;
  };

  /**
   * Handles the blur event for new password fields.
   * @param {CustomEvent} event - The blur event.
   */
  const onBlurNewPasswords = (event) => {
    validatePasswordsMatch();
  };

  /**
   * Validates the entire form for password change.
   * @returns boolean - True if the form is valid, false otherwise.
   */
  const validateForm = () => {
    const fieldsValid = ![
      _currentPasswordInput,
      _newPasswordInput,
      _repeatedPasswordInput,
    ].map((el) => el.validate()).includes(false);

    const passwordsMatch = validatePasswordsMatch();

    return fieldsValid && passwordsMatch;
  };
</script>

<div class="col-12 ml-1">
  <div class="d-flex align-items-center password-menu" onclick={() => isOpen = !isOpen}>
    <i class="fas fa-chevron-{isOpen ? 'up' : 'down'}"></i>
    <div class="ml-4">
      <div class="modal-title mt-0">{$t('route.my-profile-edit.password.title')}</div>
      <div class="section-subtitle">{$t('route.my-profile-edit.password.content')}</div>
    </div>
  </div>
  {#if isOpen}
    <div transition:fade={{ y: -200, duration: 200 }}>
      <form onsubmit={changePassword}>
        <div class="col-12 col-lg-6 ml-2">
          <BaseInput
              id="currentPwd"
              bind:this={_currentPasswordInput}
              type={isShowingCurrentPassword ? 'text' : 'password'}
              name={_currentPwdField}
              label={_currentPwdField}
              placeholder={_currentPwdField}
              prependIcon="fas fa-{isShowingCurrentPassword ? 'unlock' : 'lock'}-alt"
              bind:value={currentPassword}
              customRequired
              alternative
          >
            {#snippet appendSnippet()}
                <span>
                <i class="fas {isShowingCurrentPassword ? 'fa-eye-slash' : 'fa-eye'} pointer"
                   onclick={onShowCurrentPassword}>
                </i>
              </span>
            {/snippet}
          </BaseInput>

          <BaseInput
              id="newPwd"
              bind:this={_newPasswordInput}
              type={isShowingNewPassword ? 'text' : 'password'}
              label={_newPwdField}
              name={_newPwdField}
              placeholder={_newPwdField}
              prependIcon="fas fa-{isShowingNewPassword ? 'unlock' : 'lock'}-alt"
              bind:value={newPassword}
              customRequired
              alternative
              updateValueOnInput
              onblur={onBlurNewPasswords}
          >
            {#snippet appendSnippet()}
              <span>
                <i
                    class="fas {isShowingNewPassword ? 'fa-eye-slash' : 'fa-eye'} pointer"
                    onclick={onShowNewPassword}
                ></i>
              </span>
            {/snippet}
          </BaseInput>

          <BaseInput
              id="repeatPwd"
              bind:this={_repeatedPasswordInput}
              type={isShowingRepeatPassword ? 'text' : 'password'}
              label={_repeatedPwdField}
              name={_repeatedPwdField}
              placeholder={_repeatedPwdField}
              prependIcon="fas fa-{isShowingRepeatPassword ? 'unlock' : 'lock'}-alt"
              bind:value={repeatedPassword}
              customRequired
              alternative
              updateValueOnInput
              error={notMatchError}
              validator={({ value, defaultValidator }) => {
                if (notMatchError != null) return notMatchError;
                return defaultValidator(value);
              }}
              onblur={onBlurNewPasswords}
          >
            {#snippet appendSnippet()}
              <span>
                <i class="fas {isShowingRepeatPassword ? 'fa-eye-slash' : 'fa-eye'} pointer"
                   onclick={onShowRepeatPassword}></i>
              </span>
            {/snippet}
          </BaseInput>

          <div class="d-flex mt-4 justify-content-end">
            <BaseButton type="light" onclick={() => clearPasswords(true)}>
              <span class="btn-inner--text">{$t('common.button.cancel')}</span>
            </BaseButton>

            <BaseButton type="success" nativeType="submit">
              <span class="btn-inner--text">{$t('route.my-profile-edit.password.form.button.change-password')}</span>
            </BaseButton>
          </div>
        </div>

      </form>
    </div>
  {/if}
</div>

<style>
  .password-menu {
    cursor: pointer;
  }

  .section-subtitle {
    font-size: 0.9rem;
  }
</style>
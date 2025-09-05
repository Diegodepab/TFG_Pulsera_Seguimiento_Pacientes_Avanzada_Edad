<script>
  import { goto } from "$app/navigation";
  import { page } from "$app/state";

  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import Card from "$components/argon_template/Cards/Card.svelte";
  import EditPasswordInput from "$components/platform/user/EditPasswordInput.svelte";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Global } from "$lib/commons/global";
  import { Routes } from "$lib/commons/routes";
  import { OauthController } from "$lib/controllers/oauth_controller";
  import { PasswordController } from "$lib/controllers/password_controller";
  import { Exception } from "$lib/exceptions/exception";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";
  import { getNotificationsContext } from "svelte-notifications";

  if (!Global.notificationContext) Global.notificationContext = getNotificationsContext();

  /** @type PasswordController */
  const passwordCtl = new PasswordController();

  /** @type OauthController */
  const oauthCtl = new OauthController();

  /** @type string */
  const token = page.url.searchParams.get("token")?.trim();

  /** @type boolean */
  let validToken = $state(false);

  /** @type string */
  let password = $state();

  /** @type string */
  let repeatPassword = $state();

  /** @type EditPasswordInput */
  let editPasswordInput = $state();

  /** @type OnMount */
  onMount(async () => {
    if (token?.length > 0) {
      try {
        await oauthCtl.checkToken(token);
        validToken = true;
      } catch (e) {
        validToken = false;
      }
    }
  });

  /**
   * @param {Event} event - form event
   * @returns Promise<void>
   * @throws {Exception} Throws an error if password can´t be saved.
   */
  const confirmPassword = async (event) => {
    event.preventDefault();

    if (!editPasswordInput.validateForm()) {
      if (password != repeatPassword) return;

      CommonNotifications.validationError();
      return;
    }

    try {
      await passwordCtl.savePassword(token, password);
      CommonNotifications.genericSuccess($t("notification.entity.password.success.edit"));
      await goto(/** @type string */ Routes.LOGIN, { replaceState: true });
    } catch (e) {
      if (!(e instanceof Exception) || e.code !== 409) throw e;
      validToken = false;
    }
  };
</script>

<svelte:head>
  <title>{$t('route.edit-password.title')}</title>
</svelte:head>

<div>
  <div class="header py-7 py-lg-8 pt-lg-9">
    <div class="separator separator-bottom separator-skew zindex-100">
      <svg
          preserveAspectRatio="none"
          viewBox="0 0 2560 100"
          x="0"
          xmlns="http://www.w3.org/2000/svg"
          y="0">
      </svg>
    </div>
  </div>

  <div class="mt--8 pb-5 container">
    <div class="row justify-content-center">
      <div class="col-md-7 col-lg-5">
        <Card
            bodyClasses="px-lg-5 py-lg-5"
            className="bg-secondary border-0 mb-0 card"
            headerClasses="bg-transparent pb-5"
            noBody
        >
          <div class="card-body px-lg-5 py-lg-5">
            <div class="text-center logo-title mb-4">
              <img alt="" src="/images/logo/logo-VRExp-dark.svg" width="300"/>
            </div>

            {#if validToken}
              <div class="text-center mb-4 text-title">{$t('route.edit-password.information')}</div>

              <form class="mt-4" method="get" onsubmit={confirmPassword}>
                <EditPasswordInput
                    bind:this={editPasswordInput}
                    bind:password
                    bind:repeatPassword
                    isRequired
                    showRepeatPasswordField
                />

                <div class="text-center">
                  <BaseButton nativeType="submit" type="primary">
                    <span class="btn-inner--text">{$t('route.edit-password.form.button.confirm')}</span>
                  </BaseButton>
                </div>
              </form>
            {:else}
              <p class="text-center text-gray text-sm">{$t('route.edit-password.invalid-token')}</p>

              <div class="text-center">
                <BaseButton type="primary" onclick={() => goto('/password/reset', { replaceState: true })}>
                  <span class="btn-inner--text">{$t('route.edit-password.button.resend')}</span>
                </BaseButton>
              </div>

              <p class="text-center text-sm mt-3">
                <a class="text-primary" onclick={(_) => goto(/** @type string */ Routes.LOGIN, { replaceState: true })}>
                  {$t('route.edit-password.button.back-login')}
                </a>
              </p>
            {/if}
          </div>
        </Card>
      </div>
    </div>
  </div>
</div>



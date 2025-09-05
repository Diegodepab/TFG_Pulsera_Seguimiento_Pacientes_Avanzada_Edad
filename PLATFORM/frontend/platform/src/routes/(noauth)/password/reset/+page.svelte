<script>
  import { goto } from "$app/navigation";
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import Card from "$components/argon_template/Cards/Card.svelte";
  import BaseInput from "$components/argon_template/Inputs/BaseInput.svelte";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Routes } from "$lib/commons/routes";
  import { InputValidators } from "$lib/commons/utils";
  import { PasswordController } from "$lib/controllers/password_controller";
  import { Exception } from "$lib/exceptions/exception";
  import { ExceptionUiCtxCodes } from "$lib/exceptions/exception_codes";
  import { t } from "svelte-i18n";

  /** @type PasswordController */
  const passwordCtl = new PasswordController();

  /** @type string */
  let email = $state("");

  /** @type BaseInput */
  let _emailInput = $state("");

  /** @type boolean */
  let sentEmail = $state(false);

  /** @type string */
  const _emailField = $t("entity.user.email");

  /**
   * @param {Event} event
   * @returns void
   */
  const resetPassword = (event) => {
    event.preventDefault();

    if (!validateForm()) {
      CommonNotifications.validationError();
      return;
    }

    // Solo demostración: muestra mensaje como si se hubiera enviado el correo
    sentEmail = true;
  };

  /** @returns boolean */
  const validateForm = () => {
    return ![ _emailInput ].map((el) => el.validate()).includes(false);
  };
</script>

<svelte:head>
  <title>{$t('route.reset-password.title')}</title>
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
              <img alt="" src="/imgs/logos/error.png"  width="150"/>
            </div>

            {#if !sentEmail}
              <div class="text-center mb-4 text-title">{$t('route.reset-password.initial.title')}</div>
              <p class="text-center text-gray text-sm">{$t('route.reset-password.initial.content')}</p>

              <form class="mt-4" method="get" onsubmit={resetPassword}>
                <BaseInput
                    bind:this={_emailInput}
                    type="email"
                    class="mb-3"
                    id="email"
                    name={_emailField}
                    placeholder={_emailField}
                    prependIcon="fas fa-envelope"
                    bind:value={email}
                    customRequired
                    validator={({value, defaultValidator}) => {
                    return defaultValidator(value)
                      || InputValidators.validateEmail(value, $t, { tArgs: { field: _emailField }});
                  }}
                    alternative
                />

                <div class="text-center">
                  <BaseButton nativeType="submit" type="primary">
                    <span class="btn-inner--text">{$t('route.reset-password.button.send')}</span>
                  </BaseButton>
                </div>

                <p class="text-center text-sm mt-4">
                  {$t('route.reset-password.initial.footer')}
                  <a class="text-primary pointer"
                     href={Routes.LOGIN}
                     onclick={(_) => goto(Routes.LOGIN, { replaceState: true })}>
                    {$t('route.reset-password.button.login')}
                  </a>
                </p>
              </form>
            {:else}
              <div class="text-center mb-4 text-title">{$t('route.reset-password.sent.title')}</div>
              <p class="text-center text-gray text-sm">
                {$t('route.reset-password.sent.content')}
                <!-- Puedes personalizar este texto para indicar que es una demostración -->
              </p>
              <div class="text-center mt-4">
                <BaseButton nativeType="submit"
                            type="primary"
                            onclick={() => goto(Routes.LOGIN, { replaceState: true })}>
                  <span class="btn-inner--text">{$t('route.reset-password.button.login')}</span>
                </BaseButton>
              </div>
              <!-- Puedes eliminar el footer y el enlace de reenvío si no quieres que se repita la demostración -->
            {/if}
          </div>
        </Card>
      </div>
    </div>
  </div>
</div>

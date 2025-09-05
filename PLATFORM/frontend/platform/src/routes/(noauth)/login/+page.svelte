<script>
  import { goto } from "$app/navigation";
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import Card from "$components/argon_template/Cards/Card.svelte";
  import BaseInput from "$components/argon_template/Inputs/BaseInput.svelte";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Constants } from "$lib/commons/constants";
  import { Global } from "$lib/commons/global";
  import { SessionManager } from "$lib/commons/session_manager";
  import { userLogged } from "$lib/commons/stores";
  import { InputValidators } from "$lib/commons/utils";
  import { OauthController } from "$lib/controllers/oauth_controller";
  import { Exception } from "$lib/exceptions/exception";
  import { ExceptionUiCtxCodes } from "$lib/exceptions/exception_codes";
  import { ScopeType } from "$lib/models/oauth";
  import { t } from "svelte-i18n";
  import { getNotificationsContext } from "svelte-notifications";

  if (!Global.notificationContext) Global.notificationContext = getNotificationsContext();

  /** @type string */
  let email = $state("");

  /** @type string */
  let password = $state("");

  /** @type OauthController */
  const oauthController = new OauthController();

  /** @type boolean */
  let isShowingPassword = $state(false);

  /** @type {string|null} */
  let loginError = $state("");

  /** @type BaseInput */
  let _emailInput;

  /** @type string */
  const _emailField = $t("entity.user.email");

  /** @type BaseInput */
  let _passwordInput;

  /** @type string */
  const _passwordField = $t("entity.user.password");

  /** @returns boolean */
  const onShowPassword = () => isShowingPassword = !isShowingPassword;

  /** @returns boolean */
  const validateLogin = () => {
    return ![ _emailInput, _passwordInput ].map((el) => el.validate()).includes(false);
  };

  /**
   *  @param {Event} e
   *  @returns Promise<void>
   *  @throws {Error} Throws an error if login failed.
   *  */
  const login = async (e) => {
    e.preventDefault();
    if (!validateLogin()) {
      CommonNotifications.genericDanger($t("notification.common.validation-error"));
      return;
    }

    try {
      /** @type {import("$lib/models/oauth_token.js").OauthToken} */
      const token = await oauthController.getToken(email, password, { scope: ScopeType.FULL });
      await SessionManager.saveToken(token);
      userLogged.set(await SessionManager.user());

      await goto("/", { replaceState: true });
    } catch (e) {
      loginError = null;
      if (!(e instanceof Exception)) throw e;

      if (e.code === 401) {
        e.uiCtx = { code: ExceptionUiCtxCodes.loginInvalidCredentials };
        throw e;
      }

      if (e.code === 409) {
        if (e.apiCtx?.code === 1005) {
          loginError = $t(`exception.apiCtx.${ e.apiCtx.code }.content`);
          throw e;
        }

        e.uiCtx = { code: ExceptionUiCtxCodes.loginInvalidCredentials };

        /** @type {unknown} */
        const attemptsLeft = e.apiCtx?.extra?.attempts_left;
        if (attemptsLeft && attemptsLeft <= Constants.LOGIN_MIN_ATTEMPTS_LEFT_SHOW_MESSAGE) {
          loginError = $t(`exception.apiCtx.${ e.apiCtx.code }.content`, {
            values: { attempts_left: attemptsLeft },
          });
        }

        throw e;
      }

      e.uiCtx = { code: ExceptionUiCtxCodes.loginFailed };
      throw e;
    }
  };
</script>

<svelte:head>
  <title>{$t('route.login.title')}</title>
</svelte:head>

<div>
  <div class="header py py-lg-10 pt-lg-9">
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
        <div class="login-container">
          <Card
              bodyClasses="px-lg-5 py-lg-5"
              className="bg-secondary border-0 mb-0 card"
              headerClasses="bg-transparent pb-5"
              noBody
          >
            <div class="card-body px-lg-5 py-lg-5">
              <div class="text-center mb-5 logo-title">
                <img alt="" src="/imgs/logos/logoUMA_tracking-removebgpng.png" width="250"/>
              </div>
              <form onsubmit={login}>
                <BaseInput
                    alternative
                    autocomplete="email"
                    bind:this={_emailInput}
                    bind:value={email}
                    class="mb-3"
                    customRequired
                    id="email"
                    name={_emailField}
                    placeholder={_emailField}
                    prependIcon="fas fa-envelope"
                    type="email"
                    validator={({value, defaultValidator}) => {
                  return defaultValidator(value)
                    || InputValidators.validateEmail(value, $t, { tArgs: { field: _emailField } });
                  }}
                />

                <BaseInput
                    alternative
                    autocomplete="current-password"
                    bind:this={_passwordInput}
                    bind:value={password}
                    class="mb-3"
                    customRequired
                    showAppend
                    appendIcon
                    id="password"
                    name={_passwordField}
                    placeholder={_passwordField}
                    prependIcon="fas fa-unlock-alt"
                    type={isShowingPassword ? 'text' : 'password'}
                >
                  {#snippet appendSnippet()}
                    <i class="fas {isShowingPassword ? 'fa-eye-slash' : 'fa-eye'} ni-lg pointer"
                      onclick={onShowPassword}></i>
                  {/snippet}
                </BaseInput>

                {#if loginError}
                  <div class="login-err mb-3 text-xs text-danger">
                    <div class="mx-2">{loginError}</div>
                  </div>
                {/if}

                <div class="text-center">
                  <BaseButton nativeType="submit" type="primary">
                    <span class="btn-inner--text">{$t('route.login.button.login')}</span>
                  </BaseButton>
                </div>
              </form>
            </div>
          </Card>
          <div class="row mt-3 mb-3">
            <div class="col-6">
              <a class="text-white" href="/password/reset">
                <small>{$t('route.login.button.forgot-password')}</small>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
<style>
  .login-err {
    background: #F8D7DA;
    border-radius: 5px;
    padding: 0.5rem 0.25rem;
  }

  .login-container {
    max-width: 400px;
    width: 100%;
    margin: 0 auto;
    padding: 1rem;
    box-sizing: border-box;
  }

  .header {
    min-height: 80px;
  }

  @media (max-width: 576px) {
    .logo-title img {
      width: 140px;
    }
    .login-container {
      max-width: 100vw;
      padding: 0.5rem;
      margin-top: 2rem;
    }
    .card-body {
      padding: 0.5rem !important;
    }
    .col-md-7, .col-lg-5 {
      flex: 0 0 100%;
      max-width: 100%;
      padding: 0;
    }
    .mt--8 {
      margin-top: 0 !important;
    }
    .pb-5 {
      padding-bottom: 1rem !important;
    }
    .container {
      padding-left: 0.5rem;
      padding-right: 0.5rem;
    }
  }
</style>
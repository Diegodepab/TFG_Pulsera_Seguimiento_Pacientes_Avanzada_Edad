<script>
  import { goto } from "$app/navigation";
  import { page } from "$app/state";
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import Card from "$components/argon_template/Cards/Card.svelte";
  import BaseCheckbox from "$components/argon_template/Inputs/BaseCheckbox.svelte";
  import BaseCardModal from "$components/platform/commons/BaseCardModal.svelte";
  import EditPasswordInput from "$components/platform/user/EditPasswordInput.svelte";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Global } from "$lib/commons/global";
  import { Routes } from "$lib/commons/routes";
  import { DateUtils } from "$lib/commons/utils";
  import { OauthController } from "$lib/controllers/oauth_controller";
  import { UserController } from "$lib/controllers/user_controller";
  import { Exception } from "$lib/exceptions/exception";
  import { User } from "$lib/models/user";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";
  import { getNotificationsContext } from "svelte-notifications";

  if (!Global.notificationContext) Global.notificationContext = getNotificationsContext();

  /** @type boolean */
  let validToken = $state(false);


  /** @type {string | undefined} */
  const token = page.url.searchParams.get("token")?.trim();

  /** @type User */
  let user = User.undef();

  /** @type OauthController */
  const _oauthCtl = new OauthController();

  /** @type UserController */
  const _userCtl = new UserController();

  // form controls
  /** @type string */
  let password = $state("");

  /** @type string */
  let repeatPassword = $state("");

  /** @type EditPasswordInput */
  let _editPasswordInput = $state();

  /** @type BaseCardModal */
  let _modal = $state();

  /** @type BaseCheckbox */
  let tacCheckbox = $state();

  /** @type boolean */
  let isTaCRead = $state(false);// to avoid enable accept btn before read all TaC

  /** @type boolean */
  let acceptedTaC = $state(false);

  // user register status
  /** @type boolean */
  let isActivated = $state(false);

  /** @type boolean */
  let isCanceled = $state(false);

  /** @type EventCallback */
  const onScrollBody = (event) => {
    /** @type number */
    const pendingScroll = event.target.scrollHeight - event.target.scrollTop - 1;
    // NOTE: In some screen sizes, scrollTop is not exact and could be ±1px than clientHeight
    // isTaCRead = [-1, 0, +1].map((e) => e + event.target.clientHeight).includes(pendingScroll);
    isTaCRead = event.target.clientHeight >= pendingScroll;
  };

  /** @type OnMount */
  onMount(async () => {
    if (!token?.length) return;

    try {
      await _oauthCtl.checkToken(token);
      validToken = true;
    } catch (e) {
      validToken = false;
    }
  });

  /** @returns boolean */
  const validateRegister = () => {
    if (!_editPasswordInput.validateForm()) {
      CommonNotifications.validationError();
      return false;
    }

    if (!acceptedTaC || !user.approvalTocTs) {
      CommonNotifications.genericDanger($t("notification.entity.user.error.required-tac"));
      return false;
    }

    return true;
  };

  /**
   * @param {Event} event
   * @returns Promise<void>
   * @throws {Exception} Throws an error if register can´t be confirmed.
   */
  const confirmRegister = async (event) => {
    event.preventDefault();
    if (!validateRegister()) return;

    try {
      user.password = password;
      await _userCtl.activate(token, user);
      CommonNotifications.genericSuccess($t("notification.entity.user.success.register"));
      isActivated = true;
    } catch (e) {
      if (!(e instanceof Exception) || e.code !== 409) throw e;
      validToken = false;
    }
  };

  /** @returns Promise<void> */
  const cancelRegister = async () => {
    await _userCtl.cancelRegister(token);
    isCanceled = true;
  };

  /** @type EventCallback */
  const onCheckTaC = (event) => {
    if (isTaCRead) isTaCRead = false;

    // if checkbox value is false, reset all
    if (!event.detail.checked) {
      acceptOrRejectTaC(false, { ignoreModal: true });
      return;
    }

    _modal.openModal();
  };

  /**
   * Accepts or rejects the Terms and Conditions.
   * @param {boolean} isAccepted - Indicates whether the Terms and Conditions are accepted.
   * @param {Object} [opts] - Additional options.
   * @param {boolean} [opts.ignoreModal] - Indicates whether to ignore the modal (optional).
   * @returns void
   */
  const acceptOrRejectTaC = (isAccepted, opts) => {
    acceptedTaC = isAccepted;
    user.approvalTocTs = DateUtils.booleanToMoment(isAccepted);

    if (opts?.ignoreModal) return;
    _modal.closeModal();
  };
</script>

<svelte:head>
  <title>{$t('route.register.title')}</title>
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
            noBody>
          <div class="card-body px-lg-5 py-lg-5">
            <div class="text-center logo-title mb-4">
              <img alt="bracelet logo" src="/imgs/logos/logo-digital-bracelet.png" width="150"/>
            </div>

            {#if isActivated}
              <p class="text-center mb-4 text-title">{$t('route.register.activated')}</p>

              <div class="text-center">
                <BaseButton type="primary" onclick={() => goto(Routes.LOGIN, { replaceState: true })}>
                  <span class="btn-inner--text">{$t('route.register.button.go-login')}</span>
                </BaseButton>
              </div>

            {:else if isCanceled}
              <p class="text-center mb-2 text-title">{$t('route.register.canceled.description')}</p>

            {:else if validToken}
              <div class="text-center mb-4 text-title">{$t('route.register.initial.title')}</div>

              <form class="mt-4" method="get" onsubmit={confirmRegister}>

                <EditPasswordInput
                    bind:this={_editPasswordInput}
                    bind:password
                    bind:repeatPassword
                    showRepeatPasswordField/>

                <BaseCheckbox
                    bind:this={tacCheckbox}
                    bind:checked={acceptedTaC}
                    label={$t('route.register.accept-tac')}
                    onchecked={onCheckTaC}
                />

                <div class="text-center mt-3">
                  <BaseButton nativeType="submit" type="primary">
                    <span class="btn-inner--text">{$t('route.register.button.confirm')}</span>
                  </BaseButton>
                </div>

                <hr>

                <p class="text-center text-gray text-sm">
                  {$t('route.register.canceled.request')}
                  <a class="text-primary pointer" href="#" onclick={cancelRegister}>
                    {$t('route.register.canceled.link')}
                  </a>
                </p>
              </form>

            {:else}
              <p class="text-center mb-4 text-title">{$t('route.register.no-available')}</p>
            {/if}
          </div>
        </Card>

        <!-- Terms and conditions modal -->
        <BaseCardModal
            allowOutsideClick={false}
            bind:this={_modal}
            bodyResponsiveHeight="auto"
            modalBodyMaxHeight="700px"
            modalMaxWidth="1500px"
            onScrollBody={isTaCRead ? null : onScrollBody}
            setHtmlOverflowHidden
            size="xl"
        >
          {#snippet headerSnippet()}
            <div>
              <p class="modal-title">{$t('route.tac.title')}</p>
            </div>
          {/snippet}

          {#snippet footerSnippet()}
            <div>
              <BaseButton className="m-0" onclick={() => acceptOrRejectTaC(false)} type="secondary">
                <span class="btn-inner--text">{$t('common.button.cancel')}</span>
              </BaseButton>
              <BaseButton disabled={!isTaCRead} onclick={() => acceptOrRejectTaC(true)} type="success">
                <span class="btn-inner--text">{$t('route.register.button.agree')}</span>
              </BaseButton>
            </div>
          {/snippet}
        </BaseCardModal>
      </div>
    </div>
  </div>
</div>

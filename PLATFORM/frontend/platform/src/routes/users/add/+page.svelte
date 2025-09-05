<script>
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import LoadingContentPage from "$components/platform/commons/LoadingContentPage.svelte";
  import UserForm from "$components/platform/user/UserForm.svelte";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Global } from "$lib/commons/global";
  import { Routes } from "$lib/commons/routes";
  import { SessionManager } from "$lib/commons/session_manager";
  import { navigatorHistory } from "$lib/commons/stores";
  import { UserController } from "$lib/controllers/user_controller";
  import { User, UserStatusType } from "$lib/models/user";
  import { PermissionsEntityType, PermissionsGrantType, UserPermission } from "$lib/models/user_permission";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";
  import { getNotificationsContext } from "svelte-notifications";

  if (!Global.notificationContext) Global.notificationContext = getNotificationsContext();

  /** @type boolean */
  let checkingGrants = $state(true);

  /** @type boolean */
  let loading = $state(true);

  /** @type UserController */
  const _userCtl = new UserController();

  /** @type User */
  let user = $state(User.empty());
  user.statusName = UserStatusType.PENDING;

  /** @type UserForm */
  let _userForm = $state();

  /** @type UserPermission */
  let _entityAccess = $state();

  /** @type OnMount */
  onMount(async () => {
    _entityAccess = (await SessionManager.userPermissionsOn([ PermissionsEntityType.USER ])).at(0);

    if (!_entityAccess.uiVisibility || _entityAccess.write === PermissionsGrantType.NONE) {
      CommonNotifications.noAccessPermissions();
      return await goBack();
    }

    checkingGrants = false;

    loading = false;
  });

  /** @returns Promise<void> */
  const saveUser = async () => {
    loading = true;

    if (!_userForm.validateForm()) {
      CommonNotifications.validationError();
      loading = false;
      return;
    }

    try {
      user = await _userCtl.post(user);
    } finally {
      loading = false;
    }

    CommonNotifications.genericSuccess($t("notification.entity.user.success.add"));
    await goBack();
  };

  /** @returns Promise<void> */
  const goBack = async () => navigatorHistory.goBack(Routes.USERS);

</script>

<svelte:head>
  <title>{$t('route.user-add.title')}</title>
</svelte:head>

{#if !checkingGrants}
  <div class="page-content">
    <div class="page-content-title mt-0 d-flex justify-content-between align-items-center">
      <span>{$t('route.user-add.form-title')}</span>
    </div>
    <LoadingContentPage {loading} class="mb-3"/>

    <form onsubmit={saveUser}>
      <div class="col-12 col-lg-10 col-xl-6">
        <UserForm bind:this={_userForm} {user} readonly={loading}/>
      </div>

      <div class="row mt-5">
        <div class="d-flex col-12">
          <div class="d-flex justify-content-end col-12">
            <BaseButton type="secondary" disabled={loading} onclick={goBack}>
              <span class="btn-inner--text">{$t('common.button.cancel')}</span>
            </BaseButton>

            {#if _entityAccess.write !== PermissionsGrantType.NONE}
              <BaseButton nativeType="submit" type="success" disabled={loading}>
                <span class="btn-inner--text">{$t('common.button.save')}</span>
              </BaseButton>
            {/if}
          </div>
        </div>
      </div>
    </form>
  </div>
{/if}

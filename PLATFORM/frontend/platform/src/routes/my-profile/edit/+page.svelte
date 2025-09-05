<script>

  import { goto } from "$app/navigation";
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import LoadingContentPage from "$components/platform/commons/LoadingContentPage.svelte";
  import ChangePassword from "$components/platform/my-profile/ChangePassword.svelte";
  import ProfileForm from "$components/platform/my-profile/ProfileForm.svelte";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Global } from "$lib/commons/global";
  import { Routes } from "$lib/commons/routes";
  import { SessionManager } from "$lib/commons/session_manager";
  import { userLogged } from "$lib/commons/stores";
  import { UserController } from "$lib/controllers/user_controller";
  import { User } from "$lib/models/user";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";
  import { getNotificationsContext } from "svelte-notifications";

  if (!Global.notificationContext) Global.notificationContext = getNotificationsContext();

  /** @type boolean */
  let loading = $state(true);

  /** @type number */
  const _userId = SessionManager.userId();

  /** @type UserController */
  const _userCtl = new UserController();

  /** @type User */
  let user = $state();

  /** @type ProfileForm */
  let profileForm = $state();

  /** @type OnMount */
  onMount(async () => {
    try {

      user = await _userCtl.get(_userId);
    } finally {
      loading = false;
    }
  });

  /** @returns Promise<void> */
  const cancel = async () => await goto(Routes.MY_PROFILE);

  /** @returns Promise<void> */
  const saveUser = async () => {
    loading = true;

    if (!profileForm.validateForm()) {
      CommonNotifications.validationError();
      loading = false;
      return;
    }

    user = await _userCtl.patch(user.id, user);
    userLogged.set(user); // set new user into store to keep updated the profile + navbar
    CommonNotifications.genericSuccess($t("notification.entity.user.success.edit-profile"));
    await goto(Routes.MY_PROFILE);
  };

  // /** @returns Promise<void> */
  // const deleteAccount = async () => {
  //   if (await CommonAlerts.deleteOrDisableConfirmation($t('route.my-profile-edit.delete.account'), {
  //     gender: i18nGender.FEMALE,
  //     customKeyPath: {
  //       title: 'alert.delete-user.own.title',
  //       content: 'alert.delete-user.own.content'
  //     }
  //   })) {
  //     await _userCtl.deleteAccount();
  //     CommonNotifications.genericSuccess($t('notification.entity.user.success.delete-account'));
  //     await SessionManager.closeSession();
  //     await goto(Routes.LOGIN, { replaceState: true });
  //   }
  // };

</script>

<svelte:head>
  <title>{$t('route.my-profile-edit.title')}</title>
</svelte:head>

<div class="page-content">
  <div class="page-content-title">{$t('route.my-profile-edit.profile-title')}</div>
  <LoadingContentPage class="mb-2" {loading}/>

  <div class="pt-3">
    <form onsubmit={saveUser}>
      <ProfileForm bind:this={profileForm} readonly={loading} {user}/>

      <div class="row mt-4">
        <div class="d-flex justify-content-end col-12">
          <BaseButton onclick={cancel} type="light">
            <span class="btn-inner--text">{$t('common.button.cancel')}</span>
          </BaseButton>

          <BaseButton nativeType="submit" type="success">
            <span class="btn-inner--text">{$t('common.button.save')}</span>
          </BaseButton>
        </div>
      </div>
    </form>

    <hr class="mb-4">
    <ChangePassword/>

    <!--{#if allowDeletion}-->
    <!--  <hr class="mb-4">-->
    <!--  <div class="d-flex justify-content-end" onclick={deleteAccount}>-->
    <!--    <span class="nav-link pointer">{$t('route.my-profile-edit.delete.delete')}</span>-->
    <!--  </div>-->
    <!--{/if}-->
  </div>

</div>
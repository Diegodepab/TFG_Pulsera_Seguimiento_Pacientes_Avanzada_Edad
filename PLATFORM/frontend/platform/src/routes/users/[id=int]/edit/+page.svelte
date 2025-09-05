<script>
  import { navigating, page } from "$app/state";
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import LoadingContentPage from "$components/platform/commons/LoadingContentPage.svelte";
  import UserForm from "$components/platform/user/UserForm.svelte";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Global } from "$lib/commons/global";
  import { Routes } from "$lib/commons/routes";
  import { SessionManager } from "$lib/commons/session_manager";
  import { navigatorHistory } from "$lib/commons/stores";
  import { UserController } from "$lib/controllers/user_controller";
  import { Exception } from "$lib/exceptions/exception";
  import { User } from "$lib/models/user";
  import { PermissionsEntityType, PermissionsGrantType } from "$lib/models/user_permission";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";
  import { getNotificationsContext } from "svelte-notifications";

  if (!Global.notificationContext) Global.notificationContext = getNotificationsContext();

  /** @type UserController */
  const userCtl = new UserController();

  /** @type boolean */
  let checkingGrants = $state(true);

  /** @type boolean */
  let loading = $state(true);

  /** @type User */
  let user = $state(User.empty());

  /** @type UserForm */
  let userForm;

  /** @type UserPermission */
  let entityAccess = $state();

  let _idParam = page.params.id;

  onMount(async () => {
    // avoid user to edit itself
    if (SessionManager.userId() === _idParam) {
      await goBack();
      return;
    }

    const perms = await SessionManager.userPermissionsOn([ PermissionsEntityType.USER ]);
    entityAccess = perms.at(0);

    if (!entityAccess.uiVisibility || entityAccess.write === PermissionsGrantType.NONE) {
      CommonNotifications.noAccessPermissions();
      await goBack();
      return;
    }

    checkingGrants = false;
    await loadUserData();

  });

  /**
   * Carga los datos del usuario.
   * @returns Promise<void>
   * @throws {Exception} En caso de error al obtener los datos.
   */

  const loadUserData = async () => {
    loading = true;
    try {
      const params = new Map();
      user = await userCtl.get(_idParam, { params });

    } catch (e) {
      if (!(e instanceof Exception) || e.code !== 404) throw e;
      await goBack();
      throw e;
    } finally {
      loading = false;
    }
  };

  const saveUser = async () => {
    loading = true;

    if (!userForm.validateForm()) {
      CommonNotifications.validationError();
      loading = false;
      return;
    }

    try {
      await userCtl.patch(user.id, user);
    } finally {
      loading = false;
    }

    CommonNotifications.genericSuccess($t("notification.entity.user.success.edit"));
    await goBack();
  };

  // const deleteUser = async () => {
  //   const confirmed = await CommonAlerts.deleteOrDisableConfirmation($t("entity.user.entity-name"), {
  //     gender: i18nGender.MALE,
  //   });
  //   if (!confirmed) return;
  //
  //   loading = true;
  //   await userCtl.deleteAccount(user.id);
  //   CommonNotifications.genericSuccess($t("notification.entity.user.success.delete"));
  //   if (SessionManager.userRole() === UserRoleType.ADMIN) {
  //     await goBack();
  //   } else {
  //     await removePatternAndGoBack();
  //   }
  // };

  const removePatternAndGoBack = async () => {
    loading = true;
    await navigatorHistory.removePatternAndGoBack(
      Routes.USERS,
      new RegExp(`${Routes.USERS}/${user.id}/?`),
    );
  };

  const goBack = async () => {
    await navigatorHistory.goBack(`${ Routes.USERS }${ user?.id ? `/${ user.id }` : "" }`);
  };

  $effect(() => {
    if (navigating && page.params.id && navigating.to?.params?.id === page.params.id && page.params.id !== _idParam) {
      _idParam = page.params.id;
      loadUserData();
    }
  });
</script>


<svelte:head>
  <title>{$t('route.user-edit.title')}</title>
</svelte:head>

{#if !checkingGrants}
  <div class="page-content">
    <div class="page-content-title mt-0 d-flex justify-content-between">{$t('route.user-edit.form-title')}</div>
    <LoadingContentPage {loading} class="mb-3"/>

    <form onsubmit={saveUser}>
      <div class="row mx-0">
        <div class="col-12 col-lg-10 col-xl-6">
          <UserForm bind:this={userForm} {user} readonly={loading}/>
        </div>
      </div>

      <div class="row mt-5">
        <div class="d-flex col-12">
          <div class="d-flex flex-column flex-sm-row justify-content-end col-12 px-2">
            <BaseButton
                className="mb-2 mr-0 mr-sm-2 mb-sm-0"
                type="secondary"
                disabled={loading}
                onclick={goBack}>
              <span class="btn-inner--text">{$t('common.button.cancel')}</span>
            </BaseButton>

            <!--{#if entityAccess.del !== PermissionsGrantType.NONE && user}-->
            <!--  <BaseButton-->
            <!--      className="mb-2 mr-0 mr-sm-2 mb-sm-0"-->
            <!--      type="danger"-->
            <!--      disabled={loading}-->
            <!--      onclick={deleteUser}>-->
            <!--    <span class="btn-inner&#45;&#45;text">{$t('common.button.delete')}</span>-->
            <!--  </BaseButton>-->
            <!--{/if}-->

            {#if entityAccess.write !== PermissionsGrantType.NONE}
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
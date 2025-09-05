<script>
  import { goto } from "$app/navigation";
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
  import { PermissionsEntityType, PermissionsGrantType, UserPermission } from "$lib/models/user_permission";
  import { QueryFields } from "$lib/services/utils/query_utils";
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
  let user = $state();
  /** @type {Map<PermissionsEntityType, UserPermission>} */
  const _entitiesAccess = new Map();

  // manage changes into url from route
  let _idParam = page.params.id;

  /** @type OnMount */
  onMount(async () => {
    // check user not entered to see himself here
    if (SessionManager.userId() == page.params.id) {
      await goBack();
      return;
    }

    const permissions = await SessionManager.userPermissionsOn([ PermissionsEntityType.USER ]);
    if (permissions) {
      permissions.forEach((perm) => _entitiesAccess.set(perm.entityName, perm));
    }

    const userPermission = _entitiesAccess.get(PermissionsEntityType.USER);
    if (!userPermission.uiVisibility || userPermission.read === PermissionsGrantType.NONE) {
      CommonNotifications.noAccessPermissions();
      await goBack();
      return;
    }

    checkingGrants = false;
    await loadUserData();
  });

  /**
   * @returns Promise<void>
   * @throws Exception Throws an error if user data not loaded.
   */
  const loadUserData = async () => {
    loading = true;
    try {
      /** @type {Map<QueryFields, ?>} */
      const params = new Map();
      user = await _userCtl.get(page.params.id, { params });
    } catch (e) {
      if (!(e instanceof Exception) || e.code !== 404) throw e;
      await goBack();
      throw e;
    } finally {
      loading = false;
    }
  };

  /** @returns Promise<void> */
  const editUser = async () => await goto(`${ Routes.USERS }/${ user.id }/edit`);
  /** @returns Promise<void> */
  const goBack = async () => await navigatorHistory.goBack(Routes.USERS);

  $effect(() => {
    if (navigating && page.params.id && navigating.to?.params?.id === page.params.id && page.params.id !== _idParam) {
      _idParam = page.params.id;
      loadUserData();
    }
  });
</script>

<svelte:head>
  <title>{$t('route.user-details.title')}</title>
</svelte:head>

{#if !checkingGrants}
  <div class="page-content">
    <div class="page-content-title mt-0 d-flex justify-content-between align-items-center">
      <span>{$t('route.user-details.form-title')}</span>

      <div class="pr-0 d-flex justify-content-end">
        <BaseButton size="sm" onclick={goBack} type="primary" disabled={loading}>
          <i class="fas fa-arrow-left fa-fw"></i>
        </BaseButton>

        {#if _entitiesAccess.get(PermissionsEntityType.USER).write !== PermissionsGrantType.NONE}
          <div class="card-header-action-separator"></div>
          <BaseButton size="sm" type="primary" disabled={loading} onclick={editUser}>
            <i class="fas fa-edit fa-fw"></i>
          </BaseButton>
        {/if}
      </div>
    </div>
    <LoadingContentPage {loading} class="mb-3"/>

    <div class="row mx-0">
      <div class="col-12 col-md-6 pl-3 border-sm-0">
        <UserForm {user} readonly/>
      </div>
    </div>
  </div>
{/if}
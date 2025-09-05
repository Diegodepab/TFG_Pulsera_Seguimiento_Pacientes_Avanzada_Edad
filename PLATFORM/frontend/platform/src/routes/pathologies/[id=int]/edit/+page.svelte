<script>
  import { navigating, page } from "$app/state";
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import LoadingContentPage from "$components/platform/commons/LoadingContentPage.svelte";
  import PathologyForm from "$components/platform/pathology/PathologyForm.svelte";
  import { CommonAlerts } from "$components/platform/utils/common_alerts";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Global } from "$lib/commons/global";
  import { Routes } from "$lib/commons/routes";
  import { SessionManager } from "$lib/commons/session_manager";
  import { navigatorHistory } from "$lib/commons/stores";
  import { PathologyController } from "$lib/controllers/pathology_controller";
  import { Exception } from "$lib/exceptions/exception";
  import { Pathology } from "$lib/models/pathology";
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

  /** @type PathologyController */
  const pathologyCtl = new PathologyController();

  /** @type Pathology */
  let pathology = $state(Pathology.empty());

  /** @type pathologyForm */
  let pathologyForm = $state();

  /** @type UserPermission */
  let entityAccess = $state();

  // manage changes into url from route
  /** @type * */
  let _idParam = $state(page.params.id);

  /** @type OnMount */
  onMount(async () => {
    entityAccess = (await SessionManager.userPermissionsOn([ PermissionsEntityType.PATHOLOGY ])).at(0);

    if (!entityAccess.uiVisibility || entityAccess.write === PermissionsGrantType.NONE) {
      CommonNotifications.noAccessPermissions();
      return await goBack();
    }

    checkingGrants = false;
    await loadPathologyData();
  });

  /**
   * @returns Promise<void>
   * @throws {Exception} Throws an error if pathology data not loaded.
   */
  const loadPathologyData = async () => {
    loading = true;

    try {
      pathology = await pathologyCtl.get(_idParam);
    } catch (e) {
      if (!(e instanceof Exception) || e.code !== 404) throw e;
      await goBack();

      throw e;
    }

    loading = false;
  };

  /** @returns Promise<void> */
  const savePathology = async () => {
    loading = true;

    if (!pathologyForm.validateForm()) {
      CommonNotifications.validationError();
      loading = false;
      return;
    }

    try {
      await pathologyCtl.patch(pathology.id, pathology);
    } finally {
      loading = false;
    }

    CommonNotifications.genericSuccess($t("notification.entity.pathology.success.edit"));
    await goBack();
  };

  /** @returns Promise<void> */
  const deletePathology = async () => {
    if (!(await CommonAlerts.deleteOrDisableConfirmation($t("entity.pathology.entity-name")))) return;

    loading = true;
    await pathologyCtl.delete(pathology.id);

    CommonNotifications.genericSuccess($t("notification.entity.pathology.success.delete"));

    await removePatternAndGoBack();
  };

  /** @returns Promise<void> */
  const removePatternAndGoBack = async () => {
    loading = true;
    await navigatorHistory.removePatternAndGoBack(
      Routes.PATIENTS,
      new RegExp(`${Routes.PATHOLOGIES}/${pathology.id}/?`),
    );
  };

  /** @returns Promise<void> */
  const goBack = async () => {
    await navigatorHistory.goBack(`${ Routes.PATIENTS }`);
  };

  $effect(() => {
    if (navigating && page.params.id
      && navigating.to?.params?.id === page.params.id
      && page.params.id !== _idParam) {
      _idParam = page.params.id;
      loadPathologyData().then();
    }
  });
</script>

<svelte:head>
  <title>{$t('route.pathology-edit.title')}</title>
</svelte:head>

{#if !checkingGrants}
  <div class="page-content">
    <div class="page-content-title mt-0 d-flex justify-content-between">{$t('route.pathology-edit.form-title')}</div>
    <LoadingContentPage {loading} class="mb-3"/>

    <form onsubmit={savePathology}>
      <div class="row mx-0">
        <div class="col-12 col-lg-10 col-xl-6">
          <PathologyForm bind:this={pathologyForm} {pathology} readonly={loading}/>
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

            {#if entityAccess.del !== PermissionsGrantType.NONE && pathology}
              <BaseButton
                  className="mb-2 mr-0 mr-sm-2 mb-sm-0"
                  type="danger"
                  disabled={loading}
                  onclick={deletePathology}>
                <span class="btn-inner--text">{$t('common.button.delete')}</span>
              </BaseButton>
            {/if}

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

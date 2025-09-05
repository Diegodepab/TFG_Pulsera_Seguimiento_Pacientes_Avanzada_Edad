<script>
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import LoadingContentPage from "$components/platform/commons/LoadingContentPage.svelte";
  import PathologyForm from "$components/platform/pathology/PathologyForm.svelte";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Global } from "$lib/commons/global";
  import { Routes } from "$lib/commons/routes";
  import { navigatorHistory } from "$lib/commons/stores";
  import { PathologyController } from "$lib/controllers/pathology_controller";
  import { Pathology } from "$lib/models/pathology";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";
  import { getNotificationsContext } from "svelte-notifications";

  if (!Global.notificationContext) Global.notificationContext = getNotificationsContext();

  /** @type boolean */
  let loading = $state(true);

  /** @type PathologyController */
  const _pathologyCtl = new PathologyController();

  /** @type Pathology */
  let pathology = $state(Pathology.empty());

  /** @type PathologyForm */
  let _pathologyForm = $state();

  onMount(async () => {
    loading = false;
  });

  /** @returns Promise<void> */
  const savePathology = async () => {
    loading = true;

    if (!_pathologyForm.validateForm()) {
      CommonNotifications.validationError();
      loading = false;
      return;
    }

    try {
      pathology = await _pathologyCtl.post(pathology);
      CommonNotifications.genericSuccess($t("notification.entity.pathology.success.add"));
      await goBack();
    } catch (error) {
      CommonNotifications.genericDanger($t("notification.entity.pathology.error.add"));
    } finally {
      loading = false;
    }
  };

  /** @returns Promise<void> */
  const goBack = async () => navigatorHistory.goBack(Routes.PATHOLOGIES);
</script>

<svelte:head>
  <title>{$t('route.pathology-add.title')}</title>
</svelte:head>

{#if !loading}
  <div class="page-content">
    <div class="page-content-title mt-0 d-flex justify-content-between align-items-center">
      <span>{$t('route.pathology-add.form-title')}</span>
    </div>
    <LoadingContentPage {loading} class="mb-3"/>

    <form onsubmit={savePathology}>
      <div class="col-12 col-lg-10 col-xl-6">
        <PathologyForm bind:this={_pathologyForm} {pathology} readonly={loading}/>
      </div>

      <div class="row mt-5">
        <div class="d-flex col-12">
          <div class="d-flex justify-content-end col-12">
            <BaseButton type="secondary" disabled={loading} onclick={goBack}>
              <span class="btn-inner--text">{$t('common.button.cancel')}</span>
            </BaseButton>

            <BaseButton nativeType="submit" type="success" disabled={loading}>
              <span class="btn-inner--text">{$t('common.button.save')}</span>
            </BaseButton>
          </div>
        </div>
      </div>
    </form>
  </div>
{/if}

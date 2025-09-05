<script>
  import { goto } from "$app/navigation";
  import { navigating, page } from "$app/state";
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import LoadingContentPage from "$components/platform/commons/LoadingContentPage.svelte";
  import PatientModelForm from "$components/platform/patient-model/PatientModelForm.svelte";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Global } from "$lib/commons/global";
  import { Routes } from "$lib/commons/routes";
  import { SessionManager } from "$lib/commons/session_manager";
  import { navigatorHistory } from "$lib/commons/stores";
  import { PatientModelController } from "$lib/controllers/patient_model_controller";
  import { Exception } from "$lib/exceptions/exception";
  import { PatientModel } from "$lib/models/patient_model";
  import { PermissionsEntityType, PermissionsGrantType } from "$lib/models/user_permission";

  import { QueryFields, QueryParamsEmbed, QueryParamsRaw } from "$lib/services/utils/query_utils";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";
  import { getNotificationsContext } from "svelte-notifications";

  if (!Global.notificationContext) Global.notificationContext = getNotificationsContext();

  /** @type boolean */
  let checkingGrants = $state(true);

  /** @type boolean */
  let loading = $state(true);

  /** @type PatientModelController */
  const _patientModelCtl = new PatientModelController();

  /** @type PatientModel */
  let patientModel = $state(PatientModel.empty());

  /** @type {Map<PermissionsEntityType, UserPermission>} */
  const _entitiesAccess = new Map();

  // Manage changes into URL from route
  let _idParam = $state(page.params.id);

  /** @type OnMount */
  onMount(async () => {
    (await SessionManager.userPermissionsOn([ PermissionsEntityType.PATIENT_MODEL ]))?.forEach((permission) => {
      _entitiesAccess.set(permission.entityName, permission);
    });

    if (
      !_entitiesAccess.get(PermissionsEntityType.PATIENT_MODEL).uiVisibility ||
      _entitiesAccess.get(PermissionsEntityType.PATIENT_MODEL).read === PermissionsGrantType.NONE
    ) {
      CommonNotifications.noAccessPermissions();
      return await goBack();
    }

    checkingGrants = false;
    await loadPatientModelData();
  });

  /** @returns Promise<void>
   * @throws {Exception} Throws an error if patient model data not loaded.
   */
  const loadPatientModelData = async () => {
    loading = true;
    try {
      /** @type {Map<QueryFields, unknown>} */
      const params = new Map();
      params.set(QueryFields.RAW, [
        new QueryParamsRaw({ field: PatientModel.apiRaw.addBlobDisplayUrl, value: "true" }),
      ]);

      params.set(QueryFields.EMBED, new QueryParamsEmbed({ embeds: [ PatientModel.apiEmbeds.patient ] }));

      patientModel = await _patientModelCtl.get(page.params.id, { params });
      loading = false;
    } catch (e) {
      if (!(e instanceof Exception) || e.code !== 404) throw e;
      await goBack();

      throw e;
    }
  };

  /** @returns Promise<void> */
  const editPatientModel = async () => await goto(`${ Routes.PATIENT_MODELS }/${ patientModel.id }/edit`);
  /** @returns Promise<void> */
  const goBack = async () => await navigatorHistory.goBack(`${ Routes.PATIENTS }/${ patientModel.patientId }`);


  $effect(() => {
    if (navigating && page.params.id && navigating.to?.params?.id === page.params.id && page.params.id !== _idParam) {
      _idParam = page.params.id;
      loadPatientModelData().then();
    }
  });
</script>

<svelte:head>
  <title>{$t('route.patient-model-details.title')}</title>
</svelte:head>

{#if !checkingGrants}
  <div class="page-content">
    <div class="page-content-title mt-0 d-flex justify-content-between align-items-center">
      <span>{$t('route.patient-model-details.title')}</span>
      <div class="pr-0 d-flex justify-content-end">
        <BaseButton size="sm" onclick={goBack} type="primary" disabled={loading}>
          <i class="fas fa-arrow-left fa-fw"></i>
        </BaseButton>
        {#if _entitiesAccess.get(PermissionsEntityType.PATIENT_MODEL).write !== PermissionsGrantType.NONE}
          <div class="card-header-action-separator"></div>
          <BaseButton size="sm" type="primary" disabled={loading} onclick={editPatientModel}>
            <i class="fas fa-edit fa-fw"></i>
          </BaseButton>
        {/if}
      </div>
    </div>
    <LoadingContentPage {loading} class="mb-3"/>
    <div class="row mx-0">
      <div class="col-12 col-md-6 pl-3 border-sm-0">
        <PatientModelForm {patientModel} readonly/>
      </div>
    </div>
  </div>
{/if}

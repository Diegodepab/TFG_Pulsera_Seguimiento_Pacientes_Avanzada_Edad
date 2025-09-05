<script>
  import { navigating, page } from "$app/state";
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import LoadingContentPage from "$components/platform/commons/LoadingContentPage.svelte";
  import PatientForm from "$components/platform/patient/PatientForm.svelte";
  import { CommonAlerts } from "$components/platform/utils/common_alerts";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Global } from "$lib/commons/global";
  import { Routes } from "$lib/commons/routes";
  import { SessionManager } from "$lib/commons/session_manager";
  import { navigatorHistory } from "$lib/commons/stores";
  import { i18nGender } from "$lib/commons/ui_utils";
  import { PatientController } from "$lib/controllers/patient_controller";
  import { Exception } from "$lib/exceptions/exception";
  import { Patient } from "$lib/models/patient";
  import { PermissionsEntityType, PermissionsGrantType } from "$lib/models/user_permission";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";
  import { getNotificationsContext } from "svelte-notifications";

  if (!Global.notificationContext) Global.notificationContext = getNotificationsContext();

  /** @type BaseTable */
  let baseTable;

  /** @type boolean */
  let checkingGrants = $state(true);
  /** @type boolean */
  let loading = $state(true);

  /** @type PatientController */
  const patientCtl = new PatientController();
  /** @type Patient */
  let patient = $state(Patient.empty());
  /** @type PatientForm */
  let patientForm = $state();
  /** @type UserPermission */
  let entityAccess = $state();

  // manage changes into url from route
  /** @type {*} */
  let _idParam = $state(page.params.id);

  /** @type OnMount */
  onMount(async () => {
    entityAccess = (await SessionManager.userPermissionsOn([ PermissionsEntityType.PATIENT ])).at(0);

    if (!entityAccess.uiVisibility || entityAccess.write === PermissionsGrantType.NONE) {
      CommonNotifications.noAccessPermissions();
      return await goBack();
    }

    checkingGrants = false;
    await loadPatientData();
  });


  /**
   * @returns Promise<void>
   * @throws {Exception} Throws an error if patient data not loaded.
   */
  const loadPatientData = async () => {
    loading = true;

    try {
      patient = await patientCtl.get(_idParam);
    } catch (e) {
      if (!(e instanceof Exception) || e.code !== 404) throw e;
      await goBack();

      throw e;
    }

    loading = false;
  };

  /** @returns Promise<void> */
  const savePatient = async () => {
    loading = true;

    if (!patientForm.validateForm()) {
      CommonNotifications.validationError();
      loading = false;
      return;
    }

    try {
      await patientCtl.patch(patient.id, patient);
    } finally {
      loading = false;
    }

    CommonNotifications.genericSuccess($t("notification.entity.patient.success.edit"));
    await goBack();
  };

  /** @returns Promise<void> */
  const deletePatient = async () => {
    if (!(await CommonAlerts.deleteOrDisableConfirmation($t("entity.patient.entity-name"), {
      gender: i18nGender.MALE,
    }))) return;

    loading = true;
    await patientCtl.delete(patient.id);

    CommonNotifications.genericSuccess($t("notification.entity.patient.success.delete"));

    await removePatternAndGoBack();
  };

  /** @returns Promise<void> */
  const removePatternAndGoBack = async () => {
    loading = true;
    await navigatorHistory.removePatternAndGoBack(Routes.PATIENTS, new RegExp(`${Routes.PATIENTS}/${patient.id}/?`));
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
      loadPatientData().then();
    }
  });
</script>

<svelte:head>
  <title>{$t('route.patient-edit.title')}</title>
</svelte:head>

{#if !checkingGrants}
  <div class="page-content">
    <div class="page-content-title mt-0 d-flex justify-content-between">{$t('route.patient-edit.form-title')}</div>
    <LoadingContentPage {loading} class="mb-3"/>

    <form onsubmit={savePatient}>
      <div class="d-flex flex-column flex-md-row mx-0">
        <div class="col-12 col-md-6 pl-3 border-sm-0">
          <PatientForm bind:this={patientForm} {patient} readonly={loading}/>
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

            {#if entityAccess.del !== PermissionsGrantType.NONE && patient}
              <BaseButton
                  className="mb-2 mr-0 mr-sm-2 mb-sm-0"
                  type="danger"
                  disabled={loading}
                  onclick={deletePatient}>
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

<script>
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import LoadingContentPage from "$components/platform/commons/LoadingContentPage.svelte";
  import PatientForm from "$components/platform/patient/PatientForm.svelte";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Global } from "$lib/commons/global";
  import { Routes } from "$lib/commons/routes";
  import { SessionManager } from "$lib/commons/session_manager";
  import { navigatorHistory } from "$lib/commons/stores";
  import { PatientController } from "$lib/controllers/patient_controller";
  import { Patient } from "$lib/models/patient";
  import { UserRoleType } from "$lib/models/user";
  import { PermissionsEntityType, PermissionsGrantType, UserPermission } from "$lib/models/user_permission";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";
  import { getNotificationsContext } from "svelte-notifications";

  if (!Global.notificationContext) Global.notificationContext = getNotificationsContext();

  /** @type boolean */
  let checkingGrants = $state(true);
  /** @type boolean */
  let loading = $state(true);

  /** @type PatientController */
  const _patientCtl = new PatientController();
  /** @type Patient */
  let patient = $state(Patient.empty());

  /** @type PatientForm */
  let _patientForm = $state();
  /** @type UserPermission */
  let _entityAccess = $state();

  /** @type OnMount */
  onMount(async () => {
    _entityAccess = (await SessionManager.userPermissionsOn([ PermissionsEntityType.PATIENT ])).at(0);

    if (!_entityAccess.uiVisibility || _entityAccess.write === PermissionsGrantType.NONE) {
      CommonNotifications.noAccessPermissions();
      return await goBack();
    }

    checkingGrants = false;

    if (SessionManager.userRole() === UserRoleType.USER) patient.ownerUserId = SessionManager.userId();

    loading = false;
  });

  /** @returns Promise<void> */
  const savePatient = async () => {
    loading = true;

    if (!_patientForm.validateForm()) {
      CommonNotifications.validationError();
      loading = false;
      return;
    }

    try {
      patient = await _patientCtl.post(patient);
    } finally {
      loading = false;
    }

    CommonNotifications.genericSuccess($t("notification.entity.patient.success.add"));
    await goBack();
  };

  /** @returns Promise<void> */
  const goBack = async () => navigatorHistory.goBack(Routes.PATIENTS);

</script>

<svelte:head>
  <title>{$t('route.patient-add.title')}</title>
</svelte:head>

{#if !checkingGrants}
  <div class="page-content">
    <div class="page-content-title mt-0 d-flex justify-content-between align-items-center">
      <span>{$t('route.patient-add.form-title')}</span>
    </div>
    <LoadingContentPage {loading} class="mb-3"/>

    <form onsubmit={savePatient}>
      <div class="col-12 col-lg-10 col-xl-6">
        <PatientForm bind:this={_patientForm} {patient} readonly={loading}/>
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

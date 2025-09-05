<script>
  import { navigating, page } from "$app/state";
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import LoadingContentPage from "$components/platform/commons/LoadingContentPage.svelte";
  import PatientModelForm from "$components/platform/patient-model/PatientModelForm.svelte";
  import { CommonAlerts } from "$components/platform/utils/common_alerts";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Global } from "$lib/commons/global";
  import { Routes } from "$lib/commons/routes";
  import { SessionManager } from "$lib/commons/session_manager";
  import { navigatorHistory } from "$lib/commons/stores";
  import { i18nGender } from "$lib/commons/ui_utils";
  import { BlobStorageController } from "$lib/controllers/blob_storage/blob_storage_controller";
  import { PatientModelController } from "$lib/controllers/patient_model_controller";
  import { Exception } from "$lib/exceptions/exception";
  import { ExceptionBlobStorage } from "$lib/exceptions/exception_codes";
  import { PlatformException } from "$lib/exceptions/platform_exception";
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
  /** @type PatientModelForm */
  let _patientModelForm = $state();
  /** @type UserPermission */
  let entityAccess = $state();

  // manage changes into url from route
  /** @type * */
  let _idParam = $state(page.params.id);

  /** @type OnMount */
  onMount(async () => {
    entityAccess = (await SessionManager.userPermissionsOn([ PermissionsEntityType.PATIENT_MODEL ])).at(0);

    if (!entityAccess.uiVisibility || entityAccess.write === PermissionsGrantType.NONE) {
      CommonNotifications.noAccessPermissions();
      return await goBack();
    }

    checkingGrants = false;
    await loadPatientModelData();
  });

  /** @returns Promise<void> */
  const loadPatientModelData = async () => {
    loading = true;

    try {
      /** @type {Map<QueryFields, ?>} */
      const params = new Map();
      params.set(QueryFields.RAW, [
        new QueryParamsRaw({ field: PatientModel.apiRaw.addBlobDisplayUrl, value: "true" }),
      ]);

      params.set(QueryFields.EMBED, new QueryParamsEmbed({ embeds: [ PatientModel.apiEmbeds.patient ] }));

      patientModel = await _patientModelCtl.get(_idParam, { params });
    } catch (e) {
      if (!(e instanceof Exception) || e.code !== 404) throw e;
      await goBack();

      throw e;
    }

    loading = false;
  };

  /** @returns Promise<void> */
  const savePatientModel = async () => {
    loading = true;

    if (!_patientModelForm.validateForm()) {
      CommonNotifications.validationError();
      loading = false;
      return;
    }

    /** @type BlobStorageExceptionCtx */
    const fileCtx = {
      path: `${ SessionManager.userId() }/patient-models/${ patientModel.id }`,
      filename: patientModel.filename,
      newFilenames: _patientModelForm.getDropzoneUploadFile().getLocalFiles().map((f) => f.name),
    };

    try {
      await _patientModelForm.getDropzoneUploadFile().uploadOperation();
    } catch (e) {
      if (!(e instanceof Exception)) {
        loading = false;
        throw PlatformException.uploadFileToBlobStorage({ fromError: e, extraArgs: { fileCtx } });
      }

      e.extraArgs = { ...(e.extraArgs ?? {}), fileCtx };
      if (e.code !== ExceptionBlobStorage.errorOnFileDeletion) {
        loading = false;
        throw e;
      }

      // new video uploaded, but old not removed, so we notify without break the flow
      await PlatformException.notifyError(e, { ignoreUiNotifications: true });
    }

    try {
      await _patientModelCtl.patch(patientModel.id, patientModel);
      CommonNotifications.genericSuccess($t("notification.entity.patient-model.success.edit"));
      await goBack();
    } catch (e) {
      throw PlatformException.uploadFileToBlobStorage({
        fromError: e,
        extraArgs: { ...(e.extraArgs ?? {}), fileCtx },
      });
    } finally {
      loading = false;
    }
  };

  /** @returns Promise<void> */
  const deletePatientModel = async () => {
    if (!(await CommonAlerts.deleteOrDisableConfirmation($t("entity.patient-model.entity-name"), {
      gender: i18nGender.MALE,
    }))) return;

    /** @type BlobStorageExceptionCtx */
    const fileCtx = {
      path: `${ SessionManager.userId() }/patient-models/${ patientModel.id }`,
      filename: patientModel.filename,
    };

    const deleteUrl = (await _patientModelCtl.getDeleteSignedUrl(patientModel.id)).deleteUrl;

    try {
      await _patientModelCtl.delete(patientModel.id);
    } catch (e) {
      loading = false;
      CommonNotifications.genericDanger($t("notification.entity.patient-model.error.delete"));
      throw PlatformException.deleteFileToBlobStorage({ fromError: e, extraArgs: { ...(e.extraArgs ?? {}), fileCtx } });
    }

    try {
      await (new BlobStorageController()).delete(deleteUrl);
    } catch (e) {
      e.extraArgs = { ...(e.extraArgs ?? {}), fileCtx };
      await PlatformException.notifyError(e, { ignoreUiNotifications: true });
    } finally {
      CommonNotifications.genericSuccess($t("notification.entity.patient-model.success.delete"));
      await removePatternAndGoBack();
      loading = false;
    }
  };

  /** @returns Promise<void> */
  const removePatternAndGoBack = async () => {
    loading = true;
    await navigatorHistory.removePatternAndGoBack(
      Routes.PATIENT_MODELS,
      new RegExp(`${Routes.PATIENT_MODELS}/${patientModel.id}/?`),
    );
  };

  /** @returns Promise<void> */
  const goBack = async () => {
    await navigatorHistory.goBack(`${ Routes.PATIENT_MODELS }/${ patientModel.patientId }`);
  };

  $effect(() => {
    if (navigating && page.params.id
      && navigating.to?.params?.id === page.params.id
      && page.params.id !== _idParam) {
      _idParam = page.params.id;
      loadPatientModelData().then();
    }
  });
</script>

<svelte:head>
  <title>{$t('route.generic-organs-model-edit.title')}</title>
</svelte:head>

{#if !checkingGrants}
  <div class="page-content">
    <div class="page-content-title mt-0 d-flex justify-content-between">{$t('route.patient-model-edit.title')}</div>
    <LoadingContentPage {loading} class="mb-3"/>

    <form onsubmit={savePatientModel}>
      <div class="row mx-0">
        <div class="col-12 col-lg-10 col-xl-6">
          <PatientModelForm
              bind:this={_patientModelForm}
              {patientModel}
              readonly={loading}/>
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

            {#if entityAccess.del !== PermissionsGrantType.NONE && patientModel}
              <BaseButton
                  className="mb-2 mr-0 mr-sm-2 mb-sm-0"
                  type="danger"
                  disabled={loading}
                  onclick={deletePatientModel}>
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

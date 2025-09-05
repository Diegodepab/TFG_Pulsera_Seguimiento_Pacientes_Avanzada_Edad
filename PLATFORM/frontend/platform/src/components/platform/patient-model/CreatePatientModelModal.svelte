<script>
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import BaseCardModal from "$components/platform/commons/BaseCardModal.svelte";
  import LoadingContentPage from "$components/platform/commons/LoadingContentPage.svelte";
  import PatientModelForm from "$components/platform/patient-model/PatientModelForm.svelte";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { SessionManager } from "$lib/commons/session_manager";
  import { PatientModelController } from "$lib/controllers/patient_model_controller";
  import { Exception } from "$lib/exceptions/exception";
  import { ExceptionBlobStorage } from "$lib/exceptions/exception_codes";
  import { PlatformException } from "$lib/exceptions/platform_exception";
  import { PatientModel } from "$lib/models/patient_model";
  import { onMount } from "svelte";

  import { t } from "svelte-i18n";


  /**
   * @typedef {Object} CreatePatientModelModalProps
   * @property {string} patientId - patient id
   * @property {string} [subtitle=""] - text to display under the title
   * @property {(model: PatientModel) => void} [onSaved] - callback which executes when 'save' button is pressed and form is validated
   */

  /** @type CreatePatientModelModalProps */
  let {
    /** @type string */ patientId,
    /** @type string */ subtitle = "",
    /** @type {(model: PatientModel) => void} */ onSaved,
  } = $props();

  /** @type boolean */
  let loading = $state(true);

  let patientModel = $state(PatientModel.empty());

  /** @type PatientModelController */
  const _patientModelCtl = new PatientModelController();

  /** @type PatientModelForm  */
  let _patientModelForm = $state();

  /** @type BaseCardModal  */
  let _modal = $state();

  /** @returns void */
  export const openModal = () => _modal.openModal();

  /** @returns void */
  export const CloseModal = () => _modal.closeModal();

  /** @type OnMount */
  onMount(() => loading = false);

  /** @returns Promise<void> */
  const save = async () => {

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

      // new model uploaded, but old not removed, so we notify without break the flow
      await PlatformException.notifyError(e, { ignoreUiNotifications: true });
    }

    try {
      patientModel.patientId = patientId;
      patientModel = await _patientModelCtl.post(patientModel);
      CommonNotifications.genericSuccess($t("notification.entity.generic-organs-model.success.add"));
    } catch (error) {
      CommonNotifications.genericDanger($t("notification.entity.generic-organs-model.error.add"));
    } finally {
      loading = false;
    }
    onSaved(patientModel);
    CloseModal();
  };

  const onSubmit = async () => {
    loading = true;
    if (!_patientModelForm.validateForm()) {
      CommonNotifications.validationError();
      loading = false;
      return;
    }
    try {
      await save();
    } finally {
      loading = false;
    }
  };
</script>
<form onsubmit={onSubmit}>
  <BaseCardModal
      allowOutsideClick={false}
      bind:this={_modal}
      bodyResponsiveHeight="auto"
      modalBodyMaxHeight="500px"
      modalMaxWidth="700px"
      onCloseModal={() => patientModel = PatientModel.empty()}
      setHtmlOverflowHidden
      size="lg">

    {#snippet headerSnippet()}
      <div>
        <p class="modal-title">{$t('modal.create-patient-model.header')}</p>
        <LoadingContentPage class="my-1" {loading}/>
        {#if subtitle}
          <p class="modal-subtitle mt-0 text-danger-dark">{subtitle}</p>
        {/if}
      </div>
    {/snippet}

    {#snippet body()}
      <div>
        <PatientModelForm
            bind:patientModel
            bind:this={_patientModelForm}
            displayOnModal
            {patientId}
            readonly={loading}
        />
      </div>
    {/snippet}

    {#snippet footerSnippet()}
      <div>
        <BaseButton class="m-0" disabled={loading} onclick={_modal.closeModal} type="light">
          <span class="btn-inner--text">{$t('common.button.cancel')}</span>
        </BaseButton>

        <BaseButton disabled={loading} nativeType="submit" type="success">
          <span class="btn-inner--text">{$t('common.button.save')}</span>
        </BaseButton>
      </div>
    {/snippet}

  </BaseCardModal>
</form>
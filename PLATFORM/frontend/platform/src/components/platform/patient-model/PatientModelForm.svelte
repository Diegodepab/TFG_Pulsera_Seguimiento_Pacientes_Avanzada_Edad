<svelte:options/>
<script>
  import BaseInput from "$components/argon_template/Inputs/BaseInput.svelte";
  import {
    DropzoneFileType,
    DropzoneUploadFileUtils,
  } from "$components/platform/uploadFile/dropzone_upload_file_utils";
  import DropzoneUploadFile from "$components/platform/uploadFile/DropzoneUploadFile.svelte";
  import { PatientModelController } from "$lib/controllers/patient_model_controller";
  import { PatientModel } from "$lib/models/patient_model";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";

  /** @type boolean */
  let disabledFields = $derived(loading || readonly);

  /** @type boolean */
  let loading = $state(true);

  /** @type BaseInput */
  let _patientModelNameInput = $state();

  /** @type string */
  const _patientModelNameField = $t("entity.patient-model.name");

  /** @type BaseInput */
  let _patientModelPatientCodeInput = $state();

  /** @type string */
  const _patientModelPatientCodeField = $t("entity.patient-model.patientCode");


  /**
   * @typedef {Object} PatientModelFormProps
   * @property {PatientModel} [patientModel]
   * @property {boolean} [readonly]
   /// This prop should be only used to exec GarbageCollector methods declared on it. It should be changed.
   * @property {DropzoneUploadFile} [dropzoneUploadFile]
   */

  /** @type PatientModelFormProps */
  let {
    patientModel = $bindable(PatientModel.empty()),
    readonly = false,
    dropzoneUploadFile = $bindable(),
  } = $props();

  /** @type BlobFile */
  let currentFile = $state();

  /** @type PatientModelController */
  const _patientModelCtl = new PatientModelController();

  /** @type OnMount */
  onMount(async () => {
    loading = false;
  });

  $effect(() => {
    if (patientModel.blobDisplayUrl && (!currentFile || currentFile.id != patientModel?.id)) {
      currentFile = {
        id: patientModel.id,
        name: patientModel.filename,
        url: patientModel.url,/*  */
        displayUrl: patientModel.blobDisplayUrl,
        original: true,
      };
    }
  });

  /**
   * Sets the patient model properties based on the provided file from a custom event.
   * @param {BlobFile} file - The file object containing the id, url, and name of the patient model.
   */
  const setPatientModelBlob = (file) => {
    patientModel.id ??= Number(file.id);
    patientModel.url = file.url;
    patientModel.filename = file.name;
  };

  /** @returns boolean */
  export const validateForm = () => {
    const validators = [
      _patientModelNameInput,
      dropzoneUploadFile,
    ];

    return !validators.map((el) => el.validate()).includes(false);
  };

  /**
   * get instance component DropzoneUploadFile
   * @return {DropzoneUploadFile} dropzoneUploadFile
   */
  export const getDropzoneUploadFile = () => {
    return dropzoneUploadFile;
  };
</script>

<div class="mx-2">
  {#if !loading}
    <div class="row d-block">
      <BaseInput
          bind:this={_patientModelNameInput}
          type="text"
          name={_patientModelNameField}
          label={_patientModelNameField}
          placeholder={_patientModelNameField}
          value={patientModel.name}
          onchange={(event) => patientModel.name = event.target.value}
          customRequired
          readonly={disabledFields}
      />
      {#if patientModel?.patient?.code}
        <BaseInput
            bind:this={_patientModelPatientCodeInput}
            type="text"
            name={_patientModelPatientCodeField}
            label={_patientModelPatientCodeField}
            placeholder={_patientModelPatientCodeField}
            value={patientModel?.patient?.code}
            customRequired
            readonly
        />
      {/if}
    </div>

    <div class="col-12 px-0">
      <DropzoneUploadFile
          bind:this={dropzoneUploadFile}
          allowedType={DropzoneFileType.model}
          allowedFileTypes={DropzoneUploadFileUtils.MODEL_FILE_TYPES}
          blobFile={currentFile}
          controller={_patientModelCtl}
          disabled={disabledFields}
          displayTags
          onchangedfile={setPatientModelBlob}
          required
          showDeleteBtn={false}
          showUploadBtn={false}
      />
    </div>
  {/if}
</div>

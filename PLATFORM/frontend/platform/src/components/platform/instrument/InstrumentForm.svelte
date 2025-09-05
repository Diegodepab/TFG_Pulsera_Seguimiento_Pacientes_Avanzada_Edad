<svelte:options/>
<script>
  import BaseInput from "$components/argon_template/Inputs/BaseInput.svelte";
  import {
    DropzoneFileType,
    DropzoneUploadFileUtils,
  } from "$components/platform/uploadFile/dropzone_upload_file_utils";
  import DropzoneUploadFile from "$components/platform/uploadFile/DropzoneUploadFile.svelte";
  import { InstrumentController } from "$lib/controllers/instrument_controller";
  import { Instrument } from "$lib/models/instrument";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";

  /**
   * @typedef {Object} IntrumentFormProps
   * @property {Instrument} [instrument]
   * @property {boolean} [readonly]
   * @property {DropzoneUploadFile} dropzoneUploadFile
   */

  /** @type IntrumentFormProps */
  let {
    /** @type Instrument */ instrument = $bindable(Instrument.empty()),
    /** @type boolean */ readonly = false,
    /// This prop should be only used to exec GarbageCollector methods declared on it. It should be changed.
    /** @type DropzoneUploadFile */ dropzoneUploadFile = $bindable(),
  } = $props();

  /** @type BlobFile */
  let currentFile = $state();

  /** @type InstrumentController */
  const _instrumentCtl = new InstrumentController();

  onMount(async () => {
    loading = false;
  });

  $effect(() => {
    if (instrument.blobDisplayUrl && (!currentFile || currentFile.id != instrument?.id)) {
      currentFile = {
        id: instrument.id,
        name: instrument.filename,
        url: instrument.url,
        displayUrl: instrument.blobDisplayUrl,
        original: true,
      };
    }
  });

  /** @type boolean */
  let loading = $state(true);

  /** @type boolean */
  let disabledFields = $derived(loading || readonly);

  /** @type BaseInput */
  let _instrumentNameInput = $state();

  /** @type string */
  const _instrumentNameField = $t("entity.instrument.name");

  /** @type BaseInput */
  let _instrumentModelInput = $state();

  /** @type string */
  const _instrumentModelField = $t("entity.instrument.model");

  /**
   * Sets the instrument properties based on the provided file from a custom event.
   * @param {BlobFile} file - The file object containing the id, url, and name of the instrument.
   */
  const setInstrumentBlob = (file) => {
    instrument.id ??= Number(file.id);
    instrument.url = file.url;
    instrument.filename = file.name;
  };

  /** @returns boolean */
  export const validateForm = () => {
    const validators = [
      _instrumentNameInput,
      _instrumentModelInput,
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
          bind:this={_instrumentNameInput}
          type="text"
          name={_instrumentNameField}
          label={_instrumentNameField}
          placeholder={_instrumentNameField}
          value={instrument.name}
          onchange={(event) => instrument.name = event.target.value}
          customRequired
          readonly={disabledFields}
      />

      <BaseInput
          bind:this={_instrumentModelInput}
          type="text"
          name={_instrumentModelField}
          label={_instrumentModelField}
          placeholder={_instrumentModelField}
          value={instrument.model}
          onchange={(event) => instrument.model = event.target.value}
          customRequired
          readonly={disabledFields}
      />

      <div class="col-12 px-0">
        <DropzoneUploadFile
            bind:this={dropzoneUploadFile}
            allowedType={DropzoneFileType.model}
            allowedFileTypes={DropzoneUploadFileUtils.MODEL_FILE_TYPES}
            blobFile={currentFile}
            controller={_instrumentCtl}
            disabled={disabledFields}
            displayTags
            onchangedfile={setInstrumentBlob}
            required
            showDeleteBtn={false}
            showUploadBtn={false}
        />
      </div>
    </div>
  {/if}
</div>
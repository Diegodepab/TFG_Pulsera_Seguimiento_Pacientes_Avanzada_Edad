<script>
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import BaseProgress from "$components/argon_template/BaseProgress.svelte";
  import InputLabel from "$components/platform/commons/InputLabel.svelte";
  import {
    DropzoneFileType,
    DropzoneFileUseMode,
    DropzoneUploadFileUtils,
  } from "$components/platform/uploadFile/dropzone_upload_file_utils";
  import DropzoneUploadFileItem from "$components/platform/uploadFile/DropzoneUploadFileItem.svelte";
  import { BaseController } from "$lib/controllers/base_controller";
  import { BlobStorageController } from "$lib/controllers/blob_storage/blob_storage_controller";
  import { Exception } from "$lib/exceptions/exception";
  import { ExceptionBlobStorage } from "$lib/exceptions/exception_codes";
  import { PlatformException } from "$lib/exceptions/platform_exception";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";

  /**
   * @typedef {Object} DropzoneUploadFileProps
   * @property {string} [classNames=''] - Additional CSS classes to apply to the component
   * @property {number | null} [sizeLimitKb = null] - Maximum file size in kilobytes
   * @property {string | null} [error = ''] - Error message to display
   * @property {boolean} [required = false] - Whether the file upload is required
   * @property {boolean} [disabled = false] - Whether the dropzone is disabled
   * @property {string | null} [label = null] - Label text to display above the dropzone
   * @property {string[]} [allowedFileTypes = []] - Array of allowed file extensions
   * @property {boolean} [allowedRestoreFile = false] - Whether file restoration is allowed
   * @property {boolean} [allowedUploadSameName = false] - Whether uploading files with the same name is allowed
   * @property {boolean} [showRestoreFileBtn = false] - Whether to show the restore file button
   * @property {boolean} [showAcceptedFileTypes = true] - Whether to show the list of accepted file types
   * @property {boolean} [showFilename = true] - Whether to display the filename
   * @property {boolean} [displayTags = false] - Whether to display status tags on files
   * @property {boolean} [auto = false] - Whether to automatically upload files on selection
   * @property {boolean} [showUploadBtn = !auto] - Whether to show the upload button
   * @property {boolean} [showDeleteBtn = !auto] - Whether to show the delete button
   * @property {BlobFile | null} [blobFile = null] - Currently uploaded blob file
   * @property {BaseController} [controller] - Controller for handling blob storage operations
   * @property {Record<string, unknown>} [entityPathParams = {}] - Additional path parameters for API calls
   * @property {(files: File[]) => void} [ondraggedfile] - Callback when files are dragged into the dropzone
   * @property {(file: BlobFile) => void} [onchangedfile] - Callback when the blob file changes
   * @property {(files: File[]) => void} [onuploadfiles] - Callback when files are uploaded
   * @property {(files: (BlobFile | File)[], { local: boolean }) => void} [onremovefiles] - Callback when files are removed
   * @property {() => void} [onrestorefile] - Callback when the file is restored
   * @property {DropzoneFileUseMode} [useMode = DropzoneFileUseMode.STANDALONE] - Mode of operation (STANDALONE or EXTERNAL)
   * @property {DropzoneFileType} [allowedType = DropzoneFileType.model] - Type of file allowed (model, image, video)
   * @property {() => (string | null)} [validator = null] - Custom validation function
   * @property {(event: Event) => void} [onclick = (event) => null] - Callback for click events
   */

  /** @type DropzoneUploadFileProps */
  let {
    /** @type string */ classNames = "",
    /** @type {number | null} */ sizeLimitKb = null,
    /** @type {string | null} */ error = "",
    /** @type boolean */ required = false,
    /** @type boolean */ disabled = false,
    /** @type {string | null} */ label = null,
    /** @type string[] */ allowedFileTypes = [],
    /** @type boolean */ allowedRestoreFile = false,
    /** @type boolean */ allowedUploadSameName = false,
    /** @type boolean */ showRestoreFileBtn = false,
    /** @type boolean */ showAcceptedFileTypes = true,
    /** @type boolean */ showFilename = true,
    /** @type boolean */ displayTags = false,
    /** @type boolean */ auto = false,
    /** @type boolean */ showUploadBtn = !auto,
    /** @type boolean */ showDeleteBtn = !auto,
    /** @type {BlobFile | null} */ blobFile = null,
    /** @type BaseController */ controller,
    /** @type {Record<string, unknown>} */ entityPathParams = {},
    /** @type {(files: File[]) => void} */ ondraggedfile,
    /** @type {(file: BlobFile) => void} */ onchangedfile,
    /** @type {(files: File[]) => void} */ onuploadfiles,
    /** @type {(files: (BlobFile | File)[], { local: boolean }) => void} */ onremovefiles,
    /** @type {() => void} */ onrestorefile,
    /** @type DropzoneFileUseMode */ useMode = DropzoneFileUseMode.STANDALONE,
    /** @type DropzoneFileType */ allowedType = DropzoneFileType.model,
    /** @type {() => (string | null)} */ validator = null,
    /** @type {(event: Event) => void} */ onclick = () => null,
  } = $props();

  /**
   * @param {Event} e
   */
  const _onclick = (e) => {
    e.stopPropagation();
    e.preventDefault();
    onclick(e);
  };

  /** @type boolean */
  const __multiple = false;

  /** @type boolean */
  let _uploading = $state(false);

  /** @type boolean */
  let _removing = false;

  /** @type File[] */
  let _localFiles = $state([]);

  /** @type string[] */
  let _warnings = $state([]);

  /** @type BlobStorageController */
  const _blobCtl = new BlobStorageController();

  /** @type {number | null} */
  let currentUploadIndex = $state(null);

  /** @type UploadProgressData[] */
  let progressData = $state([]);

  /** @type boolean */
  let dragging = $state(false);

  /** Starts dragging. */
  const startDragging = (e) => {
    e.preventDefault?.();
    dragging = true;
  };

  /**
   * @param {Event} e
   */
  const stopDragging = (e) => {
    e.preventDefault?.();
    dragging = false;
  };

  /** @type HTMLInputElement */
  let fileInputVirtual;

  onMount(async () => {
    fileInputVirtual = DropzoneUploadFileUtils.buildInputFile({
      onInput: onFile,
      multiple: __multiple,
      accept: allowedFileTypes.join(","),
    });
  });

  /**
   * Handles file input from drag-and-drop or file selection.
   * @param {Event | DragEvent} e - The event triggered by file input.
   */
  const onFile = (e) => {
    stopDragging(e);
    if (disabled) return;


    let addedFiles = [];

    if (e instanceof DragEvent) {
      addedFiles = Array.from(e.dataTransfer.files ?? []).map((f) => f);
    } else {
      const target = e.target;
      addedFiles = Array.from(target.files ?? []).map((f) => f);
      target.value = "";
    }

    if (allowedUploadSameName) {
      addedFiles.forEach((file) => {
        if (file.name === blobFile?.name) {
          const renameFile = new File([ file.slice(0) ], _renameFilePrefix(file.name), { type: file.type });
          addedFiles = addedFiles.map((_f) => _f === file ? renameFile : _f);
        }
      });
    }

    _warnings = [];
    error = null;

    const _validFiles = [];
    for (const f of addedFiles) {
      if (!validateLocalFile(f)) continue;
      _validFiles.push(f);
      progressData.push({ uploading: undefined, progress: 0 });
      if (!__multiple) break;
    }

    if (!_validFiles.length) return;

    _localFiles = _validFiles;  // replace current local files with the new added files
    ondraggedfile?.(_localFiles);

    if (!auto) return;
    uploadOperation();
  };

  /**
   * Validates a local file based on its name, extension, and size.
   *
   * @param {File} file - The file to validate.
   * @returns boolean - Returns true if the file is valid, otherwise false.
   */
  const validateLocalFile = (file) => {
    let warn = null;
    const _fileExtension = DropzoneUploadFileUtils.getFileExtension(file.name);

    if (DropzoneUploadFileUtils.hasForbiddenChars(file.name)) {
      warn = $t("component.upload-dropzone.warning.forbidden-chars", {
        values: { chars: DropzoneUploadFileUtils.FILE_FORBIDDEN_CHARS.join(", ") },
      });
    } else if (allowedFileTypes?.length && !allowedFileTypes.includes(_fileExtension)) {
      warn = $t("component.upload-dropzone.warning.invalid-extension");
    } else if (!!sizeLimitKb && (sizeLimitKb * 1000) < file.size) {
      warn = $t("component.upload-dropzone.warning.invalid-size");
    }

    if (warn) {
      _warnings.push(warn);
      _warnings.push($t("component.upload-dropzone.warning.invalid-extension"));
    }

    return !warn;
  };

  /**
   * Handles the upload progress by updating the progress data.
   *
   * @param {number} value - The current upload value.
   * @param {number} total - The total value for the upload.
   * @returns void
   */
  const onUpload = (value, total) => {
    const data = progressData.at(currentUploadIndex);
    data.progress = (value / total) * 100;
    data.uploading = data.progress !== 100;
    progressData = progressData;
  };

  /**
   * Prepares signed arguments for uploading a file.
   *
   * @param {File} file - The file to be uploaded.
   * @returns Promise<UploadResponse> - The signed URL response for the upload.
   */
  const prepareSignedArgs = async (file) => {
    // NOTE: POST also replaces the file if it already exists (so, we do POST to simplify)
    return await controller.getPostSignedUrl(file, {
      reservedId: blobFile?.id,
      extraArgs: { ...(entityPathParams ?? {}) },
    });
  };

  /**
   * Checks if there are local files to upload.
   *
   * @returns boolean - True if there are local files, false otherwise.
   */
  export const willUploadFile = () => !!_localFiles.length;

  /**
   * Checks if there is a blob file to delete.
   *
   * @returns boolean - True if a blob file exists, false otherwise.
   */
  export const willDeleteFile = () => !!blobFile;

  /**
   * Uploads the current local files to the cloud.
   *
   * @returns Promise<void>
   * @throws Error - Throws an error if the file can't be uploaded.
   */
  const _uploadFileToCloud = async () => {
    if (!_localFiles.length) return;

    try {
      _uploading = true;
      currentUploadIndex = 0;
      const localFile = _localFiles.at(currentUploadIndex);
      const data = progressData.at(currentUploadIndex);

      const signedArgs = await prepareSignedArgs(localFile);
      data.uploading = true;
      progressData = progressData;

      const blobData = await _blobCtl.upload(signedArgs, localFile, { onUpload });

      const prevBlobFile = blobFile; // save value from prev blobFile to delete it if necessary
      await _updateBlobFileAfterUpload(signedArgs, blobData); // rebuild blobFile with new information

      // delete a file if there was already one with a different name
      if (prevBlobFile && prevBlobFile.name !== blobFile?.name) {
        await _removeFileFromCloud(prevBlobFile);
      }

      if (currentUploadIndex + 1 >= _localFiles.length) {
        _localFiles = [];
        progressData = [];
        currentUploadIndex = null;
        return;
      }
      currentUploadIndex++;
    } catch (e) {
      if (e instanceof Exception && e.code === ExceptionBlobStorage.errorOnFileDeletion) throw e;

      if (_localFiles.length) { // reset all files progress
        progressData.forEach((f) => {
          f.uploading = false;
          f.progress = 0;
        });
        progressData = progressData;
      }

      throw e;
    } finally {
      _uploading = false;
    }
  };

  /**
   * Updates the blob file information after a successful upload.
   *
   * @param {UploadResponse} signedArgs - The signed URL response for the upload.
   * @param {BlobStorageResponse} blobData - The response containing blob data.
   * @returns void
   */
  const _updateBlobFileAfterUpload = (signedArgs, blobData) => {
    blobFile = {
      id: blobFile?.id ?? signedArgs.reservedId,
      url: decodeURIComponent(blobData.blobUrl),
      name: decodeURIComponent((new URL(blobData.blobUrl)).pathname.split("/").at(-1)),
      displayUrl: signedArgs.displayUrl,
      deleteUrl: signedArgs.deleteUrl,
    };

    onchangedfile?.(blobFile);
  };


  /**
   * Sets the local files to be uploaded.
   *
   * @param {File[]} files - The array of files to be uploaded.
   * @returns void
   */
  export const setLocalFiles = (files) => {
    _localFiles = files;
  };

  /**
   * Retrieves the current local files pending to be uploaded.
   *
   * @returns File[] - The array of local files.
   */
  export const getLocalFiles = () => _localFiles;

  /**
   * Performs the upload operation for the specified files.
   *
   * @param {File[]} [files] - The files to upload. If not provided, uses the current local files.
   * @returns Promise<void>
   */
  export const uploadOperation = async (files) => {
    const _files = files ?? _localFiles ?? [];
    if (!_files.length) return;

    if (useMode === DropzoneFileUseMode.EXTERNAL) {
      onuploadfiles?.(_files);
      return;
    }

    // standalone
    await _uploadFileToCloud();
    onuploadfiles?.(_files);
  };

  /**
   * Deletes a file based on the provided options.
   *
   * @param {Object} [opts] - Options for the delete operation.
   * @param {boolean} [opts.local] - If true, deletes the file ONLY locally.
   * @returns Promise<void>
   */
  export const deleteOperation = async ({ local } = {}) => {
    if (local) {
      const _locals = _localFiles;
      setLocalFiles([]);
      onremovefiles?.(_locals, { local: true });
      return;
    }

    const _blobFile = blobFile; // reference copy
    if (useMode === DropzoneFileUseMode.EXTERNAL) {
      _removeFileLocally();
      onremovefiles?.([ _blobFile ]);
      return;
    }

    // standalone
    await _removeFileFromCloud(blobFile);
    onremovefiles?.([ _blobFile ]);
  };

  /**
   * Removes a file locally by resetting the blobFile reference.
   */
  const _removeFileLocally = () => {
    _removing = true;
    blobFile = null;
    _removing = false;
  };

  /**
   * Removes a file from the cloud.
   *
   * @param {BlobFile} file - The file to be removed from the cloud.
   * @returns Promise<void>
   * @throws PlatformException - Throws an error if delete signed url can´t get.
   */
  const _removeFileFromCloud = async (file) => {
    if (!file) return;
    _removing = true;

    try {
      file.deleteUrl ??= (
        await controller.getDeleteSignedUrl(file.id, { extraArgs: { ...(entityPathParams ?? {}) } })
      ).deleteUrl;
    } catch (e) {
      _removing = false;
      throw PlatformException.errorOnGetDeleteUrl({
        fromError: e,
        extraArgs: {
          original: file.original ?? false,
          fileId: file.id,
        },
      });
    }

    try {
      await _blobCtl.delete(file.deleteUrl);
      blobFile = null;
    } finally {
      _removing = false;
    }
  };

  /**
   * Renames a file by incrementing its suffix.
   *
   * @param {string} filename - The original filename.
   * @returns string - The new filename with an incremented suffix.
   */
  const _renameFilePrefix = (filename) => {
    const partsFilename = filename.split(".");
    const name = partsFilename[0];
    const extension = partsFilename[1];
    let newName;

    const matchPrefix = name.match(/_(\d+)$/); // Look for a suffix “_n” at the end of the file name.
    if (matchPrefix) {
      const number = parseInt(matchPrefix[1]) + 1; // Increment the number
      newName = name.replace(matchPrefix[0], `_${ number }`);
    } else {
      newName = `${ name }_1`; // If no suffix found, add “_1”
    }

    return `${ newName }.${ extension }`;
  };

  /**
   * Restores a file by dispatching a restore event.
   */
  const restoreFile = (e) => {
    e.stopPropagation();
    e.preventDefault();
    onrestorefile?.();
  };

  /**
   * Validates the current file state.
   * @returns boolean
   */
  export const validate = () => {
    _warnings = [];

    if (!required) return true;
    error = null;

    if (!blobFile && !_localFiles.length) {
      error = $t("common.form.field.required", { values: { field: label } });
    }
    if (validator) {
      error = validator() ?? error;
    }
    return error == null;
  };

  /**
   * Triggers a click event on the virtual file input.
   */
  const onClickInput = () => {
    if (!fileInputVirtual || disabled || _uploading || _removing) return;
    fileInputVirtual.click();
  };
</script>

{#if label}
  <InputLabel {label} {required}/>
{/if}

{#if error}
  <div class="invalid-feedback d-block mb-2">{error}</div>
{/if}

<div class="upload-dz {classNames}" class:disabled class:hovered={dragging}>
  <div
      onclick={onClickInput}
      ondragleave={stopDragging}
      ondragover={startDragging}
      ondrop={onFile}
  >
    <div class="upload-dz-hint" class:p-2={disabled}>
      {#if !disabled}
        <div class="d-flex align-items-center justify-content-start">
          <i class="fas fa-file-upload fa-fw"></i>
          <span class="text-xs text-left ml-1">
            {$t('component.upload-dropzone.drag-files', { values: { multiple: __multiple.toString() } })}
          </span>
        </div>
        <hr class="w-100 my-2">
      {/if}
      <div class="d-flex justify-content-start align-items-start flex-wrap">
        {#if blobFile}
          <div class="d-flex flex-column w-100">
            {#if displayTags && !disabled}
              {@const tagType = _localFiles.length ? 'remove' : 'active'}
              <div class="upload-dz-tag ellipsis-wrap {tagType}-tag" onclick={_onclick}>
                {$t(`component.upload-dropzone.tags.${ tagType }`)}
              </div>
            {/if}
            <DropzoneUploadFileItem
                type={allowedType}
                fileName={blobFile.name}
                url={new URL(blobFile.displayUrl)}
                toRemove={!!_localFiles.length}
                showInformation={showFilename}
                showPreview
            />
            {#if !disabled && showDeleteBtn && !_localFiles.length}
              <div class="align-self-end m-1 d-flex justify-content-end">
                <BaseButton outline type="danger" size="xs" defaultPrevented onclick={deleteOperation}>
                  <i class="fas {_uploading ? 'fa-spin fa-sync-alt' : 'fa-trash'} fa-fw"></i>
                </BaseButton>
              </div>
            {/if}
          </div>
        {/if}

        {#if !disabled && !!blobFile && !!_localFiles.length}
          <hr class="w-100 my-2">
        {/if}

        {#if allowedRestoreFile && showRestoreFileBtn}
          <div class="d-flex gap-1 flex-column align-items-start pointer"
               onclick={restoreFile}>
            <div class="warn-nt bg-warning-light soft-warning-content text-xs border-rad-2 px-2 py-1">
              <i class="fas fa-triangle-exclamation fa-lg fa-fw"></i>
              <span>{$t('component.upload-dropzone.restore-file')}</span>
            </div>
          </div>
        {/if}

        {#if _warnings?.length}
          <div class="d-flex gap-1 flex-column align-items-start">
            {#each _warnings as warn}
              <div class="warn-nt bg-warning-light soft-warning-content text-xs border-rad-2 px-2 py-1">
                <i class="fas fa-triangle-exclamation fa-lg fa-fw"></i>
                <span>{warn}</span>
              </div>
            {/each}
          </div>
        {/if}
        {#if _localFiles.length}
          <!-- current files to upload area -->
          <div class="d-flex flex-column w-100">
            {#if displayTags}
              <div class="upload-dz-tag upload-tag ellipsis-wrap" onclick={_onclick}>
                {$t('component.upload-dropzone.tags.upload')}
              </div>
            {/if}
            {#each _localFiles as file, idx (file.name)}
              {@const isUrl = !(file instanceof File)}
              <DropzoneUploadFileItem
                  type={allowedType}
                  class="mb-1"
                  fileName={file.name}
                  url={!isUrl ? URL.createObjectURL(file) : file}
                  showInformation={showFilename}
                  showPreview
              />
              {@const data = progressData.at(idx)}
              {#if _uploading && data.uploading != null}
                <BaseProgress
                    animated={data.uploading}
                    striped={data.uploading}
                    progressClasses="m-0"
                    type={data.uploading ? 'primary' : 'success'}
                    height={3}
                    value={data.progress}
                />
              {:else}
                <div style="height: 4px; width: 100%"></div>
              {/if}

              {#if !disabled}
                <div class="align-self-end m-1 d-flex justify-content-end">
                  {#if showDeleteBtn}
                    <BaseButton outline type="danger" size="xs" defaultPrevented
                                onclick={() => deleteOperation({ local: true })}>
                      <i class="fas {_uploading ? 'fa-spin fa-sync-alt' : 'fa-trash'} fa-fw"></i>
                    </BaseButton>
                  {/if}
                  {#if showUploadBtn}
                    <BaseButton
                        outline type="primary" size="xs"
                        defaultPrevented
                        disabled={!_localFiles.length}
                        onclick={_uploadFileToCloud}
                    >
                      <i class="fas {_uploading ? 'fa-spin fa-sync-alt' : 'fa-upload'} fa-fw"></i>
                    </BaseButton>
                  {/if}
                </div>
              {/if}
            {/each}
          </div>
        {/if}
      </div>
      {#if true || !disabled && showUploadBtn}
        <div
            class="align-self-end m-1 d-flex justify-content-end"
        >
        </div>
      {/if}
    </div>
  </div>
</div>

{#if showAcceptedFileTypes}
  <div class="text-xs font-italic mt-1 text-gray">
    {$t('component.upload-dropzone.accepted-types', { values: { types: allowedFileTypes.join(', ') } })}
  </div>
{/if}

{#if (
  sizeLimitKb ?? 0
) > 0}
  <div class="text-xs font-italic mt-1 text-gray">
    {$t('component.upload-dropzone.limit-size', { values: { size: DropzoneUploadFileUtils.improveSizeUnit(sizeLimitKb) } })}
  </div>
{/if}

<style>
  .upload-dz {
    position: relative;
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-orient: vertical;
    -webkit-box-direction: normal;
    -ms-flex-direction: column;
    flex-direction: column;
    border: 0.05rem dashed var(--border-regular-color);
    border-radius: .375rem;
  }

  .upload-dz label {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 0;
    cursor: pointer;
  }

  .upload-dz.disabled label {
    cursor: default !important;
  }

  .upload-dz:not(.disabled):hover,
  .upload-dz:not(.disabled).hovered {
    border-color: var(--input-text-color);
  }

  .upload-dz-hint {
    padding: 1rem 0.5rem 0 0.5rem;
    width: 100%;
    text-align: center;
    overflow: hidden;
    color: var(--input-text-color);
    -webkit-transition: all .15s ease;
    transition: all .15s ease;
    -webkit-box-ordinal-group: 0;
    -ms-flex-order: -1;
    order: -1;
  }

  .upload-dz:hover .upload-dz-hint,
  .upload-dz.hovered .upload-dz-hint {
    border-color: var(--input-text-color);
    color: #525F7F;
  }

  .upload-dz-tag {
    max-width: 100%;
    width: max-content;
    color: #F3F3F3;
    font-weight: 600;
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
  }

  .upload-dz-tag.active-tag {
    background-color: var(--primary-regular-color-dark);
  }

  .upload-dz-tag.remove-tag {
    background-color: var(--danger-regular-color);
  }

  .upload-dz-tag.upload-tag {
    background-color: var(--info-regular-color);
  }

  .warn-nt {
    text-align: start;
  }

  .warn-nt > span {
    text-wrap: auto;
  }

</style>
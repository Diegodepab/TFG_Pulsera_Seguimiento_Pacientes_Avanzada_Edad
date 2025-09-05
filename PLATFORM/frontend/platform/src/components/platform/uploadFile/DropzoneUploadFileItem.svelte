<script>
  import ThreeViewer from "$components/platform/instrument/ThreeViewer.svelte";
  import { DropzoneFileType } from "$components/platform/uploadFile/dropzone_upload_file_utils";
  import { t } from "svelte-i18n";

  /**
   * @typedef {Object} DropZoneItemProps
   * @property {DropzoneFileType} [type=DropzoneFileType.video] - Type of file in the dropzone (video, image, model)
   * @property {boolean} [showPreview=false] - Whether to display a preview of the file
   * @property {boolean} [showInformation=false] - Whether to show the file information section
   * @property {string} [url] - URL path to the file for preview purposes
   * @property {string} [fileName=""] - Name of the file to display in the information section
   * @property {boolean} [toRemove=false] - Indicates if the file is marked for removal (changes styling)
   * @property {string} [classname=""] - Additional CSS classes to apply to the component
   * @property {boolean} [asPlaceholder=false] - Whether to display the item as a placeholder
   */

  /** @type DropZoneItemProps */
  let {
    /** @type string */ className = "",
    /** @type DropzoneFileType */ type = DropzoneFileType.video,
    /** @type boolean */ showPreview = false,
    /** @type boolean */ showInformation = false,
    /** @type string */ url,
    /** @type string */ fileName = "",
    /** @type boolean */ toRemove = false,
    /** @type boolean */ asPlaceholder = false,
  } = $props();

  /**
   * @param {Event} e
   * @returns void
   */
  const _onclick = (e) => {
    e.stopPropagation();
    e.preventDefault();
  };

</script>

<div class="w-100 my-1 {className}" onclick={_onclick}>
  {#if showPreview && url}
    <div class="d-flex">
      <div class="d-flex justify-content-center dz-preview">
        {#if type === DropzoneFileType.video}
          <!-- TODO-->
          <!-- <BaseVideo controls playsinline src={url} />-->
        {:else if type === DropzoneFileType.image}
          <img src={url} alt=""/>
        {:else if type === DropzoneFileType.model}
          <ThreeViewer {url}/>
        {/if}
      </div>
    </div>
  {/if}

  {#if showInformation}
    <div
        class="mx-1 d-flex justify-content-start align-items-baseline text-xs {toRemove ? 'text-through text-danger-dark' : 'text-primary'}"
        class:mt-2={showPreview}
    >
      <i class="fal {toRemove ? 'fa-file-slash' : 'fa-file'} fa-fw sm"></i>
      <a class="ml-2 text-left" target="_blank">{fileName ?? $t('common.label.no-information')}</a>
    </div>
  {/if}
</div>

<style>
  .dz-preview {
    margin: auto;
    width: 90%;
  }

  .dz-preview img {
    width: 100%;
    border: 0.05rem solid var(--primary-regular-color-60);
    border-radius: 0.25rem;
    padding: 0.05rem;
  }
</style>

<script>
  import BaseInput from "$components/argon_template/Inputs/BaseInput.svelte";
  import { Pathology } from "$lib/models/pathology";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";
  /**
   * @typedef {Object} PathologyProps
   * @property {Pathology} [pathology]
   * @property {boolean} [readonly]
   * @property {boolean} [disabledFields]
   */

  /** @type PathologyProps */
  let {
    /** @type Pathology */ pathology = $bindable(Pathology.empty()),
    /** @type boolean */ readonly = false,
  } = $props();

  /** @type boolean */
  let disabledFields = $derived(loading || readonly);

  /** @type boolean */
  let loading = $state(true);

  /** @type BaseInput */
  let _pathologyNameInput = $state();
  /** @type string */
  const _pathologyNameField = $t("entity.pathology.name");

  /** @type OnMount */
  onMount(async () => {
    loading = false;
  });

  /** @returns boolean */
  export const validateForm = () => {
    const validators = [
      _pathologyNameInput,
    ];
    return !validators.map((el) => el.validate()).includes(false);
  };

</script>

<div class="mx-2">
  {#if !loading}
    <div class="row d-block">
      <BaseInput
          bind:this={_pathologyNameInput}
          type="text"
          name={_pathologyNameField}
          label={_pathologyNameField}
          placeholder={_pathologyNameField}
          value={pathology.name}
          onchange={(event) => pathology.name = event.target.value}
          customRequired
          readonly={disabledFields}
      />
    </div>
  {/if}
</div>
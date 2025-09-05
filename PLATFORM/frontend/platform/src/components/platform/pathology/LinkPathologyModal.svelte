<script>
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import BaseCardModal from "$components/platform/commons/BaseCardModal.svelte";
  import InfinityList from "$components/platform/commons/infinity_list/InfinityList.svelte";
  import PatientPathologyInfinityItem
    from "$components/platform/commons/infinity_list/PatientPathologyInfinityItem.svelte";
  import LoadingContentPage from "$components/platform/commons/LoadingContentPage.svelte";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { DateUtils, InputValidators } from "$lib/commons/utils";
  import { PathologyController } from "$lib/controllers/pathology_controller";
  import { PatientController } from "$lib/controllers/patient_controller";
  import { PathologySuggestionListDC } from "$lib/models/data_containers/pathology_suggestion_list_dc";
  import { PatientPathologyListDC } from "$lib/models/data_containers/patient_pathology_list_dc";
  import { Pathology } from "$lib/models/pathology";
  import { PatientPathology } from "$lib/models/patient_pathology";
  import { QueryFields, QueryParamsEmbed } from "$lib/services/utils/query_utils";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";

  /**
   * @typedef {Object} LinkPathologyProps
   * @property {Patient} patient
   * @property {PatientPathology[]} [linkedPathologies]
   * @property {(data: PatientPathologyListDC[]) => void} [onSaved]
   */

  /** @type LinkPathologyProps */
  let {
    /** @type Patient */ patient,
    /** @type PatientPathology[] */ linkedPathologies = [],
    /** @type {(results: PatientPathology[]) => void} */ onSaved,
  } = $props();

  /** @type PatientController */
  const patientCtl = new PatientController();

  /** @type PathologyController */
  const pathologyCtl = new PathologyController();

  /** @type boolean */
  let loading = $state(true);

  /** @type BaseCardModal */
  let _modal = $state();

  /** @type PathologySuggestionListDC[] */
  let preselectedItems = $derived(linkedPathologies.map((i) => {
    return new PathologySuggestionListDC({
      id: i.pathologyId,
      name: i.pathology?.name,
      detectionDate: i.detectionDate,
    });
  }));

  /** @returns void */
  export const openModal = () => _modal.openModal();

  /** @type InfinityList **/
  let _infinityList = $state();

  /** @type HTMLElement **/
  let slotBody = $state();

  /** @type OnMount */
  onMount(() => {
    loading = false;
  });

  /** @returns Promise<void> */
  const save = async () => {
    /** @type Set<PathologySuggestionListDC> */
    const _pathologies = _infinityList?.getItemsSelected() ?? new Set();

    // formatted patient-pathology to upload correctly
    const _itemsToSave = Array.from(_pathologies).map((item) => {
      return new PatientPathology(patient.id, item.id, item.detectionDate);
    });

    // TODO. SELECTION SHOULD BE VALIDATED, BUT SHOULD BE DONE WITH A METHOD OR GIVING InfinityList A VALIDATOR METHOD
    if (_itemsToSave.some((e) => !e.detectionDate || !!InputValidators.validateNotFutureDate(e.detectionDate, $t))) {
      CommonNotifications.validationError();
      return;
    }

    /** @type PatientPathology[] */
    const patientPathologies = await patientCtl.multiLinkPathologies(patient.id, _itemsToSave);
    CommonNotifications.genericSuccess($t("notification.entity.patient-pathology.success.link"));

    onSaved(patientPathologies);
    _modal.closeModal();
  };

  const onSubmit = async () => {
    loading = true;
    try {
      await save();
    } finally {
      loading = false;
    }
  };

  const scrollableFunction = async (opts) => {
    opts ??= {};
    /** @type {Map<QueryFields, unknown>} */
    opts.params ??= new Map();
    opts.params.set(
      QueryFields.EMBED,
      new QueryParamsEmbed({ embeds: [ Pathology.apiEmbeds.patientPathologies ] }),
    );

    return await pathologyCtl.search({
      ...opts,
      transformer: async (data) => {
        const suggPathology = (await Pathology.transformer(data)).toDC(PathologySuggestionListDC);
        if (suggPathology.patientPathologies?.length) {
          // set its prev detection date if the patient already has it linked
          const _patientMatch = suggPathology.patientPathologies.find((pp) => pp.patientId === patient.id);
          if (_patientMatch) suggPathology.detectionDate = _patientMatch.detectionDate;
        }

        return suggPathology;
      },
    });
  };
</script>

<form onsubmit={onSubmit}>
  <BaseCardModal
      allowOutsideClick={false}
      bind:this={_modal}
      bodyResponsiveHeight="auto"
      modalBodyMaxHeight="600px"
      modalMaxWidth="600px"
      setHtmlOverflowHidden
      size="sm"
  >
    {#snippet headerSnippet()}
      <div>
        <p class="modal-title">{$t('modal.patient-pathology.header')}</p>
        <LoadingContentPage class="my-1" {loading}/>
      </div>
    {/snippet}
    {#snippet body()}
      <div bind:this={slotBody}>
        <InfinityList
            bind:this={_infinityList}
            itemComponent={PatientPathologyInfinityItem}
            itemsPerPage={20}
            limitToSearch={5}
            {preselectedItems}
            scrollListenerEl={slotBody?.parentElement}
            {scrollableFunction}
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

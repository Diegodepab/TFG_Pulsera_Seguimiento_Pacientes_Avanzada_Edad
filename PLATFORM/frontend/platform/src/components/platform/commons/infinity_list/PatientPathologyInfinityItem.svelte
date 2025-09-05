<script>
  import BaseDateInput from "$components/platform/commons/BaseDateInput.svelte";
  import { DateUtils, InputValidators } from "$lib/commons/utils";
  import moment from "moment";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";

  /**
   * @typedef {Object} InfinityItemProps
   * @property {PathologySuggestionListDC} item - pathology item
   * @property {boolean} [selected=false] - whether the item is selected or no
   * @property {(selected: boolean, item: any) => void} [onSelect]
   */

  /** @type InfinityItemProps */
  let {
    /** @type PathologySuggestionListDC */ item = $bindable(),
    /** @type boolean */ selected = $bindable(false),
    /** @type {(selected: boolean, item: any) => void} */ onSelect,
  } = $props();

  const onTapItem = () => {
    selected = !selected;
    if (selected) item.detectionDate ??= moment();
    onSelect?.(selected, item);
  };

  onMount(() => {
    validate();
  });

  /**
   * Update the value of the detectionDate and update the Set selected
   * @param {moment.Moment} value - Value of detectionDate
   */
  const onUpdateDetectionDate = (value) => {
    item.detectionDate = value;
    onSelect?.(selected, item);
  };

  /** @type BaseDateInput */
  let _detectionDateInput = $state();

  export const validate = () => {
    _detectionDateInput?.validate();
  };

</script>

{#if item?.name}
  <div class="list--item border" class:selected onclick={onTapItem}>
    <p>{item.name}</p>
    {#if selected}
      <div class="date-item-selected">
        <div class="infinity-item-date-input" onclick={(e) => e.stopPropagation()}>
          <BaseDateInput
              bind:this={_detectionDateInput}
              inputGroupClasses="input-group-sm"
              formGroupClasses="d-flex flex-column justify-content-center align-items-end"
              value={item.detectionDate}
              onchange={onUpdateDetectionDate}
              updateValueOnInput={false}
              customRequired
              validator={({ value, defaultValidator }) => {
              return defaultValidator(item.detectionDate) || InputValidators.validateNotFutureDate(item.detectionDate, $t);
            }}
          />
        </div>
      </div>
    {/if}
  </div>
{/if}

<style>
  .list--item {
    display: flex;
    width: 100%;
    justify-content: space-between;
    align-items: center;
    background-color: #fff;
    border-radius: 5px;
    margin-top: 0.5rem;
  }

  .list--item p {
    font-size: 0.85rem;
    vertical-align: middle;
    padding: 0.5rem 0 0.5rem 0.5rem;
    margin: 0;
  }

  .date-item-selected {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
  }

  .infinity-item-date-input {
    margin: 0.5rem 1rem 0.25rem 0;
  }

  .list--item.border.selected {
    border-color: var(--success-regular-color) !important;
  }

</style>

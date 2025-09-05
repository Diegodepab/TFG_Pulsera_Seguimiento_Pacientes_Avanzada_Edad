<script>
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import BaseProgress from "$components/argon_template/BaseProgress.svelte";
  import BaseInput from "$components/argon_template/Inputs/BaseInput.svelte";
  import { BaseTableColSortType } from "$components/platform/commons/base_table/base_table_utils";
  import BaseSelect from "$components/platform/commons/BaseSelect.svelte";
  import { navigatorHistory, pagesCache } from "$lib/commons/stores";
  import { Debounce } from "$lib/commons/utils";
  import { BaseDC } from "$lib/models/data_containers/base_dc";
  import { BaseSelectListDC } from "$lib/models/data_containers/base_select_list_dc";
  import {
    QueryFields,
    QueryParamsQ,
    QueryParamsRaw,
    QueryParamsSort,
    QuerySortOrder,
  } from "$lib/services/utils/query_utils";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";
  import { get } from "svelte/store";

  /**
   * @typedef {Object} BaseTableProps
   * @property {string} [theadClasses=""] - CSS classes for the table header
   * @property {string} [tbodyClasses=""] - CSS classes for the table body
   * @property {string} [tableClasses=""] - CSS classes for the entire table
   * @property {string|null} [pageId=null] - Identifier for the page, used for context synchronization
   * @property {boolean} [syncLoadDataContext] - Whether to synchronize the load data context with the page ID
   * @property {string} [tableTitle=""] - Title of the table
   * @property {boolean} [showOptions=true] - Whether to show table options
   * @property {boolean} [showSnippet=true] - Whether to show snippets
   * @property {boolean} [showExtraActionsSnippet=true] - Whether to show extra actions snippet
   * @property {boolean} [showPagination=true] - Whether to show pagination controls
   * @property {BaseSelectListDC[]} [itemsPerPageOptions=[{ value: 50 }]] - Array of options for items per page selection
   * @property {BaseSelectListDC} [itemsPerPage] - Selected option for items per page
   * @property {BaseTableColDefinition[]} [columns=[]] - Array of column definitions
   * @property {string[]} [hiddenColumnKeys=[]] - Array of column keys to hide
   * @property {boolean} [rowClickable=true] - Whether rows are clickable
   * @property {boolean} [includeFts=true] - Whether to include full-text search
   * @property {string} [ftsText=""] - Full-text search query text
   * @property {BaseTableScrollableFunction} [scrollableFunction=null] - Function to load data with scrolling/pagination
   * @property {Snippet} [globalActionsSnippet=null] - Snippet for global table actions
   * @property {Snippet} [extraActionsSnippet=null] - Snippet for additional actions
   * @property {Snippet} [widgetColumnSnippet=null] - Snippet for rendering widget columns
   * @property {({ row: number, item: any }) => void} [onrowclick=()=>null] - Handler for row click events
   * @property {BaseDC} [DataContainerClass=BaseDC]
   */

  /** @type BaseTableProps */
  let {
    /** @type string */ theadClasses = "",
    /** @type string */ tbodyClasses = "",
    /** @type string */ tableClasses = "",
    /** @type {string | null} */ pageId = null,
    /** @type boolean */ syncLoadDataContext = pageId != null,
    /** @type string */ tableTitle = "",
    /** @type boolean */ showOptions = true,
    /** @type boolean */ showSnippet = true,
    /** @type boolean */ showExtraActionsSnippet = true,
    /** @type boolean */ showPagination = true,
    /** @type BaseSelectListDC[] */ itemsPerPageOptions = [ new BaseSelectListDC({ value: 50 }) ],
    /** @type BaseSelectListDC */ itemsPerPage = itemsPerPageOptions.at(0),
    /** @type BaseTableColDefinition[] */ columns = [],
    /** @type string[] */ hiddenColumnKeys = [],
    /** @type boolean */ rowClickable = true,
    /** @type boolean */ includeFts = true,
    /** @type string */ ftsText = "",
    /** @type BaseTableScrollableFunction */ scrollableFunction = null,
    /** @type Snippet */ children = null,
    /** @type Snippet */ globalActionsSnippet = null,
    /** @type Snippet */ extraActionsSnippet = null,
    /** @type Snippet */ widgetColumnSnippet = null,
    /** @type {({ row: number, item: any }) => void} */ onrowclick = () => null,
    /** @type BaseDC */ DataContainerClass = BaseDC,
  } = $props();

  /** @type Debounce */
  const _debounce = new Debounce(250);

  /** @type boolean */
  let loading = $state(true);

  /** @type string */
  let currentFtsText;

  /** @type boolean */
  let ftsTextAvoidReactive = false;

  /** @type ColumnsSortMap */
  let columnsSortMap = $state(new Map());

  /** @type ColumnsQFilterMap */
  let columnsQFilterMap = new Map();

  /** @type SearchResults */
  let searchResult = $state();

  /** @type {(BaseModel|BaseDC)[]} */
  let items = $derived(searchResult?.items ?? []);


  $effect(() => {
    if (!(ftsText ?? currentFtsText)?.length) return;
    currentFtsText = ftsText;

    if (!ftsTextAvoidReactive) {
      onFtsSearch();
    } else {
      ftsTextAvoidReactive = false;
    }
  });

  /** @type onMount */
  onMount(() => {
    itemsPerPage ??= itemsPerPageOptions.at(0);
    if (syncLoadDataContext && pageId) {
      loadLoadDataContext();
    } else {
      loadData();
    }
  });

  /** @return {(BaseModel|BaseDC)[]} */
  export const getItems = () => items ?? [];

  /** @return void */
  export const refreshCurrentItems = () => {
    this.items = items;
  };

  /**
   * Updates the load data context with optional pagination page.
   * @param {Object} [opts] - Optional parameters.
   * @param {string} [opts.paginationPage] - The pagination page.
   * @return void
   */
  const updateLoadDataContext = ({ paginationPage } = {}) => {
    if (pageId == null) return;

    const cache = get(pagesCache).cache;
    const pageCache = cache.get(pageId) ?? {};
    pageCache.loadDataContext = getLoadDataContext({ paginationPage });

    cache.set(pageId, pageCache);
  };

  /** @return void */
  const loadLoadDataContext = () => {
    const pageCache = get(pagesCache).cache.get(pageId);
    setLoadDataContext(pageCache?.loadDataContext);
  };

  /**
   * Gets the load data context with optional pagination page.
   * @param {Object} [opts] - Optional parameters.
   * @param {string} [opts.paginationPage] - The pagination page.
   * @return LoadDataContext - The load data context object.
   */
  const getLoadDataContext = ({ paginationPage } = {}) => {
    return { ftsText, columnsSortMap, columnsQFilterMap, paginationPage };
  };

  /**
   * Sets the load data context and loads data accordingly.
   * @param {LoadDataContext} dataContext - The load data context to set.
   * @return Promise<void> - A promise that resolves when the load data operation is completed.
   */
  const setLoadDataContext = (dataContext) => {
    if (dataContext == null) return loadData();

    columnsSortMap = dataContext.columnsSortMap;
    columnsQFilterMap = dataContext.columnsQFilterMap;

    if (dataContext.paginationPage != null) {
      ftsTextAvoidReactive = true;
      ftsText = dataContext.ftsText;
      return loadData({ page: dataContext.paginationPage });
    }

    if (!dataContext.ftsText && !currentFtsText) return loadData();

    ftsText = dataContext.ftsText;
  };

  /**
   * Loads data asynchronously with optional parameters.
   * @param {Object} [opts] - Optional parameters.
   * @param {string} [opts.page] - The pagination page.
   * @param {Map<QueryFields, unknown>} [opts.params] - Additional query parameters.
   * @return Promise<void> - A promise that resolves when the data loading operation is completed.
   */
  export const loadData = async ({ page, params } = {}) => {
    if (syncLoadDataContext) updateLoadDataContext({ paginationPage: page });

    loading = true;
    params ??= new Map();

    try {
      if (page?.length > 0) {
        searchResult = await scrollableFunction({ page });
        return;
      }

      const qFilter = buildQFilters();
      if (qFilter.length > 0) {
        if (params.get(QueryFields.Q)) {
          params.get(QueryFields.Q).push(qFilter);
        } else {
          params.set(QueryFields.Q, qFilter);
        }
      }

      const sortParams = buildSortParams();
      if (sortParams.length > 0) params.set(QueryFields.SORT, sortParams);
      if (ftsText) params.set(QueryFields.RAW, [ new QueryParamsRaw({ field: "fts", value: ftsText }) ]);
      if (!params.has(QueryFields.LIMIT)) params.set(QueryFields.LIMIT, itemsPerPage.value);

      searchResult = await scrollableFunction({ page, params });

    } finally {
      loading = false;
    }
  };

  /**
   * Retrieves the value of an item based on the provided column key.
   * @param {Object} item - The item from which to retrieve the value.
   * @param {string} columnKey - The column key specifying the path to the value within the item.
   * @param {string} undefinedScapeChar='-' - The character to use when the value is undefined.
   * @return * - The value of the item corresponding to the column key.
   */
  const itemValue = (item, columnKey, undefinedScapeChar = "-") => {
    /** @type string[] */
    const keys = columnKey.split(".");
    if (keys.length === 1) return item[columnKey] ?? undefinedScapeChar;

    const key = keys.shift();
    if (item[key] == null) return undefinedScapeChar;

    return itemValue(item[key], keys.join("."), undefinedScapeChar);
  };

  /** @return QueryParamsQ[] */
  const buildQFilters = () => {
    /** @type QueryParamsQ[] */
    const qFilters = [];

    for (const [ column, values ] of columnsQFilterMap) {
      qFilters.push(...DataContainerClass.getQFiltersFromUiField(column, values));
    }

    return qFilters;
  };

  /** @return QueryParamsSort[] */
  const buildSortParams = () => {
    /** @type QueryParamsSort[] */
    const sortParams = [];

    for (const [ column, value ] of columnsSortMap) {
      if (value !== BaseTableColSortType.UN_SORT) {
        const _value = value === BaseTableColSortType.ASC ? QuerySortOrder.ASC : QuerySortOrder.DESC;
        sortParams.push(...DataContainerClass.getSortParamFromUiField(column, _value));
      }
    }

    return sortParams;
  };


  /**
   * Handles row click event.
   * @param {Event} event - The event object.
   * @param {number} row - The index of the clicked row.
   * @param {*} item - The item associated with the clicked row.
   * @return void
   */
  const onRowClicked = (event, row, item) => {
    if (document.getSelection()?.type === "Range") return;
    onrowclick({ row, item });
  };

  /** @return void */
  export const cleanFilters = () => {
    currentFtsText = "";
    ftsText = "";
    columnsSortMap.clear();
    columnsQFilterMap.clear();

    columnsSortMap = columnsSortMap;
    columnsQFilterMap = columnsQFilterMap;

    loadData();
  };

  /** @return void */
  const onFtsSearch = () => _debounce.debounce(loadData);

  /**
   * Handles the sort event for a column.
   * @param {BaseTableColDefinition} column - The column definition.
   * @return void
   */
  const onSort = (column) => {
    const key = column.key;

    switch (columnsSortMap.get(key)) {
      case BaseTableColSortType.ASC:
        columnsSortMap.set(key, BaseTableColSortType.DESC);
        break;

      case BaseTableColSortType.DESC:
        columnsSortMap.set(key, BaseTableColSortType.UN_SORT);
        break;

      default:
        columnsSortMap.set(key, BaseTableColSortType.ASC);
    }

    columnsSortMap = columnsSortMap;
    loadData();
  };

  /**
   * Handles the query filter event for a column.
   * @param {BaseTableColDefinition} column - The column definition.
   * @param {(string|number)[]} selectedItems - The selected items for the query filter.
   * @return void
   */
  const onQFilter = (column, selectedItems) => {
    const key = column.key;
    columnsQFilterMap.set(key, selectedItems);
    columnsQFilterMap = columnsQFilterMap;
    loadData();
  };

  /**
   * Shows the column filter modal for a given column.
   * @param {BaseTableColDefinition} column - The column definition.
   * @return Promise<void> - A promise that resolves when the column filter modal is shown.
   */
  const showColumnFilter = async (column) => {
    // create or show the modal using the config information
    // 'accept' event should call to 'onQFilter' with the selected items
    // only for testing
    onQFilter(
      column,
      (await column.filterSettings.scrollableFunction()).map((item) => item.id),
    );
  };

  /** @return Promise<void> */
  const goBack = async () => await navigatorHistory.goBack("/");

  /**
   * Update the selected option and reload the data, and then call loadData().
   * @param {BaseSelectListDC} newValue
   */
  const onItemsPerPageChange = (newValue) => {
    if (typeof newValue === "object" && newValue !== null && newValue.value !== undefined) {
      itemsPerPage = newValue;
    } else {
      itemsPerPage = new BaseSelectListDC({ value: newValue });
    }
    loadData();
  };
</script>

{#if tableTitle.length > 0 && !showOptions && !showSnippet}
  <div class="table-list-title">{tableTitle}</div>
{/if}

{#if showOptions}
  <div class="d-flex justify-content-between px-1 align-items-center">
    {#if tableTitle.length > 0}
      <div class="table-list-title">{tableTitle}</div>
    {/if}

    <div class="pr-0 d-flex justify-content-end">
      <div class="mr-2">
        <BaseButton type="primary" size="sm" onclick={goBack}>
          <i class="fas fa-arrow-left fa-fw"></i>
        </BaseButton>
      </div>
      <div class="card-header-action-separator"></div>


      {#if globalActionsSnippet}
        {@render globalActionsSnippet()}
      {/if}

      <div>
        <BaseButton type="primary" size="sm" onclick={cleanFilters}>
          <i class="fas fa-rotate fa-fw"></i>
        </BaseButton>
      </div>
    </div>
  </div>

  {#if extraActionsSnippet && showExtraActionsSnippet}
    {@render extraActionsSnippet()}
  {/if}

  <div class="col-12 d-flex justify-content-between flex-wrap px-1 mt-3">
    <div class="col-4 col-md-2 pl-0 mb-4">
      <BaseSelect
          --height="28px"
          selectClasses="form-control input-group-alternative input-group-sm border-none"
          clearable={false}
          searchable={false}
          hideEmptyState
          items={itemsPerPageOptions}
          bind:value={itemsPerPage}
          showChevron
          itemId="value"
          itemLabel="value"
          onchange={onItemsPerPageChange}
      />
    </div>

    {#if includeFts}
      <div class="col-6 col-md-4 col-xl-3 pr-0">
        <BaseInput
            type="text"
            inputGroupClasses="input-group-sm"
            placeholder={$t('common.list-entity.fts')}
            updateValueOnInput
            bind:value={ftsText}
            alternative
        >
          {#snippet appendSnippet()}
            <i class="fas fa-search pointer" onclick={loadData}></i>
          {/snippet}
        </BaseInput>
      </div>
    {/if}
  </div>
{:else if showSnippet}
  <div class="d-flex justify-content-between align-items-center">
    {#if tableTitle.length > 0}
      <div class="table-list-title mb-3">{tableTitle}</div>
    {/if}

    <div class="pr-0 d-flex justify-content-end">
      {#if globalActionsSnippet}
        {@render globalActionsSnippet()}
      {/if}
    </div>
  </div>
{/if}

{#if loading}
  <BaseProgress striped animated type="success" height={4} value={100}/>
{/if}

<table class="table table-responsive {tableClasses}" class:mt-4={!showOptions && loading}>
  <thead class={theadClasses}>
  <tr>
    {#if children}
      {@render children({ test: columns })}
    {:else}
      {#each columns.filter((c) => !hiddenColumnKeys.includes(c.key)) as column}
        {@const sortable = column.sortable ?? true}
        <th
            class="py-0"
            class:sorting_asc={columnsSortMap.get(column.key) === BaseTableColSortType.ASC}
            class:sorting_desc={columnsSortMap.get(column.key) === BaseTableColSortType.DESC}
            style="min-width: {column.minWidth}; max-width: {column.maxWidth}; width: {column.width};"
        >
          <span class="{sortable ? 'pointer' : 'no-sortable'}" onclick={() => sortable ? onSort(column) : null}>
            {column.label}
            {#if sortable}
              <span class="caret-wrapper">
                <i class="sort-caret ascending"></i>
                <i class="sort-caret descending"></i>
              </span>
            {/if}
          </span>

          {#if column.filterSettings}
            <span class="pointer" onclick={() => showColumnFilter(column)}>
              <i class="fas fa-filter"></i>
            </span>
          {/if}
        </th>
      {/each}
    {/if}

  </tr>
  </thead>

  {#if !loading}
    <tbody class={tbodyClasses}>
    {#each items as item, index}
      <tr
          class:bg-row-alt={index % 2 !== 0}
          class:row-with-action={rowClickable}
          onclick={(event) => (rowClickable ? onRowClicked(event, index, item) : null)}
      >
        {#each columns.filter((c) => !hiddenColumnKeys.includes(c.key)) as column}
          <td class={column.tdStyler ? column.tdStyler(item) : ''}>
            {#if column.widgetColumn}
              {#if widgetColumnSnippet}
                {@render widgetColumnSnippet({ item, column, row: index })}
              {/if}
            {:else if column.customValue}
              {column.customValue(item)}
            {:else}
              {column.valueFormatter
                ? column.valueFormatter(itemValue(item, column.key))
                : itemValue(item, column.key)}
            {/if}
          </td>
        {/each}
      </tr>
    {/each}
    </tbody>
  {/if}
</table>

<div class="card-footer table-footer d-flex justify-content-end flex-row w-100">
  {#if showPagination}
    {@const hasPrevious = !!searchResult?.previous}
    {@const hasNext = !!searchResult?.next}
    <ul
        role="menubar"
        aria-disabled="false"
        aria-label="Pagination"
        class="pagination b-pagination"
    >
      <BaseButton
          type="primary"
          size="sm"
          disabled={!hasPrevious}
          className={!hasPrevious ? 'btn-page-disabled' : ''}
          onclick={!hasPrevious ? () => null : () => loadData({ page: searchResult?.first })}
      >
        <span class="btn-inner--text">{$t('common.list-entity.button.first')}</span>
      </BaseButton>

      <BaseButton
          type="primary"
          size="sm"
          disabled={!hasPrevious}
          className={!hasPrevious ? 'btn-page-disabled' : ''}
          onclick={!hasPrevious ? () => null : () => loadData({ page: searchResult?.previous })}
      >
        <span class="btn-inner--text">{$t('common.list-entity.button.prev')}</span>
      </BaseButton>

      <BaseButton
          type="primary"
          size="sm"
          disabled={!hasNext}
          className={!hasNext ? 'btn-page-disabled' : ''}
          onclick={!hasNext ? () => null : () => loadData({ page: searchResult?.next })}
      >
        <span class="btn-inner--text">{$t('common.list-entity.button.next')}</span>
      </BaseButton>
    </ul>
  {/if}
</div>

<style>
  .bg-row-alt {
    background-color: #f6f5f5;
  }

  tbody td:last-child {
    width: 100%;
  }

  .row-with-action {
    cursor: pointer;
  }

  .card-header-action-separator {
    height: 80%;
    width: 1px;
    border-right: 1px var(--light) solid;
    margin-right: 0.5rem;
    justify-self: center;
    align-self: center;
  }

  .no-sortable {
    height: 34px !important;
    display: flex;
    align-items: center;
  }
</style>
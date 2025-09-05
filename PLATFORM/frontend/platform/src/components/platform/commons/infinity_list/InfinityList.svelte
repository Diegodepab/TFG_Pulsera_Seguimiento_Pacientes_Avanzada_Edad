<script>
  import BaseCheckbox from "$components/argon_template/Inputs/BaseCheckbox.svelte";
  import BaseInput from "$components/argon_template/Inputs/BaseInput.svelte";
  import { Debounce } from "$lib/commons/utils";
  import { BaseModel } from "$lib/models/base_model";
  import { BaseDC } from "$lib/models/data_containers/base_dc";
  import { SearchResults } from "$lib/models/search_results";
  import { QueryFields, QueryParamsRaw } from "$lib/services/utils/query_utils";
  import { onDestroy, onMount, tick } from "svelte";
  import { t } from "svelte-i18n";

  // TODO. UPDATE THIS WITH TPV-WEB INFINITY-LIST

  /**
   * @typedef {Object} InfinityListProps
   * @property {number} [itemsPerPage]
   * @property {number} [limitToSearch]
   * @property {Set<BaseModel | BaseDC>} [preselectedItems]
   * @property {any} [itemComponent]
   * @property {string} [className = ""]
   * @property {string} [itemId = "id"]
   * @property {string} [itemLabel = "name"]
   * @property {boolean} [includeFts]
   * @property {string} [ftsText = $bindable("")]
   * @property {any} scrollableFunction - Represents a function for scrolling through a base table.
   */

  /** @type InfinityListProps */
  let {
    itemsPerPage = 50,
    limitToSearch = 10,
    preselectedItems = new Set(),
    itemComponent = null,
    className = "",
    itemId = "id",
    itemLabel = "name",
    includeFts = true,
    ftsText = $bindable(""),
    scrollableFunction,
  } = $props();

  /** @type boolean */
  let searching = $state(false);

  /** @type {SearchResults<BaseModel | BaseDC>} */
  let searchResult;

  /** @type {(BaseModel | BaseDC)[]} */
  let _items = $state([]);

  /** @type {Set<BaseModel | BaseDC>} */
  let selected = $state(new Set());

  /** @type {HTMLDivElement | null} */
  let listEl = $state(null);

  /** @type {HTMLDivElement | null} */
  let itemsContainerEl = $state(null);

  /** @type string */
  let currentFtsText = "";

  let isFirstPage = true;

  const _debounce = new Debounce(250);

  onMount(async () => {
    await init();
  });

  onDestroy(() => itemsContainerEl?.removeEventListener("scroll", checkScroll));

  const init = async () => {
    if (itemsContainerEl) itemsContainerEl.removeEventListener("scroll", checkScroll);
    itemsContainerEl?.addEventListener("scroll", checkScroll);

    preselectedItems?.forEach((item) => {
      if (!itemExistsOnSelection(item)) selected.add(item);
    });

    await checkScroll();
  };

  /**
   * @param {boolean} isChecked
   * @param {BaseModel | BaseDC} item
   */
  const onToggleItem = (isChecked, item) => {
    if (item == null) return;
    if (isChecked) {
      if (itemExistsOnSelection(item)) { // UPDATE
        selected = new Set(Array.from(selected).filter(s => s.getOwnPropertyValue(itemId) !== item.getOwnPropertyValue(itemId))); // Clean prev item
        selected.add(item);
      } else { // ADD
        selected.add(item);
      }
    } else { // DELETE
      selected = new Set(Array.from(selected).filter(s => s.getOwnPropertyValue(itemId) !== item.getOwnPropertyValue(itemId))); // Clean prev item
    }
  };

  /**
   * This get count item unread
   * @return {number}
   */
  const getUnreadItemCount = () => {
    if (!itemsContainerEl) return 0;

    const { bottom: parentBottom } = itemsContainerEl.getBoundingClientRect();

    const siblings = Array.from(itemsContainerEl?.children ?? []);
    const itemRead = siblings.filter((div) => {
      const { bottom } = div.getBoundingClientRect();
      if (bottom <= parentBottom) return true;
    });

    // Vars item read
    const lastRead = itemRead.at(-1);
    const indexLastRead = lastRead ? siblings.indexOf(lastRead) : 0;

    // Check if you are missing half of your item limitPerPage
    return siblings.length - indexLastRead;
  };

  /**
   * Function that checks if it needs to order more items and if so, orders them.
   * @return Promise<void>
   */
  const checkScroll = async () => {
    if (searching) return;

    searching = true;
    const unreadItemCount = getUnreadItemCount();

    if (unreadItemCount <= limitToSearch) {
      const params = new Map();
      params.set(QueryFields.LIMIT, itemsPerPage);

      // We do not search for more
      if (_items.length && !searchResult?.next) {
        searching = false;
        return;
      }

      await loadData();

      await checkScroll();
    }

    searching = false;
  };

 /**
 * Function where it will do the search and load the data in the list.
 * @return Promise<void>
 */
export const loadData = async () => {
  const params = new Map();

  params.set(QueryFields.LIMIT, itemsPerPage);
  if (currentFtsText) {
    params.set(
      QueryFields.RAW,
      [ new QueryParamsRaw({ field: "fts", value: currentFtsText }) ]
    );
  }

  // Si es la primera página, reiniciamos el listado
  if (isFirstPage) {
    isFirstPage = false;
    _items = [];
  }

  try {
    searching = true;

    // === CORRECCIÓN: reescribir `next` absoluto a ruta relativa ===
    let pageParam = searchResult?.next;
    if (pageParam && (pageParam.startsWith("http://") || pageParam.startsWith("https://"))) {
      try {
        const u = new URL(pageParam);
        pageParam = u.pathname + u.search;
      } catch {
        // Si URL() falla, dejamos el valor original
      }
    }

    // Llamamos al scrollableFunction con el cursor corregido
    searchResult = await scrollableFunction({
      params,
      page: pageParam || undefined
    });

    // Agregar ítems nuevos sin duplicados
    searchResult.items.forEach((i) => {
      const exists = _items.find(
        (item) => item.getOwnPropertyValue(itemId) === i.getOwnPropertyValue(itemId)
      );
      if (!exists) _items.push(i);
    });

    // Reactividad
    _items = _items;

    await tick(); // esperamos a que Svelte monte los nuevos elementos
  } catch (e) {
    console.error("error", e);
  } finally {
    searching = false;
  }
};


  /** @return {void} */
  const onFtsSearch = () => {
    _debounce.cancel();

    _debounce.debounce(() => {
      isFirstPage = true;
      searchResult.next = "";
      loadData();
    });
  };

  /**
   * External function that returns the selected list
   * @return {Set<BaseModel | BaseDC>}
   */
  export const getItemsSelected = () => selected;

  /**
   * Function that returns the identifier dynamically
   * @param {any} item Items from which the reference will be taken
   * @return {unknown}
   */
  const _getItemReference = (item) => item[itemId];

  /**
   * It will check if that item is selected
   * @param {any} item Items from which the reference will be taken
   * @return boolean
   */
  const itemExistsOnSelection = (item) => {
    return Array.from(selected).some((e) => _getItemReference(e) === _getItemReference(item));
  };

  /** Executes when fts is a callback */
  const onChangeFts = () => {
    if (!(ftsText ?? currentFtsText)?.length) return;
    currentFtsText = ftsText;
    onFtsSearch();
  };

</script>

<div bind:this={listEl} class="infinity-list {className ? className : ''}>}">
  {#if includeFts}
    <div class="">
      <BaseInput
          type="text"
          inputGroupClasses="input-group-sm"
          placeholder={$t('common.list-entity.fts')}
          updateValueOnInput
          bind:value={ftsText}
          onchange={() => onChangeFts()}
          alternative
          append
      >
        {#snippet appendSnippet()}
          <i class="fas fa-search pointer" onclick={loadData} role="button" tabindex="0"></i>
        {/snippet}
      </BaseInput>
    </div>
  {/if}

  <!-- Items -->
  <div bind:this={itemsContainerEl} class="infinity-list--items-container">
    {#if !!_items.length}
      {#each _items as item (item.getOwnPropertyValue(itemId))}
        {#if itemComponent} <!-- Items Custom -->
          {@const SvelteComponent = itemComponent}
          <SvelteComponent
              {item}
              selected={itemExistsOnSelection(item)}
              onSelect={onToggleItem}
          />
        {:else} <!-- Items base -->
          <div class="infinity-list--item border">
            <p>{item.getOwnPropertyValue(itemLabel)}</p>
            <BaseCheckbox
                classNames="m-0"
                onchecked={(/** @type {Event} */ e)=> onToggleItem(e.detail.checked, item.getOwnPropertyValue(itemId))}
                checked={selected.has(item.getOwnPropertyValue(itemId))}
            />
          </div>
        {/if}
      {/each}
    {/if}
  </div>
  {#if searching}
    <div class="w-100 h-100 text-center">
      <i class="fas fa-spinner fa-spin fa-lg"></i>
    </div>
  {/if}
</div>

<style>
  .infinity-list {
    width: 100%;
    display: flex;
    flex-direction: column;
    justify-content: start;
    align-content: start;
  }

  .infinity-list--items-container {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    overflow-y: auto;
  }

  .infinity-list--item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #fff;
    border-radius: 5px;
    margin-top: 0.5rem;
    width: 100%;
  }

  .infinity-list--item p {
    font-size: 0.85rem;
    vertical-align: middle;
    padding: 0.5rem 0 0.5rem 0.5rem;
    margin: 0;
  }
</style>

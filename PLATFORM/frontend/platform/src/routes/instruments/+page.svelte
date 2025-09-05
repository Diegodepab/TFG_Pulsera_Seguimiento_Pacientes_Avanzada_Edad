<script>
  import { goto } from "$app/navigation";
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import BaseTable from "$components/platform/commons/base_table/BaseTable.svelte";
  import BlockLoading from "$components/platform/commons/BlockLoading.svelte";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Constants } from "$lib/commons/constants";
  import { Global } from "$lib/commons/global";
  import { Routes } from "$lib/commons/routes";
  import { SessionManager } from "$lib/commons/session_manager";
  import { navigatorHistory } from "$lib/commons/stores";
  import { InstrumentController } from "$lib/controllers/instrument_controller";
  import { InstrumentListDC } from "$lib/models/data_containers/instrument_list_dc";
  import { Instrument } from "$lib/models/instrument";
  import { PermissionsEntityType, PermissionsGrantType } from "$lib/models/user_permission";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";
  import { getNotificationsContext } from "svelte-notifications";

  if (!Global.notificationContext) Global.notificationContext = getNotificationsContext();

  /** @type boolean */
  let checkingGrants = $state(true);

  /** @type boolean */
  let blockLoading = $state(false);

  /** @type InstrumentController */
  const instrumentCtl = new InstrumentController();

  /** @type UserPermission */
  let _entityAccess = $state();

  /** @type BaseTable */
  let baseTable = $state();

  /** @type BaseTableColDefinition[] */
  const columns = [
    {
      key: InstrumentListDC.uiFields.name,
      label: $t(`entity.instrument.${ InstrumentListDC.uiFields.name }`),
    },
    {
      key: InstrumentListDC.uiFields.model,
      label: $t(`entity.instrument.${ InstrumentListDC.uiFields.model }`),
      width: "100%",
    },
  ];

  /**
   * Retrieves scrollable data using a custom function.
   * @param {Object} [opts] - Optional parameters.
   * @param {string} [opts.page] - The pagination page.
   * @param {Map<QueryFields, unknown>} [opts.params] - Additional query parameters.
   * @returns Promise<SearchResults<UserListDC>> - A promise that resolves with the search results.
   */
  const scrollableFunction = async (opts) => {
    opts ??= {};
    opts.params ??= new Map();
    return instrumentCtl.search({
      ...opts,
      transformer: async (data) => (await Instrument.transformer(data)).toDC(InstrumentListDC),
    });
  };

  /** @type OnMount */
  onMount(async () => {
    _entityAccess = (await SessionManager.userPermissionsOn([ PermissionsEntityType.INSTRUMENT ])).at(0);
    if (!_entityAccess.uiVisibility) {
      CommonNotifications.noAccessPermissions();
      return await goBack();
    }
    checkingGrants = false;
  });

  /** @param {InstrumentListDC} instrument */
  const onRowClicked = async (instrument) => {
    blockLoading = true;
    await goto(`${ Routes.INSTRUMENTS }/${ instrument.id }`);
  };

  /** @returns Promise<void> */
  const goBack = async () => navigatorHistory.goBack("/");
</script>

<svelte:head>
  <title>{$t('route.instruments.title')}</title>
</svelte:head>

{#if blockLoading}
  <BlockLoading/>
{/if}

{#if !checkingGrants}
  <div class="page-content">
    <BaseTable
        pageId="instruments-index"
        bind:this={baseTable}
        tableTitle={$t('route.instruments.list')}
        {columns}
        {scrollableFunction}
        itemsPerPage={Constants.DEFAULT_ITEMS_PER_PAGE}
        itemsPerPageOptions={Constants.ITEMS_PER_PAGE_OPTIONS}
        DataContainerClass={InstrumentListDC}
        onrowclick={({item}) => onRowClicked(item)}
    >
      {#snippet globalActionsSnippet()}
        {#if _entityAccess.write !== PermissionsGrantType.NONE}
          <BaseButton
              className="mr-2"
              type="primary"
              size="sm"
              onclick={() => goto(`${Routes.INSTRUMENTS}/add`)}
          >
            <i class="fas fa-add fa-fw"></i>
          </BaseButton>
        {/if}
      {/snippet}
    </BaseTable>
  </div>
{/if}
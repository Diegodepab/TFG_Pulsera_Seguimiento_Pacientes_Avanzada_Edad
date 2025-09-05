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
  import { PathologyController } from "$lib/controllers/pathology_controller";
  import { PathologyListDC } from "$lib/models/data_containers/pathology_list_dc";
  import { Pathology } from "$lib/models/pathology";
  import { PermissionsEntityType, PermissionsGrantType } from "$lib/models/user_permission";
  import { onMount } from "svelte";
  import { date, t, time } from "svelte-i18n";
  import { getNotificationsContext } from "svelte-notifications";

  if (!Global.notificationContext) Global.notificationContext = getNotificationsContext();

  /** @type boolean */
  let checkingGrants = $state(true);
  /** @type boolean */
  let blockLoading = $state(false);

  /** @type PathologyController */
  const pathologyCtl = new PathologyController();

  /** @type UserPermission */
  let _entityAccess = $state();

  /** @type BaseTable */
  let baseTable = $state();
  /** @type BaseTableColDefinition[] */
  const columns = [
    {
      key: PathologyListDC.uiFields.name,
      label: $t(`entity.pathology.${ PathologyListDC.uiFields.name }`),
    },
    {
      key: PathologyListDC.uiFields.updateTs,
      label: $t(`entity.pathology.${ PathologyListDC.uiFields.updateTs }`),
      valueFormatter: (value) => `${ $date(value) } ${ $time(value) }`,
    },
  ];

  const scrollableFunction = async (opts) => {
    opts ??= {};
    opts.params ??= new Map();

    return pathologyCtl.search({
      ...opts,
      transformer: async (data) => (await Pathology.transformer(data)).toDC(PathologyListDC),
    });
  };

  /** @type OnMount */
  onMount(async () => {
    _entityAccess = (await SessionManager.userPermissionsOn([ PermissionsEntityType.PATHOLOGY ])).at(0);
    if (!_entityAccess.uiVisibility) {
      CommonNotifications.noAccessPermissions();
      return await goBack();
    }
    checkingGrants = false;
  });

  /** @param {PathologyListDC} pathology */
  const onRowClicked = async (pathology) => {
    blockLoading = true;
    await goto(`${ Routes.PATHOLOGIES }/${ pathology.id }`);
  };

  /** @returns Promise<void> */
  const goBack = async () => navigatorHistory.goBack("/");
</script>

<svelte:head>
  <title>{$t('route.pathologies.title')}</title>
</svelte:head>

{#if blockLoading}
  <BlockLoading/>
{/if}

{#if !checkingGrants}
  <div class="page-content">
    <BaseTable
        pageId="pathologies-index"
        bind:this={baseTable}
        tableTitle={$t('route.pathologies.list')}
        {columns}
        {scrollableFunction}
        itemsPerPage={Constants.DEFAULT_ITEMS_PER_PAGE}
        itemsPerPageOptions={Constants.ITEMS_PER_PAGE_OPTIONS}
        DataContainerClass={PathologyListDC}
        onrowclick={({item }) => onRowClicked(item)}
    >
      {#snippet globalActionsSnippet()}
        {#if _entityAccess.write !== PermissionsGrantType.NONE}
          <BaseButton
              className="mr-2"
              type="primary"
              size="sm"
              onclick={() => goto(`${Routes.PATHOLOGIES}/add`)}
          >
            <i class="fas fa-add fa-fw"></i>
          </BaseButton>
        {/if}
      {/snippet}
    </BaseTable>
  </div>
{/if}

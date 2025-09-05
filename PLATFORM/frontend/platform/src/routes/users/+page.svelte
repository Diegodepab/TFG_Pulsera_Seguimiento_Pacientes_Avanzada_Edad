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
  import { UiPillClassTranslate } from "$lib/commons/ui_utils";
  import { UserController } from "$lib/controllers/user_controller";
  import { UserListDC } from "$lib/models/data_containers/user_list_dc";
  import { User } from "$lib/models/user";
  import { PermissionsEntityType, PermissionsGrantType } from "$lib/models/user_permission";
  import { QueryComparativeOperations, QueryFields, QueryParamsQ } from "$lib/services/utils/query_utils";
  import { onMount } from "svelte";
  import { date, t, time } from "svelte-i18n";
  import { getNotificationsContext } from "svelte-notifications";

  if (!Global.notificationContext) Global.notificationContext = getNotificationsContext();

  /** @type boolean */
  let checkingGrants = $state(true);
  /** @type boolean */
  let blockLoading = $state(false);

  /** @type UserController */
  const userCtl = new UserController();
  /** @type UserPermission */
  let _entityAccess = $state();

  /** @type BaseTable */
  let baseTable = $state();
  /** @type BaseTableColDefinition[] */
  const columns = [
    {
      key: UserListDC.uiFields.fullName,
      label: $t(`entity.user.${ UserListDC.uiFields.fullName }`),
      width: "25%",
      /**
       * @param {UserListDC} item
       * @returns string
       */
      customValue: (item) => item.fullName,
    },
    {
      key: UserListDC.uiFields.email,
      label: $t(`entity.user.${ UserListDC.uiFields.email }`),
      width: "20%",
    },
    {
      key: UserListDC.uiFields.roleName,
      label: $t(`entity.user.${ UserListDC.uiFields.roleName }`),
      width: "10%",

      tdStyler: (_) => "text-capitalize",
      widgetColumn: true,
      /** @param {UserListDC} item */
      customValue: (item) => item.roleName || 'N/A',
    },
    {
      key: UserListDC.uiFields.phone,
      label: $t(`entity.user.${ UserListDC.uiFields.phone }`),
      width: "10%",
    },
    {
      key: UserListDC.uiFields.statusName,
      label: $t(`entity.user.${ UserListDC.uiFields.statusName }`),
      width: "5%",

      tdStyler: (_) => "text-left",
      widgetColumn: true,
    },
    {
      key: UserListDC.uiFields.createTs,
      label: $t(`entity.user.${ UserListDC.uiFields.createTs }`),
      width: "10%",
      valueFormatter: (value) => `${ $date(value) } ${ $time(value) }`,
      tdStyler: (_) => "text-right",
    },
    {
      key: UserListDC.uiFields.updateTs,
      label: $t(`entity.user.${ UserListDC.uiFields.updateTs }`),
      width: "10%",
      valueFormatter: (value) => `${ $date(value) } ${ $time(value) }`,
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
    const qParams = opts.params.get(QueryFields.Q) ?? [];
    qParams.push(new QueryParamsQ({
      field: User.apiFields.id,
      operation: QueryComparativeOperations.NE,
      value: SessionManager.userId(),
    }));

    opts.params.set(QueryFields.Q, qParams);

    return userCtl.search({
      ...opts,
      transformer: async (data) => (await User.transformer(data)).toDC(UserListDC),
    });
  };

  /** @type OnMount */
  onMount(async () => {
    _entityAccess = (await SessionManager.userPermissionsOn([ PermissionsEntityType.USER ])).at(0);

    if (!_entityAccess.uiVisibility) {  // not have permissions to get this.
      CommonNotifications.noAccessPermissions();
      return await goBack();
    }

    checkingGrants = false;
  });

  /**
   * Handles the row click event by navigating to the user details page.
   * @param {UserListDC} user
   */
  const onRowClicked = async (user) => {
    blockLoading = true;
    await goto(`${ Routes.USERS }/${ user.id }`);
  };

  /** @returns Promise<void> */
  const goBack = async () => navigatorHistory.goBack("/");
</script>

<svelte:head>
  <title>{$t('route.users.title')}</title>
</svelte:head>

{#if blockLoading}
  <BlockLoading/>
{/if}

{#if !checkingGrants}
  <div class="page-content">
    <BaseTable
        pageId="users-index"
        bind:this={baseTable}
        tableTitle={$t('route.users.list')}
        {columns}
        {scrollableFunction}
        itemsPerPage={Constants.DEFAULT_ITEMS_PER_PAGE}
        itemsPerPageOptions={Constants.ITEMS_PER_PAGE_OPTIONS}
        DataContainerClass={UserListDC}
        onrowclick={({item }) => onRowClicked(item)}
    >
      {#snippet globalActionsSnippet()}
        {#if _entityAccess.write !== PermissionsGrantType.NONE}
          <BaseButton className="mr-2" type="primary" size="sm" onclick={() => goto(`${Routes.USERS}/add`)}>
            <i class="fas fa-add fa-fw"></i>
          </BaseButton>
        {/if}
      {/snippet}
      {#snippet widgetColumnSnippet({ item, column, row })}
        {#if column.key === UserListDC.uiFields.roleName}
          <div class="badge badge-pill {UiPillClassTranslate.userRolePillClass(item.roleName)}">
            {item.roleName || 'N/A'}
          </div>
        {/if}

        {#if column.key === UserListDC.uiFields.statusName}
          <span class="badge badge-dot py-0">
            <i class={UiPillClassTranslate.userStatusPillClass(item.statusName)}></i>
            {$t(`entity.user.statusType.${ item.statusName }`).toLowerCase()}
          </span>
        {/if}
      {/snippet}
    </BaseTable>
  </div>
{/if}
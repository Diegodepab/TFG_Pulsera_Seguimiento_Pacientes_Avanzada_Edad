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
  import { PatientController } from "$lib/controllers/patient_controller";
  import { PatientListDC } from "$lib/models/data_containers/patient_list_dc";
  import { Patient } from "$lib/models/patient";
  import { UserRoleType } from "$lib/models/user";
  import { PermissionsEntityType, PermissionsGrantType } from "$lib/models/user_permission";
  import { QueryFields, QueryParamsEmbed } from "$lib/services/utils/query_utils";
  import { onMount } from "svelte";
  import { date, t, time } from "svelte-i18n";
  import { getNotificationsContext } from "svelte-notifications";

  if (!Global.notificationContext) Global.notificationContext = getNotificationsContext();

  const hiddenColumnKeys = SessionManager.userRole() === UserRoleType.USER ? [ PatientListDC.uiFields.ownerFullName ] : [];

  /** @type boolean */
  let checkingGrants = $state(true);

  /** @type boolean */
  let blockLoading = $state(false);

  /** @type PatientController */
  const patientCtl = new PatientController();


  /** @type UserPermission */
  let _entityAccess = $state();

  /** @type BaseTable */
  let baseTable = $state();

  /** @type BaseTableColDefinition[] */
  const columns = [
    {
      key: PatientListDC.uiFields.code,
      label: $t(`entity.patient.${ PatientListDC.uiFields.code }`),
      width: "30%",
    },
    {
      key: PatientListDC.uiFields.gender,
      label: $t(`entity.patient.${ PatientListDC.uiFields.gender }`),
      width: "10%",
      tdStyler: (_) => "text-capitalize",
      widgetColumn: true,
      /** @param {PatientListDC} item */
      customValue: (item) => $t(`entity.patients.genderType.${ item.gender }`),
    },
    {
      key: PatientListDC.uiFields.ownerFullName,
      sortable: false,
      label: $t(`entity.patient.${ PatientListDC.uiFields.ownerFullName }`),
    },
    {
      key: PatientListDC.uiFields.updateTs,
      label: $t(`entity.patient.${ PatientListDC.uiFields.updateTs }`),
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

    opts.params.set(QueryFields.EMBED, new QueryParamsEmbed({ embeds: [ Patient.apiEmbeds.ownerUser ] }));

    return patientCtl.search({
      ...opts,
      transformer: async (data) => (await Patient.transformer(data)).toDC(PatientListDC),
    });
  };

  /** @type OnMount */
  onMount(async () => {
    _entityAccess = (await SessionManager.userPermissionsOn([ PermissionsEntityType.PATIENT ])).at(0);
    if (!_entityAccess.uiVisibility) {
      CommonNotifications.noAccessPermissions();
      return await goBack();
    }

    checkingGrants = false;
  });

  /**
   * @param {PatientListDC} patient
   */
  const onRowClicked = async (patient) => {
    blockLoading = true;
    await goto(`${ Routes.PATIENTS }/${ patient.id }`);
  };

  /** @returns Promise<void> */
  const goBack = async () => navigatorHistory.goBack("/");

</script>

<svelte:head>
  <title>{$t('route.patients.title')}</title>
</svelte:head>

{#if blockLoading}
  <BlockLoading/>
{/if}

{#if !checkingGrants}
  <div class="page-content">
    <div class="row mx-0">
      <div class="col-12 px-3">
        <BaseTable
            pageId="patients-index"
            bind:this={baseTable}
            tableTitle={$t('route.patients.list')}
            {columns}
            {scrollableFunction}
            itemsPerPage={Constants.DEFAULT_ITEMS_PER_PAGE}
            itemsPerPageOptions={Constants.ITEMS_PER_PAGE_OPTIONS}
            DataContainerClass={PatientListDC}
            {hiddenColumnKeys}
            onrowclick={({ item }) => onRowClicked(item)}
        >
          {#snippet globalActionsSnippet()}
            {#if _entityAccess.write !== PermissionsGrantType.NONE}
              <BaseButton className="mr-2" type="primary" size="sm" onclick={() => goto(`${Routes.PATIENTS}/add`)}>
                <i class="fas fa-add fa-fw"></i>
              </BaseButton>
            {/if}
          {/snippet}
          <!-- Snippet for widget-column -->
          {#snippet widgetColumnSnippet({ item, column })}
            {#if column.key === PatientListDC.uiFields.gender}
              <div class="badge badge-pill {UiPillClassTranslate.patientGenderPillClass(item.gender)}">
                {$t(`entity.patient.genderType.${ item.gender }`).toLowerCase()}
              </div>
            {/if}
          {/snippet}
        </BaseTable>
      </div>
    </div>
  </div>
{/if}
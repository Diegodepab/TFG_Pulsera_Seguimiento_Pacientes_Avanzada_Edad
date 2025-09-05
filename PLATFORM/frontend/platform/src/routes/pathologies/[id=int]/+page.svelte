<script>
  import { goto } from "$app/navigation";
  import { navigating, page } from "$app/state";
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import BaseTable from "$components/platform/commons/base_table/BaseTable.svelte";
  import BlockLoading from "$components/platform/commons/BlockLoading.svelte";
  import LoadingContentPage from "$components/platform/commons/LoadingContentPage.svelte";
  import PathologyForm from "$components/platform/pathology/PathologyForm.svelte";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Constants } from "$lib/commons/constants";
  import { Global } from "$lib/commons/global";
  import { Routes } from "$lib/commons/routes";
  import { SessionManager } from "$lib/commons/session_manager";
  import { navigatorHistory } from "$lib/commons/stores";
  import { PathologyController } from "$lib/controllers/pathology_controller";
  import { PatientPathologyController } from "$lib/controllers/patient_pathology_controller";
  import { Exception } from "$lib/exceptions/exception";
  import { PatientPathologyListDC } from "$lib/models/data_containers/patient_pathology_list_dc";
  import { PatientPathology } from "$lib/models/patient_pathology";
  import { PermissionsEntityType, PermissionsGrantType } from "$lib/models/user_permission";
  import {
    QueryComparativeOperations,
    QueryFields,
    QueryParamsEmbed,
    QueryParamsQ,
  } from "$lib/services/utils/query_utils";
  import { onMount } from "svelte";
  import { date, t } from "svelte-i18n";
  import { getNotificationsContext } from "svelte-notifications";

  if (!Global.notificationContext) Global.notificationContext = getNotificationsContext();

  /** @type boolean */
  let blockLoading = $state(false);

  /** @type boolean */
  let checkingGrants = $state(true);
  /** @type boolean */
  let loading = $state(true);

  /** @type BaseTable */
  let baseTablePatients = $state();

  /** @type BaseTableColDefinition[] */
  const columnsPatients = [
    {
      key: PatientPathologyListDC.uiFields.patientCode,
      label: $t(`entity.patient-pathology.patientCode`),
      sortable: false,
    },
    {
      key: PatientPathologyListDC.uiFields.detectionDate,
      label: $t(`entity.patient-pathology.detection-date`),
      valueFormatter: (value) => `${ $date(value) }`,
    },
  ];

  /** @type PathologyController */
  const _pathologyCtl = new PathologyController();

  /** @type Pathology */
  let pathology = $state();

  /** @type {Map<PermissionsEntityType, UserPermission>} */
  const _entitiesAccess = new Map();

  // manage changes into url from route
  let _idParam = page.params.id;

  /** @type OnMount */
  onMount(async () => {
    const perms = await SessionManager.userPermissionsOn([ PermissionsEntityType.PATHOLOGY ]);
    perms?.forEach((perm) => _entitiesAccess.set(perm.entityName, perm));

    const access = _entitiesAccess.get(PermissionsEntityType.PATHOLOGY);
    if (!access.uiVisibility || access.read === PermissionsGrantType.NONE) {
      CommonNotifications.noAccessPermissions();
      await goBack();
      return;
    }
    checkingGrants = false;
    await loadPathologyData();
  });
  /**
   * Retrieves scrollable data using a custom function.
   * @param {Object} [opts] - Optional parameters.
   * @param {string} [opts.page] - The pagination page.
   * @param {Map<QueryFields, unknown>} [opts.params] - Additional query parameters.
   * @returns Promise<SearchResults<PatientPathologyListDC>> - A promise that resolves with the search results.
   */
  const scrollableFunctionPatient = async (opts) => {
    opts ??= {};
    opts.params ??= new Map();

    // QUERY
    opts.params.set(
      QueryFields.Q, [
        new QueryParamsQ({
          field: PatientPathology.apiFields.pathologyId,
          operation: QueryComparativeOperations.EQ,
          value: pathology.id,
        }),
      ],
    );

    // LIMIT
    opts.params.set(QueryFields.LIMIT, 10);

    // EMBED
    opts.params.set(QueryFields.EMBED, new QueryParamsEmbed({ embeds: [ PatientPathology.apiEmbeds.patient ] }));

    return (new PatientPathologyController()).search({
      ...opts,
      transformer: async (data) => (await PatientPathology.transformer(data)).toDC(PatientPathologyListDC),
    });
  };

  /**
   * @returns Promise<void>
   * @throws {Exception} Throws an error if pathology data not loaded.
   */
  const loadPathologyData = async () => {
    loading = true;
    try {
      /** @type {Map<QueryFields, ?>} */
      const params = new Map();
      pathology = await _pathologyCtl.get(page.params.id, { params });
    } catch (e) {
      if (!(e instanceof Exception) || e.code !== 404) throw e;
      await goBack();
      throw e;
    } finally {
      loading = false;
    }
  };

  /**
   * Handles the row click event by navigating to the models model details page.
   * @param {PatientPathologyListDC} item
   *
   */
  const onRowClicked = async (item) => {
    blockLoading = true;
    await goto(`${ Routes.PATIENTS }/${ item.patientId }`);
  };

  /** @returns Promise<void> */
  const editPathology = async () => await goto(`${ Routes.PATHOLOGIES }/${ pathology.id }/edit`);
  /** @returns Promise<void> */
  const goBack = async () => await navigatorHistory.goBack(Routes.PATHOLOGIES);

  $effect(() => {
    if (navigating && page.params.id && navigating.to?.params?.id === page.params.id && page.params.id !== _idParam) {
      _idParam = page.params.id;
      loadPathologyData();
    }
  });
</script>

<svelte:head>
  <title>{$t('route.pathology-details.title')}</title>
</svelte:head>

{#if blockLoading}
  <BlockLoading/>
{/if}

{#if !checkingGrants}
  <div class="page-content">
    <div class="page-content-title mt-0 d-flex justify-content-between align-items-center">
      <span>{$t('route.pathology-details.form-title')}</span>

      <div class="pr-0 d-flex justify-content-end">
        <BaseButton
            size="sm"
            onclick={goBack}
            type="primary"
            disabled={loading}>
          <i class="fas fa-arrow-left fa-fw"></i>
        </BaseButton>

        {#if _entitiesAccess.get(PermissionsEntityType.PATHOLOGY).write !== PermissionsGrantType.NONE}
          <div class="card-header-action-separator"></div>
          <BaseButton size="sm" type="primary" disabled={loading} onclick={editPathology}>
            <i class="fas fa-edit fa-fw"></i>
          </BaseButton>
        {/if}
      </div>
    </div>
    <LoadingContentPage {loading} class="mb-3"/>

    <div class="row mx-0">
      <div class="col-12 col-md-6 pl-3 border-sm-0">
        <PathologyForm {pathology} readonly/>
      </div>
    </div>

    {#if pathology?.id}
      <div class="col-12 pl-3 border-sm-0 mh-100 px-0">
        <BaseTable
            pageId="patient-pathology-details"
            bind:this={baseTablePatients}
            tableTitle={$t('route.patients.list')}
            showOptions={false}
            columns={columnsPatients}
            scrollableFunction={scrollableFunctionPatient}
            itemsPerPage={Constants.DEFAULT_ITEMS_PER_PAGE}
            itemsPerPageOptions={Constants.ITEMS_PER_PAGE_OPTIONS}
            DataContainerClass={PatientPathologyListDC}
            onrowclick={({ item }) => onRowClicked(item)}
        >
        </BaseTable>
      </div>
    {/if}
  </div>
{/if}
<script>
  // La verdad que llevo bastante sin tocar el código y en su momento veía sentido hacer una página de alarmas para cada paciente, pero ahora que lo pienso, quizás sería mostrar por encima solamente las alarmas del paciente.
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import { page } from "$app/stores";
  import { getNotificationsContext } from "svelte-notifications";
  import { t } from "svelte-i18n";

  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import BlockLoading from "$components/platform/commons/BlockLoading.svelte";
  import LoadingContentPage from "$components/platform/commons/LoadingContentPage.svelte";
  import BaseTable from "$components/platform/commons/base_table/BaseTable.svelte";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Global } from "$lib/commons/global";
  import { Routes } from "$lib/commons/routes";
  import { SessionManager } from "$lib/commons/session_manager";
  import { navigatorHistory } from "$lib/commons/stores";
  import { PermissionsEntityType, PermissionsGrantType } from "$lib/models/user_permission";
  import { AlarmController } from "$lib/controllers/alarm_controller";
  import { AlarmListDC } from "$lib/models/data_containers/alarm_list_dc";
  import { Constants } from "$lib/commons/constants";

  // Inicializa context de notificaciones
  if (!Global.notificationContext)
    Global.notificationContext = getNotificationsContext();

  /** @type boolean */
  let checkingGrants = $state(true);
  /** @type boolean */
  let loading = $state(true);
  /** @type boolean */
  let blockLoading = $state(false);
  /** @type import("$lib/models/user_permission").UserPermission */
  let _entityAccess = $state();

  /** @type BaseTable */
  let alarmsTable;

  /** @type BaseTableColDefinition[] */
  const alarmColumns = [
    { key: AlarmListDC.uiFields.timestamp, label: $t('entity.alarm.timestamp'), sortable: true },
    { key: AlarmListDC.uiFields.type, label: $t('entity.alarm.type'), sortable: false },
    { key: AlarmListDC.uiFields.status, label: $t('entity.alarm.status'), sortable: false }
  ];

  onMount(async () => {
    const [permission] = await SessionManager.userPermissionsOn([PermissionsEntityType.ALARM]);
    _entityAccess = permission;

    if (!_entityAccess?.uiVisibility || _entityAccess.read === PermissionsGrantType.NONE) {
      CommonNotifications.noAccessPermissions();
      return await goBack();
    }

    checkingGrants = false;
  
    // Carga inicial de datos
    loading = true;
    await alarmsTable.loadData();
    loading = false;
  });

  /** @returns Promise<void> */
  const goBack = async () => navigatorHistory.goBack(Routes.HOME);

  /** Función de scroll paginado */
  const scrollableFunctionAlarms = (opts) => {
    opts ??= {};
    opts.params ??= new Map();
    opts.params.set('limit', Constants.DEFAULT_ITEMS_PER_PAGE);
    return (new AlarmController()).search({
      ...opts,
      transformer: data => new AlarmListDC(data)
    });
  };
</script>

<svelte:head>
  <title>{$t('route.alarms.title')}</title>
</svelte:head>

{#if blockLoading}
  <BlockLoading />
{/if}

{#if !checkingGrants}
  <div class="page-content">
    <div class="page-content-title d-flex justify-content-between align-items-center">
      <span>{$t('route.alarms.title')}</span>
      <BaseButton size="sm" type="primary" onclick={goBack} disabled={blockLoading}>
        <i class="fas fa-arrow-left fa-fw"></i>
      </BaseButton>
    </div>
    <LoadingContentPage {loading} class="mb-3" />

    <BaseTable
      bind:this={alarmsTable}
      pageId="alarms-list"
      tableTitle={$t('route.alarms.list')}
      columns={alarmColumns}
      scrollableFunction={scrollableFunctionAlarms}
      itemsPerPage={Constants.DEFAULT_ITEMS_PER_PAGE}
      itemsPerPageOptions={Constants.ITEMS_PER_PAGE_OPTIONS}
      DataContainerClass={AlarmListDC}
      rowClickable={false}
    >
      <!-- acciones globales opcionales -->
    </BaseTable>
  </div>
{/if}

<style>
  .page-content { padding: 1rem; }
  .page-content-title { font-size: 1.25rem; margin-bottom: 1rem; }
</style>
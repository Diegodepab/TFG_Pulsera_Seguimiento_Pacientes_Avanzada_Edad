<script>
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import BaseTable from "$components/platform/commons/base_table/BaseTable.svelte";
  import BlockLoading from "$components/platform/commons/BlockLoading.svelte";
  import { SessionManager } from "$lib/commons/session_manager";
  import { AlarmController } from "$lib/controllers/alarm_controller";
  import { PermissionsEntityType } from "$lib/models/user_permission";
  import { AlarmListDC } from "$lib/models/data_containers/alarm_list_dc";
  import { Alarm } from "$lib/models/alarm";
  import { Constants } from "$lib/commons/constants";
  import { QueryFields, QueryParamsEmbed } from "$lib/services/utils/query_utils";
  import { t } from "svelte-i18n";

  let loading = true;
  let error = null;
  let currentUser = null;
  let hasAdminAccess = false;
  let isDoctor = false;
  let isUser = false;
  let hasAccess = false;
  let blockLoading = false;

  // Variables para BaseTable
  let tableComponent;

  // Función onRowClicked para navegar a detalles del paciente
  const onRowClicked = async (alarm) => {
    const patientId = alarm?.patientId;
    if (patientId) {
      // Navegar al paciente relacionado con la alarma
      goto(`/patients/${patientId}`);
    }
  };

  onMount(async () => {
    try {
      // Obtener usuario actual
      currentUser = await SessionManager.user();
      
      if (!currentUser) {
        error = "No hay usuario logueado";
        goto("/login");
        return;
      }

      // Verificar permisos del usuario
      try {
        const [perm] = await SessionManager.userPermissionsOn([PermissionsEntityType.ALARM]);
        hasAdminAccess = perm && perm.read !== "NONE";
      } catch (permError) {
        // Para admins, asumir que tienen acceso si hay error en permisos
        if (currentUser?.roleName === "admin") {
          hasAdminAccess = true;
        } else {
          hasAdminAccess = false;
        }
      }

      isDoctor = currentUser?.roleName === "user";
      const isAdmin = currentUser?.roleName === "admin";
      isUser = currentUser?.roleName === "user"; // Asignar valor a isUser

      // Determinar si tiene acceso - incluir USER role
      hasAccess = hasAdminAccess || isDoctor || isAdmin || isUser;

      if (!hasAccess) {
        // Redirigir al home en lugar de mostrar error
        goto("/");
        return;
      }

      loading = false;
      
    } catch (err) {
      console.error("Error en onMount:", err);
      // En caso de error, redirigir al home
      goto("/");
    }
  });

  // Función scrollable para BaseTable
  const scrollableFunction = async (opts) => {
    try {
      const alarmController = new AlarmController();
      
      // Configurar opciones y parámetros
      opts = opts || {};
      opts.params = opts.params || new Map();
      
      // Si es un usuario normal, filtrar solo sus alarmas
      if (isUser && currentUser?.patientId) {
        opts.params.set("patient_id", currentUser.patientId);
      }
      
      // Agregar embed del paciente para poder obtener el nombre
      opts.params.set(QueryFields.EMBED, new QueryParamsEmbed({ 
        embeds: ["patient"] 
      }));
      
      // Realizar la búsqueda
      const result = await alarmController.search({
        ...opts,
        transformer: async (data) => data
      });
    
      // Transformar cada item para agregar el nombre del paciente
      if (result?.items) {
        result.items = result.items.map(item => ({
          id: item.id,
          patientId: item.patient_id,
          alarmType: item.alarm_type,
          ts: item.ts,
          isUrgent: item.is_urgent,
          patientName: item.patient?.code || `Paciente ${item.patient_id}`
        }));
      }
      
      return result;
    } catch (err) {
      console.error("Error en scrollableFunction:", err);
      throw err;
    }
  };

  // Columnas usando los campos transformados
  const columns = [
    {
      key: "patientName",
      label: $t('route.alarms.columns.patient'),
      sortable: false,
      width: "200px"
    },
    {
      key: "alarmType",
      label: $t('route.alarms.columns.alarmType'),
      sortable: false,
      width: "200px",
      valueFormatter: (alarmType) => {
        const typeKey = `route.alarms.types.${alarmType}`;
        const translation = $t(typeKey);
        return translation !== typeKey ? translation : alarmType;
      }
    },
    {
      key: "ts",
      label: $t('route.alarms.columns.date'),
      sortable: true,
      width: "160px",
      valueFormatter: (isoTs) => {
        if (!isoTs) return "-";
        const date = new Date(isoTs);
        return date.toLocaleDateString('es-ES', {
          day: '2-digit',
          month: '2-digit', 
          year: 'numeric'
        });
      }
    },
    {
      key: "isUrgent",
      label: $t('route.alarms.columns.urgency'), 
      sortable: false,
      width: "120px",
      valueFormatter: (isUrgent) => isUrgent ? "❗" : ""
    }
  ];
</script>

<svelte:head>
  <title>{$t('route.alarms.title')}</title>
</svelte:head>

{#if blockLoading}
  <BlockLoading />
{/if}

{#if !loading}
  <div class="page-content">
    <div class="row mx-0">
      <div class="col-12 px-3">
        <BaseTable
          pageId="alarms-index"
          bind:this={tableComponent}
          tableTitle={isUser ? $t('route.alarms.myAlarms') : $t('route.alarms.alarmsList')}
          {columns}
          {scrollableFunction}
          itemsPerPage={Constants.DEFAULT_ITEMS_PER_PAGE}
          itemsPerPageOptions={Constants.ITEMS_PER_PAGE_OPTIONS}
          onrowclick={({ item }) => onRowClicked(item)}
        />
      </div>
    </div>
  </div>
{:else}
  <div class="d-flex justify-content-center align-items-center p-4">
    <BlockLoading />
    <span class="ml-3">{$t('route.alarms.loading')}</span>
  </div>
{/if}
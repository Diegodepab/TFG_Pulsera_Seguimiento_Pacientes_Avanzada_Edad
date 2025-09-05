<script>
  import { goto } from "$app/navigation";
  import { navigating, page } from "$app/state";
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import BaseTable from "$components/platform/commons/base_table/BaseTable.svelte";
  import BlockLoading from "$components/platform/commons/BlockLoading.svelte";
  import LoadingContentPage from "$components/platform/commons/LoadingContentPage.svelte";
  import LinkPathologyModal from "$components/platform/pathology/LinkPathologyModal.svelte";
  import CreatePatientModelModal from "$components/platform/patient-model/CreatePatientModelModal.svelte";
  import PatientForm from "$components/platform/patient/PatientForm.svelte";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Constants } from "$lib/commons/constants";
  import { Global } from "$lib/commons/global";
  import { Routes } from "$lib/commons/routes";
  import { SessionManager } from "$lib/commons/session_manager";
  import { navigatorHistory } from "$lib/commons/stores";
  import { PatientController } from "$lib/controllers/patient_controller";
  import { PatientModelController } from "$lib/controllers/patient_model_controller";
  import { PatientPathologyController } from "$lib/controllers/patient_pathology_controller";
  import { Exception } from "$lib/exceptions/exception";
  import { PathologySuggestionListDC } from "$lib/models/data_containers/pathology_suggestion_list_dc";
  import { PatientModelListDC } from "$lib/models/data_containers/patient_model_list_dc";
  import { PatientPathologyListDC } from "$lib/models/data_containers/patient_pathology_list_dc";
  import { Patient } from "$lib/models/patient";
  import { PatientModel } from "$lib/models/patient_model";
  import { PatientPathology } from "$lib/models/patient_pathology";
  import { PermissionsEntityType, PermissionsGrantType } from "$lib/models/user_permission";
  import {
    QueryComparativeOperations,
    QueryFields,
    QueryParamsEmbed,
    QueryParamsQ,
    QueryParamsSort,
    QuerySortOrder,
  } from "$lib/services/utils/query_utils";
  import { onMount } from "svelte";
  import { date, t, time } from "svelte-i18n";
  import { getNotificationsContext } from "svelte-notifications";

  import { Alarm }          from "$lib/models/alarm";
  import { AlarmController } from "$lib/controllers/alarm_controller";
  import { AlarmListDC }    from "$lib/models/data_containers/alarm_list_dc.js";
  import { StudyController } from "$lib/controllers/study_controller";
  import { StudyDateListDC } from "$lib/models/data_containers/studyDateListDC";

  if (!Global.notificationContext) Global.notificationContext = getNotificationsContext();

  /** @type boolean */
  let blockLoading = $state(false);

  /** @type BaseTable */
  let ModelTable = $state();

  /** @type BaseTableColDefinition[] */
  const ModelColumns = [
    {
      key: PatientModelListDC.uiFields.name,
      label: $t(`entity.patient-model.${ PatientModelListDC.uiFields.name }`),
      sortable: false,

    },
    {
      key: PatientModelListDC.uiFields.updateTs,
      label: $t(`entity.patient-model.${ PatientModelListDC.uiFields.updateTs }`),
      valueFormatter: (value) => `${ $date(value) } ${ $time(value) }`,
      sortable: false,
    },
  ];

  /** @type LinkPathologyModal.svelte */
  let _linkPathologyModal = $state();

  /** @type BaseTable */
  let pathologiesTable = $state();

  /** @type BaseTable */
  let alarmsTable = $state();

  /** @type BaseTableColDefinition[] */
  const pathologiesColumns = [
    {
      key: PatientPathologyListDC.uiFields.pathologyName,
      label: $t(`entity.patient-pathology.name`),
      sortable: false,
    },
    {
      key: PatientPathologyListDC.uiFields.detectionDate,
      label: $t(`entity.patient-pathology.detection-date`),
      valueFormatter: (value) => `${ $date(value) }`,
      sortable: false,
    },
  ];

  /** @type {PatientPathology[]} */
  let currPatientPathologies = $state([]);

  
  /** @type BaseTable */
  let studyDatesTable = $state();

  /** @type BaseTableColDefinition[] */
  const studyDatesColumns = [
    {
      key: StudyDateListDC.uiFields.studyDate,
      label: $t(`entity.patient-study.date`),
      sortable: false,
      width: '20%',
      valueFormatter: (value) => value,
    },
    {
      key: StudyDateListDC.uiFields.count,
      label: $t(`entity.patient-study.count`),
      sortable: false,
      width: '15%',
      valueFormatter: (value) => value ?? '-',
    },
    {
      key: StudyDateListDC.uiFields.firstTime,
      label: $t(`entity.patient-study.firstTime`),
      sortable: false,
      width: '15%',
      valueFormatter: (value) => value ?? '-',
    },
    {
      key: StudyDateListDC.uiFields.lastTime,
      label: $t(`entity.patient-study.lastTime`),
      sortable: false,
      width: '15%',
      valueFormatter: (value) => value ?? '-',
    },
    {
      key: StudyDateListDC.uiFields.lastStepCount,
      label: $t(`entity.patient-study.lastStepCount`),
      sortable: false,
      width: '15%',
      valueFormatter: (value) => value ?? '-',
    },
  ];
    
  /** @type BaseTableColDefinition[] */
  const alarmColumns = [
    {
      key: AlarmListDC.uiFields.alarmType,
        label: $t(`entity.patient-alarms.alert_type`),
        sortable: false
      },
      {
        key: AlarmListDC.uiFields.ts,
        label: $t(`entity.patient-alarms.timestamp`),
        valueFormatter: (isoTs) => {
          const d = new Date(isoTs);
          const fecha = d.toLocaleDateString("es-ES", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit"
          });
          const hora = d.toLocaleTimeString("es-ES", {
            hour12: false,
            hour: "2-digit",
            minute: "2-digit"
          });
          return `${fecha} ${hora}`;
        },
        sortable: false,
        width: "150px"
      },
      {
        key: AlarmListDC.uiFields.isUrgent,
        label: $t(`entity.patient-alarms.urgent`),
        valueFormatter: (urgente) => (urgente ? "❗" : ""),
        sortable: false,
        width: "100px"
      },
      {
        key: "actions",
        label: "Acciones",
        sortable: false,
        width: "120px"
      }
    ];

  
  /** @type StudyController */
  const studyCtl = new StudyController();

  /** @type AlarmController */
  const alarmCtl = new AlarmController();

  /** @type boolean */
  let checkingGrants = $state(true);

  /** @type boolean */
  let loading = $state(true);

  /** @type boolean */
  let deletingAlarms = $state(false);

  /** @type number */
  let alarmCount = $state(0);

  /** @type PatientController */
  const _patientCtl = new PatientController();

  /** @type Patient */
  let patient = $state(Patient.empty());

  /** @type CreatePatientModelModal */
  let _createPatientModelModal = $state();

  /** @type OnMount */
  onMount(async () => {
    checkingGrants = false;
    await loadMyPatientData();
    await loadAlarmCount();
  });

  /**
   * Carga el número de alarmas del paciente
   * @returns Promise<void>
   */
  const loadAlarmCount = async () => {
    if (!patient?.id) return;
    
    try {
      const alarmResults = await alarmCtl.search({
        params: new Map([
          [QueryFields.Q, [
            new QueryParamsQ({
              field: Alarm.apiFields.patientId,
              operation: QueryComparativeOperations.EQ,
              value: patient.id
            })
          ]],
          [QueryFields.LIMIT, 1000]
        ])
      });

      alarmCount = alarmResults?.items?.length || 0;
    } catch (error) {
      console.error("Error al cargar el número de alarmas:", error);
      alarmCount = 0;
    }
  };

  /**
   * Marca todas las alarmas del paciente como completadas (las elimina)
   * @returns Promise<void>
   */
  const deleteAllPatientAlarms = async () => {
    if (!patient?.id) return;
    
    deletingAlarms = true;
    try {
      const alarmResults = await alarmCtl.search({
        params: new Map([
          [QueryFields.Q, [
            new QueryParamsQ({
              field: Alarm.apiFields.patientId,
              operation: QueryComparativeOperations.EQ,
              value: patient.id
            })
          ]],
          [QueryFields.LIMIT, 1000]
        ])
      });

      if (alarmResults?.items?.length > 0) {
        const deletePromises = alarmResults.items.map(alarm => 
          alarmCtl.delete(alarm.id)
        );
        
        await Promise.all(deletePromises);
        
        alarmsTable?.loadData();
        await loadAlarmCount();
        
        Global.notificationContext.addNotification({
          text: `Se han completado ${alarmResults.items.length} alarma(s) correctamente.`,
          position: 'top-right',
          type: 'success',
          removeAfter: 3000
        });
      } else {
        Global.notificationContext.addNotification({
          text: 'No se encontraron alarmas para completar.',
          position: 'top-right',
          type: 'info',
          removeAfter: 3000
        });
      }
    } catch (error) {
      console.error('Error al completar alarmas:', error);
      Global.notificationContext.addNotification({
        text: 'Error al completar las alarmas. Por favor, inténtelo de nuevo.',
        position: 'top-right',
        type: 'danger',
        removeAfter: 5000
      });
    } finally {
      deletingAlarms = false;
    }
  };

  /**
   * Función paginada para obtener alarmas de este paciente.
   * @param {{ page?: string, params?: Map }} opts
   * @returns Promise<SearchResults<AlarmListDC>>
   */
  const scrollableFunctionAlarms = async (opts) => {
    opts     ??= {};
    opts.params ??= new Map();

    opts.params.set(QueryFields.Q, [
      new QueryParamsQ({
        field: Alarm.apiFields.patientId,
        operation: QueryComparativeOperations.EQ,
        value: patient.id
      })
    ]);

    opts.params.set(QueryFields.SORT, [
      new QueryParamsSort({
        field: Alarm.apiFields.ts,
        sort: QuerySortOrder.DESC
      })
    ]);

    opts.params.set(QueryFields.LIMIT, 10);

    return await alarmCtl.search({
      ...opts,
      transformer: async (data) => AlarmListDC.fromJson(data)
    });
  };

  /**
   * Carga los datos del paciente actual (usuario logueado)
   * @returns Promise<void>
   * @throws {Exception} Throws an error if patient data not loaded.
   */
  const loadMyPatientData = async () => {
    loading = true;
    try {
      const currentUser = await SessionManager.user();
      
      /** @type {Map<QueryFields, unknown>} */
      const params = new Map();
      params.set(QueryFields.Q, [
        new QueryParamsQ({
          field: Patient.apiFields.patientUserId,
          operation: QueryComparativeOperations.EQ,
          value: currentUser.id
        })
      ]);
      
      params.set(
        QueryFields.EMBED,
        new QueryParamsEmbed({
          embeds: [
            new QueryParamsEmbed({
              parent: Patient.apiEmbeds.patientPathologies,
              embeds: [ PatientPathology.apiEmbeds.pathology ],
            }),
            Patient.apiEmbeds.ownerUser,
          ],
        }),
      );

      const searchResults = await _patientCtl.search({ params });
      
      if (searchResults?.items?.length > 0) {
        patient = searchResults.items[0];
        currPatientPathologies = patient?.patientPathologies ?? [];
      } else {
        CommonNotifications.noAccessPermissions();
        await goto(Routes.DASHBOARD);
      }
    } catch (e) {
      console.error('Error loading patient data:', e);
      CommonNotifications.noAccessPermissions();
      await goto(Routes.DASHBOARD);
    } finally {
      loading = false;
    }
  };

  /** @returns Promise<void> */
  const goBack = async () => await goto(Routes.DASHBOARD);

  /**
   * Handles the row click event by navigating to the details page.
   * @param {GenericModelListDC} Model
   */
  const onRowClickedPatientModel = async (model) => {
    blockLoading = true;
    await goto(`${ Routes.PATIENT_MODELS }/${ model.id }`);
  };

  /**
   * Retrieves scrollable data using a custom function.
   * @param {Object} [opts] - Optional parameters.
   * @param {string} [opts.page] - The pagination page.
   * @param {Map<QueryFields, unknown>} [opts.params] - Additional query parameters.
   * @returns Promise<SearchResults<GenericsModelListDC>> - A promise that resolves with the search results.
   */
  const scrollableFunctionModel = async (opts) => {
    opts ??= {};
    opts.params ??= new Map();

    // QUERY
    opts.params.set(QueryFields.Q, [
      new QueryParamsQ({
        field: PatientModel.apiFields.patientId,
        operation: QueryComparativeOperations.EQ,
        value: patient.id,
      }),
    ]);

    // SORT
    opts.params.set(QueryFields.SORT, [
      new QueryParamsSort({ field: PatientModel.apiFields.updateTs, sort: QuerySortOrder.DESC }),
    ]);

    // LIMIT
    opts.params.set(QueryFields.LIMIT, 10);

    return (new PatientModelController()).search({
      ...opts,
      transformer: async (data) => (await PatientModel.transformer(data)).toDC(PatientModelListDC),
    });
  };

  /**
   * Elimina una alarma específica
   * @param {number} alarmId - ID de la alarma a eliminar
   * @returns Promise<void>
   */
  const deleteAlarm = async (alarmId) => {
    try {
      await alarmCtl.delete(alarmId);
      
      alarmsTable?.loadData();
      await loadAlarmCount();
      
      Global.notificationContext.addNotification({
        text: 'Alarma completada correctamente.',
        position: 'top-right',
        type: 'success',
        removeAfter: 3000
      });
    } catch (error) {
      console.error('Error al completar alarma:', error);
      Global.notificationContext.addNotification({
        text: 'Error al completar la alarma. Por favor, inténtelo de nuevo.',
        position: 'top-right',
        type: 'danger',
        removeAfter: 5000
      });
    }
  };

  /**
   * Retrieves scrollable data using a custom function.
   * @param {Object} [opts] - Optional parameters
   * @param {PatientPathology[]} [opts.pathologies] - Optional parameters
   * @returns SearchResults<Pathology> - A promise that resolves with the search results.
   */
  const scrollableFunctionPathology = (opts) => {
    opts ??= {};
    opts.params ??= new Map();

    // QUERY
    opts.params.set(QueryFields.Q, [
      new QueryParamsQ({
        field: PatientPathology.apiFields.patientId,
        operation: QueryComparativeOperations.EQ,
        value: patient.id,
      }),
    ]);

    // SORT
    opts.params.set(
      QueryFields.SORT, [
        new QueryParamsSort({
          field: PatientPathology.apiFields.detectionDate,
          sort: QuerySortOrder.DESC,
        }),
      ]);

    // LIMIT
    opts.params.set(QueryFields.LIMIT, 10);

    // EMBED
    opts.params.set(QueryFields.EMBED, new QueryParamsEmbed({ embeds: [ PatientPathology.apiEmbeds.pathology ] }));

    return (new PatientPathologyController()).search({
      ...opts,
      transformer: async (data) => (await PatientPathology.transformer(data)).toDC(PatientPathologyListDC),
    });
  };

  /**
   * Updates the preset and load the data into the table
   * @param {PatientPathology[]} results - patient pathologies saved
   */
  const onSavedPathologies = (results) => {
    currPatientPathologies = results;
    pathologiesTable?.loadData();
  };

  /**
   * Recupera de forma paginada las fechas de estudio de un paciente, agrupadas por día.
   * @param {Object} [opts] - Parámetros opcionales de paginación.
   * @param {string} [opts.page] - Página de la lista (cursor).
   * @param {Map<QueryFields, unknown>} [opts.params] - Parámetros de consulta adicionales.
   * @returns {Promise<SearchResults<StudyDateListDC>>}
   */
  const scrollableFunctionStudyDates = async (opts) => {
    opts     ??= {};
    opts.params ??= new Map();

      // Llamada al nuevo endpoint /studies/dates
    // OPCIONAL: si tienes cursor en opts.page, lo enviamos como ?cursor=...
    const cursorParam = opts.page ? `&cursor=${encodeURIComponent(opts.page)}` : "";
    const response = await studyCtl.listStudyDates(patient.id, cursorParam);

    // response tiene { items: [{ studyDate }], cursor }
    return {
      items: response.items.map(i =>
        new StudyDateListDC({
          studyDate:     i.studyDate,
          count:         i.count,
          firstTime:     i.firstTime,
          lastTime:      i.lastTime,
          lastStepCount: i.lastStepCount
        })
      ),
      cursor: response.cursor,
    };
  };

</script>

<svelte:head>
  <title>Mi Datos</title>
</svelte:head>

{#if blockLoading}
  <BlockLoading/>
{/if}

{#if !checkingGrants}
  <div class="page-content">
    <div class="page-content-title mt-0 d-flex justify-content-between align-items-center">
      <!-- Cambia el título directamente -->
      <span>Mi Datos</span>
      <div class="pr-0 d-flex justify-content-end">
        <BaseButton size="sm" onclick={goBack} type="primary" disabled={loading}>
          <i class="fas fa-arrow-left fa-fw"></i>
        </BaseButton>
      </div>
    </div>
    <LoadingContentPage {loading} class="mb-3"/>
    <div class="row mx-0">
      <div class="col-12 px-3 border-sm-0">
        <PatientForm {patient} readonly/>
      </div>
    </div>
    {#if patient?.id}
      <!-- Tabla de Patologías del Paciente -->
      <div class="row mx-0 mt-4">
        <div class="col-12 px-3">
          <BaseTable
            pageId="my-pathologies"
            bind:this={pathologiesTable}
            tableTitle={$t('route.patient-pathology.my-list')}
            showOptions={false}
            columns={pathologiesColumns}
            scrollableFunction={scrollableFunctionPathology}
            itemsPerPage={Constants.DEFAULT_ITEMS_PER_PAGE}
            itemsPerPageOptions={Constants.ITEMS_PER_PAGE_OPTIONS}
            DataContainerClass={PathologySuggestionListDC}
            rowClickable={false}
          />
        </div>
      </div>
      <!-- Tabla de Fechas de Estudios -->
      <div class="row mx-0 mt-4">
        <div class="col-12 px-3">
          <BaseTable
            pageId="my-study-dates"
            bind:this={studyDatesTable}
            tableTitle={$t('route.study-dates.my-list')}
            showOptions={false}
            columns={studyDatesColumns}
            scrollableFunction={scrollableFunctionStudyDates}
            itemsPerPage={Constants.DEFAULT_ITEMS_PER_PAGE}
            itemsPerPageOptions={Constants.ITEMS_PER_PAGE_OPTIONS}
            DataContainerClass={StudyDateListDC}
            onrowclick={({ item }) => {
              goto(`/myinfo/studies/${item.studyDate}`);
            }}
          />
        </div>
      </div>
      <!-- Tabla de Alarmas -->
      <div class="row mx-0 mt-4">
        <div class="col-12 px-3">
          <BaseTable
            pageId="my-alarms"
            bind:this={alarmsTable}
            tableTitle={$t('route.patient-alarms.my-list')}
            showOptions={false}
            columns={alarmColumns}
            scrollableFunction={scrollableFunctionAlarms}
            itemsPerPage={Constants.DEFAULT_ITEMS_PER_PAGE}
            itemsPerPageOptions={Constants.ITEMS_PER_PAGE_OPTIONS}
            DataContainerClass={AlarmListDC}
            rowClickable={false}
          >
            {#snippet globalActionsSnippet()}
              {#if alarmCount > 0}
                <BaseButton
                  type="warning"
                  size="sm"
                  outline
                  onclick={deleteAllPatientAlarms}
                  disabled={deletingAlarms}
                  title="Completar todas las alarmas"
                >
                  {#if deletingAlarms}
                    <i class="fas fa-spinner fa-spin"></i>
                  {:else}
                    <i class="fas fa-check-double"></i>
                  {/if}
                  {#if deletingAlarms}
                    Procesando...
                  {:else}
                    Completar todas ({alarmCount})
                  {/if}
                </BaseButton>
              {/if}
            {/snippet}
            {#snippet customColumnSnippet(item, column)}
              {#if column.key === "actions"}
                <BaseButton
                  type="success"
                  size="sm"
                  outline
                  onclick={() => deleteAlarm(item.id)}
                  title="Marcar como completada"
                >
                  <i class="fas fa-check"></i>
                </BaseButton>
              {/if}
            {/snippet}
          </BaseTable>
        </div>
      </div>
      <!-- Tabla de Modelos del Paciente -->
      <div class="row mx-0 mt-4">
        <div class="col-12 px-3">
          <BaseTable
            pageId="my-patient-models"
            bind:this={ModelTable}
            tableTitle={$t('route.patient-models.my-list')}
            showOptions={false}
            columns={ModelColumns}
            scrollableFunction={scrollableFunctionModel}
            itemsPerPage={Constants.DEFAULT_ITEMS_PER_PAGE}
            itemsPerPageOptions={Constants.ITEMS_PER_PAGE_OPTIONS}
            DataContainerClass={PatientModelListDC}
            onrowclick={({ item }) =>  onRowClickedPatientModel(item)}
          />
        </div>
      </div>
    {/if}
  </div>
{/if}

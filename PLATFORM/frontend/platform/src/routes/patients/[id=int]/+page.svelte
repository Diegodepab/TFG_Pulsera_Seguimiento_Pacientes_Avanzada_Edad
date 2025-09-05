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
  import { ChatController } from "$lib/controllers/chat_controller";
  import { Chat } from "$lib/models/chat";
  import { ChatListDC } from "$lib/models/data_containers/chat_list_dc";

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
      }
    ];

  
  /** @type StudyController */
  const studyCtl = new StudyController();

  /** @type AlarmController */
  const alarmCtl = new AlarmController();

  /** @type ChatController */
  const chatCtl = new ChatController();

  /** @type boolean */
  let checkingGrants = $state(true);

  /** @type boolean */
  let loading = $state(true);

  /** @type boolean */
  let loadingChat = $state(false);

  /** @type Chat|null */
  let patientChat = $state(null);

  /** @type boolean */
  let deletingAlarms = $state(false);

  /** @type number */
  let alarmCount = $state(0);

  /** @type PatientController */
  const _patientCtl = new PatientController();

  /** @type Patient */
  let patient = $state(Patient.empty());

  /** @type {Map<PermissionsEntityType, UserPermission>} */
  const _entitiesAccess = new Map();

  /** @type CreatePatientModelModal */
  let _createPatientModelModal = $state();

  // manage changes into url from route
  let _idParam = $state(page.params.id);

  /** @type OnMount */
  onMount(async () => {
    (await SessionManager.userPermissionsOn([ PermissionsEntityType.PATIENT ]))
      ?.forEach((userPermission) => _entitiesAccess.set(userPermission.entityName, userPermission));

    if (
      !_entitiesAccess.get(PermissionsEntityType.PATIENT).uiVisibility
      || _entitiesAccess.get(PermissionsEntityType.PATIENT).read === PermissionsGrantType.NONE
    ) {
      CommonNotifications.noAccessPermissions();
      return await goBack();
    }

    checkingGrants = false;
    await loadPatientData();
    await checkPatientChat();
    await loadAlarmCount();
  });

  /**
   * Verifica si existe un chat abierto con este paciente
   * Separa el code del paciente por espacios para buscar first_name y last_name
   * Busca si existe un usuario con esos nombres y luego verifica si hay chat
   * @returns Promise<void>
   */
  const checkPatientChat = async () => {
    if (!patient?.id) {
      loadingChat = false;
      return;
    }
    
    loadingChat = true;
    try {
      // Obtener información del usuario actual
      const currentUser = await SessionManager.user();
      const patientCode = patient.code || "";
      
      // Si no hay código del paciente, no podemos buscar
      if (!patientCode.trim()) {
        patientChat = null;
        return;
      }
      
      // Separar el code del paciente por espacios para obtener first_name y last_name
      const nameParts = patientCode.trim().split(' ');
      if (nameParts.length < 2) {
        patientChat = null;
        return;
      }
      
      const firstName = nameParts[0];
      const lastName = nameParts.slice(1).join(' '); // En caso de múltiples apellidos
      
      try {
        const token = await SessionManager.token({ ignoreExceptions: true });
        
        // Primero intentar con /summary
        let chatResults = await chatCtl.search({
          params: new Map([
            [QueryFields.LIMIT, 50]
          ]),
          extraPath: "/summary"
          // NO usar transformer para obtener datos raw
        });
        
        // Si no hay resultados con /summary, intentar sin él
        if (!chatResults?.items?.length) {
          chatResults = await chatCtl.search({
            params: new Map([
              [QueryFields.LIMIT, 50]
            ])
            // Sin extraPath
          });
        }
        
        if (chatResults?.items?.length > 0) {
          // Buscar un chat donde el nombre del otro usuario coincida exactamente
          const matchingChat = chatResults.items.find(chat => {
            const chatFirstName = (chat.other_first_name || '').toLowerCase();
            const chatLastName = (chat.other_last_name || '').toLowerCase();
            
            return chatFirstName === firstName.toLowerCase() && 
                   chatLastName === lastName.toLowerCase();
          });
          
          if (matchingChat) {
            patientChat = {
              chat_id: matchingChat.chat_id,
              other_user_id: matchingChat.other_user_id,
              other_first_name: matchingChat.other_first_name,
              other_last_name: matchingChat.other_last_name,
              last_message: matchingChat.last_message,
              last_message_ts: matchingChat.last_message_ts
            };
          } else {
            patientChat = null;
          }
        } else {
          patientChat = null;
        }
      } catch (error) {
        console.error(`Error al obtener chats: ${error.message}`);
        patientChat = null;
      }
      
    } catch (error) {
      console.error("Error al verificar chat del paciente:", error);
      patientChat = null;
    } finally {
      loadingChat = false;
    }
  };

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
          [QueryFields.LIMIT, 1000] // Obtener todas para contar
        ])
      });

      alarmCount = alarmResults?.items?.length || 0;
    } catch (error) {
      console.error("Error al cargar el número de alarmas:", error);
      alarmCount = 0;
    }
  };

  /**
   * Navega al chat del paciente
   * @returns Promise<void>
   */
  const goToPatientChat = async () => {
    if (patientChat?.chat_id) {
      await goto(`${Routes.CHATS}/${patientChat.chat_id}`);
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
      // Primero obtenemos todas las alarmas del paciente
      const alarmResults = await alarmCtl.search({
        params: new Map([
          [QueryFields.Q, [
            new QueryParamsQ({
              field: Alarm.apiFields.patientId,
              operation: QueryComparativeOperations.EQ,
              value: patient.id
            })
          ]],
          [QueryFields.LIMIT, 1000] // Obtener todas las alarmas
        ])
      });

      // Eliminar cada alarma individualmente
      if (alarmResults?.items?.length > 0) {
        const deletePromises = alarmResults.items.map(alarm => 
          alarmCtl.delete(alarm.id)
        );
        
        await Promise.all(deletePromises);
        
        // Recargar la tabla de alarmas
        alarmsTable?.loadData();
        
        // Actualizar el contador de alarmas
        await loadAlarmCount();
        
        Global.notificationContext.addNotification({
          text: `Se han eliminado ${alarmResults.items.length} alarma(s) correctamente.`,
          position: 'top-right',
          type: 'success',
          removeAfter: 3000
        });
      } else {
        Global.notificationContext.addNotification({
          text: 'No se encontraron alarmas para eliminar.',
          position: 'top-right',
          type: 'info',
          removeAfter: 3000
        });
      }
    } catch (error) {
      console.error('Error al eliminar alarmas:', error);
      Global.notificationContext.addNotification({
        text: 'Error al eliminar las alarmas. Por favor, inténtelo de nuevo.',
        position: 'top-right',
        type: 'danger',
        removeAfter: 5000
      });
    } finally {
      deletingAlarms = false;
    }
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
   * Función paginada para obtener alarmas de este paciente.
   * @param {{ page?: string, params?: Map }} opts
   * @returns Promise<SearchResults<AlarmListDC>>
   */
  const scrollableFunctionAlarms = async (opts) => {
    opts     ??= {};
    opts.params ??= new Map();

    // 1) Filtrar por patient_id = patient.id
    opts.params.set(QueryFields.Q, [
      new QueryParamsQ({
        field: Alarm.apiFields.patientId,
        operation: QueryComparativeOperations.EQ,
        value: patient.id
      })
    ]);

    // 2) Ordenar por ts DESC
    opts.params.set(QueryFields.SORT, [
      new QueryParamsSort({
        field: Alarm.apiFields.ts,
        sort: QuerySortOrder.DESC
      })
    ]);

    // 3) Límite de 10
    opts.params.set(QueryFields.LIMIT, 10);

    // 4) Ejecutar búsqueda y transformar cada objeto JSON a AlarmListDC
    return await alarmCtl.search({
      ...opts,
      transformer: async (data) => AlarmListDC.fromJson(data)
    });
  };

  /**
   * @returns Promise<void>
   * @throws {Exception} Throws an error if patient data not loaded.
   */
  const loadPatientData = async () => {
    loading = true;
    try {
      /** @type {Map<QueryFields, unknown>} */
      const params = new Map();
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

      patient = await _patientCtl.get(page.params.id, { params });
      currPatientPathologies = patient?.patientPathologies ?? [];
    } catch (e) {
      if (!(e instanceof Exception) || e.code !== 404) throw e;
      await goBack();
      throw e;
    } finally {
      loading = false;
    }
  };

  /** @returns Promise<void> */
  const editPatient = async () => await goto(`${ Routes.PATIENTS }/${ patient.id }/edit`);

  /** @returns Promise<void> */
  const goBack = async () => await navigatorHistory.goBack(Routes.PATIENTS);

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

  /**
   * Elimina una alarma específica
   * @param {number} alarmId - ID de la alarma a eliminar
   * @returns Promise<void>
   */
  const deleteAlarm = async (alarmId) => {
    try {
      await alarmCtl.delete(alarmId);
      
      // Recargar la tabla de alarmas
      alarmsTable?.loadData();
      
      // Actualizar el contador de alarmas
      await loadAlarmCount();
      
      Global.notificationContext.addNotification({
        text: 'Alarma marcada como completada correctamente.',
        position: 'top-right',
        type: 'success',
        removeAfter: 3000
      });
    } catch (error) {
      console.error('Error al eliminar alarma:', error);
      Global.notificationContext.addNotification({
        text: 'Error al eliminar la alarma. Por favor, inténtelo de nuevo.',
        position: 'top-right',
        type: 'danger',
        removeAfter: 5000
      });
    }
  };

  $effect(() => {
    if (navigating && page.params.id && page.params.id !== _idParam) {
      _idParam = page.params.id;
      loadPatientData().then();
    }
  });

</script>

<svelte:head>
  <title>{$t('route.patient-details.title')}</title>
</svelte:head>

{#if blockLoading}
  <BlockLoading/>
{/if}

{#if !checkingGrants}
  <div class="page-content">
    <div class="page-content-title mt-0 d-flex justify-content-between align-items-center">
      <span>{$t('route.patient-details.form-title')}</span>

      <div class="pr-0 d-flex justify-content-end">
        <BaseButton size="sm" onclick={goBack} type="primary" disabled={loading}>
          <i class="fas fa-arrow-left fa-fw"></i>
        </BaseButton>

        {#if _entitiesAccess.get(PermissionsEntityType.PATIENT).write !== PermissionsGrantType.NONE}
          <div class="card-header-action-separator"></div>
          <BaseButton size="sm" type="primary" disabled={loading} onclick={editPatient}>
            <i class="fas fa-edit fa-fw"></i>
          </BaseButton>
        {/if}
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
              pageId="patient-pathology-patient-detail"
              bind:this={pathologiesTable}
              tableTitle={$t('route.patient-pathology.list')}
              showOptions={false}
              columns={pathologiesColumns}
              scrollableFunction={scrollableFunctionPathology}
              itemsPerPage={Constants.DEFAULT_ITEMS_PER_PAGE}
              itemsPerPageOptions={Constants.ITEMS_PER_PAGE_OPTIONS}
              DataContainerClass={PathologySuggestionListDC}
              rowClickable={false}
          >
            {#snippet globalActionsSnippet()}
              <BaseButton
                  type="primary"
                  size="sm"
                  outline
                  onclick={() => _linkPathologyModal?.openModal()}
                  disabled={loading}
              >
                <i class="fas fa-add fa-fw"></i>
              </BaseButton>
            {/snippet}
          </BaseTable>

          <LinkPathologyModal
              bind:this={_linkPathologyModal}
              {patient}
              linkedPathologies={currPatientPathologies}
              onSaved={onSavedPathologies}
          />
        </div>
      </div>

      <!-- Tabla de Fechas de Estudios -->
      <div class="row mx-0 mt-4">
        <div class="col-12 px-3">
          <BaseTable
            pageId="patient-study-dates"
            bind:this={studyDatesTable}
            tableTitle={$t('route.study-dates.list')}
            showOptions={false}
            columns={studyDatesColumns}
            scrollableFunction={scrollableFunctionStudyDates}
            itemsPerPage={Constants.DEFAULT_ITEMS_PER_PAGE}
            itemsPerPageOptions={Constants.ITEMS_PER_PAGE_OPTIONS}
            DataContainerClass={StudyDateListDC}
            onrowclick={({ item }) => {
              goto(`${Routes.PATIENTS}/${patient.id}/studies/${item.studyDate}`);
            }}
          />
        </div>
      </div>

      <!-- Tabla de Alarmas -->
      <div class="row mx-0 mt-4">
        <div class="col-12 px-3">
          <BaseTable
            pageId="patient-alarms"
            bind:this={alarmsTable}
            tableTitle={$t('route.patient-alarms.list')}
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

      <!-- Tabla de Modelos del Paciente 
      <div class="row mx-0 mt-4">
        <div class="col-12 px-3">
          <BaseTable
              pageId="patient-model-patient-detail"
              bind:this={ModelTable}
              tableTitle={$t('route.patient-models.list')}
              showOptions={false}
              columns={ModelColumns}
              scrollableFunction={scrollableFunctionModel}
              itemsPerPage={Constants.DEFAULT_ITEMS_PER_PAGE}
              itemsPerPageOptions={Constants.ITEMS_PER_PAGE_OPTIONS}
              DataContainerClass={PatientModelListDC}
              onrowclick={({ item }) =>  onRowClickedPatientModel(item)}
          >
            {#snippet globalActionsSnippet()}
              {#if _entitiesAccess.get(PermissionsEntityType.PATIENT)?.write !== PermissionsGrantType.NONE}
                <BaseButton
                    type="primary"
                    size="sm"
                    outline
                    onclick={() => _createPatientModelModal?.openModal()}
                    disabled={loading}
                >
                  <i class="fas fa-add fa-fw"></i>
                </BaseButton>
              {/if}
            {/snippet}
          </BaseTable>

          <CreatePatientModelModal
              bind:this={_createPatientModelModal}
              patientId={patient.id}
              onSaved={() => ModelTable?.loadData()}
          />
        </div>
      </div>

      -->

      <!-- Chat con el Paciente -->
      {#if loadingChat}
        <div class="row mx-0 mt-4">
          <div class="col-12 px-3">
            <div class="card border-info">
              <div class="card-body py-2 text-center">
                <small class="text-muted">
                  <i class="fas fa-spinner fa-spin mr-1"></i>
                  Verificando disponibilidad de chat...
                </small>
              </div>
            </div>
          </div>
        </div>
      {:else if patientChat}
        <div class="row mx-0 mt-4">
          <div class="col-12 px-3">
            <div class="card border-success">
              <div class="card-header bg-success text-white d-flex justify-content-between align-items-center">
                <h6 class="mb-0">
                  <i class="fas fa-comments mr-2"></i>
                  Chat Disponible
                </h6>
                <BaseButton
                  type="light"
                  size="sm"
                  onclick={goToPatientChat}
                >
                  Abrir Chat <i class="fas fa-external-link-alt ml-1"></i>
                </BaseButton>
              </div>
              <div class="card-body py-2">
                <small class="text-muted">
                  <i class="fas fa-user mr-1"></i>
                  Existe un chat activo con: <strong>{patientChat.other_first_name} {patientChat.other_last_name}</strong>
                </small>
              </div>
            </div>
          </div>
        </div>
      {/if}
    {/if}

  </div>
{/if}

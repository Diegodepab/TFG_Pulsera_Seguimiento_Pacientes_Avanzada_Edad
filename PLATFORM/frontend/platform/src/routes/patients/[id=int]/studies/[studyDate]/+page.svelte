<script>
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import { page } from "$app/stores";
  import { getNotificationsContext } from "svelte-notifications";
  import { t } from "svelte-i18n";

  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import BlockLoading from "$components/platform/commons/BlockLoading.svelte";
  import MedicalCharts from "$components/platform/charts/MedicalCharts.svelte";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Global } from "$lib/commons/global";
  import { Routes } from "$lib/commons/routes";
  import { SessionManager } from "$lib/commons/session_manager";
  import { navigatorHistory } from "$lib/commons/stores";
  import { PermissionsEntityType } from "$lib/models/user_permission";
  // Importar controlador y modelo
  import { StudyController } from "$lib/controllers/study_controller";
  import { PatientController } from "$lib/controllers/patient_controller"; 
  import { Study } from "$lib/models/study";
  import { Patient } from "$lib/models/patient";
  import { QueryFields, QueryParamsEmbed } from "$lib/services/utils/query_utils";

  // Inicializa contexto de notificaciones
  if (!Global.notificationContext) Global.notificationContext = getNotificationsContext();

  /** @type boolean */
  let checkingGrants = $state(true);
  /** @type boolean */
  let blockLoading = $state(false);
  /** @type boolean */
  let loadingData = $state(false);
  /** @type import("$lib/models/user_permission").UserPermission */
  let _entityAccess = $state();

  // Parámetros de ruta
  /** @type {string} */
  let studyDate = $state('');
  /** @type {number} */
  let patientId = $state(0);
  page.subscribe(($page) => {
    studyDate = $page.params.studyDate;
    patientId = Number($page.params.id);
  });

  const studyCtl = new StudyController();
  const patientCtl = new PatientController();
  /** @type {Study[]} */
  let studies = $state([]);
  /** @type {string} */
  let patientName = $state('Cargando...');
  /** @type {Patient} */
  let patient = $state(Patient.empty());

  onMount(async () => {
    const [permission] = await SessionManager.userPermissionsOn([PermissionsEntityType.STUDY]);
    _entityAccess = permission;

    if (!_entityAccess?.uiVisibility) {
      CommonNotifications.noAccessPermissions();
      return await goBack();
    }

    checkingGrants = false;
    await loadPatientName(); // Cargar nombre del paciente primero
    await loadStudies();
  });

  /** Carga el nombre del paciente */
  async function loadPatientName() {
    try {
      patient = await patientCtl.get(patientId);
      
      // Usar el código del paciente que contiene el nombre completo
      if (patient.code && patient.code.trim() && !patient.code.startsWith('Paciente #')) {
        patientName = patient.code;
      } else {
        patientName = `Paciente #${patientId}`;
      }
    } catch (error) {
      console.warn('No se pudo cargar el nombre del paciente:', error);
      // Fallback al formato original
      patientName = `Paciente #${patientId}`;
    }
  }

  /**
   * Formatea la fecha de manera amigable
   * @param {string} dateStr
   * @returns {string}
   */
  function formatDisplayDate(dateStr) {
    try {
      const date = new Date(dateStr + 'T00:00:00');
      return date.toLocaleDateString('es-ES', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric'
      });
    } catch (error) {
      return dateStr; // Fallback al formato original
    }
  }

  /** Carga todos los estudios del día siguiendo la paginación */
  async function loadAllStudies(baseUrl) {
    let allItems = [];
    let nextUrl = baseUrl;
    let pageCount = 0;
    const maxPages = 10; // Límite de seguridad para evitar bucles infinitos
    
    while (nextUrl && pageCount < maxPages) {
      const text = await studyCtl.fetch.getUrl(nextUrl);
      const response = JSON.parse(text);
      
      if (response.items && Array.isArray(response.items)) {
        allItems = allItems.concat(response.items);
      }
      
      // Verificar si hay más páginas
      if (response.next && response.next !== nextUrl) {
        // Si response.next es una URL relativa, usar la base del host
        if (response.next.startsWith('/')) {
          // Es una URL relativa como "/v1/studies?..." 
          const hostBase = new URL(studyCtl.fetch.host).origin; // Solo "http://localhost:3000"
          nextUrl = `${hostBase}${response.next}`;
        } else {
          // Es una URL completa
          nextUrl = response.next;
        }
      } else {
        nextUrl = null; // No hay más páginas
      }
      
      pageCount++;
    }
    
    return allItems;
  }

  /** Carga los estudios del día */
  async function loadStudies() {
    blockLoading = true;
    loadingData = true;
    try {
      // Asegurarse de que el header OAuth esté configurado
      await studyCtl.fetch.oauthHeader();
      
      try {
        // Intentar directamente con filtros de fecha
        const params = new URLSearchParams({
          patient_id: patientId.toString(),
          ts_from: `${studyDate}T00:00:00`,
          ts_to: `${studyDate}T23:59:59`,
          limit: '2500'
        });
        
        const url = `${studyCtl.fetch.host}${studyCtl.fetch.path}?${params.toString()}`;
        
        // Cargar todas las páginas si hay paginación
        const allItems = await loadAllStudies(url);
        
        // Transformar los datos
        if (allItems.length > 0) {
          studies = await Promise.all(
            allItems.map(item => Study.fromJson(item))
          );
        } else {
          studies = [];
        }
        
      } catch (filterError) {
        // Fallback: cargar sin filtros y filtrar en frontend
        const params = new URLSearchParams({
          patient_id: patientId.toString(),
          limit: '2500'
        });
        
        const url = `${studyCtl.fetch.host}${studyCtl.fetch.path}?${params.toString()}`;
        
        const allItems = await loadAllStudies(url);
        
        // Filtrar en el frontend por fecha
        const targetDate = new Date(studyDate + 'T00:00:00');
        const nextDay = new Date(studyDate + 'T23:59:59');
        
        const filteredItems = allItems.filter(item => {
          const itemDate = new Date(item.ts);
          return itemDate >= targetDate && itemDate <= nextDay;
        });
        
        // Transformar los datos filtrados
        if (filteredItems.length > 0) {
          studies = await Promise.all(
            filteredItems.map(item => Study.fromJson(item))
          );
        } else {
          studies = [];
        }
      }
    } catch (e) {
      console.error('Error cargando estudios:', e);
      studies = [];
      CommonNotifications.genericDanger('Error al cargar los estudios médicos');
    } finally {
      loadingData = false;
      blockLoading = false;
    }
  }

  const goBack = async () => navigatorHistory.goBack(Routes.PATIENTS);
</script>

<svelte:head>
  <title>Estudio Médico - {studyDate}</title>
</svelte:head>

{#if blockLoading}
  <BlockLoading />
{/if}

{#if !checkingGrants}
  <div class="page-content">
    <div class="page-header">
      <div class="page-title-section">
        <h1 class="page-title">
          <i class="fas fa-heartbeat text-danger"></i>
          Monitoreo Médico
        </h1>
        <div class="page-subtitle">
          <div class="patient-info">
            <i class="fas fa-user text-primary"></i>
            <span class="patient-name">{patientName}</span>
          </div>
          <div class="study-date-highlight">
            <i class="fas fa-calendar-day text-success"></i>
            <span class="date-label">Estudio del día:</span>
            <span class="study-date">{formatDisplayDate(studyDate)}</span>
          </div>
        </div>
      </div>
      <BaseButton size="sm" type="secondary" onclick={goBack} disabled={loadingData}>
        <i class="fas fa-arrow-left fa-fw"></i>
        Volver
      </BaseButton>
    </div>

    {#if loadingData}
      <div class="loading-state">
        <div class="loading-content">
          <div class="spinner-border text-primary" role="status"></div>
          <p class="loading-text">Cargando datos médicos...</p>
        </div>
      </div>
    {:else if studies.length === 0}
      <div class="empty-state">
        <div class="empty-content">
          <i class="fas fa-chart-line fa-3x text-muted mb-3"></i>
          <h4>No hay datos disponibles</h4>
          <p class="text-muted">No se encontraron estudios para este paciente en la fecha <strong>{studyDate}</strong>.</p>
          <div class="info-box">
            <p><strong>💡 Información:</strong></p>
            <p>Los datos de ejemplo solo están disponibles para los últimos 15 días.</p>
            <p>Prueba con una fecha más reciente, como <strong>2025-08-11</strong> (hoy).</p>
          </div>
          <BaseButton type="primary" onclick={goBack}>
            <i class="fas fa-arrow-left fa-fw"></i>
            Volver a la lista
          </BaseButton>
        </div>
      </div>
    {:else}
      <MedicalCharts {studies} {studyDate} />
    {/if}
  </div>
{/if}

<style>
  .page-content { 
    padding: 1.5rem; 
    min-height: 100vh;
    background: #f8f9fa;
  }
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 2rem;
    background: white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  }
  
  .page-title-section {
    flex: 1;
  }
  
  .page-title {
    font-size: 1.75rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
    color: #495057;
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }
  
  .page-subtitle {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .patient-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .patient-name {
    font-size: 1.2rem;
    font-weight: 600;
    color: #495057;
  }

  .study-date-highlight {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: linear-gradient(135deg, #e8f5e8, #f0f8ff);
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #28a745;
  }

  .date-label {
    font-size: 0.9rem;
    color: #6c757d;
    font-weight: 500;
  }
  
  .study-date {
    font-size: 1.1rem;
    color: #155724;
    font-weight: 600;
    text-transform: capitalize;
  }
  
  .loading-state, .empty-state {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 400px;
  }
  
  .loading-content, .empty-content {
    text-align: center;
    max-width: 400px;
  }
  
  .loading-text {
    margin-top: 1rem;
    color: #6c757d;
    font-size: 1.1rem;
  }
  
  .empty-content h4 {
    color: #495057;
    margin-bottom: 1rem;
  }
  
  .info-box {
    background: #e7f3ff;
    border: 1px solid #bee5eb;
    border-radius: 0.375rem;
    padding: 1rem;
    margin: 1rem 0;
    text-align: left;
  }
  
  .info-box p {
    margin: 0.5rem 0;
    color: #495057;
  }
  
  .info-box strong {
    color: #0056b3;
  }
  
  @media (max-width: 768px) {
    .page-content {
      padding: 1rem;
    }
    
    .page-header {
      flex-direction: column;
      gap: 1rem;
      align-items: stretch;
    }
    
    .page-title {
      font-size: 1.5rem;
    }
  }
</style>

<script>
  import { onMount, onDestroy } from 'svelte';
  import { browser } from '$app/environment';

  /** @type {Array<{id: number, patient_id: number, step_count: number, bpm: number, spo2: number, ts: string}>} */
  export let studies = [];
  
  /** @type {string} */
  export let studyDate = '';

  // Referencias a los canvas y charts
  let stepsCanvas, bpmCanvas, spo2Canvas;
  let stepsChart, bpmChart, spo2Chart;
  let Chart, zoomPlugin;

  // Variables para el slider temporal
  let timeSlider;
  let currentTimeRange = { start: 0, end: 100 };
  let totalDataPoints = 0;

  // Estadísticas simples
  let stats = {
    totalSteps: 0,
    avgBpm: 0,
    avgSpo2: 0,
    maxBpm: 0,
    minBpm: 0,
    maxSpo2: 0,
    minSpo2: 0,
    studyCount: 0
  };

  $: if (studies.length > 0) {
    calculateStats();
    if (browser && Chart) {
      updateCharts();
    }
  }

  function calculateStats() {
    // Crear una copia del array para evitar mutar el original
    const sortedStudies = [...studies].sort((a, b) => new Date(a.ts) - new Date(b.ts));
    
    // Filtrar valores válidos con conversión explícita a números
    const bpmValues = sortedStudies
      .map(s => Number(s.bpm))
      .filter(v => !isNaN(v) && v > 0);
    const spo2Values = sortedStudies
      .map(s => Number(s.spo2))
      .filter(v => !isNaN(v) && v > 0);
    const stepValues = sortedStudies
      .map(s => Number(s.stepCount || s.step_count))
      .filter(v => !isNaN(v) && v >= 0);
    
    
    stats.studyCount = sortedStudies.length;
    // El total de pasos es el valor máximo (último valor acumulativo)
    stats.totalSteps = stepValues.length > 0 ? Math.max(...stepValues) : 0;
    stats.avgBpm = bpmValues.length > 0 ? Math.round(bpmValues.reduce((sum, v) => sum + v, 0) / bpmValues.length) : 0;
    stats.avgSpo2 = spo2Values.length > 0 ? Math.round(spo2Values.reduce((sum, v) => sum + v, 0) / spo2Values.length) : 0;
    stats.maxBpm = bpmValues.length > 0 ? Math.max(...bpmValues) : 0;
    stats.minBpm = bpmValues.length > 0 ? Math.min(...bpmValues) : 0;
    stats.maxSpo2 = spo2Values.length > 0 ? Math.max(...spo2Values) : 0;
    stats.minSpo2 = spo2Values.length > 0 ? Math.min(...spo2Values) : 0;
  }

  function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('es-ES', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  }

  function formatDate(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleDateString('es-ES');
  }

  function updateCharts() {
    if (!browser || !Chart || studies.length === 0) return;

    // Crear una copia ordenada por tiempo
    const sortedStudies = [...studies].sort((a, b) => new Date(a.ts) - new Date(b.ts));
    
    // Preparar datos para las gráficas
    const labels = sortedStudies.map(s => formatTime(s.ts));
    // Convertir explícitamente a números y filtrar valores válidos
    const stepsData = sortedStudies.map(s => {
      const steps = Number(s.stepCount || s.step_count);
      return isNaN(steps) ? 0 : steps;
    });
    const bpmData = sortedStudies.map(s => {
      const bpm = Number(s.bpm);
      return isNaN(bpm) ? 0 : bpm;
    });
    const spo2Data = sortedStudies.map(s => {
      const spo2 = Number(s.spo2);
      return isNaN(spo2) ? 0 : spo2;
    });

    // Crear gráfica de pasos acumulativos
    createStepsChart(labels, stepsData);
    
    // Crear gráfica de BPM con escalas dinámicas
    createBpmChart(labels, bpmData);
    
    // Crear gráfica de SpO2 con escalas dinámicas
    createSpo2Chart(labels, spo2Data);

    // Inicializar el control de tiempo
    totalDataPoints = labels.length;
    currentTimeRange = { start: 0, end: 100 };
  }

  function createStepsChart(labels, data) {
    if (stepsChart) {
      stepsChart.destroy();
    }
    
    if (!stepsCanvas) return;

    // Filtrar valores válidos y calcular escalas dinámicas
    const validData = data.filter(v => v != null && v >= 0);
    const minSteps = validData.length > 0 ? Math.min(...validData) : 0;
    const maxSteps = validData.length > 0 ? Math.max(...validData) : 100;
    const stepRange = maxSteps - minSteps;
    const yMin = Math.max(0, minSteps - stepRange * 0.1);
    const yMax = maxSteps + stepRange * 0.1;

    stepsChart = new Chart(stepsCanvas, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Pasos Acumulativos',
          data: data,
          borderColor: '#28a745',
          backgroundColor: 'rgba(40, 167, 69, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointRadius: 2,
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          intersect: false,
          mode: 'index'
        },
        plugins: {
          title: {
            display: true,
            text: 'Pasos Acumulativos a lo largo del día',
            font: { size: 16, weight: 'bold' }
          },
          legend: {
            display: false
          },
          zoom: {
            zoom: {
              wheel: { enabled: true },
              pinch: { enabled: true },
              mode: 'x'
            },
            pan: {
              enabled: true,
              mode: 'x'
            }
          }
        },
        scales: {
          y: {
            min: validData.length > 0 ? yMin : 0,
            max: validData.length > 0 ? yMax : undefined,
            title: {
              display: true,
              text: 'Pasos',
              font: { weight: 'bold' }
            },
            grid: { color: 'rgba(0,0,0,0.1)' }
          },
          x: {
            title: {
              display: true,
              text: 'Hora',
              font: { weight: 'bold' }
            },
            grid: { color: 'rgba(0,0,0,0.1)' }
          }
        }
      }
    });
  }

  function createBpmChart(labels, data) {
    if (bpmChart) {
      bpmChart.destroy();
    }
    
    if (!bpmCanvas) return;

    // Calcular escalas dinámicas
    const validData = data.filter(v => v > 0);
    const minBpm = validData.length > 0 ? Math.min(...validData) : 60;
    const maxBpm = validData.length > 0 ? Math.max(...validData) : 100;
    const yMin = Math.max(40, minBpm - 5);
    const yMax = Math.min(120, maxBpm + 5);

    bpmChart = new Chart(bpmCanvas, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'BPM',
          data: data,
          borderColor: '#dc3545',
          backgroundColor: 'rgba(220, 53, 69, 0.1)',
          borderWidth: 3,
          fill: false,
          tension: 0.4,
          pointRadius: 2,
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          intersect: false,
          mode: 'index'
        },
        plugins: {
          title: {
            display: true,
            text: 'Frecuencia Cardíaca (BPM)',
            font: { size: 16, weight: 'bold' }
          },
          legend: {
            display: false
          },
          zoom: {
            zoom: {
              wheel: { enabled: true },
              pinch: { enabled: true },
              mode: 'x'
            },
            pan: {
              enabled: true,
              mode: 'x'
            }
          }
        },
        scales: {
          y: {
            min: yMin,
            max: yMax,
            title: {
              display: true,
              text: 'BPM',
              font: { weight: 'bold' }
            },
            grid: { color: 'rgba(0,0,0,0.1)' }
          },
          x: {
            title: {
              display: true,
              text: 'Hora',
              font: { weight: 'bold' }
            },
            grid: { color: 'rgba(0,0,0,0.1)' }
          }
        }
      }
    });
  }

  function createSpo2Chart(labels, data) {
    if (spo2Chart) {
      spo2Chart.destroy();
    }
    
    if (!spo2Canvas) return;

    // Calcular escalas dinámicas
    const validData = data.filter(v => v > 0);
    const minSpo2 = validData.length > 0 ? Math.min(...validData) : 95;
    const maxSpo2 = validData.length > 0 ? Math.max(...validData) : 100;
    const yMin = Math.max(85, minSpo2 - 2);
    const yMax = Math.min(100, maxSpo2 + 2);

    spo2Chart = new Chart(spo2Canvas, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'SpO2',
          data: data,
          borderColor: '#007bff',
          backgroundColor: 'rgba(0, 123, 255, 0.1)',
          borderWidth: 3,
          fill: false,
          tension: 0.4,
          pointRadius: 2,
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          intersect: false,
          mode: 'index'
        },
        plugins: {
          title: {
            display: true,
            text: 'Saturación de Oxígeno (SpO2)',
            font: { size: 16, weight: 'bold' }
          },
          legend: {
            display: false
          },
          zoom: {
            zoom: {
              wheel: { enabled: true },
              pinch: { enabled: true },
              mode: 'x'
            },
            pan: {
              enabled: true,
              mode: 'x'
            }
          }
        },
        scales: {
          y: {
            min: yMin,
            max: yMax,
            title: {
              display: true,
              text: 'SpO2 (%)',
              font: { weight: 'bold' }
            },
            grid: { color: 'rgba(0,0,0,0.1)' }
          },
          x: {
            title: {
              display: true,
              text: 'Hora',
              font: { weight: 'bold' }
            },
            grid: { color: 'rgba(0,0,0,0.1)' }
          }
        }
      }
    });
  }

  onDestroy(() => {
    if (stepsChart) stepsChart.destroy();
    if (bpmChart) bpmChart.destroy();
    if (spo2Chart) spo2Chart.destroy();
  });

  onMount(async () => {
    if (browser) {
      // Importar Chart.js dinámicamente solo en el cliente
      const ChartModule = await import('chart.js');
      const zoomPluginModule = await import('chartjs-plugin-zoom');
      
      Chart = ChartModule.Chart;
      zoomPlugin = zoomPluginModule.default;
      
      // Registrar todos los componentes de Chart.js y el plugin de zoom
      Chart.register(...ChartModule.registerables, zoomPlugin);
      
      // Inicializar gráficas si ya tenemos datos
      if (studies.length > 0) {
        updateCharts();
      }
    }
  });

  function resetZoom() {
    if (!browser || !Chart) return;
    if (stepsChart) stepsChart.resetZoom();
    if (bpmChart) bpmChart.resetZoom();
    if (spo2Chart) spo2Chart.resetZoom();
    
    // Resetear el slider y mostrar todos los datos
    currentTimeRange = { start: 0, end: 100 };
    if (timeSlider) timeSlider.value = 0;
    
    // Restaurar todos los datos originales
    if (studies.length > 0) {
      updateCharts();
    }
  }

  function handleTimeSliderChange(event) {
    const sliderValue = parseInt(event.target.value);
    const windowSize = 20; // Mostrar 20% de los datos a la vez
    
    currentTimeRange.start = sliderValue;
    currentTimeRange.end = Math.min(100, sliderValue + windowSize);
    
    applyTimeFilter();
  }

  function applyTimeFilter() {
    if (!browser || !Chart || studies.length === 0) return;
    
    const startIndex = Math.floor((currentTimeRange.start / 100) * totalDataPoints);
    const endIndex = Math.ceil((currentTimeRange.end / 100) * totalDataPoints);
    
    // Filtrar los datos originales
    const sortedStudies = [...studies].sort((a, b) => new Date(a.ts) - new Date(b.ts));
    const filteredStudies = sortedStudies.slice(startIndex, endIndex);
    
    if (filteredStudies.length === 0) return;
    
    // Preparar datos filtrados con conversión numérica
    const labels = filteredStudies.map(s => formatTime(s.ts));
    const stepsData = filteredStudies.map(s => {
      const steps = Number(s.stepCount || s.step_count);
      return isNaN(steps) ? 0 : steps;
    });
    const bpmData = filteredStudies.map(s => {
      const bpm = Number(s.bpm);
      return isNaN(bpm) ? 0 : bpm;
    });
    const spo2Data = filteredStudies.map(s => {
      const spo2 = Number(s.spo2);
      return isNaN(spo2) ? 0 : spo2;
    });
    
    // Actualizar cada gráfica con los datos filtrados
    if (stepsChart) {
      stepsChart.data.labels = labels;
      stepsChart.data.datasets[0].data = stepsData;
      stepsChart.update();
    }
    
    if (bpmChart) {
      bpmChart.data.labels = labels;
      bpmChart.data.datasets[0].data = bpmData;
      bpmChart.update();
    }
    
    if (spo2Chart) {
      spo2Chart.data.labels = labels;
      spo2Chart.data.datasets[0].data = spo2Data;
      spo2Chart.update();
    }
  }
</script>

<!-- Panel de información básica - PRIMERO -->
<div class="info-panel">
  <div class="info-header">
    <h3>
      <i class="fas fa-chart-line text-primary"></i>
      Resumen del día: {studyDate}
    </h3>
    <div class="study-count">
      <span class="badge badge-primary">{stats.studyCount} registros</span>
    </div>
  </div>
  
  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-icon">
        <i class="fas fa-walking text-success"></i>
      </div>
      <div class="stat-content">
        <div class="stat-value">{stats.totalSteps.toLocaleString()}</div>
        <div class="stat-label">Pasos totales</div>
      </div>
    </div>
    
    <div class="stat-card">
      <div class="stat-icon">
        <i class="fas fa-heartbeat text-danger"></i>
      </div>
      <div class="stat-content">
        <div class="stat-value">{stats.avgBpm}</div>
        <div class="stat-label">BPM promedio</div>
        <div class="stat-range">Rango: {stats.minBpm}-{stats.maxBpm}</div>
      </div>
    </div>
    
    <div class="stat-card">
      <div class="stat-icon">
        <i class="fas fa-lungs text-primary"></i>
      </div>
      <div class="stat-content">
        <div class="stat-value">{stats.avgSpo2}%</div>
        <div class="stat-label">SpO2 promedio</div>
        <div class="stat-range">Rango: {stats.minSpo2}-{stats.maxSpo2}%</div>
      </div>
    </div>
  </div>
</div>

<!-- Gráficas médicas con zoom y slider -->
<div class="charts-container">
  <div class="charts-header">
    <h4>
      <i class="fas fa-chart-area text-primary"></i>
      Gráficas Médicas
    </h4>
    <div class="chart-controls">
      <button class="btn btn-sm btn-outline-secondary" on:click={resetZoom}>
        <i class="fas fa-search-minus"></i>
        Reset Zoom
      </button>
      
      <!-- Slider de navegación temporal -->
      <div class="time-slider-container ms-3">
        <label for="timeSlider" class="form-label mb-0 me-2">
          <i class="fas fa-clock text-primary"></i>
          Navegación Temporal:
        </label>
        <input 
          type="range" 
          class="form-range time-slider" 
          id="timeSlider"
          min="0" 
          max="80" 
          step="5"
          value="0"
          bind:this={timeSlider}
          on:input={handleTimeSliderChange}
        />
        <small class="text-muted">
          Posición: {currentTimeRange.start}% - {currentTimeRange.end}%
        </small>
      </div>
      
      <small class="text-muted ms-2">
        💡 Usa la rueda del mouse para hacer zoom, arrastra para navegar
      </small>
    </div>
  </div>
  
  <div class="chart-grid">
    <div class="chart-card">
      <canvas bind:this={stepsCanvas} class="chart-canvas"></canvas>
    </div>
    
    <div class="chart-card">
      <canvas bind:this={bpmCanvas} class="chart-canvas"></canvas>
    </div>
    
    <div class="chart-card">
      <canvas bind:this={spo2Canvas} class="chart-canvas"></canvas>
    </div>
  </div>
</div>

<!-- Tabla de datos detallada -->
<div class="data-table-container">
  <div class="table-header">
    <h4>
      <i class="fas fa-table text-secondary"></i>
      Registros detallados
    </h4>
  </div>
  
  <div class="table-responsive">
    <table class="table table-striped">
      <thead>
        <tr>
          <th>Hora</th>
          <th>Fecha</th>
          <th>Pasos</th>
          <th>BPM</th>
          <th>SpO2</th>
        </tr>
      </thead>
      <tbody>
        {#each studies as study}
          <tr>
            <td class="font-monospace">{formatTime(study.ts)}</td>
            <td>{formatDate(study.ts)}</td>
            <td>
              <span class="badge badge-success">{study.stepCount || study.step_count || 0}</span>
            </td>
            <td>
              <span class="badge badge-{study.bpm >= 60 && study.bpm <= 100 ? 'success' : 'warning'}">
                {study.bpm} BPM
              </span>
            </td>
            <td>
              <span class="badge badge-{study.spo2 >= 95 ? 'success' : study.spo2 >= 90 ? 'warning' : 'danger'}">
                {study.spo2}%
              </span>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
  
  {#if studies.length === 0}
    <div class="no-data">
      <i class="fas fa-info-circle fa-2x text-muted mb-3"></i>
      <p class="text-muted">No hay datos disponibles para esta fecha</p>
    </div>
  {/if}
</div>

<style>
  .charts-container {
    margin-bottom: 2rem;
  }

  .charts-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    background: #f8f9fa;
    border-radius: 0.5rem 0.5rem 0 0;
    border-bottom: 1px solid #e9ecef;
    margin-bottom: 0;
  }

  .charts-header h4 {
    margin: 0;
    color: #495057;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .chart-controls {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .time-slider-container {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    min-width: 250px;
  }

  .time-slider {
    width: 150px;
    height: 6px;
    border-radius: 3px;
    background: #e9ecef;
    outline: none;
    -webkit-appearance: none;
  }

  .time-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: #007bff;
    cursor: pointer;
    border: 2px solid white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  }

  .time-slider::-moz-range-thumb {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: #007bff;
    cursor: pointer;
    border: 2px solid white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  }

  .btn {
    padding: 0.375rem 0.75rem;
    border: 1px solid #6c757d;
    border-radius: 0.375rem;
    background: white;
    color: #6c757d;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.875rem;
  }

  .btn:hover {
    background: #6c757d;
    color: white;
  }

  .chart-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
    background: white;
    padding: 1.5rem;
    border-radius: 0 0 0.5rem 0.5rem;
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  }

  .chart-card {
    background: #fafafa;
    border-radius: 0.5rem;
    padding: 1.5rem;
    border: 1px solid #e9ecef;
    height: 400px;
    position: relative;
  }

  .chart-canvas {
    width: 100% !important;
    height: 100% !important;
  }

  .info-panel {
    background: white;
    border-radius: 0.5rem;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  }

  .info-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e9ecef;
  }

  .info-header h3 {
    margin: 0;
    color: #495057;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .study-count .badge {
    font-size: 0.875rem;
    padding: 0.5rem 0.75rem;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
  }

  .stat-card {
    display: flex;
    align-items: center;
    padding: 1.25rem;
    background: #f8f9fa;
    border-radius: 0.5rem;
    border-left: 4px solid #007bff;
  }

  .stat-icon {
    font-size: 2rem;
    margin-right: 1rem;
    opacity: 0.8;
  }

  .stat-content {
    flex: 1;
  }

  .stat-value {
    font-size: 1.75rem;
    font-weight: 600;
    color: #495057;
    line-height: 1;
  }

  .stat-label {
    font-size: 0.875rem;
    color: #6c757d;
    margin-top: 0.25rem;
    font-weight: 500;
  }

  .stat-range {
    font-size: 0.75rem;
    color: #adb5bd;
    margin-top: 0.125rem;
  }

  .data-table-container {
    background: white;
    border-radius: 0.5rem;
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    overflow: hidden;
  }

  .table-header {
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #e9ecef;
    background: #f8f9fa;
  }

  .table-header h4 {
    margin: 0;
    color: #495057;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .table-responsive {
    max-height: 500px;
    overflow-y: auto;
  }

  .table {
    margin: 0;
  }

  .table th {
    background: #f8f9fa;
    border-top: none;
    font-weight: 600;
    color: #495057;
    position: sticky;
    top: 0;
    z-index: 10;
  }

  .table td {
    vertical-align: middle;
  }

  .badge {
    padding: 0.375rem 0.75rem;
    font-size: 0.75rem;
    font-weight: 500;
    border-radius: 0.375rem;
  }

  .badge-primary {
    background-color: #007bff;
    color: white;
  }

  .badge-success {
    background-color: #28a745;
    color: white;
  }

  .badge-warning {
    background-color: #ffc107;
    color: #212529;
  }

  .badge-danger {
    background-color: #dc3545;
    color: white;
  }

  .font-monospace {
    font-family: 'Courier New', monospace;
    font-size: 0.875rem;
  }

  .no-data {
    text-align: center;
    padding: 3rem;
    color: #6c757d;
  }

  .text-primary { color: #007bff !important; }
  .text-success { color: #28a745 !important; }
  .text-danger { color: #dc3545 !important; }
  .text-secondary { color: #6c757d !important; }
  .text-muted { color: #6c757d !important; }
  .ms-2 { margin-left: 0.5rem; }

  @media (max-width: 768px) {
    .charts-header {
      flex-direction: column;
      gap: 1rem;
      align-items: flex-start;
    }
    
    .chart-controls {
      flex-direction: column;
      width: 100%;
      gap: 1rem;
    }
    
    .time-slider-container {
      min-width: auto;
      width: 100%;
      flex-direction: column;
      gap: 0.5rem;
    }
    
    .time-slider {
      width: 100%;
    }
    
    .chart-card {
      height: 300px;
      padding: 1rem;
    }
    
    .stats-grid {
      grid-template-columns: 1fr;
    }
    
    .stat-card {
      padding: 1rem;
    }
    
    .stat-icon {
      font-size: 1.5rem;
    }
    
    .stat-value {
      font-size: 1.5rem;
    }
    
    .info-header {
      flex-direction: column;
      gap: 1rem;
      align-items: flex-start;
    }
  }

  @media (min-width: 1200px) {
    .chart-grid {
      grid-template-columns: repeat(2, 1fr);
    }
    
    .chart-card:first-child {
      grid-column: 1 / -1;
    }
  }
</style>

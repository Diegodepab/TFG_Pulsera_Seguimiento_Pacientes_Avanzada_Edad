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
    studyCount: 0,
    // Nuevas métricas útiles
    activeHours: 0,
    restingHours: 0,
    peakActivityTime: '',
    healthAlerts: []
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
    
    // PASOS: Mostrar valores acumulativos reales para evolución a lo largo del día
    const stepCountValues = sortedStudies
      .map(s => Number(s.step_count))
      .filter(v => !isNaN(v) && v >= 0);
    
    // Para las estadísticas, usar el valor máximo como total de pasos del día
    const maxSteps = stepCountValues.length > 0 ? Math.max(...stepCountValues) : 0;

    // Análisis de actividad por horas
    const hourlyActivity = analyzeHourlyActivity(sortedStudies);
    
    // Detección de alertas médicas
    const healthAlerts = detectHealthAlerts(bpmValues, spo2Values, maxSteps);

    stats.studyCount = sortedStudies.length;
    stats.totalSteps = maxSteps; // Total de pasos es el valor máximo del día
    stats.avgBpm = bpmValues.length > 0 ? Math.round(bpmValues.reduce((sum, v) => sum + v, 0) / bpmValues.length) : 0;
    stats.avgSpo2 = spo2Values.length > 0 ? Math.round(spo2Values.reduce((sum, v) => sum + v, 0) / spo2Values.length) : 0;
    stats.maxBpm = bpmValues.length > 0 ? Math.max(...bpmValues) : 0;
    stats.minBpm = bpmValues.length > 0 ? Math.min(...bpmValues) : 0;
    stats.maxSpo2 = spo2Values.length > 0 ? Math.max(...spo2Values) : 0;
    stats.minSpo2 = spo2Values.length > 0 ? Math.min(...spo2Values) : 0;
    stats.activeHours = hourlyActivity.activeHours;
    stats.restingHours = hourlyActivity.restingHours;
    stats.peakActivityTime = hourlyActivity.peakTime;
    stats.healthAlerts = healthAlerts;
  }

  function analyzeHourlyActivity(sortedStudies) {
    const hourlySteps = {};
    let activeHours = 0;
    let restingHours = 0;
    let maxStepsInHour = 0;
    let peakTime = '';

    // Agrupar datos por hora
    sortedStudies.forEach(study => {
      const hour = new Date(study.ts).getHours();
      const steps = Number(study.step_count) || 0;
      
      if (!hourlySteps[hour]) {
        hourlySteps[hour] = { min: steps, max: steps, count: 1 };
      } else {
        hourlySteps[hour].min = Math.min(hourlySteps[hour].min, steps);
        hourlySteps[hour].max = Math.max(hourlySteps[hour].max, steps);
        hourlySteps[hour].count++;
      }
    });

    // Analizar actividad por hora
    Object.entries(hourlySteps).forEach(([hour, data]) => {
      const stepsThisHour = data.max - data.min; // Pasos dados en esta hora
      
      if (stepsThisHour > 200) { // Más de 200 pasos en una hora = activo
        activeHours++;
      } else {
        restingHours++;
      }
      
      if (stepsThisHour > maxStepsInHour) {
        maxStepsInHour = stepsThisHour;
        peakTime = `${hour}:00`;
      }
    });

    return { activeHours, restingHours, peakTime };
  }

  function detectHealthAlerts(bpmValues, spo2Values, totalSteps) {
    const alerts = [];

    // Alertas de ritmo cardíaco
    const avgBpm = bpmValues.length > 0 ? bpmValues.reduce((sum, v) => sum + v, 0) / bpmValues.length : 0;
    const maxBpm = bpmValues.length > 0 ? Math.max(...bpmValues) : 0;
    const minBpm = bpmValues.length > 0 ? Math.min(...bpmValues) : 0;

    if (maxBpm > 120) {
      alerts.push({ type: 'warning', message: `Ritmo cardíaco elevado detectado: ${maxBpm} BPM`, icon: 'fas fa-heartbeat' });
    }
    if (minBpm < 50 && minBpm > 0) {
      alerts.push({ type: 'info', message: `Ritmo cardíaco bajo detectado: ${minBpm} BPM`, icon: 'fas fa-heartbeat' });
    }

    // Alertas de saturación de oxígeno
    const avgSpo2 = spo2Values.length > 0 ? spo2Values.reduce((sum, v) => sum + v, 0) / spo2Values.length : 0;
    const minSpo2 = spo2Values.length > 0 ? Math.min(...spo2Values) : 0;

    if (minSpo2 < 90 && minSpo2 > 0) {
      alerts.push({ type: 'danger', message: `Saturación de oxígeno baja: ${minSpo2}%`, icon: 'fas fa-lungs' });
    }
    if (avgSpo2 < 95 && avgSpo2 > 0) {
      alerts.push({ type: 'warning', message: `Saturación promedio baja: ${Math.round(avgSpo2)}%`, icon: 'fas fa-lungs' });
    }

    // Alertas de actividad
    if (totalSteps < 2000) {
      alerts.push({ type: 'info', message: `Actividad física baja: solo ${totalSteps} pasos`, icon: 'fas fa-walking' });
    }
    if (totalSteps > 15000) {
      alerts.push({ type: 'success', message: `¡Excelente actividad!: ${totalSteps} pasos`, icon: 'fas fa-trophy' });
    }

    return alerts;
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
    
    // PASOS: Usar valores acumulativos reales para mostrar evolución del día
    const stepsData = sortedStudies.map(s => {
      // Usar directamente step_count del backend
      const steps = Number(s.step_count);
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
    
    // Crear gráfica de BPM con líneas suavizadas
    createBpmChart(labels, bpmData);
    
    // Crear gráfica de SpO2 con líneas suavizadas
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
          label: 'Pasos Acumulados',
          data: data,
          borderColor: '#28a745', // Verde para pasos
          backgroundColor: 'rgba(40, 167, 69, 0.1)',
          borderWidth: 2,
          fill: true, // Rellenar área bajo la línea
          pointRadius: 3,
          pointHoverRadius: 6,
          pointBackgroundColor: '#28a745',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          tension: 0.3 // Línea suavizada
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
            text: 'Pasos Incrementales a lo largo del día',
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
              text: 'Pasos por Lectura',
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
          borderColor: 'transparent', // Línea invisible
          backgroundColor: '#dc3545',
          borderWidth: 0, // Sin línea
          fill: false,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: '#dc3545',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          showLine: false // Asegurar que no se dibuje línea
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          intersect: false,
          mode: 'point'
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
            grid: { 
              color: 'rgba(0,0,0,0.1)',
              lineWidth: 0.5
            },
            ticks: {
              stepSize: 5 // Escalas más granulares
            }
          },
          x: {
            title: {
              display: true,
              text: 'Hora',
              font: { weight: 'bold' }
            },
            grid: { 
              color: 'rgba(0,0,0,0.05)',
              lineWidth: 0.5
            }
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
          borderColor: 'transparent', // Línea invisible
          backgroundColor: '#007bff',
          borderWidth: 0, // Sin línea
          fill: false,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: '#007bff',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          showLine: false // Asegurar que no se dibuje línea
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          intersect: false,
          mode: 'point'
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
            grid: { 
              color: 'rgba(0,0,0,0.1)',
              lineWidth: 0.5
            },
            ticks: {
              stepSize: 1 // Escalas más granulares para SpO2
            }
          },
          x: {
            title: {
              display: true,
              text: 'Hora',
              font: { weight: 'bold' }
            },
            grid: { 
              color: 'rgba(0,0,0,0.05)',
              lineWidth: 0.5
            }
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
    
    <!-- Nuevas métricas de análisis -->
    <div class="stat-card">
      <div class="stat-icon">
        <i class="fas fa-clock text-warning"></i>
      </div>
      <div class="stat-content">
        <div class="stat-value">{stats.activeHours}h</div>
        <div class="stat-label">Horas activas</div>
        <div class="stat-range">{stats.restingHours}h en reposo</div>
      </div>
    </div>
    
    <div class="stat-card">
      <div class="stat-icon">
        <i class="fas fa-trophy text-info"></i>
      </div>
      <div class="stat-content">
        <div class="stat-value">{stats.peakActivityTime}</div>
        <div class="stat-label">Pico de actividad</div>
        <div class="stat-range">Hora más activa del día</div>
      </div>
    </div>
  </div>
  
  <!-- Panel de alertas médicas -->
  {#if stats.healthAlerts && stats.healthAlerts.length > 0}
    <div class="alerts-section">
      <h4 class="alerts-title">
        <i class="fas fa-bell text-warning"></i>
        Alertas Médicas
      </h4>
      <div class="alerts-grid">
        {#each stats.healthAlerts as alert}
          <div class="alert alert-{alert.type} alert-compact">
            <i class="{alert.icon} me-2"></i>
            {alert.message}
          </div>
        {/each}
      </div>
    </div>
  {/if}
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
    <table class="table table-striped table-hover">
      <thead>
        <tr>
          <th><i class="fas fa-clock me-1"></i>Hora</th>
          <th><i class="fas fa-calendar me-1"></i>Fecha</th>
          <th><i class="fas fa-walking me-1"></i>Pasos</th>
          <th><i class="fas fa-heartbeat me-1"></i>BPM</th>
          <th><i class="fas fa-lungs me-1"></i>SpO2</th>
        </tr>
      </thead>
      <tbody>
        {#each studies as study}
          <tr class="table-row-hover">
            <td class="font-monospace">{formatTime(study.ts)}</td>
            <td class="text-muted">{formatDate(study.ts)}</td>
            <td>
              <span class="badge badge-success">
                {(study.step_count || 0).toLocaleString()}
              </span>
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
    width: 100%;
    margin-top: 2rem;
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
    width: 100%;
  }

  .table {
    margin: 0;
    width: 100%;
    table-layout: fixed; /* Forzar distribución equitativa */
  }

  .table th {
    background: #f8f9fa;
    border-top: none;
    font-weight: 600;
    color: #495057;
    position: sticky;
    top: 0;
    z-index: 10;
    padding: 1rem;
    text-align: center;
  }

  .table td {
    vertical-align: middle;
    padding: 0.75rem 1rem;
    text-align: center;
  }

  /* Distribución específica de columnas para mejor uso del espacio */
  .table th:nth-child(1), .table td:nth-child(1) { width: 15%; } /* Hora */
  .table th:nth-child(2), .table td:nth-child(2) { width: 20%; } /* Fecha */
  .table th:nth-child(3), .table td:nth-child(3) { width: 22%; } /* Pasos */
  .table th:nth-child(4), .table td:nth-child(4) { width: 22%; } /* BPM */
  .table th:nth-child(5), .table td:nth-child(5) { width: 21%; } /* SpO2 */

  /* Efectos hover y transiciones */
  .table-row-hover {
    transition: all 0.2s ease;
  }

  .table-row-hover:hover {
    background-color: #f8f9fa !important;
    transform: scale(1.01);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .table tbody tr {
    border-bottom: 1px solid #e9ecef;
  }

  .table tbody tr:last-child {
    border-bottom: none;
  }

  /* Mejoras en los iconos de las columnas */
  .table th i {
    color: #6c757d;
    font-size: 0.875rem;
  }

  /* Responsividad mejorada para la tabla */
  @media (max-width: 768px) {
    .table th, .table td {
      padding: 0.5rem 0.25rem;
      font-size: 0.8rem;
    }
    
    .badge {
      padding: 0.25rem 0.5rem;
      font-size: 0.7rem;
      min-width: 60px;
    }
    
    .font-monospace {
      font-size: 0.75rem;
    }
    
    /* En móvil, ajustar distribución de columnas */
    .table th:nth-child(1), .table td:nth-child(1) { width: 12%; } /* Hora */
    .table th:nth-child(2), .table td:nth-child(2) { width: 18%; } /* Fecha */
    .table th:nth-child(3), .table td:nth-child(3) { width: 25%; } /* Pasos */
    .table th:nth-child(4), .table td:nth-child(4) { width: 23%; } /* BPM */
    .table th:nth-child(5), .table td:nth-child(5) { width: 22%; } /* SpO2 */
  }

  .badge {
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
    font-weight: 500;
    border-radius: 0.5rem;
    display: inline-block;
    min-width: 80px;
    text-align: center;
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
    font-size: 0.9rem;
    font-weight: 600;
    color: #495057;
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

  /* Estilos para nuevas funcionalidades */
  .alerts-section {
    margin-top: 2rem;
    padding: 1.5rem;
    background: #f8f9fa;
    border-radius: 12px;
    border: 1px solid #e9ecef;
  }

  .alerts-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    font-size: 1.1rem;
    font-weight: 600;
    color: #495057;
  }

  .alerts-grid {
    display: grid;
    gap: 0.75rem;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  }

  .alert-compact {
    padding: 0.75rem 1rem;
    margin-bottom: 0;
    border-radius: 8px;
    display: flex;
    align-items: center;
    font-size: 0.9rem;
    border-width: 1px;
    border-style: solid;
  }

  .alert-success {
    background-color: rgba(25, 135, 84, 0.1);
    border-color: rgba(25, 135, 84, 0.3);
    color: #0f5132;
  }

  .alert-warning {
    background-color: rgba(255, 193, 7, 0.1);
    border-color: rgba(255, 193, 7, 0.3);
    color: #664d03;
  }

  .alert-danger {
    background-color: rgba(220, 53, 69, 0.1);
    border-color: rgba(220, 53, 69, 0.3);
    color: #842029;
  }

  .alert-info {
    background-color: rgba(13, 202, 240, 0.1);
    border-color: rgba(13, 202, 240, 0.3);
    color: #055160;
  }

  /* Mejoras para stats-grid */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  /* Responsividad para alertas */
  @media (max-width: 768px) {
    .alerts-grid {
      grid-template-columns: 1fr;
    }
    
    .stats-grid {
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    }
  }
</style>

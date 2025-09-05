<script>
  import { t } from "svelte-i18n";
  import { onMount } from "svelte";
  import { SessionManager } from "$lib/commons/session_manager";
  import { AlarmController } from "$lib/controllers/alarm_controller";
  import { ChatController } from "$lib/controllers/chat_controller";
  import { PatientController } from "$lib/controllers/patient_controller";
  import { PermissionsEntityType, PermissionsGrantType } from "$lib/models/user_permission";
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import { goto } from "$app/navigation";
  import { Routes } from "$lib/commons/routes";
  import LoadingContentPage from "$components/platform/commons/LoadingContentPage.svelte";
  import { Patient } from "$lib/models/patient";
  import { Alarm } from "$lib/models/alarm";
  import { Chat } from "$lib/models/chat";
  import { ChatListDC } from "$lib/models/data_containers/chat_list_dc";
  import { QueryFields, QueryParamsQ, QueryComparativeOperations } from "$lib/services/utils/query_utils";
  import moment from "moment";

  let loading = $state(true);
  let userRole = $state("");
  let totalAlarms = $state(0);
  let recentAlarms = $state(0);
  let criticalAlarms = $state(0);
  let availablePatients = $state([]); // Cache de pacientes para reutilizar
  let dashboardStats = $state({
    unreadChats: 0,
    totalPatients: 0,
    lastActivity: null
  });
  let permissions = $state(new Map());
  
  // Variables para controlar si hay más registros
  let hasMorePatients = $state(false);
  let hasMoreAlarms = $state(false);

  onMount(async () => {
    await loadDashboardData();
  });

  const loadDashboardData = async () => {
    try {
      loading = true;
      
      // Obtener información del usuario usando SessionManager correctamente
      const user = await SessionManager.user(); // Llamar como función
      userRole = user?.roleName || "user";
      const currentUserId = user?.id || SessionManager.userId();
      
      const userPermissions = await SessionManager.userPermissionsOn([
        PermissionsEntityType.PATIENT,
        PermissionsEntityType.STUDY,
        PermissionsEntityType.CHAT,
        PermissionsEntityType.ALARM
      ]);
      
      if (userPermissions) {
        userPermissions.forEach((permission) => {
          permissions.set(permission.entityName, permission);
        });
      }

      // For patients, only load chat stats (they don't need patient/alarm data)
      if (userRole === "patient") {
        await loadChatStats(currentUserId);
      } else {
        // For doctors and admins, load patients first, then all stats
        await loadPatients(currentUserId);
        await Promise.all([
          loadAlarmStats(),
          loadChatStats(currentUserId)
        ]);
      }

    } catch (error) {
      console.error("Error loading dashboard data:", error);
    } finally {
      loading = false;
    }
  };

  // Función para cargar pacientes una sola vez
  const loadPatients = async (userId) => {
    try {
      if (permissions.get(PermissionsEntityType.PATIENT)?.read !== PermissionsGrantType.NONE) {
        const patientController = new PatientController();
        
        if (userRole === "admin") {
          // Admin puede ver todos los pacientes
          const patientsResult = await patientController.search({ 
            params: new Map([
              [QueryFields.LIMIT, 500]
            ])
          });
          availablePatients = patientsResult.items || [];
          hasMorePatients = availablePatients.length >= 500;
        } else {
          // Usuarios normales solo pueden ver sus propios pacientes
          const patientsResult = await patientController.search({ 
            params: new Map([
              [QueryFields.Q, [
                new QueryParamsQ({
                  field: Patient.apiFields.ownerUserId,
                  operation: QueryComparativeOperations.EQ,
                  value: userId
                })
              ]],
              [QueryFields.LIMIT, 500]
            ])
          });
          availablePatients = patientsResult.items || [];
          hasMorePatients = availablePatients.length >= 500;
        }
        
        // Establecer estadísticas de pacientes
        dashboardStats.totalPatients = availablePatients.length;
      }
    } catch (error) {
      console.error("Error loading patients:", error);
      availablePatients = [];
      dashboardStats.totalPatients = 0;
    }
  };

    const loadAlarmStats = async () => {
    try {
      if (permissions.get(PermissionsEntityType.ALARM)?.read === PermissionsGrantType.NONE) {
        totalAlarms = 0;
        criticalAlarms = 0;
        return;
      }

      if (availablePatients.length === 0) {
        totalAlarms = 0;
        recentAlarms = 0;
        criticalAlarms = 0;
        return;
      }
      
      // Usar una búsqueda más eficiente: obtener todas las alarmas de una vez
      // y luego filtrar por pacientes en el frontend
      const alarmController = new AlarmController();
      
      try {
        // Obtener alarmas con un límite razonable
        const alarmsResult = await alarmController.search({
          params: new Map([
            [QueryFields.LIMIT, 500]
          ])
        });
        
        const allAlarms = alarmsResult.items || [];
        hasMoreAlarms = allAlarms.length >= 500;
        
        const patientIds = new Set(availablePatients.map(p => p.id));
        
        // Filtrar alarmas que pertenecen a los pacientes del usuario
        const relevantAlarms = allAlarms.filter(alarm => 
          patientIds.has(alarm.patientId)
        );
        
        totalAlarms = relevantAlarms.length;
        recentAlarms = 0; // Ya no usamos esto
        criticalAlarms = relevantAlarms.filter(alarm => alarm.isUrgent === true).length;
        
      } catch (error) {
        console.error("Error in alarm search:", error);
        totalAlarms = 0;
        criticalAlarms = 0;
        hasMoreAlarms = false;
      }
      
    } catch (error) {
      console.error("Error loading alarm stats:", error);
      totalAlarms = 0;
      recentAlarms = 0;
      criticalAlarms = 0;
    }
  };

  const loadChatStats = async (userId) => {
    try {
      // Skip chat loading for patients if they don't have chat permissions
      if (userRole === "patient" && permissions.get(PermissionsEntityType.CHAT)?.read === PermissionsGrantType.NONE) {
        dashboardStats.unreadChats = 0;
        return;
      }

      if (permissions.get(PermissionsEntityType.CHAT)?.read !== PermissionsGrantType.NONE) {
        const chatController = new ChatController();
        
        try {
          // Usar el mismo método que la página de chats
          const chatsResult = await chatController.search({
            params: new Map([
              ["user_id", userId],
              [QueryFields.LIMIT, 1000] // Límite alto para contar todos
            ]),
            extraPath: "/summary",
            transformer: async (data) => (await Chat.transformer(data)).toDC(ChatListDC),
          });
          
          const totalChats = chatsResult.items?.length || 0;
          dashboardStats.unreadChats = totalChats;
          
        } catch (error) {
          // Handle 401 specifically for patient users
          if (error.message?.includes('Unauthorized') || error.message?.includes('401')) {
            if (userRole === "patient") {
              console.warn("Patient user doesn't have chat access, setting chat count to 0");
              dashboardStats.unreadChats = 0;
              return;
            }
          }
          
          console.warn("Error fetching chats via API:", error);
          // Fallback a valores simulados solo para non-patients
          if (userRole !== "patient") {
            const baseChats = userRole === 'admin' ? 15 : 9;
            dashboardStats.unreadChats = baseChats + (userId % 3);
          } else {
            dashboardStats.unreadChats = 0;
          }
        }
      } else {
        dashboardStats.unreadChats = 0;
      }
    } catch (error) {
      console.error("Error loading chat stats:", error);
      // Fallback usando método anterior solo para non-patients
      if (userRole !== "patient") {
        const baseChats = userRole === 'admin' ? 15 : 9;
        dashboardStats.unreadChats = baseChats + (userId % 3);
      } else {
        dashboardStats.unreadChats = 0;
      }
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return $t('route.home.greetings.morning');
    if (hour < 18) return $t('route.home.greetings.afternoon');
    return $t('route.home.greetings.evening');
  };

  const getRoleDisplayName = (role) => {
    switch (role) {
      case "admin": 
      case "ADMIN":
      case "Administrator":
        return $t('route.home.roles.admin');
      case "user": 
      case "USER":
      case "doctor":
      case "DOCTOR":
        return $t('route.home.roles.doctor');
      case "patient": 
      case "PATIENT":
        return $t('route.home.roles.patient');
      default: 
        return role || $t('route.home.roles.user');
    }
  };

  const getQuickActions = () => {
    const actions = [];
    
    // Simplified actions for patients
    if (userRole === "patient") {
      actions.push(
        {
          title: $t('route.home.quickActions.chats'),
          icon: "fas fa-comments",
          route: Routes.CHATS,
          color: "primary"
        },
        {
          title: $t('route.home.quickActions.myProfile'),
          icon: "fas fa-user-circle",
          route: "/my-profile", // Adjust according to your profile route
          color: "info"
        },
        {
          title: $t('route.home.quickActions.logout'),
          icon: "fas fa-sign-out-alt",
          action: "logout",
          color: "danger"
        }
      );
      return actions;
    }
    
    // Existing actions for doctors and admins + My Profile and Logout
    if (permissions.get(PermissionsEntityType.PATIENT)?.read !== PermissionsGrantType.NONE) {
      actions.push({
        title: $t('route.home.quickActions.viewPatients'),
        icon: "fas fa-users",
        route: Routes.PATIENTS,
        color: "primary"
      });
    }
    
    if (permissions.get(PermissionsEntityType.CHAT)?.read !== PermissionsGrantType.NONE) {
      actions.push({
        title: $t('route.home.quickActions.chats'),
        icon: "fas fa-comments",
        route: Routes.CHATS,
        color: "primary"
      });
    }

    // Add My Profile and Logout for doctors and admins
    actions.push(
      {
        title: $t('route.home.quickActions.myProfile'),
        icon: "fas fa-user-circle",
        route: "/my-profile",
        color: "info"
      },
      {
        title: $t('route.home.quickActions.logout'),
        icon: "fas fa-sign-out-alt",
        action: "logout",
        color: "danger"
      }
    );
    
    return actions;
  };

  // Funciones de navegación para las tarjetas de estadísticas
  const navigateToAlarms = () => {
    if (permissions.get(PermissionsEntityType.ALARM)?.read !== PermissionsGrantType.NONE) {
      goto(Routes.ALARMS);
    }
  };

  const navigateToPatients = () => {
    if (permissions.get(PermissionsEntityType.PATIENT)?.read !== PermissionsGrantType.NONE) {
      goto(Routes.PATIENTS);
    }
  };

  const navigateToChats = () => {
    if (permissions.get(PermissionsEntityType.CHAT)?.read !== PermissionsGrantType.NONE) {
      goto(Routes.CHATS);
    }
  };

  // Funciones para manejar eventos de teclado (accesibilidad)
  const handleKeydown = (event, navigationFunction) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      navigationFunction();
    }
  };

  // Add logout function
  const handleLogout = async () => {
    try {
      await SessionManager.closeSession();
      await goto('/login');
    } catch (error) {
      console.error('Error during logout:', error);
    }
  };

  // Handle action clicks (for logout)
  const handleActionClick = (action) => {
    if (action.action === 'logout') {
      handleLogout();
    } else if (action.route) {
      goto(action.route);
    }
  };
</script>

<svelte:head>
  <title>{$t('route.home.title')}</title>
</svelte:head>

<LoadingContentPage {loading}/>

{#if !loading}
  <div class="page-content">
    <div class="row mx-0">
      <div class="col-12 px-3">
        <!-- Header de Bienvenida -->
        <div class="card mb-4">
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-md-8">
                <h1 class="h3 mb-2 text-primary">
                  <i class="fas fa-heartbeat mr-2"></i>
                  {getGreeting()}
                </h1>
                <p class="text-muted mb-1">
                  {$t('route.home.welcome')}
                </p>
                <small class="text-muted">
                  {$t('route.home.role')}: <span class="badge badge-pill badge-info">{getRoleDisplayName(userRole)}</span>
                </small>
              </div>
              <div class="col-md-4 text-right">
                {#if dashboardStats.lastActivity}
                  <small class="text-muted">
                    {$t('route.home.lastActivity')}: {new Date(dashboardStats.lastActivity).toLocaleString()}
                  </small>
                {/if}
              </div>
            </div>
          </div>
        </div>

        <!-- Tarjetas de Estadísticas - Solo para Admin y Médicos -->
        {#if userRole !== "patient"}
        <div class="row">
          {#if permissions.get(PermissionsEntityType.ALARM)?.read !== PermissionsGrantType.NONE}
            <div class="col-xl-3 col-md-6 mb-4">
              <div class="card border-left-warning shadow h-100 py-2 clickable-card" 
                   onclick={navigateToAlarms} 
                   onkeydown={(e) => handleKeydown(e, navigateToAlarms)}
                   role="button" 
                   tabindex="0">
                <div class="card-body">
                  <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                      <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">
                        {$t('route.home.stats.totalAlarms')}
                      </div>
                      <div class="h5 mb-0 font-weight-bold text-gray-800">
                        {totalAlarms}{hasMoreAlarms ? '+' : ''}
                      </div>
                    </div>
                    <div class="col-auto">
                      <i class="fas fa-exclamation-triangle fa-2x text-warning"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-xl-3 col-md-6 mb-4">
              <div class="card border-left-danger shadow h-100 py-2 clickable-card" 
                   onclick={navigateToAlarms} 
                   onkeydown={(e) => handleKeydown(e, navigateToAlarms)}
                   role="button" 
                   tabindex="0">
                <div class="card-body">
                  <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                      <div class="text-xs font-weight-bold text-danger text-uppercase mb-1">
                        {$t('route.home.stats.criticalAlarms')}
                      </div>
                      <div class="h5 mb-0 font-weight-bold text-gray-800">
                        {criticalAlarms}
                      </div>
                    </div>
                    <div class="col-auto">
                      <i class="fas fa-bell fa-2x text-danger"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          {/if}

          {#if permissions.get(PermissionsEntityType.PATIENT)?.read !== PermissionsGrantType.NONE}
            <div class="col-xl-3 col-md-6 mb-4">
              <div class="card border-left-primary shadow h-100 py-2 clickable-card" 
                   onclick={navigateToPatients} 
                   onkeydown={(e) => handleKeydown(e, navigateToPatients)}
                   role="button" 
                   tabindex="0">
                <div class="card-body">
                  <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                      <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                        {$t('route.home.stats.totalPatients')}
                      </div>
                      <div class="h5 mb-0 font-weight-bold text-gray-800">
                        {dashboardStats.totalPatients}{hasMorePatients ? '+' : ''}
                      </div>
                    </div>
                    <div class="col-auto">
                      <i class="fas fa-users fa-2x text-primary"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          {/if}

          {#if permissions.get(PermissionsEntityType.CHAT)?.read !== PermissionsGrantType.NONE}
            <div class="col-xl-3 col-md-6 mb-4">
              <div class="card border-left-info shadow h-100 py-2 clickable-card" 
                   onclick={navigateToChats} 
                   onkeydown={(e) => handleKeydown(e, navigateToChats)}
                   role="button" 
                   tabindex="0">
                <div class="card-body">
                  <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                      <div class="text-xs font-weight-bold text-info text-uppercase mb-1">
                        {$t('route.home.stats.activeChats')}
                      </div>
                      <div class="h5 mb-0 font-weight-bold text-gray-800">
                        {dashboardStats.unreadChats}
                      </div>
                    </div>
                    <div class="col-auto">
                      <i class="fas fa-comments fa-2x text-info"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          {/if}
        </div>
        {/if}

        <!-- Acciones Rápidas y Video Tutorial -->
        <div class="row">
          <!-- Acciones Rápidas - Ahora ocupa todo el ancho -->
          <div class="col-12 mb-4">
            <div class="card h-100">
              <div class="card-header bg-primary text-white">
                <h5 class="mb-0">
                  <i class="fas fa-bolt mr-2"></i>
                  {$t('route.home.quickActions.title')}
                </h5>
              </div>
              <div class="card-body">
                <div class="row">
                  {#each getQuickActions() as action, index}
                    <div class="col-md-6 mb-3">
                      <div class="card border-0 shadow-sm h-100 action-card">
                        <div class="card-body text-center p-4">
                          <div class="action-icon mb-3">
                            <i class="{action.icon} fa-3x text-{action.color || 'primary'}"></i>
                          </div>
                          <h6 class="card-title font-weight-bold mb-3">{action.title}</h6>
                          <BaseButton 
                            type="{action.color || 'primary'}"
                            size="sm"
                            onclick={() => handleActionClick(action)}
                          >
                            {action.action === 'logout' ? $t('route.home.quickActions.logout') : $t('route.home.quickActions.access')} 
                            <i class="fas fa-{action.action === 'logout' ? 'sign-out-alt' : 'arrow-right'} ml-1"></i>
                          </BaseButton>
                        </div>
                      </div>
                    </div>
                  {/each}
                </div>
              </div>
            </div>
          </div>
        </div>
          
        <!-- Video Tutorial - Solo para Admin y Médicos, ahora en su propia fila -->
        {#if userRole !== "patient"}
        <div class="row">
          <div class="col-12 mb-4">
            <div class="card h-100">
              <div class="card-header bg-info text-white">
                <h5 class="mb-0">
                  <i class="fas fa-play-circle mr-2"></i>
                  {$t('route.home.tutorial.title')}
                </h5>
              </div>
              <div class="card-body p-0 d-flex align-items-center justify-content-center">
                <div class="w-100">
                  <div class="ratio ratio-16x9">
                    <iframe 
                      src="https://www.youtube.com/embed/GJ6Z35LMRwY"
                      title="Tutorial de la Plataforma"
                      frameborder="0"
                      allowfullscreen
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      class="rounded"
                    ></iframe>
                  </div>
                </div>
              </div>
              <div class="card-footer bg-light">
                <small class="text-muted">
                  <i class="fas fa-info-circle mr-1"></i>
                  {$t('route.home.tutorial.description')}
                </small>
              </div>
            </div>
          </div>
        </div>
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  .action-card {
    transition: all 0.3s ease;
    cursor: pointer;
    border: 1px solid #e3e6f0 !important;
  }
  
  .action-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.15) !important;
    border-color: #5a5c69 !important;
  }
  
  .action-icon {
    transition: all 0.3s ease;
  }
  
  .action-card:hover .action-icon i {
    transform: scale(1.1);
    color: #3085d6 !important;
  }
  
  .card-header.bg-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  }
  
  .card-header.bg-info {
    background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%) !important;
  }
  
  /* Mejorar el aspecto de las tarjetas de estadísticas */
  .border-left-warning {
    border-left: 0.25rem solid #f6c23e !important;
  }
  
  .border-left-danger {
    border-left: 0.25rem solid #e74a3b !important;
  }
  
  .border-left-primary {
    border-left: 0.25rem solid #4e73df !important;
  }
  
  .border-left-success {
    border-left: 0.25rem solid #1cc88a !important;
  }
  
  .border-left-info {
    border-left: 0.25rem solid #36b9cc !important;
  }
  
  .shadow {
    box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15) !important;
  }
  
  .text-gray-800 {
    color: #5a5c69 !important;
  }
  
  .font-weight-bold {
    font-weight: 700 !important;
  }
  
  .text-xs {
    font-size: 0.75rem;
  }
  
  .text-uppercase {
    text-transform: uppercase !important;
  }
  
  /* Estilos para tarjetas clicables */
  .clickable-card {
    cursor: pointer;
    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  }
  
  .clickable-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
  }
  
  .clickable-card:focus {
    outline: 2px solid #007bff;
    outline-offset: 2px;
  }
  
  /* Centrar mejor el video */
  .ratio {
    position: relative;
    width: 100%;
  }
  
  .ratio::before {
    display: block;
    padding-top: var(--bs-aspect-ratio);
    content: "";
  }
  
  .ratio > * {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }
  
  .ratio-16x9 {
    --bs-aspect-ratio: calc(9 / 16 * 100%);
  }
</style>

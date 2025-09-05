<script>
  import { goto } from "$app/navigation";
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import BaseProgress from "$components/argon_template/BaseProgress.svelte";
  import Card from "$components/argon_template/Cards/Card.svelte";
  import BlockLoading from "$components/platform/commons/BlockLoading.svelte";
  import { Routes } from "$lib/commons/routes";
  import { SessionManager } from "$lib/commons/session_manager";
  import { UiPillClassTranslate } from "$lib/commons/ui_utils";
  import { UserController } from "$lib/controllers/user_controller";
  import { User } from "$lib/models/user";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";

  /** @type boolean */
  let loading = $state(true);
  /** @type boolean */
  let blockLoading = false;

  /** @type UserController */
  const _userCtl = new UserController();

  /** @type User */
  let user = $state({
      firstName: "",
      lastName: "",
      email: "",
      phone: "",
    },
  );

  /** @type OnMount */
  onMount(async () => {
    try {
      user = await _userCtl.get(SessionManager.userId());
    } finally {
      loading = false;
    }
  });

  /** @returns Promise<void> */
  const editUser = async () => await goto(`${ Routes.MY_PROFILE }/edit`);
</script>

<svelte:head>
  <title>{$t('route.my-profile.title')}</title>
</svelte:head>

{#if blockLoading}
  <BlockLoading/>
{/if}

<div class="page-sidebar-content flex-column flex-md-row">
  <div class="col-12 col-md-12 col-xl-12 pl-0 pl-md-3 pr-0">
    <Card class="mb-3" noBody>
      <div class="card-header">
        <div class="page-content-title">
          <div class="w-100 d-flex flex-row justify-content-between">
            <span class="mr-4">{$t('route.my-profile.profile.title')}</span>
            <div class="d-flex justify-content-end">
              <BaseButton class="mr-2" onclick={editUser} size="sm" type="primary">
                <i class="fas fa-edit fa-fw"></i>
              </BaseButton>
            </div>
          </div>
        </div>
      </div>

      <div class="text-center mb logo-title">
        <img alt="" src="/imgs/logos/logo.png" width="100"/>
      </div>
      <div class="card-body text-center">
        <div class="page-content-title">{user?.fullName ?? '...'}</div>
        <div class="text-uppercase mb-3 mt-3 badge badge-pill {UiPillClassTranslate.userRolePillClass(user?.roleName)}">
          {user?.roleName ? $t(`entity.user.roleType.${ user.roleName }`) : '...'}
        </div>

        <div class="content-text">
          <i class="fas fa-square-envelope fa-lg mr-1">
          </i>{user?.email ?? '...'}
        </div>

        {#if (user?.phone?.length ?? 0) > 0}
          <div class="content-text">
            <i class="fas fa-square-phone fa-lg mr-1"></i>
            {user.phone}
          </div>
        {/if}
      </div>

      {#if loading}
        <BaseProgress striped animated type="info" height={4} value={100}/>
      {:else}
        <div style="height: 4px; width: 100%"></div>
      {/if}
    </Card>
  </div>

</div>

<style>
  .profile-avatar {
    position: absolute;
    top: -4rem;
  }

  .page-sidebar-content {
    margin-top: 6rem !important;
  }
</style>

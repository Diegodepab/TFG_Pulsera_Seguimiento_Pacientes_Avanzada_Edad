<script>
  import { goto } from "$app/navigation";
  import { navigating, page } from "$app/state";
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import LoadingContentPage from "$components/platform/commons/LoadingContentPage.svelte";
  import InstrumentForm from "$components/platform/instrument/InstrumentForm.svelte";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Global } from "$lib/commons/global";
  import { Routes } from "$lib/commons/routes";
  import { SessionManager } from "$lib/commons/session_manager";
  import { navigatorHistory } from "$lib/commons/stores";
  import { InstrumentController } from "$lib/controllers/instrument_controller";
  import { Exception } from "$lib/exceptions/exception";
  import { PlatformException } from "$lib/exceptions/platform_exception";
  import { Instrument } from "$lib/models/instrument";
  import { PermissionsEntityType, PermissionsGrantType, UserPermission } from "$lib/models/user_permission";

  import { QueryFields, QueryParamsRaw } from "$lib/services/utils/query_utils";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";
  import { getNotificationsContext } from "svelte-notifications";

  if (!Global.notificationContext) Global.notificationContext = getNotificationsContext();

  /** @type boolean */
  let checkingGrants = $state(true);

  /** @type boolean */
  let loading = $state(true);

  /** @type InstrumentController */
  const _instrumentCtl = new InstrumentController();

  /** @type Instrument */
  let instrument = $state();

  /** @type {Map<PermissionsEntityType, UserPermission>} */
  const _entitiesAccess = new Map();

  // Manage changes into URL from route
  let _idParam = page.params.id;


  /**
   * Asynchronously requests the display URL for a given instrument and updates the instrument's display URL.
   * If an error occurs during the request, it notifies the error while omitting UI notifications.
   *
   * @async
   * @returns Promise<void> - A promise that resolves when the operation is complete.
   * @throws {Error} Throws an error if the request to get the signed URL fails.
   */
  const requestDisplayUrl = async () => {
    try {
      instrument.blobDisplayUrl = (await _instrumentCtl.getSignedUrl(instrument.id)).displayUrl;
    } catch (e) {
      // Notify but omit the rest of notifications. Model will not be displayed.
      await PlatformException.notifyError(e, { ignoreUiNotifications: true });
    }
  };

  /** @type OnMount */
  onMount(async () => {
    const permissions = await SessionManager.userPermissionsOn([ PermissionsEntityType.INSTRUMENT ]);
    permissions?.forEach(permission => {
      _entitiesAccess.set(permission.entityName, permission);
    });

    const access = _entitiesAccess.get(PermissionsEntityType.INSTRUMENT);
    if (!access.uiVisibility || access.read === PermissionsGrantType.NONE) {
      CommonNotifications.noAccessPermissions();
      return await goBack();
    }

    checkingGrants = false;
    await loadInstrumentData();
  });

  /** @returns Promise<void>
   * @throws {Exception} Throws an error if instrument data not loaded.
   */
  const loadInstrumentData = async () => {
    loading = true;
    try {
      const params = new Map();
      params.set(QueryFields.RAW, [
        new QueryParamsRaw({ field: Instrument.apiRaw.addBlobDisplayUrl, value: "true" }),
      ]);
      instrument = await _instrumentCtl.get(page.params.id, { params });
    } catch (e) {
      if (!(e instanceof Exception) || e.code !== 404) throw e;
      await goBack();
      throw e;
    } finally {
      loading = false;
    }
  };

  /** @returns Promise<void> */
  const editInstrument = async () => await goto(`${ Routes.INSTRUMENTS }/${ instrument.id }/edit`);

  /** @returns Promise<void> */
  const goBack = async () => await navigatorHistory.goBack(Routes.INSTRUMENTS);


  $effect(() => {
    if (navigating && page.params.id && navigating.to?.params?.id === page.params.id && page.params.id !== _idParam) {
      _idParam = page.params.id;
      loadInstrumentData();
    }
  });

  // if an item receives enough information and not have display url, it has a method to request it if necessary
  $effect(() => {
    if (!instrument?.id || !!instrument?.blobDisplayUrl) return;

    requestDisplayUrl();
  });
</script>

<svelte:head>
  <title>{$t('route.instrument-details.title')}</title>
</svelte:head>

{#if !checkingGrants}
  <div class="page-content">
    <div class="page-content-title mt-0 d-flex justify-content-between align-items-center">
      <span>{$t('route.instrument-details.form-title')}</span>

      <div class="pr-0 d-flex justify-content-end">
        <BaseButton size="sm" onclick={goBack} type="primary" disabled={loading}>
          <i class="fas fa-arrow-left fa-fw"></i>
        </BaseButton>

        {#if _entitiesAccess.get(PermissionsEntityType.INSTRUMENT).write !== PermissionsGrantType.NONE}
          <div class="card-header-action-separator"></div>
          <BaseButton size="sm" type="primary" disabled={loading} onclick={editInstrument}>
            <i class="fas fa-edit fa-fw"></i>
          </BaseButton>
        {/if}
      </div>
    </div>
    <LoadingContentPage {loading} class="mb-3"/>

    <div class="row mx-0">
      <div class="col-12 col-md-6 pl-3 border-sm-0">
        <InstrumentForm {instrument} readonly/>
      </div>
    </div>
  </div>
{/if}
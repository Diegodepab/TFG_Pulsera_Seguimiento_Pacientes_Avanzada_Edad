<script>
  import { navigating, page } from "$app/state";
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import LoadingContentPage from "$components/platform/commons/LoadingContentPage.svelte";
  import InstrumentForm from "$components/platform/instrument/InstrumentForm.svelte";
  import { CommonAlerts } from "$components/platform/utils/common_alerts";
  import { CommonNotifications } from "$components/platform/utils/common_notifications";
  import { Global } from "$lib/commons/global";
  import { Routes } from "$lib/commons/routes";
  import { SessionManager } from "$lib/commons/session_manager";
  import { navigatorHistory } from "$lib/commons/stores";
  import { i18nGender } from "$lib/commons/ui_utils";
  import { BlobStorageController } from "$lib/controllers/blob_storage/blob_storage_controller";
  import { InstrumentController } from "$lib/controllers/instrument_controller";
  import { Exception } from "$lib/exceptions/exception";
  import { ExceptionBlobStorage } from "$lib/exceptions/exception_codes";
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
  let instrument = $state(Instrument.empty());

  /** @type InstrumentForm */
  let _instrumentForm = $state();

  /** @type UserPermission */
  let entityAccess = $state();

  // manage changes into url from route
  /** @type * */
  let _idParam = $state(page.params.id);

  /** @type OnMount */
  onMount(async () => {
    entityAccess = (await SessionManager.userPermissionsOn([ PermissionsEntityType.PATIENT ])).at(0);

    if (!entityAccess.uiVisibility || entityAccess.write === PermissionsGrantType.NONE) {
      CommonNotifications.noAccessPermissions();
      return await goBack();
    }

    checkingGrants = false;
    await loadInstrumentData();
  });

  /** @returns Promise<void>
   * @throws {Exception} Throws an error if instrument data not loaded.
   * */
  const loadInstrumentData = async () => {
    loading = true;

    try {
      /** @type {Map<QueryFields, ?>} */
      const params = new Map();
      params.set(QueryFields.RAW, [
        new QueryParamsRaw({ field: Instrument.apiRaw.addBlobDisplayUrl, value: "true" }),
      ]);
      instrument = await _instrumentCtl.get(_idParam, { params });
    } catch (e) {
      if (!(e instanceof Exception) || e.code !== 404) throw e;
      await goBack();

      throw e;
    }

    loading = false;
  };

  /** @returns Promise<void>
   * @throws {PlatformException} Throws an error if the request to upload fails.
   * */
  const saveInstrument = async () => {
    loading = true;

    if (!_instrumentForm.validateForm()) {
      CommonNotifications.validationError();
      loading = false;
      return;
    }

    /** @type BlobStorageExceptionCtx */
    const fileCtx = {
      path: `${ SessionManager.userId() }/instrument/${ instrument.id }`,
      filename: instrument.filename,
      newFilenames: _instrumentForm.getDropzoneUploadFile().getLocalFiles().map((f) => f.name),
    };

    try {
      await _instrumentForm.getDropzoneUploadFile().uploadOperation();
    } catch (e) {
      if (!(e instanceof Exception)) {
        loading = false;
        throw PlatformException.uploadFileToBlobStorage({ fromError: e, extraArgs: { fileCtx } });
      }

      e.extraArgs = { ...(e.extraArgs ?? {}), fileCtx };
      if (e.code !== ExceptionBlobStorage.errorOnFileDeletion) {
        loading = false;
        throw e;
      }

      // new video uploaded, but old not removed, so we notify without break the flow
      await PlatformException.notifyError(e, { ignoreUiNotifications: true });
    }

    try {
      await _instrumentCtl.patch(instrument.id, instrument);
      CommonNotifications.genericSuccess($t("notification.entity.instrument.success.edit"));
      await goBack();
    } catch (e) {
      throw PlatformException.uploadFileToBlobStorage({
        fromError: e,
        extraArgs: { ...(e.extraArgs ?? {}), fileCtx },
      });
    } finally {
      loading = false;
    }

  };

  /** @returns Promise<void>
   * @throws {PlatformException} Throws an error if instrument delete request fails.
   * */
  const deleteInstrument = async () => {
    if (!(await CommonAlerts.deleteOrDisableConfirmation($t("entity.instrument.entity-name"), {
      gender: i18nGender.MALE,
    }))) return;

    loading = true;
    /** @type BlobStorageExceptionCtx */
    const fileCtx = {
      path: `${ SessionManager.userId() }/instrument/${ instrument.id }`,
      filename: instrument.filename,
    };

    const deleteUrl = (await _instrumentCtl.getDeleteSignedUrl(instrument.id)).deleteUrl;

    try {
      await _instrumentCtl.delete(instrument.id);
    } catch (e) {
      loading = false;
      CommonNotifications.genericDanger($t("notification.entity.instrument.error.delete"));
      throw PlatformException.deleteFileToBlobStorage({
        fromError: e,
        extraArgs: { ...(e.extraArgs ?? {}), fileCtx },
      });
    }

    try {
      await (new BlobStorageController()).delete(deleteUrl);
    } catch (e) {
      e.extraArgs = { ...(e.extraArgs ?? {}), fileCtx };
      await PlatformException.notifyError(e, { ignoreUiNotifications: true });
    } finally {
      CommonNotifications.genericSuccess($t("notification.entity.instrument.success.delete"));
      await removePatternAndGoBack();
      loading = false;
    }
  };

  /** @returns Promise<void> */
  const removePatternAndGoBack = async () => {
    loading = true;
    await navigatorHistory.removePatternAndGoBack(
      Routes.INSTRUMENTS,
      new RegExp(`${Routes.INSTRUMENTS}/${instrument.id}/?`),
    );
  };

  /** @returns Promise<void> */
  const goBack = async () => navigatorHistory.goBack(`${ Routes.INSTRUMENTS }`);

  $effect(() => {
    if (navigating && page.params.id
      && navigating.to?.params?.id === page.params.id
      && page.params.id !== _idParam) {
      _idParam = page.params.id;
      loadInstrumentData().then();
    }
  });
</script>

<svelte:head>
  <title>{$t('route.instrument-edit.title')}</title>
</svelte:head>

{#if !checkingGrants}
  <div class="page-content">
    <div class="page-content-title mt-0 d-flex justify-content-between">{$t('route.instrument-edit.form-title')}</div>
    <LoadingContentPage {loading} class="mb-3"/>

    <form onsubmit={saveInstrument}>
      <div class="row mx-0">
        <div class="col-12 col-lg-10 col-xl-6">
          <InstrumentForm
              bind:this={_instrumentForm}
              {instrument}
              readonly={loading}/>
        </div>
      </div>

      <div class="row mt-5">
        <div class="d-flex col-12">
          <div class="d-flex flex-column flex-sm-row justify-content-end col-12 px-2">
            <BaseButton
                className="mb-2 mr-0 mr-sm-2 mb-sm-0"
                type="secondary"
                disabled={loading}
                onclick={goBack}>
              <span class="btn-inner--text">{$t('common.button.cancel')}</span>
            </BaseButton>

            {#if entityAccess.del !== PermissionsGrantType.NONE && instrument}
              <BaseButton
                  className="mb-2 mr-0 mr-sm-2 mb-sm-0"
                  type="danger"
                  disabled={loading}
                  onclick={deleteInstrument}>
                <span class="btn-inner--text">{$t('common.button.delete')}</span>
              </BaseButton>
            {/if}

            {#if entityAccess.write !== PermissionsGrantType.NONE}
              <BaseButton nativeType="submit" type="success" disabled={loading}>
                <span class="btn-inner--text">{$t('common.button.save')}</span>
              </BaseButton>
            {/if}
          </div>
        </div>
      </div>
    </form>
  </div>
{/if}

<script>
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
  import { ExceptionBlobStorage } from "$lib/exceptions/exception_codes";
  import { PlatformException } from "$lib/exceptions/platform_exception";
  import { Instrument } from "$lib/models/instrument";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";
  import { getNotificationsContext } from "svelte-notifications";


  if (!Global.notificationContext) Global.notificationContext = getNotificationsContext();

  /** @type boolean */
  let loading = $state(true);

  /** @type InstrumentController */
  const _instrumentCtl = new InstrumentController();

  /** @type Instrument */
  let instrument = $state(Instrument.empty());

  /** @type InstrumentForm */
  let _instrumentForm = $state();

  onMount(async () => {
    loading = false;
  });

  /**
   * @returns Promise<void>
   * @throws {PlatformException} If instrument can´t be saved
   */
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

      // new model uploaded, but old not removed, so we notify without break the flow
      await PlatformException.notifyError(e, { ignoreUiNotifications: true });
    }

    try {
      instrument = await _instrumentCtl.post(instrument);
      CommonNotifications.genericSuccess($t("notification.entity.instrument.success.add"));
      await goBack();
    } catch (error) {
      CommonNotifications.genericDanger($t("notification.entity.instrument.error.add"));
    } finally {
      loading = false;
    }
  };

  /** @returns Promise<void> */
  const goBack = async () => navigatorHistory.goBack(Routes.INSTRUMENTS);
</script>

<svelte:head>
  <title>{$t('route.instrument-add.title')}</title>
</svelte:head>

{#if !loading}
  <div class="page-content">
    <div class="page-content-title mt-0 d-flex justify-content-between align-items-center">
      <span>{$t('route.instrument-add.form-title')}</span>
    </div>
    <LoadingContentPage {loading} class="mb-3"/>

    <form onsubmit={saveInstrument}>
      <div class="col-12 col-lg-10 col-xl-6">
        <InstrumentForm
            bind:this={_instrumentForm}
            {instrument}
            readonly={loading}/>
      </div>

      <div class="row mt-5">
        <div class="d-flex col-12">
          <div class="d-flex justify-content-end col-12">
            <BaseButton type="secondary" disabled={loading} onclick={goBack}>
              <span class="btn-inner--text">{$t('common.button.cancel')}</span>
            </BaseButton>

            <BaseButton nativeType="submit" type="success" disabled={loading}>
              <span class="btn-inner--text">{$t('common.button.save')}</span>
            </BaseButton>
          </div>
        </div>
      </div>
    </form>
  </div>
{/if}

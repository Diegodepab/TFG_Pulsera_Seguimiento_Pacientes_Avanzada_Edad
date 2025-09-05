<script>
  import Card from "$components/argon_template/Cards/Card.svelte";
  import Modal from "$components/argon_template/Modal.svelte";

  /**
   * @typedef {Object} BaseCardModalProps
   * @property {string} [headerClasses] - Additional CSS classes to apply to the modal header
   * @property {boolean} [allowOutsideClick] - Whether clicking outside the modal should close it
   * @property {boolean} [setHtmlOverflowHidden] - Whether to set overflow:hidden on the HTML element when modal is open
   * @property {boolean} [show] - Controls the visibility of the modal
   * @property {boolean} [noBody] - If true, doesn't render the default modal body wrapper
   * @property {(_) => void} [onScrollBody] - Callback function triggered when the modal body is scrolled
   * @property {string} [modalMaxWidth] - Controls the maxWidth property for modal body, building a dynamic CSS class.
   * Requires to indicate the unit.
   * @property {*} [modalBodyMaxHeight] - Controls the maxHeight property for modal, building a dynamic CSS class.
   * Requires to indicate the unit
   * @property {"auto" | "600" | "700" | "800" | "900" | "1200"} [bodyResponsiveHeight] - Controls the maxHeight condition
   * for MediaQuery property for modal body, building a dynamic CSS class. Requires an existing CSS class
   * @property {"sm" | "lg" | "xl" | "xxl"} [size] - Controls the size of the modal - usually, when bodyResponsiveHeight >= 900, size must be 'xl'
   * @property {"center" | "end"} [footerPosition] - Controls the alignment of elements in the modal footer
   * @property {() => void} [onCloseModal] - Callback function triggered when the modal is closed
   * @property {Snippet} [headerSnippet] - Snippet to render custom content in the modal header
   * @property {Snippet} [children] - Main content to render in the modal
   * @property {Snippet} [body] - Alternative snippet for modal body content
   * @property {Snippet} [footerSnippet] - Snippet to render custom content in the modal footer
   */

  /** @type BaseCardModalProps */
  let {
    /** @type string */ headerClasses = "",
    /** @type boolean */ allowOutsideClick = true,
    /** @type boolean */ setHtmlOverflowHidden = false,
    /** @type boolean */ show = $bindable(false),
    /** @type boolean */ noBody = false,
    /** @type {(_) => void} */ onScrollBody = null,
    /** @type string */ modalMaxWidth = "600px",
    /** @type {string | null} */ modalBodyMaxHeight = null,
    /** @type {"auto" | "600" | "700" | "800" | "900" | "1200"} */ bodyResponsiveHeight = "600",
    /** @type string */ size = "lg",
    /** @type string */ footerPosition = "end",
    /** @type {() => void} */ onCloseModal = null,
    /** @type Snippet */ headerSnippet,
    /** @type Snippet */ children,
    /** @type Snippet */ body,
    /** @type Snippet */ footerSnippet,
  } = $props();

  /** @type Modal */
  let _modal = $state();

  const headerRender = $derived(headerSnippet);

  export const openModal = () => _modal.openModal();

  /**
   * @param {Object} [opts]
   * @param {boolean} opts.ignoreDispatch
   * @return {void}
   */
  export const closeModal = (opts) => {
    _modal.closeModal({ ignoreDispatch: opts?.ignoreDispatch });
  };

</script>

<Modal
    {allowOutsideClick}
    bind:show
    bind:this={_modal}
    bodyClasses="p-0"
    maxWidth={modalMaxWidth}
    {onCloseModal}
    {setHtmlOverflowHidden}
    {size}
>
  <Card
      bodyClasses="px-lg-5 py-lg-3"
      classNames="bg-secondary border-0 mb-0 card h-100"
      headerClasses="bg-transparent {headerClasses} {noBody ? 'd-none' : ''}"
      noBody
  >
    {#snippet headerSnippet()}
      <div class="w-100">
        {@render headerRender?.()}
      </div>
    {/snippet}

    {#if noBody}
      {@render children?.()}
    {:else }
      <div
          class="card-body body-responsive-{bodyResponsiveHeight}"
          class:modal-max-height={!!modalBodyMaxHeight}
          onscroll={onScrollBody}
          style="--modalBodyMaxHeight: {modalBodyMaxHeight}"
      >
        {@render body?.()}
      </div>
    {/if}

    {#if footerSnippet}
      <div class="modal-footer-responsive actions justify-content-{footerPosition}">
        {@render footerSnippet?.()}
      </div>
    {/if}
  </Card>
</Modal>

<style>
  .modal-footer-responsive {
    padding: 1.25rem 1.5rem;
    border-top: 1px solid rgba(0, 0, 0, .05);
    gap: 0.5rem;
  }

  .modal-footer-responsive.actions {
    display: flex;
    flex-wrap: wrap;
  }

  .modal-max-height {
    max-height: var(--modalBodyMaxHeight) !important;
  }

  @media (max-height: 768px) {
    .modal-max-height {
      max-height: 100% !important;
    }
  }

  /*
    MediaQuery condition cannot be build dynamically, so it's necessary define a class for everyone
  */

  .body-responsive-auto {
    overflow: auto;
  }

  @media (max-height: 600px) {
    .body-responsive-600 {
      overflow: auto;
    }
  }

  @media (max-height: 700px) {
    .body-responsive-700 {
      overflow: auto;
    }
  }

  @media (max-height: 800px) {
    .body-responsive-800 {
      overflow: auto;
    }
  }

  @media (max-height: 900px) {
    .body-responsive-900 {
      overflow: auto;
    }
  }

  @media (max-height: 1200px) {
    .body-responsive-1200 {
      overflow: auto;
    }
  }
</style>
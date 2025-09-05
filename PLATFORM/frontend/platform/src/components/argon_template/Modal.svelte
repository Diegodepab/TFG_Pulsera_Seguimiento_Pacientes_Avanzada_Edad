<script>
  import { GeneralActions } from "$components/directives/general_actions";
  import { fly } from "svelte/transition";

  /**
   * @typedef {Object} ModalProps
   * @property {string} [classNames = ""] - Additional CSS classes to apply to the modal's outermost container
   * @property {string} [modalClasses = ""] - Additional CSS classes to apply to the modal dialog element
   * @property {string} [modalContentClasses = ""] - Additional CSS classes to apply to the modal content wrapper
   * @property {string} [headerClasses = ""] - Additional CSS classes to apply to the modal header
   * @property {string} [bodyClasses = ""] - Additional CSS classes to apply to the modal body
   * @property {string} [footerClasses = ""] - Additional CSS classes to apply to the modal footer
   * @property {number} [animationDuration = 500] - Duration of the opening/closing animation in milliseconds
   * @property {boolean} [show = false] - Controls whether the modal is visible
   * @property {"notice" | "mini" | "" | null} [type = null] - Predefined modal style variant
   * @property {string} [gradient = ""] - Background gradient style to apply to the modal
   * @property {"sm" | "md" | "lg" | "xl" | null} [size = null] - Predefined modal size
   * @property {string} [maxWidth = "600px"] - Custom maximum width for the modal
   * @property {boolean} [showCloseIcon = false] - Whether to display the close icon in the header
   * @property {boolean} [setHtmlOverflowHidden = false] - Whether to prevent scrolling of the page when modal is open
   * @property {boolean} [allowOutsideClick = true] - Whether clicking outside the modal closes it
   * @property {import("svelte").Snippet} [children] - Content to display in the modal body
   * @property {import("svelte").Snippet} [headerSnippet] - Custom content for the modal header
   * @property {import("svelte").Snippet} [closeButtonSnippet] - Custom close button to use instead of the default
   * @property {import("svelte").Snippet} [footerSnippet] - Custom content for the modal footer
   * @property {(event: Event) => void} [onCloseModal = () => null] - Callback function triggered when modal is closed
   */

  /** @type ModalProps */
  let {
    /** @type string */ classNames = "",
    /** @type string */ modalClasses = "",
    /** @type string */ modalContentClasses = "",
    /** @type string */ headerClasses = "",
    /** @type string */ bodyClasses = "",
    /** @type string */ footerClasses = "",
    /** @type number */ animationDuration = 500,
    /** @type boolean */ show = $bindable(false),
    /** @type {"notice" | "mini"  | null} */ type = null,
    /** @type string */ gradient = "",
    /** @type {"sm" | "md" | "lg" | "xl" | null} */ size = null,
    /** @type string */ maxWidth = "600px",
    /** @type boolean */ showCloseIcon = false,
    /** @type boolean */ setHtmlOverflowHidden = false,
    /** @type boolean */ allowOutsideClick = true,
    /** @type Snippet */ children,
    /** @type Snippet */ headerSnippet,
    /** @type Snippet */ closeButtonSnippet,
    /** @type Snippet */ footerSnippet,
    /** @type {(event: Event) => void} */ onCloseModal = (_) => null,
  } = $props();


  $effect(() => {
    if (setHtmlOverflowHidden) {
      const htmlStyle = document.querySelector("html")?.style;
      show ? htmlStyle?.setProperty("overflow", "hidden") : htmlStyle?.removeProperty("overflow");
    }
  });

  // required to add or remove classes when modal is controlled by bind:show
  $effect(() => {
    if (show) {
      document.body.classList.add("modal-show");
    } else {
      document.body.classList.remove("modal-show");
    }
  });

  /** @return void */
  export const openModal = () => {
    show = true;
    document.body.classList.add("modal-show");
  };

  /**
   * @param {Event} event
   * @return void
   */
  export const closeModal = (event) => {
    if (typeof onCloseModal === "function") {
      onCloseModal(event);
    }
    show = false;
    document.body.classList.remove("modal-show");

    // if (!opts?.ignoreDispatch) dispatch('dispatch:modal-close');
  };

</script>

{#if show}
  <div>
    <div
        use:GeneralActions.outModalClick={{ ignore: !allowOutsideClick }}
        onoutclick={closeModal}
        onkeydown-esc={closeModal}
        in:fly={{ y: -100, duration: animationDuration }}
        out:fly={{ y: -100, duration: animationDuration }}
        class="modal show {classNames}"
        ref="app-modal"
        {size}
        hide-header={!headerSnippet}
        modal-class="{type === 'mini' ? 'modal-mini' : ''} {modalClasses} modal-custom-width"
        tabindex="-1"
        role="dialog"
        centered
        onclose={closeModal}
        onhide={closeModal}
        header-class={headerClasses}
        footer-class={footerClasses}
        content-class="{gradient ? `bg-gradient-${gradient}` : ''} {modalContentClasses}"
        body-class={bodyClasses}
        aria-hidden={!show}
        style="display: block; --maxWidth: {maxWidth}">
      <div
          class="modal-dialog modal-dialog-centered {size ? `modal-${size}` : ''} {modalClasses}"
          class:modal-max-width={maxWidth}
      >
        <div class="modal-content {gradient ? `bg-gradient-${gradient}` : ''} {modalContentClasses}">
          {#if headerSnippet}
            <header class="modal-header {headerClasses}">
              {@render headerSnippet()}

              {#if closeButtonSnippet}
                {@render closeButtonSnippet()}
              {:else}
                {#if showCloseIcon}
                  <button
                      type="button"
                      class="close"
                      onclick={closeModal}
                      data-dismiss="modal"
                      aria-label="Close">
                    <span aria-hidden={!show} class:text-white={gradient}>×</span>
                  </button>
                {/if}
              {/if}
            </header>
          {/if}

          <div class="modal-body {bodyClasses}">
            {@render children?.()}
          </div>

          {#if footerSnippet}
            <footer class="modal-footer {footerClasses}">
              {@render footerSnippet()}
            </footer>
          {/if}

        </div>
      </div>
    </div>
  </div>
  <div class="modal-backdrop"></div>
{/if}

<style>
  .modal-max-width {
    max-width: var(--maxWidth);
  }

  .modal-backdrop {
    background-color: rgba(0, 0, 0, 0.6) !important;
  }
</style>

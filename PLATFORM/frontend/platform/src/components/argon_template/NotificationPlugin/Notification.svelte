<script>
  import { fade } from "svelte/transition";

  /**
   * @typedef {Object} NotificationProps
   * @property {string} [type="default"] - Alert type/style (info, success, warning, danger, etc.)
   * @property {boolean} [dismissible=true] - Whether the notification can be dismissed
   * @property {string} [icon=""] - Icon class to display in the notification
   * @property {string} [notifyClassNames=""] - Additional CSS classes for the notification
   * @property {boolean} [visible=true] - Whether the notification is visible
   * @property {boolean} [dataNotify=false] - Whether to use data-notify attributes
   * @property {() => void} [onremove] - Function to execute when the notification is removed
   * @property {Snippet} children
   * @property {Snippet} iconSnippet - Snippet to replace left position icon (main notification icon)
   * @property {Snippet} dismissIconSnippet - Snippet to replace the dismiss icon. Receives the dismissAlert method to dismiss.
   */

  /** @type NotificationProps */
  let {
    /** @type string */ type = "default",
    /** @type boolean */ dismissible = true,
    /** @type string */ icon = "",
    /** @type string */ notifyClassNames = "",
    /** @type boolean */ visible = true,
    /** @type boolean */ dataNotify = false,
    /** @type {(event: Event) => void} */ onclick,
    /** @type {() => void} */ onremove,
    /** @type Snippet */ children,
    /** @type Snippet */ iconSnippet,
    /** @type Snippet */ dismissIconSnippet,
  } = $props();

  /**
   * @param {Event} event
   * @return void
   */
  const dismissAlert = (event) => {
    event.preventDefault();
    event.stopPropagation();

    visible = false;
    onremove?.();
  };
</script>

<div transition:fade>
  <div
      class="alert alert-{type} {notifyClassNames}"
      class:alert-notify={dataNotify}
      class:alert-dismissible={dismissible}
      data-notify={dataNotify ? 'container' : ''}
      model={visible}
      role="alert"
      variant={type}
      onclick={onclick}
  >
    {#if !dismissible}
      {@render children?.()}
    {:else}
      {#if iconSnippet}
        {@render iconSnippet()}
      {:else if icon}
    <span class="alert-icon" data-notify="icon">
     <i class={icon}></i>
    </span>
      {/if}

      {#if children}
        <span class="alert-text">{@render children()}</span>
      {/if}

      {#if dismissIconSnippet}
        {@render dismissIconSnippet(dismissAlert)}
      {:else}
        <button type="button" class="close" data-dismiss="alert" aria-label="Close" onclick={dismissAlert}>
          <span aria-hidden="true" onclick={dismissAlert}>×</span>
        </button>
      {/if}
    {/if}
  </div>
</div>
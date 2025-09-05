<script>
  import { v1 as uuidv1 } from "uuid";
  /**
   * @typedef {Object} BaseProgressProps
   * @property {string} [id = uuidv1()] - Unique identifier for the progress bar
   * @property {boolean} [striped = false] - Whether the progress bar is striped
   * @property {boolean} [animated = false] - Whether the progress bar is animated
   * @property {string} [label = ""] - Progress bar label
   * @property {number} [height = 3] - Bar height
   * @property {"default" | "danger" | "primary"} [type = "default"] - The visual style of the progress bar
   * @property {boolean} [showLabel = false] - Whether the label should be shown when set
   * @property {string} [wrapperClasses = ""] - Additional CSS classes for the wrapper
   * @property {string} [progressClasses = ""] - Additional CSS classes for the progress element
   * @property {string} [progressLabelPercentageClasses = ""] - Additional CSS classes for the percentage label
   * @property {string} [size = ""] - Size variant of the progress bar
   * @property {number} [value = 0] - Percentage value
   * @property {import("svelte").Snippet} [children] - Custom content for the percentage display
   * @property {import("svelte").Snippet} [labelSnippet] - Label snippet
   */

  /** @type BaseProgressProps */
  let {
    /** @type string */ id = uuidv1(),
    /** @type boolean */ striped = false,
    /** @type boolean */ animated = false,
    /** @type string */ label = "",
    /** @type number */ height = 3,
    /** @type {"default" | "danger" | "primary"} */ type = "default",
    /** @type boolean */ showLabel = false,
    /** @type string */ wrapperClasses = "",
    /** @type string */ progressClasses = "",
    /** @type string */ progressLabelPercentageClasses = "",
    /** @type string */ size = "",
    /** @type number */ value = 0,
    /** @type Snippet */ children,
    /** @type Snippet */ labelSnippet,
  } = $props();

  /**
   * @param {number} value
   * @return number
   */
  const validator = (value) => {
    return (value >= 0 && value <= 100) ? value : 0;
  };

  value = validator(value);
</script>

<div {id} style="width: 100%">
  <div class="wrapper {wrapperClasses}">
    {#if showLabel}
      <div class="progress-{type}">
        {#if label}
          <div class="progress-label">
            {#if labelSnippet}
              {@render labelSnippet()}
            {:else}
              <span>{label}</span>
            {/if}
          </div>
        {/if}

        <div class="progress-percentage {progressLabelPercentageClasses}">
          {#if children}
            {@render children()}
          {:else}
            <span>{value}%</span>
          {/if}
        </div>
      </div>
    {/if}

    <div class="progress {progressClasses}" {size} style="height: {height}px">
      <div
          aria-valuemax="100"
          aria-valuemin="0"
          aria-valuenow={value}
          class="progressbar {type ? `bg-${type}` : ''}"
          class:progress-bar-striped={striped}
          class:progress-bar-animated={animated}
          style="width: {value}%;"
          {value}>
      </div>
    </div>
  </div>
</div>

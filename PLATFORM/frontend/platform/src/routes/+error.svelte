<script>
  import { dev } from "$app/environment";
  import { page } from "$app/state";
  import InternalError from "$components/platform/errors/InternalError.svelte";
  import NotFound from "$components/platform/errors/NotFound.svelte";
  import { onMount } from "svelte";

  let { form, data } = $props();

  /** @type {App.Error | null} */
  const error = page.error;
  /** @type number */
  const status = page.status;
  /** @type {NotFound | InternalError} */
  const renderScreen = status == 404 ? NotFound : InternalError;

  /** @type OnMount */
  onMount(() => {
    if (dev) console.error(status, error);
  });

  const SvelteComponent = $derived(renderScreen);
</script>

<SvelteComponent {error} {status}/>

{#if dev && error?.stack}
  <div class="d-flex justify-content-center">
    <div class="p-3 m-3 w-100 w-lg-75 stacktrace">
      <span class="text-left">Stack: {error.stack}</span>
    </div>
  </div>
{/if}

<style>
  .stacktrace {
    border-radius: 0.5rem;
    background-color: var(--secondary-regular-color-light);
  }
</style>

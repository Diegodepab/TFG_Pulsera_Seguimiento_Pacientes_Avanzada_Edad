<script>
  import moment from "moment";
  import { isLoading as loadingT, t } from "svelte-i18n";


  /** @type string */
  let lang = $state("en");

  /** @type string */
  let aboutUsTitle = $state("...");

  /** @type string */
  let docsTitle = $state("...");

  /** @type string */
  let tacTitle = $state("...");


  /** @type string */
  let aboutUsHref = $state("");

  /** @type string */
  let docsHref = $state("");

  /** @type string */
  let tacHref = $state("");

  $effect(() => {
    if (!$loadingT) {
      lang = $t("common.extra.lang");

      aboutUsTitle = $t("route.personal.title");
      aboutUsHref = `https://diegodepab.github.io/`;

      docsTitle = $t("route.docs.title");
      docsHref = `/docs/${ lang }`;

      tacTitle = $t("route.tac.title");
      tacHref = `https://www.uma.es/etsi-informatica/info/71616/trabajo-de-fin-de-grado/`;
    }
  });

</script>
<footer>
  <div class="row justify-content-around">
    <div class="row small px-2 mb-2 mx-2 justify-content-start text-white order-2 order-md-1">
      <span class="text-center mx-1">
        Diego De Pablo, Universidad de Málaga, Trabajo de fin de grado 
      </span>
    </div>
    <div class="row small px-2 mb-2 mx-2 justify-content-end order-1 order-md-2 gap">
      <a class="text-white text-underline mr-4" href={aboutUsHref}>{aboutUsTitle}</a>
      <a class="text-white text-underline mr-4" href={docsHref}>{docsTitle}</a>
      <a class="text-white text-underline" href={tacHref}>{tacTitle}</a>
    </div>
  </div>
</footer>

<style>
  footer {
    z-index: 5;
    width: 100%;
    position: fixed;
    bottom: 0;
    padding: 0.5rem 0.25rem 0.25rem 0.25rem;
    background: var(--primary-regular-color-dark);
  }

  .gap {
    gap: .5rem;
  }
</style>

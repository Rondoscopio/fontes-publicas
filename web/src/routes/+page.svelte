<script lang="ts">
  import { onMount, type Component } from 'svelte';
  import { resolve } from '$app/paths';
  import { query } from '$lib/client';
  import type { Dashboard } from '$lib/catalog';
  import { sources } from '$lib/links';
  import { displayText } from '$lib/labels';
  import LoadState from '$lib/LoadState.svelte';

  let report = $state<Dashboard>();
  let failed = $state(false);
  let attempt = $state(0);
  let dashboardReady = $state(false);
  let dashboardSection = $state<HTMLElement>();
  let mapSection = $state<HTMLElement>();
  let MapView = $state<Component>();
  let mapLoadFailed = $state(false);
  let mapLoading = false;
  const number = new Intl.NumberFormat('pt-BR');

  async function loadMap() {
    if (MapView || mapLoading) return;
    mapLoading = true;
    mapLoadFailed = false;
    try {
      MapView = (await import('$lib/BrazilMap.svelte')).default;
    } catch {
      mapLoadFailed = true;
    } finally {
      mapLoading = false;
    }
  }

  onMount(() => {
    if (typeof IntersectionObserver === 'undefined') {
      dashboardReady = true;
      void loadMap();
      return;
    }

    const dashboardObserver = new IntersectionObserver(
      ([entry]) => {
        if (entry?.isIntersecting) {
          dashboardReady = true;
          dashboardObserver.disconnect();
        }
      },
      { rootMargin: '0px' },
    );
    if (dashboardSection) dashboardObserver.observe(dashboardSection);

    return () => {
      dashboardObserver.disconnect();
    };
  });

  $effect(() => {
    const section = mapSection;
    if (!section || MapView) return;
    if (typeof IntersectionObserver === 'undefined') {
      void loadMap();
      return;
    }
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry?.isIntersecting) {
          observer.disconnect();
          void loadMap();
        }
      },
      { rootMargin: '160px 0px' },
    );
    observer.observe(section);
    return () => observer.disconnect();
  });

  $effect(() => {
    void attempt;
    if (!dashboardReady) return;
    failed = false;
    let current = true;
    query('dashboard')
      .then((result) => {
        if (current) report = result;
      })
      .catch(() => {
        if (current) failed = true;
      });
    return () => {
      current = false;
    };
  });
  const charts = $derived(
    report
      ? [
          {
            name: 'Categorias',
            filter: 'categoria',
            color: 'violet',
            rows: report.porCategoria,
          },
          {
            name: 'Tipos de fonte',
            filter: 'tipo',
            color: 'teal',
            rows: report.porTipo,
          },
          {
            name: 'Cobertura por UF',
            filter: 'uf',
            color: 'indigo',
            rows: report.porUf,
          },
        ]
      : [],
  );
</script>

<svelte:head>
  <title>OSINT Rondônia · Catálogo de fontes abertas</title>
  <meta
    name="description"
    content="Explore as fontes públicas, ferramentas e referências do catálogo OSINT Rondônia."
  />
</svelte:head>

<section class="hero">
  <div class="hero-content">
    <p class="eyebrow">Rondoscópio · OSINT Rondônia</p>
    <h1>Fontes abertas<br />para explorar Rondônia.</h1>
    <p>
      Encontre fontes públicas, ferramentas e referências. Navegue por tema,
      cobertura territorial e relações entre fichas.
    </p>
    <a class="button primary" href={sources()}
      >Explorar fontes <span aria-hidden="true">→</span></a
    >
  </div>
  <div class="signal" aria-hidden="true">
    <i></i><i></i><i></i><i></i><b></b><b></b><b></b>
  </div>
</section>

<div class="home-dashboard" bind:this={dashboardSection}>
  {#if report}
    <section class="metrics" aria-label="Totais do catálogo">
      <a href={sources()}
        ><strong>{number.format(report.fontes)}</strong><span
          >Fontes cadastradas</span
        ><i aria-hidden="true">↗</i></a
      >
      <a href={resolve('/categorias/')}
        ><strong>{number.format(report.categorias)}</strong><span
          >Categorias</span
        ><i aria-hidden="true">↗</i></a
      >
      <a href={resolve('/listas/')}
        ><strong>{number.format(report.listas)}</strong><span
          >Listas temáticas</span
        ><i aria-hidden="true">↗</i></a
      >
    </section>
    <section
      class="section map-lazy-section"
      bind:this={mapSection}
      aria-labelledby="map-lazy-heading"
    >
      {#if MapView}
        <MapView />
      {:else if mapLoadFailed}
        <div class="map-card card map-placeholder" role="alert">
          <h2 id="map-lazy-heading">Fontes por município</h2>
          <p>Não foi possível carregar o mapa interativo.</p>
          <button class="button" type="button" onclick={loadMap}
            >Tentar novamente</button
          >
        </div>
      {:else}
        <div
          class="map-card card map-placeholder"
          role="status"
          aria-live="polite"
          aria-busy="true"
        >
          <p class="eyebrow">Cobertura territorial</p>
          <h2 id="map-lazy-heading">Fontes por município</h2>
          <p class="muted">
            O mapa interativo será carregado quando esta área estiver próxima.
          </p>
        </div>
      {/if}
    </section>
    <section class="section">
      <h2>Como o catálogo se distribui</h2>
      <p class="muted">
        Os oito grupos com mais fichas em cada recorte. Uma ficha pode aparecer
        em várias categorias ou UFs.
      </p>
      <div class="charts">
        {#each charts as chart (chart.filter)}
          <section class="chart card {chart.color}">
            <h3>{chart.name}</h3>
            <ul class="bars">
              {#each chart.rows as row (row.id)}
                <li>
                  <a href={sources({ [chart.filter]: row.id })}>
                    <span>{displayText(row.nome)}</span><strong
                      >{number.format(row.total)}</strong
                    >
                    <span aria-hidden="true" class="track"
                      ><i
                        style:width={(100 * row.total) / chart.rows[0].total +
                          '%'}
                      ></i></span
                    >
                  </a>
                </li>
              {/each}
            </ul>
            <details>
              <summary>Ver tabela</summary>
              <table>
                <caption class="sr-only">{chart.name}</caption><thead
                  ><tr><th scope="col">Grupo</th><th scope="col">Fontes</th></tr
                  ></thead
                >
                <tbody
                  >{#each chart.rows as row (row.id)}<tr
                      ><th scope="row">{displayText(row.nome)}</th><td
                        >{number.format(row.total)}</td
                      ></tr
                    >{/each}</tbody
                >
              </table>
            </details>
          </section>
        {/each}
      </div>
    </section>
  {:else if failed}
    <LoadState {failed} retry={() => attempt++} />
  {:else}
    <div class="dashboard-loading" role="status" aria-live="polite">
      <span class="status-dot" aria-hidden="true"></span>
      <span>Resumo do catálogo</span>
    </div>
  {/if}
</div>

<style>
  .dashboard-loading,
  .map-placeholder {
    display: grid;
    align-content: center;
    gap: 0.65rem;
  }
  .dashboard-loading {
    min-height: 7rem;
    margin-top: 1.1rem;
    padding: 1.25rem;
    grid-template-columns: auto 1fr;
    align-items: center;
    color: var(--muted);
  }
  .map-lazy-section {
    min-height: 28rem;
  }
  .map-placeholder {
    min-height: 24rem;
    margin: 0;
    padding: clamp(1rem, 2vw, 1.5rem);
  }
  .map-placeholder h2,
  .map-placeholder p {
    margin-bottom: 0;
  }
</style>

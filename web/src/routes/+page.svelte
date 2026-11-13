<script lang="ts">
  import { resolve } from '$app/paths';
  import { query } from '$lib/client';
  import type { Dashboard } from '$lib/catalog';
  import { sources } from '$lib/links';
  import { displayText } from '$lib/labels';
  import LoadState from '$lib/LoadState.svelte';

  let report = $state<Dashboard>();
  let failed = $state(false);
  let attempt = $state(0);
  const number = new Intl.NumberFormat('pt-BR');
  $effect(() => {
    void attempt;
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
    <p class="eyebrow">Catálogo de fontes abertas</p>
    <h1>Explore o acervo<br /> do OSINT Rondônia.</h1>
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

{#if report}
  <section class="metrics" aria-label="Totais do catálogo">
    <a href={sources()}
      ><strong>{number.format(report.fontes)}</strong><span
        >Fontes cadastradas</span
      ><i aria-hidden="true">↗</i></a
    >
    <a href={resolve('/categorias/')}
      ><strong>{number.format(report.categorias)}</strong><span>Categorias</span
      ><i aria-hidden="true">↗</i></a
    >
    <a href={resolve('/listas/')}
      ><strong>{number.format(report.listas)}</strong><span
        >Listas temáticas</span
      ><i aria-hidden="true">↗</i></a
    >
  </section>
  <section class="section">
    <h2>Como o catálogo se distribui</h2>
    <p class="muted">
      Os oito grupos com mais fichas em cada recorte. Uma ficha pode aparecer em
      várias categorias ou UFs.
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
{:else}
  <LoadState {failed} retry={() => attempt++} />
{/if}

<script lang="ts">
  import { catalogOptions } from './client';
  import { fold, PAGE_SIZE } from './catalog';
  import type { Options } from './catalog';
  import type { Category, Item } from './catalog';
  import { graphLink, sources } from './links';
  import { displayLabel, displayText } from './labels';
  import Choice from './Choice.svelte';
  import LoadState from './LoadState.svelte';

  let { kind }: { kind: 'categorias' | 'listas' | 'abrangencia' } = $props();
  const copy = {
    categorias: [
      'Categorias',
      'Explore as classificações do catálogo por tema.',
    ],
    listas: [
      'Listas temáticas',
      'Consulte as fichas que reúnem todos os temas de uma lista.',
    ],
    abrangencia: [
      'Abrangência',
      'Explore fontes por cobertura territorial declarada.',
    ],
  };
  let options = $state<Options>();
  let failed = $state(false);
  let attempt = $state(0);
  let search = $state('');
  let uf = $state('');
  let municipality = $state('');
  let nationwide = $state(false);
  let limit = $state(PAGE_SIZE);
  $effect(() => {
    void attempt;
    failed = false;
    let current = true;
    catalogOptions()
      .then((value) => {
        if (current) options = value;
      })
      .catch(() => {
        if (current) failed = true;
      });
    return () => {
      current = false;
    };
  });
  type Entry = Item & {
    tipo_classificacao?: string;
    categorias?: Category[];
  };
  const entries = $derived.by((): Entry[] => {
    if (!options) return [];
    if (kind === 'categorias') return options.categorias;
    if (kind === 'listas') return options.listas;
    return options.ufs;
  });
  const rows = $derived(
    entries.filter(
      (item) =>
        fold(displayText(item.nome)).includes(fold(search.trim())) ||
        fold(item.nome).includes(fold(search.trim())),
    ),
  );
  const municipalities = $derived(
    options?.municipios
      .filter((item) => !uf || item.uf === uf)
      .map((item) => ({
        ...item,
        nome: uf
          ? item.nome
          : item.nome +
            ' / ' +
            options?.ufs.find(({ id }) => id === item.uf)?.nome,
      })) ?? [],
  );
</script>

<svelte:head><title>{copy[kind][0]} · OSINT Rondônia</title></svelte:head>
<div class="page-heading">
  <p class="eyebrow">Catálogo</p>
  <h1>{copy[kind][0]}</h1>
  <p>{copy[kind][1]}</p>
</div>
{#if options}
  {#if kind === 'abrangencia'}
    <div class="card filters">
      <div class="filter-grid">
        <Choice
          id="estado"
          label="UF"
          items={options.ufs}
          bind:value={
            () => uf,
            (value) => {
              uf = value;
              municipality = '';
            }
          }
        />
        <Choice
          id="cidade"
          label="Município"
          items={municipalities}
          bind:value={municipality}
        />
        <label class="check"
          ><input type="checkbox" bind:checked={nationwide} /> Incluir cobertura nacional</label
        >
      </div>
      <a
        class="button primary"
        href={sources({
          uf,
          municipio: municipality,
          nacional: nationwide ? '1' : '',
        })}>Ver fontes →</a
      >
    </div>
  {/if}
  <div class="field index-search">
    <label for="indice"
      >{kind === 'abrangencia' ? 'Buscar UF' : 'Buscar pelo nome'}</label
    >
    <input
      id="indice"
      type="search"
      bind:value={search}
      oninput={() => {
        limit = PAGE_SIZE;
      }}
    />
  </div>
  <p class="muted" aria-live="polite">
    {rows.length}
    {rows.length === 1 ? 'resultado' : 'resultados'}
  </p>
  <ul class="index-list">
    {#each rows.slice(0, limit) as item (item.id)}
      <li class="card">
        <div>
          <h2>
            <a
              href={sources({
                [kind === 'categorias'
                  ? 'categoria'
                  : kind === 'listas'
                    ? 'lista'
                    : 'uf']: item.id,
              })}>{displayText(item.nome)}</a
            >
          </h2>
          {#if 'tipo_classificacao' in item}<p class="muted">
              {displayLabel(item.tipo_classificacao ?? '')}
            </p>{/if}
          {#if 'categorias' in item}
            <ul class="chips">
              {#each item.categorias as category (category.id)}
                <li>
                  <a class="pill" href={sources({ categoria: category.id })}
                    >{displayText(category.nome)}</a
                  >
                </li>
              {/each}
            </ul>
          {/if}
        </div>
        {#if kind === 'categorias'}<a
            class="button"
            href={graphLink('categoria', item.id)}
            >Ver relações <span class="sr-only"
              >de {displayText(item.nome)}</span
            >↗</a
          >{/if}
      </li>
    {/each}
  </ul>
  {#if rows.length > limit}<button
      class="button"
      onclick={() => {
        limit += PAGE_SIZE;
      }}>Mostrar mais</button
    >{/if}
{:else}
  <LoadState {failed} retry={() => attempt++} />
{/if}

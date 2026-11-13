<script lang="ts">
  import { createIndexViewModel } from '$lib/features/index/index.viewmodel.svelte';
  import { graphLink, sources } from './links';
  import { displayLabel, displayText } from './labels';
  import Choice from './Choice.svelte';
  import LoadState from './LoadState.svelte';

  let { kind }: { kind: 'categorias' | 'listas' | 'abrangencia' } = $props();
  const vm = createIndexViewModel(() => kind);
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
  const options = $derived(vm.options.data);
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
          bind:value={() => vm.uf, (value) => (vm.uf = value)}
        />
        <Choice
          id="cidade"
          label="Município"
          items={vm.municipalities}
          bind:value={vm.municipality}
        />
        <label class="check"
          ><input type="checkbox" bind:checked={vm.nationwide} /> Incluir cobertura
          nacional</label
        >
      </div>
      <a
        class="button primary"
        href={sources({
          uf: vm.uf,
          municipio: vm.municipality,
          nacional: vm.nationwide ? '1' : '',
        })}>Ver fontes →</a
      >
    </div>
  {/if}
  <div class="field index-search">
    <label for="indice"
      >{kind === 'abrangencia' ? 'Buscar UF' : 'Buscar pelo nome'}</label
    >
    <input id="indice" type="search" bind:value={vm.search} />
  </div>
  <p class="muted" aria-live="polite">
    {vm.resultCount}
    {vm.resultCount === 1 ? 'resultado' : 'resultados'}
  </p>
  <ul class="index-list">
    {#each vm.visibleRows as item (item.id)}
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
  {#if vm.hasMore}<button class="button" onclick={vm.loadMore}
      >Mostrar mais</button
    >{/if}
{:else}
  <LoadState
    failed={vm.options.isError}
    retry={() => void vm.options.refetch()}
  />
{/if}

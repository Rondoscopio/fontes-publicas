<script lang="ts">
  import { browser } from '$app/environment';
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import { createSourcesViewModel } from '$lib/features/sources/sources.viewmodel.svelte';
  import { PAGE_SIZE } from '$lib/catalog';
  import type { Filters } from '$lib/catalog';
  import { sources } from '$lib/links';
  import Choice from '$lib/Choice.svelte';
  import LoadState from '$lib/LoadState.svelte';
  import SourceDetail from '$lib/SourceDetail.svelte';
  import { displayLabel, displayText } from '$lib/labels';

  const params = $derived(
    browser ? page.url.searchParams : new URLSearchParams(),
  );
  const detailId = $derived(params.get('id') ?? '');
  const filters = $derived<Filters>({
    q: params.get('q') ?? '',
    categoria: params.get('categoria') ?? '',
    tipo: params.get('tipo') ?? '',
    triagem: params.get('triagem') ?? '',
    uf: params.get('uf') ?? '',
    municipio: params.get('municipio') ?? '',
    lista: params.get('lista') ?? '',
    nacional: params.get('nacional') === '1',
    ordem: params.get('ordem') === 'desc' ? 'desc' : 'asc',
    pagina: Math.max(1, Number.parseInt(params.get('pagina') ?? '1', 10) || 1),
  });
  const vm = createSourcesViewModel(
    () => filters,
    () => detailId,
  );
  const result = $derived(vm.search.data);
  const options = $derived(vm.options.data);
  const detail = $derived(vm.detail.data);
  const failed = $derived(
    detailId ? vm.detail.isError : vm.search.isError || vm.options.isError,
  );
  let draft = $state<Filters>({
    q: '',
    categoria: '',
    tipo: '',
    triagem: '',
    uf: '',
    municipio: '',
    lista: '',
    nacional: false,
    ordem: 'asc',
    pagina: 1,
  });
  const paramsFrom = (value: Filters, currentPage: number) => ({
    ...value,
    nacional: value.nacional ? '1' : '',
    pagina: currentPage > 1 ? currentPage : undefined,
    ordem: value.ordem === 'desc' ? 'desc' : '',
  });
  $effect(() => {
    draft = { ...filters };
  });
  const totalPages = $derived(Math.ceil((result?.total ?? 0) / PAGE_SIZE));
  const list = $derived(options?.listas.find(({ id }) => id === draft.lista));
  const municipalities = $derived(
    options?.municipios
      .filter((item) => !draft.uf || item.uf === draft.uf)
      .map((item) => ({
        ...item,
        nome: draft.uf
          ? item.nome
          : item.nome +
            ' / ' +
            options?.ufs.find(({ id }) => id === item.uf)?.nome,
      })) ?? [],
  );
</script>

<svelte:head
  ><title
    >{detail ? displayText(detail.fonte.nome) : 'Explorar fontes'} · OSINT Rondônia</title
  ></svelte:head
>
{#if detailId}
  <p class="breadcrumb"><a href={sources()}>← Voltar às fontes</a></p>
  {#if detail === null}
    <h1>Fonte não encontrada</h1>
    <p>Confira o endereço ou volte à lista de fontes.</p>
  {:else if detail}
    <SourceDetail {detail} />
  {:else}
    <LoadState
      failed={vm.detail.isError}
      retry={() => void vm.detail.refetch()}
    />
  {/if}
{:else}
  <div class="page-heading">
    <p class="eyebrow">Catálogo</p>
    <h1>Explorar fontes</h1>
    <p>
      Pesquise no acervo e combine filtros para encontrar as fichas que você
      procura.
    </p>
  </div>
  <form
    class="card filters"
    onsubmit={(event) => {
      event.preventDefault();
      void goto(sources(paramsFrom(draft, 1)), { keepFocus: true });
    }}
  >
    <div class="search-row">
      <div class="field">
        <label for="busca">Nome ou descrição</label>
        <input
          id="busca"
          type="search"
          maxlength="160"
          placeholder="Buscar no catálogo"
          bind:value={draft.q}
        />
      </div>
      <button class="button primary" type="submit">Aplicar filtros</button>
    </div>
    {#if options}
      <div class="filter-grid">
        <Choice
          id="categoria"
          label="Categoria"
          items={options.categorias.map((item) => ({
            ...item,
            nome: `${displayText(item.nome)} · ${displayLabel(item.tipo_classificacao)}`,
          }))}
          bind:value={draft.categoria}
        />
        <Choice
          id="tipo"
          label="Tipo de fonte"
          items={options.tipos}
          bind:value={draft.tipo}
        />
        <Choice
          id="triagem"
          label="Triagem"
          items={[
            { id: 'sem-registro', nome: 'Sem registro' },
            ...options.triagens,
          ]}
          bind:value={draft.triagem}
        />
        <Choice
          id="ordem"
          label="Ordem"
          items={[
            { id: 'asc', nome: 'Nome (A–Z)' },
            { id: 'desc', nome: 'Nome (Z–A)' },
          ]}
          bind:value={draft.ordem}
        />
        <Choice
          id="uf"
          label="UF de cobertura"
          items={options.ufs}
          bind:value={
            () => draft.uf,
            (value) => {
              draft.uf = value;
              draft.municipio = '';
            }
          }
        />
        <Choice
          id="municipio"
          label="Município de cobertura"
          items={municipalities}
          bind:value={draft.municipio}
        />
        <Choice
          id="lista"
          label="Lista temática"
          items={options.listas}
          bind:value={draft.lista}
        />
        <label class="check"
          ><input type="checkbox" bind:checked={draft.nacional} /> Incluir cobertura
          nacional</label
        >
      </div>
      {#if list}<p class="muted">
          A lista {displayText(list.nome)} exige todos os seus temas.
        </p>{/if}
    {/if}
    <a href={sources()}>Limpar filtros</a>
  </form>

  {#if result}
    <section class="section" aria-labelledby="resultados">
      <h2 id="resultados" aria-live="polite">
        {result.total.toLocaleString('pt-BR')}
        {result.total === 1 ? 'fonte encontrada' : 'fontes encontradas'}
      </h2>
      {#if result.items.length}
        <div class="card table-scroll">
          <table class="results">
            <thead
              ><tr
                ><th scope="col">Fonte</th><th scope="col">Tipo</th><th
                  scope="col">Triagem</th
                ></tr
              ></thead
            >
            <tbody>
              {#each result.items as item (item.id)}
                <tr
                  ><th scope="row"
                    ><a href={sources({ id: item.id })}
                      >{displayText(item.nome)}</a
                    >
                    {#if item.descricao}<p class="excerpt">
                        {displayText(item.descricao)}
                      </p>{/if}</th
                  >
                  <td>{item.tipo ? displayText(item.tipo) : '—'}</td><td
                    ><span class="pill"
                      >{item.status_triagem
                        ? displayText(item.status_triagem)
                        : 'Sem registro'}</span
                    ></td
                  >
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
        {#if totalPages > 1}
          <nav class="pagination" aria-label="Paginação de fontes">
            {#if result.page > 1}<a
                class="button"
                href={sources(paramsFrom(filters, result.page - 1))}
                >← Anterior</a
              >{/if}
            <span>Página {result.page} de {totalPages}</span>
            {#if result.page < totalPages}<a
                class="button"
                href={sources(paramsFrom(filters, result.page + 1))}
                >Próxima →</a
              >{/if}
          </nav>
        {/if}
      {:else}
        <p class="notice">
          Nenhuma ficha corresponde aos filtros selecionados.
        </p>
      {/if}
    </section>
  {:else}
    <LoadState
      {failed}
      retry={() => {
        void vm.search.refetch();
        void vm.options.refetch();
      }}
    />
  {/if}
{/if}

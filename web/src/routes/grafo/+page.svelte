<script lang="ts">
  import { browser } from '$app/environment';
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import { query } from '$lib/client';
  import { GRAPH_LIMIT } from '$lib/catalog';
  import type { Graph, GraphNode, NodeKind } from '$lib/catalog';
  import { graphLink, sources } from '$lib/links';
  import { displayText } from '$lib/labels';
  import LoadState from '$lib/LoadState.svelte';

  const params = $derived(
    browser ? page.url.searchParams : new URLSearchParams(),
  );
  const kind = $derived(params.get('tipo'));
  const id = $derived(params.get('id') ?? '');
  const currentPage = $derived(
    Math.max(
      1,
      Math.min(10000, Number.parseInt(params.get('pagina') ?? '1', 10) || 1),
    ),
  );
  let graph = $state<Graph | null>();
  let failed = $state(false);
  let attempt = $state(0);
  let canvas = $state<HTMLDivElement>();
  let visualFailed = $state(false);
  const key = (node: GraphNode) => node.kind + ':' + node.id;
  const names = { fonte: 'Fonte', categoria: 'Categoria', origem: 'Origem' };

  $effect(() => {
    void attempt;
    graph = undefined;
    failed = false;
    if (
      !id ||
      (kind !== 'fonte' && kind !== 'categoria' && kind !== 'origem')
    ) {
      graph = null;
      return;
    }
    let current = true;
    query('graph', kind, id, (currentPage - 1) * GRAPH_LIMIT)
      .then((value) => {
        if (current) graph = value;
      })
      .catch(() => {
        if (current) failed = true;
      });
    return () => {
      current = false;
    };
  });

  $effect(() => {
    const container = canvas;
    const data = graph;
    visualFailed = false;
    if (!container || !data || !data.neighbors.length) return;
    let current = true;
    let destroy: (() => void) | undefined;
    import('cytoscape')
      .then(({ default: cytoscape }) => {
        if (!current) return;
        const center = key(data.center);
        const nodes = new Map(
          [data.center, ...data.neighbors].map((node) => [key(node), node]),
        );
        const network = cytoscape({
          container,
          elements: [
            ...[...nodes.values()].map((node) => ({
              data: {
                id: key(node),
                label: displayText(node.nome),
                kind: node.kind,
                href: graphLink(node.kind, node.id),
              },
              classes: key(node) === center ? 'center' : '',
            })),
            ...data.neighbors.map((node, i) => ({
              data: {
                id: 'edge-' + i,
                source: node.direction === 'out' ? center : key(node),
                target: node.direction === 'out' ? key(node) : center,
              },
            })),
          ],
          style: [
            {
              selector: 'node',
              style: {
                'background-color': '#6552bb',
                label: 'data(label)',
                'font-size': 10,
                'text-wrap': 'ellipsis',
                'text-max-width': '102px',
                color: '#24204a',
                'text-margin-y': -6,
              },
            },
            {
              selector: 'node[kind = "categoria"]',
              style: {
                'background-color': '#168577',
                shape: 'round-rectangle',
              },
            },
            {
              selector: 'node[kind = "origem"]',
              style: { 'background-color': '#ac7622', shape: 'diamond' },
            },
            {
              selector: 'node.center',
              style: {
                width: 45,
                height: 45,
                'border-width': 3,
                'border-color': '#312060',
              },
            },
            {
              selector: 'edge',
              style: {
                width: 1,
                'line-color': '#afa6ce',
                'target-arrow-color': '#afa6ce',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
              },
            },
          ],
          layout: {
            name: 'concentric',
            concentric: (node) => (node.id() === center ? 2 : 1),
            levelWidth: () => 1,
            padding: 36,
          },
          minZoom: 0.15,
          maxZoom: 3,
        });
        destroy = () => network.destroy();
        network.on('tap', 'node', (event) => {
          if (event.target.id() !== center)
            void goto(event.target.data('href'));
        });
      })
      .catch(() => {
        if (current) visualFailed = true;
      });
    return () => {
      current = false;
      destroy?.();
    };
  });
</script>

<svelte:head><title>Grafo de relações · OSINT Rondônia</title></svelte:head>
<p class="breadcrumb"><a href={sources()}>← Voltar às fontes</a></p>
<div class="page-heading">
  <p class="eyebrow">Rede do catálogo</p>
  <h1>{graph ? displayText(graph.center.nome) : 'Grafo de relações'}</h1>
  {#if graph?.center.kind === 'fonte'}<a href={sources({ id: graph.center.id })}
      >Abrir ficha da fonte ↗</a
    >{/if}
  {#if graph?.center.kind === 'categoria'}<a
      href={sources({ categoria: graph.center.id })}
      >Ver fontes da categoria ↗</a
    >{/if}
</div>
{#if graph}
  {#if graph.neighbors.length}
    <p class="muted">
      Selecione um nó ou um link da lista para explorar suas relações. Use o
      scroll para ampliar.
    </p>
    {#if visualFailed}<p class="notice">
        O desenho do grafo não está disponível. Consulte a lista de relações.
      </p>{/if}
    <div
      class="card graph"
      aria-hidden="true"
      hidden={visualFailed}
      bind:this={canvas}
    ></div>
    <p class="legend">
      <span>● Fonte</span><span>■ Categoria</span><span>◆ Origem</span>
    </p>
  {/if}
  <section class="section">
    <h2>Relações diretas ({graph.total.toLocaleString('pt-BR')})</h2>
    <ul class="index-list">
      {#each graph.neighbors as node (key(node) + node.direction + node.relacao)}
        <li class="card">
          <div>
            <span class="muted"
              >{names[node.kind]} · {displayText(node.relacao)}</span
            ><br /><a href={graphLink(node.kind, node.id)}
              >{displayText(node.nome)}</a
            >
          </div>
        </li>
      {:else}
        <li class="notice">Nenhuma relação nesta página.</li>
      {/each}
    </ul>
    {#if graph.total > GRAPH_LIMIT || currentPage > 1}
      <nav class="pagination" aria-label="Paginação de relações">
        {#if currentPage > 1}<a
            class="button"
            href={graphLink(
              graph.center.kind,
              graph.center.id,
              currentPage - 1,
            )}>← Anterior</a
          >{/if}
        <span>Página {currentPage}</span>
        {#if currentPage * GRAPH_LIMIT < graph.total}<a
            class="button"
            href={graphLink(
              graph.center.kind,
              graph.center.id,
              currentPage + 1,
            )}>Próxima →</a
          >{/if}
      </nav>
    {/if}
  </section>
{:else if graph === null}
  <p class="notice">
    Selecione uma fonte ou categoria para abrir suas relações.
  </p>
{:else}
  <LoadState {failed} retry={() => attempt++} />
{/if}

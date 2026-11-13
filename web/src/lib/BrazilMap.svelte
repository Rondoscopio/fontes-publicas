<script lang="ts">
  import { asset } from '$app/paths';
  import { goto } from '$app/navigation';
  import { geoMercator, geoPath } from 'd3-geo';
  import { select } from 'd3-selection';
  import { zoom, zoomIdentity } from 'd3-zoom';
  import { feature } from 'topojson-client';
  import type { Feature, FeatureCollection, Geometry } from 'geojson';
  import { query } from '$lib/client';
  import type { CoverageMap, MunicipalityCoverage } from '$lib/catalog';
  import { sources } from '$lib/links';
  import Choice from '$lib/Choice.svelte';
  import LoadState from '$lib/LoadState.svelte';

  type MapFeature = Feature<Geometry, { codigo_ibge: string }>;
  type TopologyObject = {
    type: 'GeometryCollection';
    geometries: {
      type: string;
      id: string;
      properties: { codigo_ibge: string };
    }[];
  };
  type MapTopology = {
    type: 'Topology';
    objects: { municipios: TopologyObject };
    arcs: unknown[];
    bbox?: number[];
    transform?: unknown;
  };

  let coverage = $state<CoverageMap>();
  let shapes = $state<MapFeature[]>([]);
  let failed = $state(false);
  let attempt = $state(0);
  let includeNational = $state(false);
  let shapeRequest: Promise<MapFeature[]> | undefined;
  let mapSvg = $state<SVGSVGElement>();
  let mapLayer = $state<SVGGElement>();
  let zoomBehavior = $state<ReturnType<typeof zoom<SVGSVGElement, unknown>>>();
  let selectedId = $state('');
  let municipalitySearch = $state('');
  let tableLimit = $state(100);

  const byId = $derived(
    new Map((coverage?.municipalities ?? []).map((item) => [item.id, item])),
  );
  const selectedMunicipality = $derived(byId.get(selectedId));
  const visibleTableRows = $derived.by(() => {
    const term = municipalitySearch.trim().toLocaleLowerCase('pt-BR');
    return (coverage?.municipalities ?? [])
      .filter(
        (item) =>
          !term ||
          `${item.nome} ${item.uf_sigla}`
            .toLocaleLowerCase('pt-BR')
            .includes(term),
      )
      .slice(0, tableLimit);
  });
  const maximum = $derived(
    Math.max(0, ...(coverage?.municipalities ?? []).map((item) => item.total)),
  );
  const number = new Intl.NumberFormat('pt-BR');

  async function loadMap() {
    failed = false;
    try {
      shapeRequest ??= fetch(asset('/maps/municipios-brasil.topojson')).then(
        async (response) => {
          if (!response.ok) throw new Error('Falha ao carregar o mapa.');
          const topology = (await response.json()) as MapTopology;
          const collection = feature(
            topology as never,
            topology.objects.municipios as never,
          ) as unknown as FeatureCollection<Geometry, { codigo_ibge: string }>;
          const ids = collection.features.map(
            (shape) => shape.properties.codigo_ibge,
          );
          if (new Set(ids).size !== ids.length) {
            throw new Error('A malha contém códigos municipais repetidos.');
          }
          return collection.features as MapFeature[];
        },
      );
      const [mapShapes, totals] = await Promise.all([
        shapeRequest,
        query('coverageMap', includeNational),
      ]);
      const ids = new Set(
        mapShapes.map((shape) => shape.properties.codigo_ibge),
      );
      if (
        mapShapes.length !== totals.municipalities.length ||
        totals.municipalities.some((item) => !ids.has(item.id))
      ) {
        throw new Error('A geometria territorial não corresponde ao catálogo.');
      }
      shapes = mapShapes;
      coverage = totals;
    } catch {
      shapeRequest = undefined;
      failed = true;
    }
  }

  $effect(() => {
    void attempt;
    void includeNational;
    void loadMap();
  });

  const projection = $derived.by(() => {
    if (!shapes.length) return undefined;
    return geoMercator().fitExtent(
      [
        [12, 12],
        [988, 588],
      ],
      { type: 'FeatureCollection', features: shapes },
    );
  });
  const path = $derived(projection ? geoPath(projection) : undefined);

  $effect(() => {
    const svg = mapSvg;
    const layer = mapLayer;
    if (!svg || !layer) return;
    const behavior = zoom<SVGSVGElement, unknown>()
      .scaleExtent([1, 12])
      .on('zoom', (event) => {
        select(layer).attr('transform', event.transform.toString());
      });
    zoomBehavior = behavior;
    select(svg).call(behavior).on('dblclick.zoom', null);
    select(layer).on('click.catalog', (event: MouseEvent) => {
      const pathElement = (event.target as Element).closest<SVGPathElement>(
        '.municipality-shape',
      );
      const code = pathElement?.dataset.codigoIbge;
      if (code) activateMunicipality(byId.get(code));
    });
    return () => {
      select(svg).on('.zoom', null);
      select(layer).on('.catalog', null);
    };
  });

  function zoomBy(factor: number) {
    if (mapSvg && zoomBehavior)
      select(mapSvg).call(zoomBehavior.scaleBy, factor);
  }

  function activateMunicipality(item: MunicipalityCoverage | undefined) {
    if (!item) return;
    void goto(
      sources({
        uf: item.uf,
        municipio: item.id,
        nacional: includeNational ? '1' : '',
      }),
    );
  }

  function color(total: number) {
    if (!total) return 'var(--map-empty)';
    const ratio = maximum ? Math.log1p(total) / Math.log1p(maximum) : 0;
    return `color-mix(in srgb, var(--map-fill) ${Math.round(48 + ratio * 52)}%, var(--map-empty))`;
  }
</script>

<section class="map-card card" aria-labelledby="coverage-map-heading">
  <div class="map-heading">
    <div>
      <p class="eyebrow">Cobertura territorial</p>
      <h2 id="coverage-map-heading">Fontes por município</h2>
      <p class="muted">
        A cobertura estadual aparece em todos os municípios da UF. A cobertura
        nacional pode ser incluída no mapa.
      </p>
    </div>
    <label class="check national-toggle">
      <input type="checkbox" bind:checked={includeNational} />
      Incluir fontes nacionais
    </label>
  </div>

  {#if coverage && shapes.length && path}
    <div class="map-controls" aria-label="Controles do mapa">
      <button
        class="map-control"
        type="button"
        aria-label="Aumentar zoom"
        onclick={() => zoomBy(1.5)}>+</button
      >
      <button
        class="map-control"
        type="button"
        aria-label="Diminuir zoom"
        onclick={() => zoomBy(1 / 1.5)}>−</button
      >
      <button
        class="map-control reset-zoom"
        type="button"
        onclick={() =>
          mapSvg &&
          zoomBehavior &&
          select(mapSvg).call(zoomBehavior.transform, zoomIdentity)}
        >Redefinir</button
      >
    </div>
    <div class="map-viewport">
      <svg
        bind:this={mapSvg}
        class="brazil-map"
        viewBox="0 0 1000 600"
        role="img"
        aria-labelledby="map-title map-description"
      >
        <title id="map-title">Mapa de cobertura por município no Brasil</title>
        <desc id="map-description">
          5.571 municípios. Arraste para mover e use os controles de zoom. Passe
          o ponteiro sobre uma área para ver quantas fontes cobrem o município.
        </desc>
        <g bind:this={mapLayer}>
          {#each shapes as shape (shape.properties.codigo_ibge)}
            {@const item = byId.get(shape.properties.codigo_ibge)}
            <path
              class="municipality-shape"
              data-codigo-ibge={shape.properties.codigo_ibge}
              d={path(shape) ?? ''}
              fill={color(item?.total ?? 0)}
            >
              <title>
                {item?.nome ?? 'Município'} / {item?.uf_sigla ?? ''}: {number.format(
                  item?.total ?? 0,
                )}
                {item?.total === 1 ? 'fonte' : 'fontes'}.
              </title>
            </path>
          {/each}
        </g>
      </svg>
    </div>
    <div class="map-caption">
      <span>Arraste para mover · Use o zoom ou busque um município</span>
      <span class="map-legend" aria-label="Legenda de cobertura">
        <i></i> Sem cobertura
        <i></i> Mais fontes
      </span>
    </div>
    <div class="map-search">
      <Choice
        id="map-municipio"
        label="Buscar município no mapa"
        items={coverage.municipalities.map((item) => ({
          id: item.id,
          nome: `${item.nome} / ${item.uf_sigla}`,
        }))}
        bind:value={selectedId}
      />
      <button
        class="button primary"
        type="button"
        disabled={!selectedMunicipality}
        onclick={() => activateMunicipality(selectedMunicipality)}
        >Ver fontes</button
      >
    </div>
    <details class="map-table-details">
      <summary>Consultar a cobertura em tabela</summary>
      <div class="field map-table-search">
        <label for="map-table-search">Filtrar municípios</label>
        <input
          id="map-table-search"
          type="search"
          bind:value={municipalitySearch}
        />
      </div>
      <div class="table-scroll">
        <table class="results">
          <caption class="sr-only">Fontes por município</caption>
          <thead
            ><tr
              ><th scope="col">Município</th><th scope="col">UF</th><th
                scope="col">Fontes</th
              ></tr
            ></thead
          >
          <tbody>
            {#each visibleTableRows as item (item.id)}
              <tr>
                <th scope="row">{item.nome}</th>
                <td>{item.uf_sigla}</td>
                <td
                  ><a
                    href={sources({
                      uf: item.uf,
                      municipio: item.id,
                      nacional: includeNational ? '1' : '',
                    })}>{number.format(item.total)}</a
                  ></td
                >
              </tr>
            {:else}
              <tr><td colspan="3">Nenhum município corresponde à busca.</td></tr
              >
            {/each}
          </tbody>
        </table>
      </div>
      {#if visibleTableRows.length === tableLimit}
        <button class="button" type="button" onclick={() => (tableLimit += 100)}
          >Mostrar mais municípios</button
        >
      {/if}
    </details>
  {:else}
    <LoadState {failed} retry={() => attempt++} />
  {/if}
</section>

<style>
  .map-card {
    padding: clamp(1rem, 2vw, 1.5rem);
    position: relative;
  }
  .map-heading,
  .map-caption,
  .map-search {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
  }
  .map-heading h2 {
    font-size: 1.55rem;
    margin-bottom: 0.45rem;
  }
  .map-heading p:not(.eyebrow) {
    margin-bottom: 0;
  }
  .national-toggle {
    white-space: nowrap;
  }
  .map-controls {
    position: absolute;
    z-index: 1;
    right: 1.5rem;
    top: 8.5rem;
    display: grid;
    gap: 0.35rem;
  }
  .map-control {
    min-width: 2.5rem;
    min-height: 2.5rem;
    border: 1px solid var(--border);
    border-radius: 0.5rem;
    background: var(--surface);
    color: var(--ink);
    font-weight: 750;
    box-shadow: 0 0.2rem 0.8rem #0002;
  }
  .reset-zoom {
    font-size: 0.75rem;
  }
  .map-viewport {
    margin-top: 1rem;
    border: 1px solid var(--border);
    border-radius: 0.65rem;
    background: var(--map-water);
    overflow: hidden;
  }
  .brazil-map {
    display: block;
    width: 100%;
    min-height: 25rem;
    touch-action: none;
    cursor: grab;
  }
  .brazil-map:active {
    cursor: grabbing;
  }
  .municipality-shape {
    stroke: var(--map-boundary);
    stroke-width: 0.35;
    vector-effect: non-scaling-stroke;
    cursor: pointer;
    transition: filter 100ms ease;
  }
  .municipality-shape:hover {
    stroke: var(--ink);
    stroke-width: 1.4;
    filter: brightness(1.12);
  }
  .map-caption {
    min-height: 3rem;
    flex-wrap: wrap;
    color: var(--muted);
    font-size: 0.86rem;
  }
  .map-legend {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
  }
  .map-legend i {
    width: 1.3rem;
    height: 0.65rem;
    display: inline-block;
    background: var(--map-empty);
    border: 1px solid var(--map-boundary);
    border-radius: 0.15rem;
  }
  .map-legend i + i {
    background: var(--map-fill);
  }
  .map-search {
    align-items: end;
    max-width: 48rem;
    margin-top: 0.75rem;
  }
  .map-search :global(.field) {
    flex: 1;
  }
  .map-table-details {
    margin-top: 1rem;
  }
  .map-table-details summary {
    cursor: pointer;
    color: var(--brand);
    font-weight: 700;
  }
  .map-table-search {
    max-width: 28rem;
    margin-block: 1rem;
  }
  @media (max-width: 640px) {
    .map-heading,
    .map-search {
      align-items: stretch;
      flex-direction: column;
    }
    .national-toggle {
      white-space: normal;
    }
    .map-controls {
      right: 1.25rem;
      top: 11.5rem;
    }
    .brazil-map {
      min-height: 18rem;
    }
    .map-caption {
      align-items: flex-start;
      flex-direction: column;
      padding-top: 0.5rem;
    }
  }
</style>

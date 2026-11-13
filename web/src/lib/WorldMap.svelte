<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { sources } from '$lib/links';
  import { displayText } from '$lib/labels';
  import LoadState from '$lib/LoadState.svelte';
  import { createMapViewModel } from '$lib/features/map/map.viewmodel.svelte';
  import { registerPmtiles } from '$lib/features/map/adapters/pmtiles-runtime';
  import type { Map as MapLibreMap, MapLayerMouseEvent } from 'maplibre-gl';
  import type { Basemap, Projection } from '$lib/features/map/domain/types';
  import 'maplibre-gl/dist/maplibre-gl.css';

  type SelectedPlace = {
    name: string;
    country: string;
    countryId: string | null;
    ufSigla?: string;
    municipalityId?: string;
  };

  let mapElement = $state<HTMLDivElement>();
  let mapLoaded = $state(false);
  let mapFailed = $state(false);
  let basemap = $state<Basemap>('borders');
  let projection = $state<Projection>('mercator');
  let selectedPlace = $state<SelectedPlace>();
  let brazilReady = $state(false);
  let search = $state('');
  let tableLimit = $state(50);
  let map: MapLibreMap | undefined;
  let worldArchiveUrl = '';
  let municipalityArchiveUrl = '';
  const featureStateCounts = new Map<string, number>();
  const vm = createMapViewModel();
  const coverage = $derived(vm.coverage.data);
  const states = $derived(
    coverage?.states.map((item) => ({
      ...item,
      total: item.total + (vm.includeNational ? item.nationalIncrement : 0),
    })) ?? [],
  );
  const municipalities = $derived(
    coverage?.municipalities.map((item) => ({
      ...item,
      total: item.total + (vm.includeNational ? item.nationalIncrement : 0),
    })) ?? [],
  );
  const selectedState = $derived(
    states.find((item) => item.sigla === selectedPlace?.ufSigla),
  );
  const selectedMunicipality = $derived(
    municipalities.find((item) => item.id === selectedPlace?.municipalityId),
  );
  const filteredMunicipalities = $derived.by(() => {
    const query = search.trim().toLocaleLowerCase('pt-BR');
    return municipalities
      .filter((item) =>
        `${item.nome} ${item.uf_sigla}`
          .toLocaleLowerCase('pt-BR')
          .includes(query),
      )
      .slice(0, tableLimit);
  });
  const number = new Intl.NumberFormat('pt-BR');
  const naturalEarthUrl =
    'https://www.naturalearthdata.com/about/terms-of-use/';

  function applyCoverage() {
    if (!map || !mapLoaded || !coverage) return;

    if (map.isSourceLoaded('world-regions')) {
      const stateCoverage = new Map(
        states.map((item) => [item.sigla, item.total]),
      );
      const visibleRegions = new Set<string>();
      for (const feature of map.querySourceFeatures('world-regions', {
        sourceLayer: 'regions',
      })) {
        const uf = String(feature.properties?.uf_sigla ?? '');
        const id = String(feature.id ?? feature.properties?.map_id ?? '');
        if (!uf || !id || visibleRegions.has(id)) continue;
        visibleRegions.add(id);
        const count = stateCoverage.get(uf) ?? 0;
        const cacheKey = `admin1:${id}`;
        if (featureStateCounts.get(cacheKey) === count) continue;
        map.setFeatureState(
          { source: 'world-regions', sourceLayer: 'regions', id },
          { count },
        );
        featureStateCounts.set(cacheKey, count);
      }
    }

    if (!brazilReady || !map.isSourceLoaded('brazil-municipalities')) return;
    const coverageById = new Map(
      municipalities.map((item) => [item.id, item.total]),
    );
    const visibleIds = new Set<string>();
    for (const feature of map.querySourceFeatures('brazil-municipalities', {
      sourceLayer: 'municipios',
    })) {
      const id = String(feature.id ?? feature.properties?.codigo_ibge ?? '');
      if (!id || visibleIds.has(id)) continue;
      visibleIds.add(id);
      const count = coverageById.get(id) ?? 0;
      const cacheKey = `municipality:${id}`;
      if (featureStateCounts.get(cacheKey) === count) continue;
      map.setFeatureState(
        {
          source: 'brazil-municipalities',
          sourceLayer: 'municipios',
          id,
        },
        { count },
      );
      featureStateCounts.set(cacheKey, count);
    }
  }

  function boundsOf(coordinates: unknown) {
    const bounds: [[number, number], [number, number]] = [
      [Infinity, Infinity],
      [-Infinity, -Infinity],
    ];
    const visit = (value: unknown) => {
      if (!Array.isArray(value)) return;
      if (
        value.length >= 2 &&
        typeof value[0] === 'number' &&
        typeof value[1] === 'number'
      ) {
        bounds[0][0] = Math.min(bounds[0][0], value[0]);
        bounds[0][1] = Math.min(bounds[0][1], value[1]);
        bounds[1][0] = Math.max(bounds[1][0], value[0]);
        bounds[1][1] = Math.max(bounds[1][1], value[1]);
        return;
      }
      for (const child of value) visit(child);
    };
    visit(coordinates);
    return bounds;
  }

  function loadBrazilMunicipalities() {
    if (!map || !mapLoaded || map.getSource('brazil-municipalities')) return;
    map.addSource('brazil-municipalities', {
      type: 'vector',
      url: municipalityArchiveUrl,
      promoteId: { municipios: 'codigo_ibge' },
    });
    map.addLayer({
      id: 'brazil-municipality-fill',
      type: 'fill',
      source: 'brazil-municipalities',
      'source-layer': 'municipios',
      minzoom: 3.5,
      paint: {
        'fill-color': [
          'interpolate',
          ['linear'],
          ['coalesce', ['feature-state', 'count'], 0],
          0,
          '#edf1e7',
          1,
          '#c4dfc2',
          10,
          '#82bc85',
          100,
          '#287246',
        ],
        'fill-opacity': 0.92,
        'fill-outline-color': '#718475',
      },
    });
    map.addLayer({
      id: 'brazil-municipality-hit',
      type: 'line',
      source: 'brazil-municipalities',
      'source-layer': 'municipios',
      minzoom: 3.5,
      paint: { 'line-color': '#526557', 'line-width': 0.35 },
    });
    map.on('click', 'brazil-municipality-hit', selectMunicipality);
    map.on('mouseenter', 'brazil-municipality-hit', () => {
      if (map) map.getCanvas().style.cursor = 'pointer';
    });
    map.on('mouseleave', 'brazil-municipality-hit', () => {
      if (map) map.getCanvas().style.cursor = '';
    });
  }

  function selectCountry(event: MapLayerMouseEvent) {
    const feature = event.features?.[0];
    if (!feature) return;
    const properties = feature.properties ?? {};
    const countryId = String(properties.map_id ?? feature.id ?? '');
    const name = String(properties.name ?? 'País');
    selectedPlace = { name, country: name, countryId };
    if (feature.geometry && 'coordinates' in feature.geometry) {
      const bounds = boundsOf(feature.geometry.coordinates);
      if (Number.isFinite(bounds[0][0])) {
        map?.fitBounds(bounds, { padding: 56, maxZoom: 5, duration: 750 });
      }
    }
    if (countryId === 'BRA') loadBrazilMunicipalities();
  }

  function selectRegion(event: MapLayerMouseEvent) {
    const feature = event.features?.[0];
    if (!feature) return;
    const properties = feature.properties ?? {};
    const name = String(properties.name ?? 'Região administrativa');
    const country = String(properties.country_name ?? '');
    const countryId = properties.country_id
      ? String(properties.country_id)
      : null;
    const iso3166_2 = String(properties.iso_3166_2 ?? '');
    const ufSigla = String(
      properties.uf_sigla ??
        (iso3166_2.startsWith('BR-') ? iso3166_2.slice(3) : ''),
    );
    selectedPlace = {
      name,
      country,
      countryId,
      ufSigla: ufSigla || undefined,
    };
  }

  function selectMunicipality(event: MapLayerMouseEvent) {
    const feature = event.features?.[0];
    if (!feature) return;
    const id = String(feature.properties?.codigo_ibge ?? feature.id ?? '');
    const item = municipalities.find((municipality) => municipality.id === id);
    if (!item) return;
    selectedPlace = {
      name: item.nome,
      country: item.uf_sigla,
      countryId: 'BRA',
      municipalityId: item.id,
    };
  }

  function goToBrazil() {
    selectedPlace = { name: 'Brasil', country: 'Brasil', countryId: 'BRA' };
    loadBrazilMunicipalities();
    map?.fitBounds(
      [
        [-74, -34],
        [-34, 6],
      ],
      { padding: 52, maxZoom: 4.5, duration: 750 },
    );
  }

  function useBasemap(next: Basemap) {
    basemap = next;
    if (!map || !mapLoaded) return;
    if (next === 'relief' && !map.getSource('world-relief')) {
      map.addSource('world-relief', {
        type: 'image',
        url: vm.assets.reliefImageUrl,
        coordinates: [
          [-180, 85],
          [180, 85],
          [180, -85],
          [-180, -85],
        ],
      });
      map.addLayer(
        {
          id: 'world-relief-layer',
          type: 'raster',
          source: 'world-relief',
          layout: { visibility: 'visible' },
          paint: { 'raster-opacity': 0.95 },
        },
        'world-countries-fill',
      );
    }
    if (next === 'satellite' && !map.getSource('satellite-imagery')) {
      map.addSource('satellite-imagery', {
        type: 'raster',
        tiles: vm.satellite.tiles,
        tileSize: vm.satellite.tileSize,
        maxzoom: vm.satellite.maxzoom,
        attribution: vm.satellite.attribution,
      });
      map.addLayer(
        {
          id: 'satellite-imagery-layer',
          type: 'raster',
          source: 'satellite-imagery',
          layout: { visibility: 'visible' },
          paint: { 'raster-opacity': 1 },
        },
        'world-countries-fill',
      );
    }
    if (map.getLayer('world-relief-layer')) {
      map.setLayoutProperty(
        'world-relief-layer',
        'visibility',
        next === 'relief' ? 'visible' : 'none',
      );
    }
    if (map.getLayer('satellite-imagery-layer')) {
      map.setLayoutProperty(
        'satellite-imagery-layer',
        'visibility',
        next === 'satellite' ? 'visible' : 'none',
      );
    }
    map.setPaintProperty(
      'world-countries-fill',
      'fill-color',
      next === 'borders' ? '#dfe8dc' : '#f5f5ed',
    );
    map.setPaintProperty(
      'world-countries-fill',
      'fill-opacity',
      next === 'borders' ? 1 : 0.22,
    );
    if (map.getLayer('brazil-admin1-coverage')) {
      map.setPaintProperty(
        'brazil-admin1-coverage',
        'fill-opacity',
        next === 'borders' ? 0.86 : 0.58,
      );
    }
    map.setPaintProperty(
      'world-country-boundaries',
      'line-color',
      next === 'satellite' ? '#ffffff' : '#607265',
    );
    map.setPaintProperty(
      'world-admin1-boundaries',
      'line-color',
      next === 'satellite' ? '#ffffff' : '#738276',
    );
  }

  function setProjection(next: Projection) {
    projection = next;
    map?.setProjection({ type: next });
  }

  function openMunicipality(item: (typeof municipalities)[number]) {
    void goto(
      sources({
        uf: item.uf,
        municipio: item.id,
        nacional: vm.includeNational ? '1' : '',
      }),
    );
  }

  function openState(item: (typeof states)[number]) {
    void goto(
      sources({
        uf: item.id,
        nacional: vm.includeNational ? '1' : '',
      }),
    );
  }

  $effect(() => {
    void coverage;
    applyCoverage();
  });

  $effect(() => {
    const includeNational = vm.includeNational;
    if (mapLoaded) {
      selectedPlace = undefined;
      applyCoverage();
    }
    void includeNational;
  });

  onMount(() => {
    let cancelled = false;
    void (async () => {
      try {
        const maplibre = await import('maplibre-gl');
        if (cancelled || !mapElement) return;
        [worldArchiveUrl, municipalityArchiveUrl] = registerPmtiles(maplibre, [
          vm.assets.worldTilesUrl,
          vm.assets.brazilMunicipalityTilesUrl,
        ]);
        map = new maplibre.Map({
          container: mapElement,
          style: {
            version: 8,
            sources: {},
            layers: [
              {
                id: 'background',
                type: 'background',
                paint: { 'background-color': '#e8ece5' },
              },
            ],
          },
          center: [0, 18],
          zoom: 1.25,
          minZoom: 0.8,
          maxZoom: 10,
          attributionControl: false,
          renderWorldCopies: true,
          cooperativeGestures: true,
        });
        map.on('load', () => {
          if (!map) return;
          map.addSource('world-countries', {
            type: 'vector',
            url: worldArchiveUrl,
            promoteId: { countries: 'map_id', regions: 'map_id' },
          });
          map.addLayer({
            id: 'world-countries-fill',
            type: 'fill',
            source: 'world-countries',
            'source-layer': 'countries',
            paint: { 'fill-color': '#dfe8dc', 'fill-opacity': 1 },
          });
          map.addLayer({
            id: 'world-country-boundaries',
            type: 'line',
            source: 'world-countries',
            'source-layer': 'countries',
            paint: { 'line-color': '#607265', 'line-width': 0.75 },
          });
          map.addSource('world-regions', {
            type: 'vector',
            url: worldArchiveUrl,
            promoteId: { countries: 'map_id', regions: 'map_id' },
          });
          map.addLayer(
            {
              id: 'brazil-admin1-coverage',
              type: 'fill',
              source: 'world-regions',
              'source-layer': 'regions',
              minzoom: 1.7,
              filter: ['==', ['get', 'country_id'], 'BRA'],
              paint: {
                'fill-color': [
                  'interpolate',
                  ['linear'],
                  ['coalesce', ['feature-state', 'count'], 0],
                  0,
                  '#edf1e7',
                  1,
                  '#c4dfc2',
                  10,
                  '#82bc85',
                  100,
                  '#287246',
                ],
                'fill-opacity': 0.86,
              },
            },
            'world-country-boundaries',
          );
          map.addLayer({
            id: 'world-admin1-hit',
            type: 'fill',
            source: 'world-regions',
            'source-layer': 'regions',
            minzoom: 1.7,
            paint: { 'fill-color': '#ffffff', 'fill-opacity': 0.005 },
          });
          map.addLayer({
            id: 'world-admin1-boundaries',
            type: 'line',
            source: 'world-regions',
            'source-layer': 'regions',
            minzoom: 1.7,
            paint: {
              'line-color': '#738276',
              'line-width': [
                'interpolate',
                ['linear'],
                ['zoom'],
                2,
                0.15,
                6,
                0.8,
              ],
              'line-opacity': [
                'interpolate',
                ['linear'],
                ['zoom'],
                2,
                0.4,
                6,
                0.85,
              ],
            },
          });
          map.on('click', 'world-countries-fill', selectCountry);
          map.on('click', 'world-admin1-hit', selectRegion);
          for (const layer of ['world-countries-fill', 'world-admin1-hit']) {
            map.on('mouseenter', layer, () => {
              if (map) map.getCanvas().style.cursor = 'pointer';
            });
            map.on('mouseleave', layer, () => {
              if (map) map.getCanvas().style.cursor = '';
            });
          }
          map.on('sourcedata', (event) => {
            if (event.sourceId === 'world-regions' && event.isSourceLoaded) {
              applyCoverage();
            }
            if (
              event.sourceId === 'brazil-municipalities' &&
              event.isSourceLoaded
            ) {
              brazilReady = true;
              applyCoverage();
            }
          });
          map.on('error', (event) => {
            if (event.error.message.includes('world-')) mapFailed = true;
          });
          mapLoaded = true;
          useBasemap(basemap);
          if (vm.coverage.isError) mapFailed = true;
        });
        map.on('error', (event) => {
          if (event.error.message.includes('WebGL')) mapFailed = true;
        });
      } catch {
        mapFailed = true;
      }
    })();
    return () => {
      cancelled = true;
      map?.remove();
      map = undefined;
    };
  });
</script>

<section class="map-card card" aria-labelledby="coverage-map-heading">
  <div class="map-heading">
    <div>
      <p class="eyebrow">Mapa global</p>
      <h2 id="coverage-map-heading">Explore países e regiões</h2>
      <p class="muted">
        A base mostra países e divisões administrativas de primeiro nível. A
        cobertura detalhada do catálogo está disponível nos territórios que ele
        declara; hoje, o recorte municipal é do Brasil.
      </p>
    </div>
    <label class="check national-toggle">
      <input
        type="checkbox"
        bind:checked={
          () => vm.includeNational, (value) => (vm.includeNational = value)
        }
      />
      Incluir fontes nacionais na cobertura do Brasil
    </label>
  </div>

  <div class="map-toolbar" aria-label="Opções do mapa">
    <fieldset class="map-modes">
      <legend>Camada de base</legend>
      <button
        type="button"
        aria-pressed={basemap === 'borders'}
        onclick={() => useBasemap('borders')}>Bordas</button
      >
      <button
        type="button"
        aria-pressed={basemap === 'relief'}
        onclick={() => useBasemap('relief')}>Relevo</button
      >
      <button
        type="button"
        aria-pressed={basemap === 'satellite'}
        onclick={() => useBasemap('satellite')}>Satélite</button
      >
    </fieldset>
    <button
      class="button"
      type="button"
      onclick={() =>
        setProjection(projection === 'mercator' ? 'globe' : 'mercator')}
    >
      {projection === 'mercator' ? 'Ver globo' : 'Ver mapa 2D'}
    </button>
    <button class="button" type="button" onclick={goToBrazil}
      >Ir ao Brasil</button
    >
    <span class="map-zoom-controls">
      <button
        class="map-control"
        type="button"
        aria-label="Aumentar zoom"
        onclick={() => map?.zoomIn()}>+</button
      >
      <button
        class="map-control"
        type="button"
        aria-label="Diminuir zoom"
        onclick={() => map?.zoomOut()}>−</button
      >
    </span>
  </div>

  <div
    bind:this={mapElement}
    class="world-map"
    aria-label="Mapa interativo mundial de países e regiões administrativas"
    aria-busy={!mapLoaded}
  ></div>

  {#if mapFailed}
    <div class="map-fallback" role="alert">
      <p>
        Não foi possível carregar a visualização interativa. A tabela de
        cobertura continua disponível abaixo.
      </p>
      <button class="button" type="button" onclick={() => location.reload()}
        >Tentar novamente</button
      >
    </div>
  {:else if !mapLoaded}
    <p class="muted map-status" role="status" aria-live="polite">
      Carregando mapa e dados territoriais…
    </p>
  {/if}

  {#if selectedPlace}
    <div class="map-selection" role="status" aria-live="polite">
      <div>
        <strong>{displayText(selectedPlace.name)}</strong>
        {#if selectedPlace.municipalityId && selectedMunicipality}
          <span
            >{number.format(selectedMunicipality.total)}
            {selectedMunicipality.total === 1 ? 'fonte' : 'fontes'} com cobertura
            declarada</span
          >
        {:else if selectedPlace.ufSigla && selectedState}
          <span
            >{number.format(selectedState.total)}
            {selectedState.total === 1 ? 'fonte' : 'fontes'} com cobertura declarada</span
          >
        {:else if selectedPlace.ufSigla}
          <span>Carregando cobertura para a UF selecionada…</span>
        {:else if selectedPlace.countryId === 'BRA'}
          <span
            >Use o zoom sobre o Brasil para ver as divisões municipais e a
            cobertura.</span
          >
        {:else}
          <span
            >O catálogo não declara cobertura subnacional estruturada para esta
            região.</span
          >
        {/if}
      </div>
      {#if selectedMunicipality}
        <button
          class="button primary"
          type="button"
          onclick={() => openMunicipality(selectedMunicipality)}
          >Abrir fontes</button
        >
      {:else if selectedState}
        <button
          class="button primary"
          type="button"
          onclick={() => openState(selectedState)}>Abrir fontes</button
        >
      {/if}
    </div>
  {/if}

  <div class="map-caption">
    <span
      >{coverage
        ? `${number.format(municipalities.length)} municípios brasileiros com dados consultáveis`
        : 'Cobertura do catálogo'}</span
    >
    <span class="map-legend"><i></i> Sem cobertura <i></i> Mais fontes</span>
  </div>
  <p class="map-attribution">
    Limites e relevo: <a
      href={naturalEarthUrl}
      target="_blank"
      rel="noopener noreferrer">Natural Earth, domínio público</a
    >
    · Municípios do Brasil:
    <a
      href="https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/"
      target="_blank"
      rel="noopener noreferrer">IBGE, DTB 2025</a
    >.
    {#if basemap === 'satellite'}
      Imagem: <a
        href={vm.satellite.attributionUrl}
        target="_blank"
        rel="noopener noreferrer">{vm.satellite.attribution}</a
      >
      (composição Terra/MODIS, {vm.satellite.tiles[0].split('/')[8]}). We
      acknowledge the use of imagery provided by services from NASA's Global
      Imagery Browse Services (GIBS), part of NASA's Earth Science Data and
      Information System (ESDIS).
    {/if}
  </p>

  {#if coverage}
    <details class="map-table-details">
      <summary>Consultar a cobertura brasileira em tabela</summary>
      <h3>Fontes por UF</h3>
      <div class="table-scroll">
        <table class="results">
          <caption class="sr-only">Fontes por unidade da federação</caption>
          <thead
            ><tr
              ><th scope="col">UF</th><th scope="col">Sigla</th><th scope="col"
                >Fontes</th
              ></tr
            ></thead
          ><tbody>
            {#each states as item (item.id)}
              <tr>
                <th scope="row">{item.nome}</th>
                <td>{item.sigla}</td>
                <td
                  ><a
                    href={sources({
                      uf: item.id,
                      nacional: vm.includeNational ? '1' : '',
                    })}>{number.format(item.total)}</a
                  ></td
                >
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
      <h3>Detalhe por município</h3>
      <div class="field map-table-search">
        <label for="map-table-search">Filtrar municípios</label>
        <input
          id="map-table-search"
          type="search"
          bind:value={search}
          oninput={() => (tableLimit = 50)}
        />
      </div>
      <div class="table-scroll">
        <table class="results">
          <caption class="sr-only">Fontes por município brasileiro</caption>
          <thead
            ><tr
              ><th scope="col">Município</th><th scope="col">UF</th><th
                scope="col">Fontes</th
              ></tr
            ></thead
          >
          <tbody>
            {#each filteredMunicipalities as item (item.id)}
              <tr>
                <th scope="row">{item.nome}</th>
                <td>{item.uf_sigla}</td>
                <td
                  ><a
                    href={sources({
                      uf: item.uf,
                      municipio: item.id,
                      nacional: vm.includeNational ? '1' : '',
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
      {#if filteredMunicipalities.length === tableLimit}
        <button class="button" type="button" onclick={() => (tableLimit += 100)}
          >Mostrar mais municípios</button
        >
      {/if}
    </details>
  {:else if vm.coverage.isError}
    <LoadState
      failed={vm.coverage.isError}
      retry={() => void vm.coverage.refetch()}
    />
  {:else}
    <p class="muted" role="status">Carregando os dados de cobertura…</p>
  {/if}
</section>

<style>
  .map-toolbar,
  .map-heading,
  .map-selection,
  .map-caption {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
  }
  .map-toolbar {
    flex-wrap: wrap;
    margin: 1rem 0;
  }
  .map-modes {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin: 0;
    padding: 0;
    border: 0;
  }
  .map-modes legend {
    float: left;
    margin: 0 0.5rem 0 0;
    padding-top: 0.55rem;
    color: var(--muted);
    font-size: 0.85rem;
  }
  .map-modes button {
    padding: 0.5rem 0.8rem;
    border: 1px solid var(--border);
    border-radius: 999px;
    background: var(--surface);
    color: var(--text);
    cursor: pointer;
  }
  .map-modes button[aria-pressed='true'] {
    border-color: var(--accent);
    background: var(--accent-soft);
    color: var(--accent-strong);
  }
  .map-zoom-controls {
    display: inline-flex;
    gap: 0.35rem;
  }
  .map-control {
    min-width: 2.2rem;
    min-height: 2.2rem;
    border: 1px solid var(--border);
    border-radius: 0.55rem;
    background: var(--surface);
    color: var(--text);
    font-size: 1.2rem;
    cursor: pointer;
  }
  .world-map {
    width: 100%;
    height: clamp(24rem, 58vw, 42rem);
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: 0.9rem;
    background: #e8ece5;
  }
  .world-map :global(.maplibregl-canvas) {
    outline: none;
  }
  .world-map :global(.maplibregl-ctrl-attrib) {
    font-size: 0.7rem;
  }
  .map-selection {
    margin-top: 0.8rem;
    padding: 0.85rem 1rem;
    border: 1px solid var(--border);
    border-radius: 0.75rem;
    background: var(--surface-muted);
  }
  .map-selection div {
    display: grid;
    gap: 0.2rem;
  }
  .map-selection span,
  .map-caption,
  .map-attribution,
  .map-status {
    color: var(--muted);
    font-size: 0.85rem;
  }
  .map-caption {
    justify-content: flex-start;
    flex-wrap: wrap;
    margin-top: 0.7rem;
  }
  .map-legend {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
  }
  .map-legend i {
    width: 0.8rem;
    height: 0.8rem;
    border: 1px solid #718475;
    background: #edf1e7;
  }
  .map-legend i + i {
    background: #287246;
  }
  .map-attribution {
    margin: 0.65rem 0 0;
  }
  .map-fallback {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.75rem;
  }
  .map-table-search {
    max-width: 24rem;
    margin: 1rem 0;
  }
  .national-toggle {
    max-width: 24rem;
  }
  @media (max-width: 700px) {
    .map-heading,
    .map-selection {
      align-items: flex-start;
      flex-direction: column;
    }
    .map-toolbar {
      align-items: flex-start;
    }
    .map-modes {
      width: 100%;
    }
    .map-modes legend {
      float: none;
      width: 100%;
      padding: 0;
    }
    .world-map {
      height: 26rem;
    }
  }
</style>

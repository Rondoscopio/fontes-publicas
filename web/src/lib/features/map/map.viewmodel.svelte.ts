import { createQuery } from '@tanstack/svelte-query';
import { CATALOG_USE_CASES, GEOGRAPHY_USE_CASES } from '$lib/app/tokens';
import { getAppContainer } from '$lib/app/container-context.svelte';
import type { CatalogUseCases } from '$lib/features/catalog/application/catalog-use-cases';
import type { GeographyUseCases } from './application/geography-use-cases';

function latestAvailableDate() {
  const date = new Date();
  date.setUTCDate(date.getUTCDate() - 2);
  return date.toISOString().slice(0, 10);
}

export function createMapViewModel() {
  const container = getAppContainer();
  const catalog = container.get<CatalogUseCases>(CATALOG_USE_CASES);
  const geography = container.get<GeographyUseCases>(GEOGRAPHY_USE_CASES);
  const assets = geography.assets();
  const satellite = geography.satelliteLayer(latestAvailableDate());

  let includeNational = $state(false);
  const coverage = createQuery(() => ({
    queryKey: ['catalog', 'coverage-map'],
    queryFn: () => catalog.coverageMap(),
  }));

  return {
    assets,
    satellite,
    coverage,
    get includeNational() {
      return includeNational;
    },
    set includeNational(value: boolean) {
      includeNational = value;
    },
  };
}

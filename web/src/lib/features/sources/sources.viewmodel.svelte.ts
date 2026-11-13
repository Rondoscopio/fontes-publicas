import { createQuery } from '@tanstack/svelte-query';
import { CATALOG_USE_CASES } from '$lib/app/tokens';
import { getAppContainer } from '$lib/app/container-context.svelte';
import type { CatalogUseCases } from '$lib/features/catalog/application/catalog-use-cases';
import type { Filters } from '$lib/catalog';

export function createSourcesViewModel(
  filters: () => Filters,
  detailId: () => string,
) {
  const catalog = getAppContainer().get<CatalogUseCases>(CATALOG_USE_CASES);
  const options = createQuery(() => ({
    queryKey: ['catalog', 'options'],
    queryFn: () => catalog.options(),
    enabled: !detailId(),
  }));
  const search = createQuery(() => ({
    queryKey: ['catalog', 'search', filters()],
    queryFn: () => catalog.search(filters()),
    enabled: !detailId(),
  }));
  const detail = createQuery(() => ({
    queryKey: ['catalog', 'detail', detailId()],
    queryFn: () => catalog.detail(detailId()),
    enabled: Boolean(detailId()),
  }));
  return { options, search, detail };
}

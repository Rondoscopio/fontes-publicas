import { createQuery } from '@tanstack/svelte-query';
import { CATALOG_USE_CASES } from '$lib/app/tokens';
import { getAppContainer } from '$lib/app/container-context.svelte';
import type { CatalogUseCases } from '$lib/features/catalog/application/catalog-use-cases';
import type { NodeKind } from '$lib/catalog';

export function createGraphViewModel(
  kind: () => NodeKind | '',
  id: () => string,
  offset: () => number,
) {
  const catalog = getAppContainer().get<CatalogUseCases>(CATALOG_USE_CASES);
  const graph = createQuery(() => ({
    queryKey: ['catalog', 'graph', kind(), id(), offset()],
    queryFn: () => catalog.graph(kind() as NodeKind, id(), offset()),
    enabled: Boolean(kind() && id()),
  }));
  return { graph };
}

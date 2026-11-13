import { createQuery } from '@tanstack/svelte-query';
import { CATALOG_USE_CASES } from '$lib/app/tokens';
import { getAppContainer } from '$lib/app/container-context.svelte';
import type { CatalogUseCases } from '$lib/features/catalog/application/catalog-use-cases';

export function createHomeViewModel(isVisible: () => boolean) {
  const catalog = getAppContainer().get<CatalogUseCases>(CATALOG_USE_CASES);
  const dashboard = createQuery(() => ({
    queryKey: ['catalog', 'dashboard'],
    queryFn: () => catalog.dashboard(),
    enabled: isVisible(),
  }));
  return { dashboard };
}

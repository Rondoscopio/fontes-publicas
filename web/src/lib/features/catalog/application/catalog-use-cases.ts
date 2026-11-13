import type { CatalogReader } from '../ports/catalog-reader';

export function createCatalogUseCases(reader: CatalogReader) {
  return {
    options: () => reader.options(),
    dashboard: () => reader.dashboard(),
    coverageMap: (includeNational = false) =>
      reader.coverageMap(includeNational),
    search: (filters: Parameters<CatalogReader['search']>[0]) =>
      reader.search(filters),
    detail: (id: string) => reader.detail(id),
    graph: (
      kind: Parameters<CatalogReader['graph']>[0],
      id: string,
      offset = 0,
    ) => reader.graph(kind, id, offset),
  };
}

export type CatalogUseCases = ReturnType<typeof createCatalogUseCases>;

import { catalogOptions, query } from '$lib/client';
import type { CatalogReader } from '../ports/catalog-reader';

export class WorkerCatalogReader implements CatalogReader {
  options() {
    return catalogOptions();
  }

  dashboard() {
    return query('dashboard');
  }

  coverageMap(includeNational = false) {
    return query('coverageMap', includeNational);
  }

  search(filters: Parameters<CatalogReader['search']>[0]) {
    return query('search', filters);
  }

  detail(id: string) {
    return query('detail', id);
  }

  graph(kind: Parameters<CatalogReader['graph']>[0], id: string, offset = 0) {
    return query('graph', kind, id, offset);
  }
}

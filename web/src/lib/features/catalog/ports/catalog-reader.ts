import type {
  CoverageMap,
  Dashboard,
  Detail,
  Filters,
  Graph,
  NodeKind,
  Options,
  SearchResult,
} from '$lib/catalog';

/** Read-only application port implemented by the SQLite Web Worker adapter. */
export interface CatalogReader {
  options(): Promise<Options>;
  dashboard(): Promise<Dashboard>;
  coverageMap(includeNational?: boolean): Promise<CoverageMap>;
  search(filters: Filters): Promise<SearchResult>;
  detail(id: string): Promise<Detail | null>;
  graph(kind: NodeKind, id: string, offset?: number): Promise<Graph | null>;
}

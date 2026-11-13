export type Item = { id: string; nome: string };
export type CatalogValue = string | number | Uint8Array | null;
export type Count = Item & { total: number };
export type Category = Item & { tipo_classificacao: string };
export type Municipality = Item & { uf: string };
export type MunicipalityCoverage = Municipality & {
  total: number;
  uf_sigla: string;
  nationalIncrement: number;
};
export type StateCoverage = Item & {
  sigla: string;
  total: number;
  nationalIncrement: number;
};
export type Source = Item & {
  descricao: string | null;
  tipo: string | null;
  status_triagem: string | null;
};
export type Filters = {
  q: string;
  categoria: string;
  tipo: string;
  triagem: string;
  uf: string;
  municipio: string;
  lista: string;
  nacional: boolean;
  ordem: 'asc' | 'desc';
  pagina: number;
};
export type Options = {
  categorias: Category[];
  tipos: Item[];
  triagens: Item[];
  ufs: Item[];
  municipios: Municipality[];
  listas: (Item & { categorias: Category[] })[];
};
export type Dashboard = {
  fontes: number;
  categorias: number;
  listas: number;
  porCategoria: Count[];
  porTipo: Count[];
  porUf: Count[];
};
export type CoverageMap = {
  states: StateCoverage[];
  municipalities: MunicipalityCoverage[];
  national: boolean;
};
export type Detail = {
  fonte: Source & Record<string, CatalogValue>;
  categorias: Category[];
  urls: { id: string; nome: string | null; papel: string; url: string }[];
  origens: {
    tipo_origem: string;
    valor_original: string;
    fonte_id: string | null;
    nome: string | null;
  }[];
  abrangencias: {
    papel: string;
    nacional: number;
    internacional: number;
    ufs: Item[];
    municipios: Municipality[];
  }[];
};
export type NodeKind = 'fonte' | 'categoria' | 'origem';
export type GraphNode = Item & { kind: NodeKind };
export type Neighbor = GraphNode & { relacao: string; direction: 'out' | 'in' };
export type Graph = { center: GraphNode; neighbors: Neighbor[]; total: number };
export type SearchResult = {
  total: number;
  page: number;
  items: Source[];
};

export const PAGE_SIZE = 25;
export const GRAPH_LIMIT = 40;

export function fold(value: string) {
  return value
    .normalize('NFD')
    .replace(/\p{M}/gu, '')
    .toLocaleLowerCase('pt-BR');
}

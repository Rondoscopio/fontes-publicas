import type { Database, SqlValue } from 'sql.js';

export type Item = { id: string; nome: string };
export type Count = Item & { total: number };
export type Category = Item & { tipo_classificacao: string };
export type Municipality = Item & { uf: string };
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
export type Detail = {
  fonte: Source & Record<string, SqlValue>;
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
export const PAGE_SIZE = 25;
export const GRAPH_LIMIT = 40;

export function fold(value: string) {
  return value
    .normalize('NFD')
    .replace(/\p{M}/gu, '')
    .toLocaleLowerCase('pt-BR');
}

export function openCatalog(db: Database) {
  db.run('PRAGMA query_only = ON');
  db.create_function('fold', (value: string | null) => fold(value ?? ''));
  const rows = <T>(sql: string, params: SqlValue[] = []): T[] => {
    const statement = db.prepare(sql, params);
    try {
      const result: T[] = [];
      while (statement.step()) result.push(statement.getAsObject() as T);
      return result;
    } finally {
      statement.free();
    }
  };
  const options = (): Options => {
    const categories = rows<Category>(
      'SELECT * FROM categoria ORDER BY fold(nome), id',
    );
    const categoryById = new Map(
      categories.map((category) => [category.id, category]),
    );
    const listCategories = new Map<string, Category[]>();
    for (const link of rows<{ lista_id: string; categoria_id: string }>(
      'SELECT lc.* FROM lista_categoria lc JOIN categoria c ON c.id = lc.categoria_id ORDER BY fold(c.nome), c.id',
    )) {
      const list = listCategories.get(link.lista_id) ?? [];
      list.push(categoryById.get(link.categoria_id)!);
      listCategories.set(link.lista_id, list);
    }
    return {
      categorias: categories,
      tipos: rows<Item>('SELECT id, nome FROM tipo ORDER BY fold(nome), id'),
      triagens: rows<Item>(
        'SELECT DISTINCT status_triagem id, status_triagem nome FROM fonte WHERE status_triagem IS NOT NULL ORDER BY nome',
      ),
      ufs: rows<Item>(
        'SELECT CAST(codigo_ibge AS TEXT) id, nome FROM uf ORDER BY fold(nome)',
      ),
      municipios: rows<Municipality>(
        'SELECT CAST(m.codigo_ibge AS TEXT) id, m.nome, CAST(m.uf_codigo_ibge AS TEXT) uf FROM municipio m ORDER BY fold(m.nome), m.uf_codigo_ibge',
      ),
      listas: rows<Item>(
        'SELECT id, nome FROM lista ORDER BY fold(nome), id',
      ).map((list) => ({
        ...list,
        categorias: listCategories.get(list.id) ?? [],
      })),
    };
  };
  const dashboard = (): Dashboard => {
    const totals = rows<Pick<Dashboard, 'fontes' | 'categorias' | 'listas'>>(`
      SELECT (SELECT COUNT(*) FROM fonte) fontes, (SELECT COUNT(*) FROM categoria) categorias,
             (SELECT COUNT(*) FROM lista) listas
    `)[0];
    return {
      ...totals,
      porCategoria: rows<Count>(`
        SELECT c.id, c.nome, COUNT(DISTINCT fc.fonte_id) total FROM categoria c
        JOIN fonte_categoria fc ON fc.categoria_id = c.id GROUP BY c.id
        ORDER BY total DESC, fold(c.nome), c.id LIMIT 8
      `),
      porTipo: rows<Count>(`
        SELECT t.id, t.nome, COUNT(DISTINCT f.id) total FROM tipo t
        JOIN fonte f ON f.tipo_id = t.id GROUP BY t.id
        ORDER BY total DESC, fold(t.nome), t.id LIMIT 8
      `),
      porUf: rows<Count>(`
        WITH cobertura AS (
          SELECT fa.fonte_id, au.uf_codigo_ibge FROM fonte_abrangencia fa
          JOIN abrangencia_uf au USING (abrangencia_id) WHERE fa.papel = 'cobertura'
          UNION
          SELECT fa.fonte_id, m.uf_codigo_ibge FROM fonte_abrangencia fa
          JOIN abrangencia_municipio am USING (abrangencia_id)
          JOIN municipio m ON m.codigo_ibge = am.municipio_codigo_ibge WHERE fa.papel = 'cobertura'
        )
        SELECT CAST(u.codigo_ibge AS TEXT) id, u.nome, COUNT(DISTINCT c.fonte_id) total
        FROM cobertura c JOIN uf u ON u.codigo_ibge = c.uf_codigo_ibge
        GROUP BY u.codigo_ibge ORDER BY total DESC, fold(u.nome) LIMIT 8
      `),
    };
  };
  const search = (filters: Filters) => {
    const clauses: string[] = [];
    const params: SqlValue[] = [];
    const add = (sql: string, ...values: SqlValue[]) => {
      clauses.push(sql);
      params.push(...values);
    };
    if (filters.q.trim()) {
      const query = fold(filters.q.trim());
      add(
        '(instr(fold(f.nome), ?) > 0 OR instr(fold(f.descricao), ?) > 0)',
        query,
        query,
      );
    }
    if (filters.categoria)
      add(
        'EXISTS (SELECT 1 FROM fonte_categoria fc WHERE fc.fonte_id = f.id AND fc.categoria_id = ?)',
        filters.categoria,
      );
    if (filters.tipo) add('f.tipo_id = ?', filters.tipo);
    if (filters.triagem === 'sem-registro') add('f.status_triagem IS NULL');
    else if (filters.triagem) add('f.status_triagem = ?', filters.triagem);
    if (filters.lista)
      add(
        `
      EXISTS (SELECT 1 FROM lista_categoria WHERE lista_id = ?) AND NOT EXISTS (
        SELECT 1 FROM lista_categoria lc WHERE lc.lista_id = ? AND NOT EXISTS (
          SELECT 1 FROM fonte_categoria fc WHERE fc.fonte_id = f.id AND fc.categoria_id = lc.categoria_id
        )
      )
    `,
        filters.lista,
        filters.lista,
      );
    if (filters.uf || filters.municipio || filters.nacional) {
      const territories: string[] = [];
      const ids: SqlValue[] = [];
      if (filters.municipio) {
        territories.push(`EXISTS (SELECT 1 FROM abrangencia_municipio am JOIN municipio m
          ON m.codigo_ibge = am.municipio_codigo_ibge WHERE am.abrangencia_id = a.id
          AND m.codigo_ibge = ? ${filters.uf ? 'AND m.uf_codigo_ibge = ?' : ''})`);
        ids.push(filters.municipio);
        if (filters.uf) ids.push(filters.uf);
      } else if (filters.uf) {
        territories.push(`EXISTS (SELECT 1 FROM abrangencia_uf au WHERE au.abrangencia_id = a.id AND au.uf_codigo_ibge = ?)
          OR EXISTS (SELECT 1 FROM abrangencia_municipio am JOIN municipio m ON m.codigo_ibge = am.municipio_codigo_ibge
          WHERE am.abrangencia_id = a.id AND m.uf_codigo_ibge = ?)`);
        ids.push(filters.uf, filters.uf);
      }
      if (filters.nacional) territories.push('a.nacional = 1');
      add(
        `EXISTS (SELECT 1 FROM fonte_abrangencia fa JOIN abrangencia a ON a.id = fa.abrangencia_id
        WHERE fa.fonte_id = f.id AND fa.papel = 'cobertura' AND (${territories.join(' OR ')}))`,
        ...ids,
      );
    }
    const where = clauses.length ? 'WHERE ' + clauses.join(' AND ') : '';
    const total = rows<{ total: number }>(
      'SELECT COUNT(*) total FROM fonte f ' + where,
      params,
    )[0].total;
    const page = Math.min(
      filters.pagina,
      Math.max(1, Math.ceil(total / PAGE_SIZE)),
    );
    return {
      total,
      page,
      items: rows<Source>(
        `SELECT f.id, f.nome, f.descricao, f.status_triagem, t.nome tipo
        FROM fonte f LEFT JOIN tipo t ON t.id = f.tipo_id ${where}
        ORDER BY fold(f.nome) ${filters.ordem === 'desc' ? 'DESC' : 'ASC'}, f.id
        LIMIT ? OFFSET ?`,
        [...params, PAGE_SIZE, (page - 1) * PAGE_SIZE],
      ),
    };
  };
  const detail = (id: string): Detail | null => {
    const fonte = rows<Detail['fonte']>(
      `SELECT f.*, t.nome tipo, sv.valor_original validacao FROM fonte f
      LEFT JOIN tipo t ON t.id = f.tipo_id LEFT JOIN status_validacao sv ON sv.id = f.status_validacao_id
      WHERE f.id = ?`,
      [id],
    )[0];
    if (!fonte) return null;
    return {
      fonte,
      categorias: rows<Category>(
        `SELECT c.* FROM fonte_categoria fc JOIN categoria c ON c.id = fc.categoria_id
        WHERE fc.fonte_id = ? ORDER BY fold(c.nome), c.id`,
        [id],
      ),
      urls: rows<Detail['urls'][number]>(
        'SELECT id, nome, papel, url FROM fonte_url WHERE fonte_id = ? ORDER BY ordem, id',
        [id],
      ),
      origens: rows<Detail['origens'][number]>(
        `SELECT fo.tipo_origem, o.valor_original, f.id fonte_id, f.nome
        FROM fonte_origem fo JOIN origem o ON o.id = fo.origem_id LEFT JOIN fonte f ON f.id = o.fonte_referenciada_id
        WHERE fo.fonte_id = ? ORDER BY fo.tipo_origem`,
        [id],
      ),
      abrangencias: rows<
        Omit<Detail['abrangencias'][number], 'ufs' | 'municipios'> & {
          id: string;
        }
      >(
        'SELECT a.*, fa.papel FROM fonte_abrangencia fa JOIN abrangencia a ON a.id = fa.abrangencia_id WHERE fa.fonte_id = ? ORDER BY fa.papel',
        [id],
      ).map((coverage) => ({
        ...coverage,
        ufs: rows<Item>(
          `SELECT CAST(u.codigo_ibge AS TEXT) id, u.nome FROM abrangencia_uf au
          JOIN uf u ON u.codigo_ibge = au.uf_codigo_ibge WHERE au.abrangencia_id = ? ORDER BY fold(u.nome)`,
          [coverage.id],
        ),
        municipios: rows<Municipality>(
          `SELECT CAST(m.codigo_ibge AS TEXT) id, m.nome || ' / ' || u.sigla nome, CAST(u.codigo_ibge AS TEXT) uf
          FROM abrangencia_municipio am JOIN municipio m ON m.codigo_ibge = am.municipio_codigo_ibge
          JOIN uf u ON u.codigo_ibge = m.uf_codigo_ibge WHERE am.abrangencia_id = ? ORDER BY fold(m.nome), u.sigla`,
          [coverage.id],
        ),
      })),
    };
  };
  const graph = (kind: NodeKind, id: string, offset = 0): Graph | null => {
    const tables = {
      fonte: ['fonte', 'nome'],
      categoria: ['categoria', 'nome'],
      origem: ['origem', 'valor_original'],
    };
    const [table, label] = tables[kind];
    const item = rows<Item>(
      `SELECT id, ${label} nome FROM ${table} WHERE id = ?`,
      [id],
    )[0];
    if (!item) return null;
    const queries = {
      fonte: `
        SELECT c.id, c.nome, 'categoria' kind, 'Classificação' relacao, 'out' direction
        FROM fonte_categoria fc JOIN categoria c ON c.id = fc.categoria_id WHERE fc.fonte_id = ?
        UNION
        SELECT COALESCE(f.id, o.id), COALESCE(f.nome, o.valor_original),
               CASE WHEN f.id IS NULL THEN 'origem' ELSE 'fonte' END, 'Origem', 'out'
        FROM fonte_origem fo JOIN origem o ON o.id = fo.origem_id
        LEFT JOIN fonte f ON f.id = o.fonte_referenciada_id WHERE fo.fonte_id = ?
        UNION
        SELECT f.id, f.nome, 'fonte', 'Cita esta fonte', 'in'
        FROM origem o JOIN fonte_origem fo ON fo.origem_id = o.id
        JOIN fonte f ON f.id = fo.fonte_id WHERE o.fonte_referenciada_id = ?
      `,
      categoria: `SELECT f.id, f.nome, 'fonte' kind, 'Classificação' relacao, 'in' direction
        FROM fonte_categoria fc JOIN fonte f ON f.id = fc.fonte_id WHERE fc.categoria_id = ?`,
      origem: `SELECT DISTINCT f.id, f.nome, 'fonte' kind, 'Cita esta origem' relacao, 'in' direction
        FROM fonte_origem fo JOIN fonte f ON f.id = fo.fonte_id WHERE fo.origem_id = ?`,
    };
    const sql = queries[kind];
    const params = kind === 'fonte' ? [id, id, id] : [id];
    const total = rows<{ total: number }>(
      `SELECT COUNT(*) total FROM (${sql})`,
      params,
    )[0].total;
    return {
      center: { ...item, kind },
      total,
      neighbors: rows<Neighbor>(
        `SELECT * FROM (${sql}) ORDER BY fold(nome), kind, id, relacao, direction LIMIT ? OFFSET ?`,
        [...params, GRAPH_LIMIT, offset],
      ),
    };
  };
  return { options, dashboard, search, detail, graph };
}

export type Catalog = ReturnType<typeof openCatalog>;
export type SearchResult = ReturnType<Catalog['search']>;

import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import initSqlJs from 'sql.js';
import { openCatalog, PAGE_SIZE } from '../src/lib/catalog.ts';
import type { Filters } from '../src/lib/catalog.ts';

const sqlite = await initSqlJs();
const file = new URL('../../data/exports/catalog.sqlite', import.meta.url);
const catalog = openCatalog(new sqlite.Database(readFileSync(file)));
const filters: Filters = {
  q: '',
  categoria: '',
  tipo: '',
  triagem: '',
  uf: '',
  municipio: '',
  lista: '',
  nacional: false,
  ordem: 'asc',
  pagina: 1,
};

test('a distribuição real abre, conta fichas e pagina sem repetição', () => {
  const first = catalog.search(filters);
  const next = catalog.search({ ...filters, pagina: 2 });
  assert.ok(first.total > PAGE_SIZE);
  assert.equal(catalog.dashboard().fontes, first.total);
  assert.equal(first.items.length, PAGE_SIZE);
  assert.equal(
    new Set([...first.items, ...next.items].map(({ id }) => id)).size,
    2 * PAGE_SIZE,
  );
  assert.equal(catalog.search({ ...filters, q: "x%' OR 1=1 --" }).total, 0);
  assert.deepEqual(
    catalog.search({ ...filters, q: 'RÔNDÔNIA' }),
    catalog.search({ ...filters, q: 'rondonia' }),
  );
});

test('lista exige todos os temas e grafo reproduz relações da categoria', () => {
  const db = new sqlite.Database(readFileSync(file));
  db.run(`
    INSERT INTO fonte (id, nome) VALUES ('teste-a', 'FONTE TESTE A'), ('teste-b', 'FONTE TESTE B');
    INSERT INTO categoria VALUES ('teste-c1', 'Tema 1', 'principal'), ('teste-c2', 'Tema 2', 'principal');
    INSERT INTO lista VALUES ('teste-lista', 'Lista teste');
    INSERT INTO lista_categoria VALUES ('teste-lista','teste-c1'), ('teste-lista','teste-c2');
    INSERT INTO fonte_categoria VALUES ('teste-a','teste-c1'), ('teste-a','teste-c2'), ('teste-b','teste-c1');
  `);
  const fixture = openCatalog(db);
  assert.deepEqual(
    fixture
      .search({ ...filters, lista: 'teste-lista' })
      .items.map(({ id }) => id),
    ['teste-a'],
  );
  const graph = fixture.graph('categoria', 'teste-c1');
  assert.equal(graph?.total, 2);
  assert.deepEqual(
    graph?.neighbors.map(({ id }) => id),
    ['teste-a', 'teste-b'],
  );
  assert.equal(fixture.detail('teste-a')?.categorias.length, 2);
});

test('cobertura municipal implica UF, localidade declarada fica separada e nacional é opt-in', () => {
  const db = new sqlite.Database(readFileSync(file));
  db.run(`
    INSERT INTO fonte (id, nome) VALUES ('teste-m', 'FONTE TESTE Municipal'), ('teste-n', 'FONTE TESTE Nacional'), ('teste-l', 'FONTE TESTE Localidade');
    INSERT INTO abrangencia VALUES ('teste-a', 0, 0), ('teste-nacional', 1, 0);
    INSERT INTO abrangencia_uf VALUES ('teste-a', 11);
    INSERT INTO abrangencia_municipio VALUES ('teste-a', 1100205);
    INSERT INTO fonte_abrangencia (fonte_id, abrangencia_id, papel) VALUES
      ('teste-m', 'teste-a', 'cobertura'), ('teste-n', 'teste-nacional', 'cobertura'), ('teste-l', 'teste-a', 'localidade_declarada');
  `);
  const fixture = openCatalog(db);
  const territory = { ...filters, q: 'FONTE TESTE', uf: '11' };
  assert.deepEqual(
    fixture.search(territory).items.map(({ id }) => id),
    ['teste-m'],
  );
  assert.deepEqual(
    fixture
      .search({ ...territory, municipio: '1100205' })
      .items.map(({ id }) => id),
    ['teste-m'],
  );
  assert.deepEqual(
    fixture.search({ ...territory, nacional: true }).items.map(({ id }) => id),
    ['teste-m', 'teste-n'],
  );
});

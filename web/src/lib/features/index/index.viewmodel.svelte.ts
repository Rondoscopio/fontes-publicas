import { createQuery } from '@tanstack/svelte-query';
import { CATALOG_USE_CASES } from '$lib/app/tokens';
import { getAppContainer } from '$lib/app/container-context.svelte';
import { fold, PAGE_SIZE, type Category, type Item } from '$lib/catalog';
import type { CatalogUseCases } from '$lib/features/catalog/application/catalog-use-cases';

export type IndexKind = 'categorias' | 'listas' | 'abrangencia';
type Entry = Item & { tipo_classificacao?: string; categorias?: Category[] };

export function createIndexViewModel(getKind: () => IndexKind) {
  const catalog = getAppContainer().get<CatalogUseCases>(CATALOG_USE_CASES);
  const options = createQuery(() => ({
    queryKey: ['catalog', 'options'],
    queryFn: () => catalog.options(),
  }));
  let search = $state('');
  let uf = $state('');
  let municipality = $state('');
  let nationwide = $state(false);
  let limit = $state(PAGE_SIZE);

  const entries = $derived.by((): Entry[] => {
    const data = options.data;
    if (!data) return [];
    if (getKind() === 'categorias') return data.categorias;
    if (getKind() === 'listas') return data.listas;
    return data.ufs;
  });
  const rows = $derived(
    entries.filter((item) => fold(item.nome).includes(fold(search.trim()))),
  );
  const municipalities = $derived(
    (options.data?.municipios ?? [])
      .filter((item) => !uf || item.uf === uf)
      .map((item) => ({
        ...item,
        nome: uf
          ? item.nome
          : item.nome +
            ' / ' +
            (options.data?.ufs.find(({ id }) => id === item.uf)?.nome ?? ''),
      })),
  );

  return {
    options,
    get search() {
      return search;
    },
    set search(value: string) {
      search = value;
      limit = PAGE_SIZE;
    },
    get uf() {
      return uf;
    },
    set uf(value: string) {
      uf = value;
      municipality = '';
    },
    get municipality() {
      return municipality;
    },
    set municipality(value: string) {
      municipality = value;
    },
    get nationwide() {
      return nationwide;
    },
    set nationwide(value: boolean) {
      nationwide = value;
    },
    get rows() {
      return rows;
    },
    get municipalities() {
      return municipalities;
    },
    get visibleRows() {
      return rows.slice(0, limit);
    },
    get hasMore() {
      return rows.length > limit;
    },
    get resultCount() {
      return rows.length;
    },
    loadMore() {
      limit += PAGE_SIZE;
    },
  };
}

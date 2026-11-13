import { resolve } from '$app/paths';
import type { NodeKind } from './catalog';

export function sources(
  values: Record<string, string | number | undefined> = {},
) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(values))
    if (value) params.set(key, String(value));
  return resolve('/fontes/') + (params.size ? '?' + params : '');
}

export function graphLink(kind: NodeKind, id: string, page = 1) {
  const params = new URLSearchParams({ tipo: kind, id });
  if (page > 1) params.set('pagina', String(page));
  return resolve('/grafo/') + '?' + params;
}

export function httpLink(value: string) {
  try {
    const url = new URL(value);
    if (url.protocol === 'https:' || url.protocol === 'http:') return url.href;
  } catch {
    return null;
  }
  return null;
}

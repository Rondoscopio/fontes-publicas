import { asset } from '$app/paths';
import type { Catalog } from './catalog';

export const databaseUrl = () => asset('/' + __CATALOG_FILE__);

let worker: Worker | undefined;
let sequence = 0;
const pending = new Map<
  number,
  { resolve: (value: unknown) => void; reject: (reason: Error) => void }
>();

function getWorker() {
  if (worker) return worker;
  const instance = new Worker(new URL('./catalog.worker.ts', import.meta.url), {
    type: 'module',
  });
  instance.onmessage = ({ data }) => {
    const request = pending.get(data.id);
    if (!request) return;
    pending.delete(data.id);
    if (data.error) request.reject(new Error(data.error));
    else request.resolve(data.result);
  };
  instance.onerror = () => {
    for (const request of pending.values())
      request.reject(new Error('Não foi possível iniciar o catálogo.'));
    pending.clear();
    instance.terminate();
    worker = undefined;
  };
  worker = instance;
  return instance;
}

export function query<K extends keyof Catalog>(
  operation: K,
  ...args: Parameters<Catalog[K]>
): Promise<ReturnType<Catalog[K]>> {
  const instance = getWorker();
  const id = ++sequence;
  return new Promise((resolve, reject) => {
    pending.set(id, {
      resolve: (value) => resolve(value as ReturnType<Catalog[K]>),
      reject,
    });
    instance.postMessage({
      id,
      url: new URL(databaseUrl(), location.href).href,
      operation,
      args,
    });
  });
}

let options: ReturnType<typeof query<'options'>> | undefined;
export function catalogOptions() {
  options ??= query('options').catch((error: unknown) => {
    options = undefined;
    throw error;
  });
  return options;
}

import { PMTiles, Protocol } from 'pmtiles';

type MapLibreRuntime = typeof import('maplibre-gl');

const protocol = new Protocol();
let registered = false;
const registeredArchives = new Set<string>();

export function registerPmtiles(
  maplibre: MapLibreRuntime,
  archiveUrls: string[],
): string[] {
  if (!registered) {
    maplibre.addProtocol('pmtiles', protocol.tile);
    registered = true;
  }

  return archiveUrls.map((path) => {
    const url = new URL(path, window.location.href).href;
    if (!registeredArchives.has(url)) {
      protocol.add(new PMTiles(url));
      registeredArchives.add(url);
    }
    return `pmtiles://${url}`;
  });
}

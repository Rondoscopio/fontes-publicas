import type { GeographyReader } from '../ports/geography-reader';

export function createGeographyUseCases(reader: GeographyReader) {
  return {
    assets: () => reader.assets(),
    satelliteLayer: (date: string) => reader.satelliteLayer(date),
  };
}

export type GeographyUseCases = ReturnType<typeof createGeographyUseCases>;

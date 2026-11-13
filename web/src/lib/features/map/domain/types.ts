export type Basemap = 'borders' | 'relief' | 'satellite';
export type Projection = 'mercator' | 'globe';

export type MapAssets = {
  worldTilesUrl: string;
  brazilMunicipalityTilesUrl: string;
  reliefImageUrl: string;
};

export type SatelliteLayer = {
  tiles: string[];
  attribution: string;
  attributionUrl: string;
  maxzoom: number;
  tileSize: number;
};

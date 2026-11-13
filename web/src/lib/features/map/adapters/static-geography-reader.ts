import { asset } from '$app/paths';
import type { MapAssets, SatelliteLayer } from '../domain/types';
import type { GeographyReader } from '../ports/geography-reader';

export class StaticGeographyReader implements GeographyReader {
  assets(): MapAssets {
    return {
      worldTilesUrl: asset('/maps/world.pmtiles'),
      brazilMunicipalityTilesUrl: asset('/maps/municipios-brasil.pmtiles'),
      reliefImageUrl: asset('/maps/world-relief.webp'),
    };
  }

  satelliteLayer(date: string): SatelliteLayer {
    return {
      tiles: [
        `https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/${date}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg`,
      ],
      attribution: 'NASA GIBS',
      attributionUrl: 'https://worldview.earthdata.nasa.gov/',
      maxzoom: 9,
      tileSize: 256,
    };
  }
}

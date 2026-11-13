import { execFileSync } from 'node:child_process';
import { stat, unlink } from 'node:fs/promises';

const inputDirectory = '/cache/build';
const outputDirectory = '/output/maps';

async function buildArchive({ name, minZoom, maxZoom, layers }) {
  const mbtilesPath = `${inputDirectory}/${name}.mbtiles`;
  const pmtilesPath = `${outputDirectory}/${name}.pmtiles`;
  const args = [
    '--force',
    `--output=${mbtilesPath}`,
    `--minimum-zoom=${minZoom}`,
    `--maximum-zoom=${maxZoom}`,
    '--no-feature-limit',
    '--no-tile-size-limit',
    '--read-parallel',
  ];
  for (const layer of layers) {
    args.push('-L', JSON.stringify(layer));
  }
  execFileSync('tippecanoe', args, { stdio: 'inherit' });
  execFileSync('pmtiles', ['convert', mbtilesPath, pmtilesPath], {
    stdio: 'inherit',
  });
  const result = await stat(pmtilesPath);
  if (result.size < 1024) {
    throw new Error(
      `${name}.pmtiles ficou menor que o cabeçalho mínimo esperado.`,
    );
  }
  execFileSync('pmtiles', ['show', pmtilesPath], { stdio: 'inherit' });
  console.log(`${pmtilesPath}: ${result.size} bytes`);
}

for (const obsolete of [
  'municipios-brasil.geojson',
  'world-countries.geojson',
  'world-regions.geojson',
  'municipios-brasil.topojson',
]) {
  try {
    await unlink(`${outputDirectory}/${obsolete}`);
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
  }
}

await buildArchive({
  name: 'world',
  minZoom: 0,
  maxZoom: 8,
  layers: [
    {
      file: `${inputDirectory}/world-countries.geojson`,
      layer: 'countries',
    },
    {
      file: `${inputDirectory}/world-regions.geojson`,
      layer: 'regions',
    },
  ],
});

await buildArchive({
  name: 'municipios-brasil',
  minZoom: 3,
  maxZoom: 9,
  layers: [
    {
      file: `${inputDirectory}/municipios-brasil.geojson`,
      layer: 'municipios',
    },
  ],
});

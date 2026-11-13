import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { createReadStream, createWriteStream } from 'node:fs';
import { mkdir, readFile, stat, unlink, writeFile } from 'node:fs/promises';
import { Readable } from 'node:stream';
import { pipeline } from 'node:stream/promises';
import AdmZip from 'adm-zip';
import mapshaper from 'mapshaper';
import sharp from 'sharp';

const manifest = JSON.parse(
  await readFile('/workspace/.config/geodata/world-2025.json', 'utf8'),
);
const cacheDirectory = '/cache/natural-earth';
const buildDirectory = '/cache/build';
const outputDirectory = '/output/maps';
await mkdir(cacheDirectory, { recursive: true });
await mkdir(buildDirectory, { recursive: true });
await mkdir(outputDirectory, { recursive: true });

async function ensureDownload(source) {
  const archivePath = `${cacheDirectory}/${source.name}.zip`;
  try {
    await stat(archivePath);
  } catch {
    const response = await fetch(source.source_url, { redirect: 'follow' });
    if (!response.ok || !response.body) {
      throw new Error(
        `Download Natural Earth (${source.name}) falhou: HTTP ${response.status}.`,
      );
    }
    await pipeline(
      Readable.fromWeb(response.body),
      createWriteStream(archivePath),
    );
  }
  const digest = createHash('sha256');
  for await (const chunk of createReadStream(archivePath)) digest.update(chunk);
  const actualSha256 = digest.digest('hex');
  if (source.sha256 === 'TO_FILL') {
    console.log(`${source.name}.sha256=${actualSha256}`);
  } else if (actualSha256 !== source.sha256) {
    throw new Error(
      `SHA-256 de ${source.name} diverge: ${actualSha256}; esperado ${source.sha256}.`,
    );
  }
  return archivePath;
}

const sources = await Promise.all(
  manifest.sources.map(async (source) => ({
    source,
    archivePath: await ensureDownload(source),
  })),
);
const unpinned = sources.filter(({ source }) => source.sha256 === 'TO_FILL');
if (unpinned.length) {
  throw new Error(
    `Registre os hashes SHA-256 impressos em .config/geodata/world-2025.json e execute novamente.`,
  );
}

function findValue(properties, names) {
  const values = new Map(
    Object.entries(properties).map(([key, value]) => [
      key.toLowerCase(),
      value,
    ]),
  );
  for (const name of names) {
    const value = values.get(name.toLowerCase());
    if (value !== undefined && value !== null && String(value).trim()) {
      return String(value).trim();
    }
  }
  return null;
}

async function extractShapefile(archivePath, shapefile) {
  const archive = new AdmZip(archivePath);
  const prefix = shapefile.slice(0, -4).toLowerCase();
  const directory = `${cacheDirectory}/${prefix}`;
  await mkdir(directory, { recursive: true });
  for (const entry of archive.getEntries()) {
    const name = entry.entryName.split('/').at(-1);
    if (!name || !name.toLowerCase().startsWith(prefix + '.')) continue;
    if (!/\.(shp|shx|dbf|prj|cpg)$/iu.test(name)) continue;
    await writeFile(`${directory}/${name}`, entry.getData());
  }
  return `${directory}/${shapefile}`;
}

const countrySource = sources.find(({ source }) => source.name === 'countries');
const regionSource = sources.find(({ source }) => source.name === 'regions');
const reliefSource = sources.find(({ source }) => source.name === 'relief');
if (!countrySource || !regionSource || !reliefSource) {
  throw new Error('O manifesto precisa declarar países, regiões e relevo.');
}

const countryIntermediate = `${cacheDirectory}/countries.geojson`;
const countryShapefile = await extractShapefile(
  countrySource.archivePath,
  countrySource.source.shapefile,
);
await mapshaper.runCommands(
  `-i "${countryShapefile}" -simplify dp ${countrySource.source.simplify} keep-shapes -o format=geojson precision=0.001 "${countryIntermediate}"`,
);
const countryCollection = JSON.parse(
  await readFile(countryIntermediate, 'utf8'),
);
if (countryCollection.type !== 'FeatureCollection') {
  throw new Error('A saída de países não é um GeoJSON FeatureCollection.');
}
const countryAliases = new Map();
const countries = countryCollection.features.map((feature) => {
  const properties = feature.properties ?? {};
  const id = findValue(properties, ['ADM0_A3', 'SOV_A3', 'ISO_A3']);
  const name = findValue(properties, [
    'ADMIN',
    'NAME_EN',
    'NAME',
    'SOVEREIGNT',
  ]);
  if (!id || !name) {
    throw new Error('País sem código ou nome na malha Natural Earth.');
  }
  for (const alias of [
    id,
    findValue(properties, ['SOV_A3']),
    findValue(properties, ['ISO_A3']),
    findValue(properties, ['ADM0_A3_US']),
    findValue(properties, ['BRK_A3']),
  ]) {
    if (alias) countryAliases.set(alias, id);
  }
  return {
    ...feature,
    id,
    properties: {
      map_id: id,
      name,
      iso_a3: findValue(properties, ['ISO_A3']) ?? id,
      continent: findValue(properties, ['CONTINENT']),
    },
  };
});
const countryIds = countries.map((feature) => feature.id);
if (
  countries.length < countrySource.source.minimum_features ||
  new Set(countryIds).size !== countries.length
) {
  throw new Error(
    `Países Natural Earth inválidos: ${countries.length} feições, ${new Set(countryIds).size} IDs únicos.`,
  );
}

const regionIntermediate = `${cacheDirectory}/regions.geojson`;
const regionShapefile = await extractShapefile(
  regionSource.archivePath,
  regionSource.source.shapefile,
);
await mapshaper.runCommands(
  `-i "${regionShapefile}" -simplify dp ${regionSource.source.simplify} keep-shapes -o format=geojson precision=0.001 "${regionIntermediate}"`,
);
const regionCollection = JSON.parse(await readFile(regionIntermediate, 'utf8'));
if (regionCollection.type !== 'FeatureCollection') {
  throw new Error('A saída de regiões não é um GeoJSON FeatureCollection.');
}
const regions = regionCollection.features.map((feature) => {
  const properties = feature.properties ?? {};
  const rawCountry = findValue(properties, ['ADM0_A3', 'SOV_A3', 'ISO_A3']);
  const rawId = findValue(properties, ['ADM1_CODE', 'ADM1_CODE_ALT', 'GNS_ID']);
  const name =
    findValue(properties, ['NAME', 'NAME_EN', 'NAME_LOCAL']) ?? rawId;
  const id = rawCountry && rawId ? `${rawCountry}:${rawId}` : rawId;
  const iso3166_2 = findValue(properties, ['ISO_3166_2']);
  const countryId = rawCountry
    ? (countryAliases.get(rawCountry) ?? rawCountry)
    : null;
  if (!id || !name) {
    throw new Error('Divisão administrativa sem código ou nome estável.');
  }
  return {
    ...feature,
    id,
    properties: {
      map_id: id,
      name,
      country_id: countryId,
      country_name: findValue(properties, ['ADMIN', 'SOVEREIGNT']),
      iso_3166_2: iso3166_2,
      uf_sigla:
        countryId === 'BRA' && iso3166_2?.startsWith('BR-')
          ? iso3166_2.slice(3)
          : null,
      type: findValue(properties, ['TYPE_EN', 'TYPE']),
    },
  };
});
const regionIds = regions.map((feature) => feature.id);
if (
  regions.length < regionSource.source.minimum_features ||
  new Set(regionIds).size !== regions.length
) {
  throw new Error(
    `Regiões Natural Earth inválidas: ${regions.length} feições, ${new Set(regionIds).size} IDs únicos.`,
  );
}
const brazilUfCodes = regions
  .filter((feature) => feature.properties.country_id === 'BRA')
  .map((feature) => feature.properties.uf_sigla)
  .filter(Boolean);
if (brazilUfCodes.length !== 27 || new Set(brazilUfCodes).size !== 27) {
  throw new Error(
    `Natural Earth precisa identificar 27 UFs brasileiras por ISO 3166-2; encontrou ${brazilUfCodes.length} códigos e ${new Set(brazilUfCodes).size} únicos.`,
  );
}

for (const [collection, source] of [
  [{ type: 'FeatureCollection', features: countries }, countrySource],
  [{ type: 'FeatureCollection', features: regions }, regionSource],
]) {
  await writeFile(
    `${buildDirectory}/${source.source.output}`,
    JSON.stringify(collection) + '\n',
  );
}

const reliefArchive = new AdmZip(reliefSource.archivePath);
const rasterEntry = reliefArchive
  .getEntries()
  .find((entry) => /\.(tif|tiff|png|jpe?g)$/iu.test(entry.entryName));
if (!rasterEntry) {
  throw new Error('O pacote de relevo Natural Earth não contém imagem raster.');
}
const sourceRasterPath = `${cacheDirectory}/relief-source.tif`;
const projectedRasterPath = `${buildDirectory}/world-relief-3857.tif`;
await writeFile(sourceRasterPath, rasterEntry.getData());
const webMercatorLimit = 20037508.342789244;
execFileSync(
  'gdalwarp',
  [
    '-overwrite',
    '-t_srs',
    'EPSG:3857',
    '-te',
    String(-webMercatorLimit),
    String(-webMercatorLimit),
    String(webMercatorLimit),
    String(webMercatorLimit),
    '-ts',
    '4096',
    '4096',
    '-r',
    'bilinear',
    '-wm',
    '128',
    '-wo',
    'NUM_THREADS=2',
    '-co',
    'COMPRESS=DEFLATE',
    '-co',
    'PREDICTOR=2',
    '-co',
    'TILED=YES',
    sourceRasterPath,
    projectedRasterPath,
  ],
  { stdio: 'inherit' },
);
const projectedRelief = sharp(projectedRasterPath);
const projectedMetadata = await projectedRelief.metadata();
if (projectedMetadata.width !== 4096 || projectedMetadata.height !== 4096) {
  throw new Error(
    `O relevo reprojetado deveria medir 4096×4096; recebeu ${projectedMetadata.width}×${projectedMetadata.height}.`,
  );
}
const reliefPath = `${outputDirectory}/${reliefSource.source.output}`;
await projectedRelief.webp({ quality: 82, effort: 5 }).toFile(reliefPath);
await Promise.all([unlink(sourceRasterPath), unlink(projectedRasterPath)]);

console.log(
  `Gerados ${countries.length} países, ${regions.length} regiões Admin-1 e relevo Natural Earth reprojetado para EPSG:3857 (${manifest.edition}).`,
);

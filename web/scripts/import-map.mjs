import { createHash } from 'node:crypto';
import { createReadStream, createWriteStream } from 'node:fs';
import { mkdir, readFile, stat, writeFile } from 'node:fs/promises';
import { Readable, Transform } from 'node:stream';
import { pipeline } from 'node:stream/promises';
import AdmZip from 'adm-zip';
import mapshaper from 'mapshaper';

const manifest = JSON.parse(
  await readFile('/workspace/.config/geodata/municipios-2025.json', 'utf8'),
);
const archivePath = '/cache/BR_Municipios_2025.zip';
const sourceIds = new Set(
  (await readFile('/input/municipio.csv', 'utf8'))
    .split(/\r?\n/u)
    .slice(1)
    .filter(Boolean)
    .map((row) => row.split(',', 1)[0]),
);

if (sourceIds.size !== manifest.expected_features) {
  throw new Error(
    `municipio.csv tem ${sourceIds.size} IDs; esperado ${manifest.expected_features}.`,
  );
}

try {
  await stat(archivePath);
} catch {
  const response = await fetch(manifest.source_url, { redirect: 'follow' });
  if (!response.ok || !response.body) {
    throw new Error(`Download do IBGE falhou: HTTP ${response.status}.`);
  }
  await mkdir('/cache', { recursive: true });
  await pipeline(
    Readable.fromWeb(response.body),
    createWriteStream(archivePath),
  );
}

const digest = createHash('sha256');
await pipeline(
  createReadStream(archivePath),
  new Transform({
    transform(chunk, _encoding, callback) {
      digest.update(chunk);
      callback(null, chunk);
    },
  }),
  new Transform({
    transform(_chunk, _encoding, callback) {
      callback();
    },
  }),
);
const actualSha256 = digest.digest('hex');
if (manifest.sha256 === 'TO_FILL_AFTER_DOWNLOAD') {
  throw new Error(
    `Download concluído. Registre este SHA-256 no manifesto: ${actualSha256}`,
  );
}
if (actualSha256 !== manifest.sha256) {
  throw new Error(
    `SHA-256 da malha diverge: ${actualSha256}; esperado ${manifest.sha256}.`,
  );
}

const shapefileDirectory = '/cache/ibge-municipios-2025';
await mkdir(shapefileDirectory, { recursive: true });
const archive = new AdmZip(archivePath);
for (const extension of ['shp', 'shx', 'dbf', 'prj', 'cpg']) {
  const name = `BR_Municipios_2025.${extension}`;
  const entry = archive.getEntry(name);
  if (!entry)
    throw new Error(`Arquivo ${name} ausente no pacote oficial do IBGE.`);
  await writeFile(`${shapefileDirectory}/${name}`, entry.getData());
}

const outputPath = '/output/maps/municipios-brasil.topojson';
await mkdir('/output/maps', { recursive: true });
await mapshaper.runCommands(
  `-i "${shapefileDirectory}/BR_Municipios_2025.shp" -simplify dp 5% keep-shapes -filter-fields CD_MUN -o format=topojson "${outputPath}"`,
);

const generated = JSON.parse(await readFile(outputPath, 'utf8'));
const [objectName, object] = Object.entries(generated.objects)[0] ?? [];
if (!object || object.type !== 'GeometryCollection') {
  throw new Error('A saída do IBGE não contém uma coleção municipal TopoJSON.');
}
object.geometries = object.geometries.filter((geometry) =>
  sourceIds.has(String(geometry.properties?.CD_MUN ?? geometry.id ?? '')),
);
const ids = object.geometries.map((geometry) =>
  String(geometry.properties?.CD_MUN ?? geometry.id ?? ''),
);
const uniqueIds = new Set(ids);
const missing = [...sourceIds].filter((id) => !uniqueIds.has(id));
const unexpected = ids.filter((id) => !sourceIds.has(id));
if (
  ids.length !== manifest.expected_features ||
  uniqueIds.size !== ids.length ||
  missing.length ||
  unexpected.length
) {
  throw new Error(
    `Geometrias inconsistentes: ${ids.length} total, ${uniqueIds.size} únicas, ${missing.length} ausentes e ${unexpected.length} extras.`,
  );
}
for (const geometry of object.geometries) {
  geometry.id = String(geometry.properties.CD_MUN);
  geometry.properties = { codigo_ibge: geometry.id };
}
generated.objects = { municipios: object };
await writeFile(outputPath, JSON.stringify(generated) + '\n');
console.log(
  `Geradas ${ids.length} geometrias simplificadas (${objectName}) a partir da malha IBGE 2025; SHA-256 ${actualSha256}.`,
);

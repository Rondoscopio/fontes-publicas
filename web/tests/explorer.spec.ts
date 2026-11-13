import { expect, test } from '@playwright/test';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import sharp from 'sharp';

test('início, marca, mapa global, gráficos e SQLite idêntico ao catálogo', async ({
  page,
  request,
}) => {
  const html = await request.get('./');
  expect(html.ok()).toBe(true);
  expect(await html.text()).toContain('Fontes abertas');
  await page.goto('./');
  await expect(
    page.getByRole('link', { name: 'Rondoscópio — OSINT Rondônia, início' }),
  ).toBeVisible();
  const commitLink = page.getByRole('link', { name: 'Commit 0123456' });
  await expect(commitLink).toHaveAttribute(
    'href',
    'https://github.com/Rondoscopio/osint-rondonia/commit/0123456789abcdef0123456789abcdef01234567',
  );
  await expect(commitLink).toHaveAttribute('target', '_blank');
  await expect(commitLink).toHaveAttribute('rel', 'noopener noreferrer');
  const buildLink = page.getByRole('link', { name: 'Build #42' });
  await expect(buildLink).toHaveAttribute(
    'href',
    'https://github.com/Rondoscopio/osint-rondonia/actions/runs/4242',
  );
  await expect(buildLink).toHaveAttribute('target', '_blank');
  await expect(buildLink).toHaveAttribute('rel', 'noopener noreferrer');
  await expect(
    page.getByRole('navigation', { name: 'Navegação do catálogo' }),
  ).toBeVisible();
  await page.locator('.home-dashboard').scrollIntoViewIfNeeded();
  await expect(
    page.getByRole('heading', { name: 'Explore países e regiões' }),
  ).toBeVisible();
  await page.getByRole('button', { name: 'Carregar mapa interativo' }).click();
  await expect(page.locator('.world-map canvas')).toBeVisible({
    timeout: 30000,
  });
  const icon = page.locator('link[rel="icon"]');
  const iconResponse = await request.get(
    new URL((await icon.getAttribute('href'))!, page.url()).href,
  );
  expect(iconResponse.ok()).toBe(true);
  await expect(
    page.getByRole('heading', { name: 'Como o catálogo se distribui' }),
  ).toBeVisible();
  await page.getByText('Ver tabela').first().click();
  await expect(page.getByRole('table', { name: 'Categorias' })).toBeVisible();
  const link = page.getByRole('link', { name: 'SQLite' });
  const response = await request.get(
    new URL((await link.getAttribute('href'))!, page.url()).href,
  );
  expect(response.ok()).toBe(true);
  const hash = (data: Buffer) =>
    createHash('sha256').update(data).digest('hex');
  expect(hash(await response.body())).toBe(
    hash(
      readFileSync(
        new URL('../../data/exports/catalog.sqlite', import.meta.url),
      ),
    ),
  );
});

test('mapa alterna projeção e camadas e mantém cobertura municipal acessível', async ({
  page,
}) => {
  const workerResponses: Array<{
    url: string;
    status: number;
    contentType: string;
  }> = [];
  const mapResponses: Array<{ url: string; status: number }> = [];
  const mapErrors: string[] = [];
  page.on('response', (response) => {
    if (response.url().includes('maplibre-gl-worker')) {
      workerResponses.push({
        url: response.url(),
        status: response.status(),
        contentType: response.headers()['content-type'] ?? '',
      });
    }
    if (response.url().includes('/maps/world.pmtiles')) {
      mapResponses.push({ url: response.url(), status: response.status() });
    }
  });
  page.on('pageerror', (error) => mapErrors.push(error.message));
  page.on('console', (message) => {
    if (message.type() === 'error') mapErrors.push(message.text());
  });
  page.on('requestfailed', (request) => {
    if (request.url().includes('maplibre-gl-worker')) {
      mapErrors.push(`${request.url()}: ${request.failure()?.errorText}`);
    }
  });
  await page.goto('./');
  await page.locator('.home-dashboard').scrollIntoViewIfNeeded();
  await expect(
    page.getByRole('heading', { name: 'Explore países e regiões' }),
  ).toBeVisible();
  await page.getByRole('button', { name: 'Carregar mapa interativo' }).click();
  await expect(page.locator('.world-map canvas')).toBeVisible({
    timeout: 30000,
  });
  await expect.poll(() => workerResponses.length).toBeGreaterThan(0);
  expect(workerResponses[0].status).toBe(200);
  expect(workerResponses[0].contentType).toMatch(/javascript/u);
  expect(workerResponses[0].url).toContain(
    '/osint-rondonia/_app/immutable/workers/maplibre-gl-worker-',
  );
  try {
    await expect(page.locator('.world-map')).toHaveAttribute(
      'aria-busy',
      'false',
      { timeout: 8000 },
    );
  } catch {
    throw new Error(
      `Mapa ainda carregando: ${JSON.stringify({ workerResponses, mapResponses, mapErrors })}`,
    );
  }
  const mapInsets = await page.locator('.map-card').evaluate((card) => {
    const map = card.querySelector('.world-map');
    if (!map) throw new Error('Área cartográfica ausente.');
    const cardBounds = card.getBoundingClientRect();
    const mapBounds = map.getBoundingClientRect();
    return {
      left: mapBounds.left - cardBounds.left,
      right: cardBounds.right - mapBounds.right,
    };
  });
  expect(mapInsets.left).toBeGreaterThanOrEqual(14);
  expect(mapInsets.right).toBeGreaterThanOrEqual(14);
  const mapImage = await sharp(
    await page.locator('.world-map canvas').screenshot(),
  )
    .raw()
    .toBuffer({ resolveWithObject: true });
  let darkBorderPixels = 0;
  for (
    let offset = 0;
    offset < mapImage.data.length;
    offset += mapImage.info.channels
  ) {
    if (
      mapImage.data[offset] < 150 &&
      mapImage.data[offset + 1] < 165 &&
      mapImage.data[offset + 2] < 155
    ) {
      darkBorderPixels += 1;
    }
  }
  expect(darkBorderPixels).toBeGreaterThan(100);
  await page.getByRole('button', { name: 'Ver globo' }).click();
  await expect(page.getByRole('button', { name: 'Ver mapa 2D' })).toBeVisible();

  const localReliefRequest = page.waitForResponse((response) =>
    response.url().includes('world-relief.webp'),
  );
  await page.getByRole('button', { name: 'Relevo' }).click();
  const reliefResponse = await localReliefRequest;
  expect(reliefResponse.ok()).toBe(true);
  const reliefDimensions = await sharp(await reliefResponse.body()).metadata();
  expect([reliefDimensions.width, reliefDimensions.height]).toEqual([
    4096, 4096,
  ]);

  const satelliteRequests: string[] = [];
  await page.route('https://gibs.earthdata.nasa.gov/**', async (route) => {
    satelliteRequests.push(route.request().url());
    await route.abort();
  });
  await page.getByRole('button', { name: 'Satélite' }).click();
  await expect(page.getByText(/NASA GIBS/)).toBeVisible();
  await expect(page.locator('.map-attribution')).toContainText(
    "We acknowledge the use of imagery provided by services from NASA's Global Imagery Browse Services",
  );
  await expect.poll(() => satelliteRequests.length).toBeGreaterThan(0);
  expect(satelliteRequests[0]).toContain(
    'MODIS_Terra_CorrectedReflectance_TrueColor',
  );

  const municipalitiesRequest = page.waitForResponse((response) =>
    response.url().includes('municipios-brasil.pmtiles'),
  );
  await page.getByRole('button', { name: 'Ir ao Brasil' }).click();
  expect((await municipalitiesRequest).ok()).toBe(true);
  await page.getByText('Consultar a cobertura brasileira em tabela').click();
  await expect(
    page
      .getByRole('table', { name: 'Fontes por unidade da federação' })
      .getByRole('row'),
  ).toHaveCount(28);
  const tableSearch = page.getByRole('searchbox', {
    name: 'Filtrar municípios',
  });
  await tableSearch.fill('Porto Velho');
  const row = page.getByRole('row', { name: /Porto Velho RO/ });
  await expect(row).toBeVisible();
  await page
    .getByLabel('Incluir fontes nacionais na cobertura do Brasil')
    .check();
  await expect(
    page.getByRole('table', { name: 'Fontes por município brasileiro' }),
  ).toBeVisible();
  await expect(
    page.getByRole('row', { name: /Porto Velho RO/ }).getByRole('link'),
  ).toHaveAttribute('href', /nacional=1/);
  await row.getByRole('link').click();
  await expect(page).toHaveURL(/municipio=1100205/);
  await expect(page).toHaveURL(/nacional=1/);
});

test('falha do worker do mapa informa que a visualização não carregou', async ({
  page,
}) => {
  await page.route(/maplibre-gl-worker.*\.js/u, (route) => route.abort());
  await page.goto('./');
  await page.locator('.home-dashboard').scrollIntoViewIfNeeded();
  await page.getByRole('button', { name: 'Carregar mapa interativo' }).click();
  await expect(page.getByRole('alert')).toContainText(
    'Não foi possível carregar a visualização interativa.',
    { timeout: 30000 },
  );
});

test('home adia SQLite e mapa; municípios só carregam ao entrar no Brasil', async ({
  page,
}) => {
  await page.setViewportSize({ width: 1280, height: 280 });
  const requests = new Set<string>();
  page.on('request', (request) => {
    const url = request.url();
    if (
      url.includes('.sqlite') ||
      url.includes('sql-wasm') ||
      url.includes('world.pmtiles') ||
      url.includes('municipios-brasil.pmtiles') ||
      url.includes('world-relief.webp') ||
      url.includes('gibs.earthdata.nasa.gov')
    ) {
      requests.add(url);
    }
  });

  await page.goto('./');
  await expect(
    page.getByRole('heading', {
      name: 'Fontes abertas para explorar Rondônia.',
    }),
  ).toBeVisible();
  await page.waitForTimeout(300);
  expect(requests.size).toBe(0);

  await page.locator('.home-dashboard').scrollIntoViewIfNeeded();
  await expect(
    page.getByRole('heading', { name: 'Explore países e regiões' }),
  ).toBeVisible();
  await expect(
    page.getByRole('button', { name: 'Carregar mapa interativo' }),
  ).toBeVisible();
  expect([...requests].some((url) => url.includes('.pmtiles'))).toBe(false);
  await expect(page.locator('.world-map canvas')).toHaveCount(0);

  await page.getByRole('button', { name: 'Carregar mapa interativo' }).click();
  await expect(page.locator('.world-map canvas')).toBeVisible({
    timeout: 30000,
  });
  await expect
    .poll(() => [...requests].some((url) => url.includes('world.pmtiles')))
    .toBe(true);
  expect(
    [...requests].some((url) => url.includes('municipios-brasil.pmtiles')),
  ).toBe(false);
  expect([...requests].some((url) => url.includes('world-relief.webp'))).toBe(
    false,
  );
  expect([...requests].some((url) => url.includes('.sqlite'))).toBe(true);

  const municipalitiesRequest = page.waitForResponse((response) =>
    response.url().includes('municipios-brasil.pmtiles'),
  );
  await page.getByRole('button', { name: 'Ir ao Brasil' }).click();
  expect((await municipalitiesRequest).ok()).toBe(true);
});

test('home em viewport desktop não inicia o mapa sem ação explícita', async ({
  page,
}) => {
  await page.setViewportSize({ width: 1440, height: 960 });
  const mapRequests: string[] = [];
  page.on('request', (request) => {
    if (
      /\.pmtiles(?:$|\?)/.test(request.url()) ||
      request.url().includes('world-relief.webp') ||
      request.url().includes('gibs.earthdata.nasa.gov')
    ) {
      mapRequests.push(request.url());
    }
  });

  await page.goto('./');
  await expect(
    page.getByRole('button', { name: 'Carregar mapa interativo' }),
  ).toBeVisible();
  await page.waitForTimeout(500);
  expect(mapRequests).toEqual([]);
  await expect(page.locator('.world-map canvas')).toHaveCount(0);
  const largeScripts = await page.evaluate(() =>
    performance
      .getEntriesByType('resource')
      .filter(
        (entry) =>
          entry.name.endsWith('.js') &&
          (entry as PerformanceResourceTiming).transferSize > 500_000,
      )
      .map((entry) => entry.name),
  );
  expect(largeScripts).toEqual([]);
});

test('mapa limita o pixel ratio em telas de alta densidade', async ({
  browser,
}) => {
  const context = await browser.newContext({
    baseURL: 'http://127.0.0.1:4173/osint-rondonia/',
    viewport: { width: 1440, height: 960 },
    deviceScaleFactor: 3,
  });
  const page = await context.newPage();
  try {
    await page.goto('./');
    await page
      .getByRole('button', { name: 'Carregar mapa interativo' })
      .click();
    const canvas = page.locator('.world-map canvas');
    await expect(canvas).toBeVisible({ timeout: 30000 });
    const ratios = await canvas.evaluate((element) => {
      const rect = element.getBoundingClientRect();
      const mapCanvas = element as HTMLCanvasElement;
      return {
        devicePixelRatio: window.devicePixelRatio,
        backingStoreRatio: mapCanvas.width / rect.width,
      };
    });
    expect(ratios.devicePixelRatio).toBe(3);
    expect(ratios.backingStoreRatio).toBeLessThanOrEqual(2);
  } finally {
    await context.close();
  }
});

test('filtros abrem no clique e o chevron acompanha o estado', async ({
  page,
}) => {
  await page.goto('./fontes/');

  const type = page.getByRole('combobox', { name: 'Tipo de fonte' });
  const typeChevron = page.locator('.combo-trigger svg').nth(1);
  await expect(type).toHaveAttribute('aria-expanded', 'false');
  await type.click();
  await expect(type).toHaveAttribute('aria-expanded', 'true');
  await expect(page.getByRole('listbox')).toBeVisible();
  await expect(typeChevron).toHaveClass(/expanded/);
  await type.fill('ferramenta');
  await expect(
    page.getByRole('option', { name: 'Ferramenta ou Serviço' }),
  ).toBeVisible();
  await expect(
    page.getByRole('option', { name: /ferramenta_ou_servico/ }),
  ).toHaveCount(0);
  await type.fill('portal');
  await expect(
    page.getByRole('option', { name: 'Portal de Notícias', exact: true }),
  ).toBeVisible();
  await page
    .getByRole('button', { name: 'Mostrar opções de Tipo de fonte' })
    .click();
  await expect(page.getByRole('listbox')).toBeHidden();
  await expect(typeChevron).not.toHaveClass(/expanded/);

  const triage = page.getByRole('combobox', { name: 'Triagem' });
  await triage.click();
  await expect(
    page.getByRole('option', { name: 'Sem registro' }),
  ).toBeVisible();
  await page.getByRole('option', { name: 'Sem registro' }).click();
  await expect(triage).toHaveValue('Sem registro');

  const order = page.getByRole('combobox', { name: 'Ordem' });
  await order.click();
  await page.getByRole('option', { name: 'Nome (Z–A)' }).click();
  await expect(order).toHaveValue('Nome (Z–A)');
});

test('busca compartilhável, histórico, ficha e grafo navegável', async ({
  page,
}) => {
  await page.goto('./fontes/');
  await expect(page.getByRole('table')).toBeVisible();
  await expect(
    page.getByRole('cell', { name: 'Sessões' }).first(),
  ).toBeVisible();
  await expect(page.getByText('pendente', { exact: true })).toHaveCount(0);
  await page
    .getByRole('searchbox', { name: 'Nome ou descrição' })
    .fill('atlas da imprensa');
  await page.getByRole('button', { name: 'Aplicar filtros' }).click();
  await expect(page).toHaveURL(/q=atlas\+da\+imprensa/);
  const source = page.getByRole('link', { name: /Atlas da Imprensa/ }).first();
  await expect(source).toBeVisible();
  await source.click();
  await expect(
    page.getByRole('heading', { level: 1, name: /Atlas da Imprensa/ }),
  ).toBeVisible();
  await page.reload();
  await expect(
    page.getByRole('heading', { level: 1, name: /Atlas da Imprensa/ }),
  ).toBeVisible();
  await page.getByRole('link', { name: 'Explorar relações' }).click();
  await expect(
    page.getByRole('heading', { name: /Relações diretas/ }),
  ).toBeVisible();
  await expect(page.locator('.graph canvas').first()).toBeVisible();
  const neighbor = page.locator('.index-list a').first();
  await neighbor.focus();
  await neighbor.press('Enter');
  await expect(page).toHaveURL(/grafo\/\?tipo=/);
  await page.goBack();
  await expect(page).toHaveURL(/grafo\/\?tipo=fonte/);
  await page.goBack();
  await expect(
    page.getByRole('heading', { level: 1, name: /Atlas da Imprensa/ }),
  ).toBeVisible();
  await page.goForward();
  await expect(
    page.getByRole('heading', { name: /Relações diretas/ }),
  ).toBeVisible();
});

test('mobile, filtros por teclado e recuperação da falha de download', async ({
  page,
}) => {
  await page.setViewportSize({ width: 375, height: 780 });
  await page.route('**/*.sqlite', (route) => route.abort(), { times: 1 });
  await page.goto('./fontes/');
  await expect(page.getByRole('alert')).toContainText('Não foi possível');
  await page.getByRole('button', { name: 'Tentar novamente' }).click();
  await expect(page.getByRole('table')).toBeVisible();
  const uf = page.getByRole('combobox', { name: 'UF de cobertura' });
  await uf.fill('rondonia');
  await uf.press('ArrowDown');
  await expect(page.getByRole('option', { name: 'Rondônia' })).toBeVisible();
  await uf.press('Enter');
  await page.getByRole('button', { name: 'Aplicar filtros' }).click();
  await expect(page).toHaveURL(/uf=11/);
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(
    375,
  );
});

test('busca global, alternância persistente de tema e navegação móvel', async ({
  page,
}) => {
  await page.emulateMedia({ colorScheme: 'dark' });
  await page.goto('./');
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await page
    .getByRole('searchbox', { name: 'Buscar no catálogo' })
    .fill('Atlas da Imprensa');
  await page.getByRole('button', { name: 'Buscar', exact: true }).click();
  await expect(page).toHaveURL(/fontes\/\?q=Atlas\+da\+Imprensa/);
  await expect(
    page.getByRole('searchbox', { name: 'Nome ou descrição' }),
  ).toHaveValue('Atlas da Imprensa');

  const theme = page.getByRole('button', { name: 'Ativar tema claro' });
  await theme.click();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
  await expect
    .poll(() =>
      page.evaluate(() => localStorage.getItem('osint-rondonia-theme')),
    )
    .toBe('light');
  await page.reload();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');

  await page.setViewportSize({ width: 375, height: 780 });
  const menu = page.getByRole('button', { name: 'Abrir navegação' });
  await menu.focus();
  await menu.press('Enter');
  await expect(page.getByRole('dialog')).toBeVisible();
  await expect(
    page.getByRole('dialog').getByRole('link', { name: 'Créditos' }),
  ).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.getByRole('dialog')).toBeHidden();
});

test('páginas Sobre, Legal e Créditos são navegáveis', async ({ page }) => {
  const pages = [
    { path: 'sobre/', title: 'Sobre o catálogo', nav: 'Sobre' },
    { path: 'legal/', title: 'Informações legais', nav: 'Legal' },
    { path: 'creditos/', title: 'Créditos', nav: 'Créditos' },
  ];
  for (const item of pages) {
    await page.goto(`./${item.path}`);
    await expect(
      page.getByRole('heading', { level: 1, name: item.title }),
    ).toBeVisible();
    await expect(
      page
        .getByRole('navigation', { name: 'Navegação do catálogo' })
        .getByRole('link', { name: item.nav }),
    ).toHaveAttribute('aria-current', 'page');
    await expect(
      page.getByRole('link', { name: 'Rondoscópio — OSINT Rondônia, início' }),
    ).toBeVisible();
  }
});

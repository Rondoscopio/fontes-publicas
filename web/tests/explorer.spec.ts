import { expect, test } from '@playwright/test';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

test('início, marca, mapa, gráficos e SQLite idêntico ao catálogo', async ({
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
  await expect(
    page.getByRole('navigation', { name: 'Navegação do catálogo' }),
  ).toBeVisible();
  await expect(
    page.getByRole('heading', { name: 'Fontes por município' }),
  ).toBeVisible();
  await expect(page.locator('.municipality-shape')).toHaveCount(5571, {
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

test('mapa tem alternativa tabular, seleção municipal e camada nacional opcional', async ({
  page,
}) => {
  await page.goto('./');
  await expect(page.locator('.municipality-shape')).toHaveCount(5571, {
    timeout: 30000,
  });
  await page.getByText('Consultar a cobertura em tabela').click();
  const tableSearch = page.getByRole('searchbox', {
    name: 'Filtrar municípios',
  });
  await tableSearch.fill('Porto Velho');
  const row = page.getByRole('row', { name: /Porto Velho RO/ });
  await expect(row).toBeVisible();
  await page.getByLabel('Incluir fontes nacionais').check();
  await expect(
    page.getByRole('row', { name: /Porto Velho RO/ }).getByRole('link'),
  ).toHaveAttribute('href', /nacional=1/);
  await page
    .locator('.municipality-shape[data-codigo-ibge="1100205"]')
    .click({ force: true });
  await expect(page).toHaveURL(/municipio=1100205/);
  await expect(page).toHaveURL(/nacional=1/);
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

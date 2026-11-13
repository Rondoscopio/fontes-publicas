import { expect, test } from '@playwright/test';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

test('HTML inicial, gráficos, e SQLite idêntico ao catálogo', async ({
  page,
  request,
}) => {
  const html = await request.get('./');
  expect(html.ok()).toBe(true);
  expect(await html.text()).toContain('Explore o acervo');
  await page.goto('./');
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
  const link = page.getByRole('link', { name: 'Baixar SQLite' });
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

test('busca compartilhável, histórico, ficha e grafo navegável', async ({
  page,
}) => {
  await page.goto('./fontes/');
  await expect(page.getByRole('table')).toBeVisible();
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

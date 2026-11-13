import { Container } from 'inversify';
import { createCatalogUseCases } from '$lib/features/catalog/application/catalog-use-cases';
import { WorkerCatalogReader } from '$lib/features/catalog/adapters/worker-catalog-reader';
import { StaticGeographyReader } from '$lib/features/map/adapters/static-geography-reader';
import { createGeographyUseCases } from '$lib/features/map/application/geography-use-cases';
import {
  CATALOG_READER,
  CATALOG_USE_CASES,
  GEOGRAPHY_READER,
  GEOGRAPHY_USE_CASES,
} from './tokens';

export function createAppContainer() {
  const container = new Container();
  container
    .bind(CATALOG_READER)
    .toDynamicValue(() => new WorkerCatalogReader())
    .inSingletonScope();
  container
    .bind(CATALOG_USE_CASES)
    .toDynamicValue((context) =>
      createCatalogUseCases(context.get(CATALOG_READER)),
    )
    .inSingletonScope();
  container
    .bind(GEOGRAPHY_READER)
    .toDynamicValue(() => new StaticGeographyReader())
    .inSingletonScope();
  container
    .bind(GEOGRAPHY_USE_CASES)
    .toDynamicValue((context) =>
      createGeographyUseCases(context.get(GEOGRAPHY_READER)),
    )
    .inSingletonScope();
  return container;
}

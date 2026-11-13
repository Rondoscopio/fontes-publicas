import { getContext } from 'svelte';
import type { Container } from 'inversify';
import { APP_CONTAINER } from './tokens';

export function getAppContainer() {
  return getContext<Container>(APP_CONTAINER);
}

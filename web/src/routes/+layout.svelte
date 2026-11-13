<script lang="ts">
  import '@fontsource-variable/dm-sans';
  import '../app.css';
  import { resolve } from '$app/paths';
  import { page } from '$app/state';
  import { databaseUrl } from '$lib/client';
  let { children } = $props();
  const navigation = [
    { route: '/', name: 'Visão geral' },
    { route: '/fontes/', name: 'Fontes' },
    { route: '/categorias/', name: 'Categorias' },
    { route: '/listas/', name: 'Listas' },
    { route: '/abrangencia/', name: 'Abrangência' },
  ] as const;
</script>

<a class="skip" href="#conteudo">Ir para o conteúdo</a>
<header class="site-header">
  <div class="masthead wrap">
    <a class="brand" href={resolve('/')}>
      <span class="mark" aria-hidden="true"><i></i></span>
      <span>OSINT <strong>Rondônia</strong></span>
    </a>
    <a class="download" href={databaseUrl()} download="catalog.sqlite">
      <span aria-hidden="true">↓</span> Baixar SQLite
    </a>
  </div>
  <nav class="nav wrap" aria-label="Navegação principal">
    {#each navigation as item (item.route)}
      <a
        href={resolve(item.route)}
        aria-current={page.route.id === item.route.replace(/\/$/, '') ||
        (item.route === '/' && page.route.id === '/')
          ? 'page'
          : undefined}>{item.name}</a
      >
    {/each}
  </nav>
</header>
<main id="conteudo" class="wrap" tabindex="-1">
  <noscript
    ><p class="notice">
      Ative o JavaScript para explorar o catálogo ou baixe o SQLite acima.
    </p></noscript
  >
  {@render children()}
</main>
<footer class="wrap footer">
  <span>OSINT Rondônia · Rondoscópio</span>
  <a href="https://github.com/Rondoscopio/osint-rondonia"
    >Dados e código no GitHub ↗</a
  >
</footer>

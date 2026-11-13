<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { asset, resolve } from '$app/paths';
  import { page } from '$app/state';
  import { Dialog } from 'bits-ui';
  import '@fontsource-variable/dm-sans';
  import '../app.css';
  import { databaseUrl } from '$lib/client';
  import { sources } from '$lib/links';
  import SidebarNav from '$lib/SidebarNav.svelte';

  let { children } = $props();
  let theme = $state<'light' | 'dark'>(
    typeof document !== 'undefined' &&
      document.documentElement.dataset.theme === 'dark'
      ? 'dark'
      : 'light',
  );
  let mobileMenuOpen = $state(false);
  let searchText = $state('');
  let searchInput = $state<HTMLInputElement>();

  $effect(() => {
    searchText = page.url.searchParams.get('q') ?? '';
    if (typeof document !== 'undefined') {
      document.documentElement.dataset.theme = theme;
    }
  });

  onMount(() => {
    const stored = localStorage.getItem('osint-rondonia-theme');
    theme =
      stored === 'light' || stored === 'dark'
        ? stored
        : matchMedia('(prefers-color-scheme: dark)').matches
          ? 'dark'
          : 'light';
  });

  function toggleTheme() {
    theme = theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('osint-rondonia-theme', theme);
  }

  function submitSearch(event: SubmitEvent) {
    event.preventDefault();
    void goto(sources(searchText.trim() ? { q: searchText.trim() } : {}));
  }

  function globalShortcuts(event: KeyboardEvent) {
    if (
      (event.metaKey || event.ctrlKey) &&
      event.key.toLocaleLowerCase() === 'k'
    ) {
      event.preventDefault();
      searchInput?.focus();
    }
    if (event.key === 'Escape') mobileMenuOpen = false;
  }
</script>

<svelte:window onkeydown={globalShortcuts} />

<Dialog.Root bind:open={mobileMenuOpen}>
  <a class="skip" href="#conteudo">Ir para o conteúdo</a>
  <header class="site-header">
    <div class="topbar">
      <Dialog.Trigger class="menu-toggle" aria-label="Abrir navegação">
        <svg
          aria-hidden="true"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
        >
          <path d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </Dialog.Trigger>
      <a
        class="brand"
        href={resolve('/')}
        aria-label="Rondoscópio — OSINT Rondônia, início"
      >
        <img src={asset('/favicon.svg')} alt="" width="38" height="38" />
        <span class="brand-copy">
          <strong>Rondoscópio</strong>
          <small>OSINT Rondônia</small>
        </span>
      </a>
      <form class="global-search" role="search" onsubmit={submitSearch}>
        <label class="sr-only" for="global-search">Buscar no catálogo</label>
        <svg
          aria-hidden="true"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.8"
          stroke-linecap="round"
        >
          <circle cx="10.5" cy="10.5" r="6.5" /><path d="m16 16 5 5" />
        </svg>
        <input
          bind:this={searchInput}
          id="global-search"
          type="search"
          placeholder="Buscar fontes, temas e territórios"
          bind:value={searchText}
        />
        <kbd>⌘ K</kbd>
        <button class="search-submit" type="submit">Buscar</button>
      </form>
      <div class="topbar-actions">
        <a class="download" href={databaseUrl()} download="catalog.sqlite">
          <svg
            aria-hidden="true"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M12 3v12m0 0 4-4m-4 4-4-4M4 17v3h16v-3" />
          </svg>
          <span>SQLite</span>
        </a>
        <button
          class="theme-toggle"
          type="button"
          aria-label={theme === 'light'
            ? 'Ativar tema escuro'
            : 'Ativar tema claro'}
          title={theme === 'light' ? 'Ativar tema escuro' : 'Ativar tema claro'}
          onclick={toggleTheme}
        >
          {#if theme === 'light'}
            <svg
              aria-hidden="true"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M20.9 13A8.9 8.9 0 0 1 11 3.1 9 9 0 1 0 20.9 13Z" />
            </svg>
          {:else}
            <svg
              aria-hidden="true"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
            >
              <circle cx="12" cy="12" r="4" /><path
                d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"
              />
            </svg>
          {/if}
        </button>
      </div>
    </div>
  </header>

  <div class="workspace">
    <aside class="sidebar" aria-label="Navegação lateral">
      <SidebarNav />
      <div class="sidebar-bottom">
        <span class="status-dot" aria-hidden="true"></span>
        <span>Catálogo público</span>
      </div>
    </aside>
    <div class="content-column">
      <main id="conteudo" class="main-area" tabindex="-1">
        <noscript>
          <p class="notice">
            Ative o JavaScript para explorar o catálogo ou baixe o SQLite no
            cabeçalho.
          </p>
        </noscript>
        {@render children()}
      </main>
      <footer class="site-footer">
        <span>Rondoscópio · OSINT Rondônia</span>
        <nav aria-label="Informações do projeto">
          <a href={resolve('/sobre/')}>Sobre</a>
          <a href={resolve('/legal/')}>Legal</a>
          <a href={resolve('/creditos/')}>Créditos</a>
          <a
            href="https://github.com/Rondoscopio/osint-rondonia"
            rel="noreferrer">Código e dados ↗</a
          >
        </nav>
      </footer>
    </div>
  </div>

  <Dialog.Portal>
    <Dialog.Overlay class="mobile-overlay" />
    <Dialog.Content class="mobile-sidebar">
      <div class="mobile-sidebar-heading">
        <Dialog.Title>Navegação</Dialog.Title>
        <Dialog.Close class="mobile-close" aria-label="Fechar navegação"
          >×</Dialog.Close
        >
      </div>
      <SidebarNav onNavigate={() => (mobileMenuOpen = false)} />
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

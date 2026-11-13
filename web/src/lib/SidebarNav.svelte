<script lang="ts">
  import { resolve } from '$app/paths';
  import { page } from '$app/state';
  import NavIcon from './NavIcon.svelte';

  let { onNavigate = () => {} }: { onNavigate?: () => void } = $props();
  const groups = [
    {
      title: 'Explorar',
      items: [
        { route: '/', name: 'Visão geral', icon: 'overview' },
        { route: '/fontes', name: 'Fontes', icon: 'sources' },
        { route: '/categorias', name: 'Categorias', icon: 'categories' },
        { route: '/listas', name: 'Listas temáticas', icon: 'lists' },
        { route: '/abrangencia', name: 'Abrangência', icon: 'coverage' },
        { route: '/grafo', name: 'Relações', icon: 'graph' },
      ],
    },
    {
      title: 'Sobre o projeto',
      items: [
        { route: '/sobre', name: 'Sobre', icon: 'about' },
        { route: '/legal', name: 'Legal', icon: 'legal' },
        { route: '/creditos', name: 'Créditos', icon: 'credits' },
      ],
    },
  ] as const;

  function active(route: string) {
    if (route === '/') return page.route.id === '/';
    return page.route.id === route || page.route.id?.startsWith(route + '/');
  }
</script>

<nav class="sidebar-nav" aria-label="Navegação do catálogo">
  {#each groups as group (group.title)}
    <section class="sidebar-group" aria-labelledby={'nav-' + group.title}>
      <h2 id={'nav-' + group.title}>{group.title}</h2>
      <ul>
        {#each group.items as item (item.route)}
          <li>
            <a
              class:active={active(item.route)}
              href={resolve(item.route === '/' ? '/' : `${item.route}/`)}
              aria-current={active(item.route) ? 'page' : undefined}
              onclick={onNavigate}
            >
              <span class="sidebar-icon"><NavIcon name={item.icon} /></span>
              <span>{item.name}</span>
            </a>
          </li>
        {/each}
      </ul>
    </section>
  {/each}
</nav>

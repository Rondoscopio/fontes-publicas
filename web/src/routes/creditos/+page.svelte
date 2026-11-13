<script lang="ts">
  import { createInstitutionalViewModel } from '$lib/features/institutional/institutional.viewmodel';
  const vm = createInstitutionalViewModel('creditos');
</script>

<svelte:head>
  <title>{vm.title}</title>
  <meta name="description" content={vm.description} />
</svelte:head>

<div class="page-heading">
  <p class="eyebrow">{vm.eyebrow}</p>
  <h1>{vm.heading}</h1>
  <p>{vm.lead}</p>
</div>

<div class="info-grid">
  <section class="card panel">
    <h2>Projeto</h2>
    <p>
      O catálogo é parte do <a href="https://github.com/Rondoscopio"
        >Rondoscópio ↗</a
      >. Sua curadoria organiza referências e metadados; a inclusão de uma
      origem não implica endosso nem confirmação individual de seus conteúdos.
    </p>
    <p>
      As contribuições são registradas no histórico público do
      <a
        href="https://github.com/Rondoscopio/osint-rondonia/graphs/contributors"
        >repositório ↗</a
      >. Esta página não atribui registros a pessoas quando a proveniência não
      identifica autoria individual.
    </p>
  </section>

  <section class="card panel">
    <h2>Territórios</h2>
    <p>
      A tabela territorial usa a Divisão Territorial Brasileira 2025 e o mapa
      usa a Malha Municipal Digital 2025 do
      <a
        href="https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/15774-malhas.html"
        >Instituto Brasileiro de Geografia e Estatística (IBGE) ↗</a
      >. Os códigos de município e UF conectam a malha às fichas de abrangência.
    </p>
    <p>
      O mapa global de países e divisões administrativas de primeiro nível usa
      dados públicos do
      <a href="https://www.naturalearthdata.com/about/terms-of-use/"
        >Natural Earth ↗</a
      >, publicados em domínio público. A composição de relevo também é do
      Natural Earth.
    </p>
    <p>
      A camada de satélite opcional usa imagens Terra/MODIS servidas pelo
      <a href="https://worldview.earthdata.nasa.gov/">NASA GIBS ↗</a>. A NASA
      solicita a seguinte atribuição: “We acknowledge the use of imagery
      provided by services from NASA's Global Imagery Browse Services (GIBS),
      part of NASA's Earth Science Data and Information System (ESDIS).” A
      camada requer conexão externa; seu uso não implica associação ou endosso
      da NASA.
    </p>
  </section>

  <section class="card panel">
    <h2>Diretórios e referências catalogadas</h2>
    <ul class="credit-list">
      <li>
        <a href="https://github.com/jivoi/awesome-osint">Awesome OSINT ↗</a>
      </li>
      <li>
        <a href="https://github.com/osintbrazuca/osint-brazuca"
          >OSINT Brazuca ↗</a
        >
      </li>
      <li><a href="https://www.chelfoapi.com/">Chelfo API ↗</a></li>
      <li>
        <a href="https://atlasdaimprensa.com.br/rondonia-jornais/"
          >Atlas da Imprensa — Rondônia ↗</a
        >
      </li>
    </ul>
    <p class="muted">
      A proveniência registrada varia por ficha. Consulte os links e as notas da
      própria ficha para ver a referência específica.
    </p>
  </section>

  <section class="card panel">
    <h2>Software</h2>
    <p>
      A interface utiliza
      <a href="https://svelte.dev/">SvelteKit ↗</a>,
      <a href="https://bits-ui.com/">Bits UI ↗</a>,
      <a href="https://maplibre.org/">MapLibre GL JS ↗</a>,
      <a href="https://tanstack.com/query/latest/docs/framework/svelte/overview"
        >TanStack Query ↗</a
      >
      e
      <a href="https://sql.js.org/">SQL.js ↗</a>. Cada componente e biblioteca
      mantém sua licença e seus avisos próprios.
    </p>
  </section>
</div>

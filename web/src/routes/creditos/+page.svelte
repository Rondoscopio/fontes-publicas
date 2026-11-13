<svelte:head>
  <title>Créditos e proveniência · Rondoscópio</title>
  <meta
    name="description"
    content="Créditos do projeto, dados territoriais, proveniência e software do catálogo OSINT Rondônia."
  />
</svelte:head>

<div class="page-heading">
  <p class="eyebrow">Atribuição</p>
  <h1>Créditos</h1>
  <p>Quem mantém o projeto e de onde vêm os dados de referência.</p>
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
      <a href="https://d3js.org/">D3 ↗</a> e
      <a href="https://sql.js.org/">SQL.js ↗</a>. Cada componente e biblioteca
      mantém sua licença e seus avisos próprios.
    </p>
  </section>
</div>

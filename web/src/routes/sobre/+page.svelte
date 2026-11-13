<script lang="ts">
  import { resolve } from '$app/paths';
</script>

<svelte:head>
  <title>Sobre o catálogo · Rondoscópio</title>
  <meta
    name="description"
    content="Conheça o propósito, o escopo e os limites do catálogo OSINT Rondônia."
  />
</svelte:head>

<div class="page-heading">
  <p class="eyebrow">O projeto</p>
  <h1>Sobre o catálogo</h1>
  <p>
    O OSINT Rondônia reúne fontes públicas, ferramentas e referências para
    pesquisa, jornalismo, investigação e fiscalização cidadã.
  </p>
</div>

<div class="info-grid">
  <section class="card panel">
    <h2>O que você encontra</h2>
    <p>
      Fichas para serviços e bases públicas, ferramentas, documentos e
      diretórios. Cada ficha pode reunir endereço, descrição, categorias,
      abrangência e proveniência, conforme os dados disponíveis.
    </p>
    <p>
      Use a <a href={resolve('/fontes/')}>busca de fontes</a> para combinar
      texto, categoria, tipo, triagem e território. As relações entre registros
      também podem ser exploradas no <a href={resolve('/grafo/')}>grafo</a>.
    </p>
  </section>

  <section class="card panel">
    <h2>Como interpretar</h2>
    <p>
      A presença no catálogo não significa que um endereço esteja disponível,
      que a ferramenta tenha sido testada ou que uma fonte endosse o
      Rondoscópio. Parte das fichas aguarda triagem editorial.
    </p>
    <p>
      Categorias e abrangências descrevem os registros catalogados. Elas não
      atestam precisão, independência editorial, atualidade ou qualidade dos
      dados da fonte externa.
    </p>
  </section>

  <section class="card panel">
    <h2>Dados abertos e navegação</h2>
    <p>
      O catálogo está disponível em CSV e SQLite. A interface baixa o SQLite do
      próprio site e consulta os dados no navegador; filtros podem ser
      compartilhados pela URL.
    </p>
    <a
      class="button primary"
      href="https://github.com/Rondoscopio/osint-rondonia/issues"
    >
      Propor correção ou melhoria ↗
    </a>
  </section>
</div>

<script lang="ts">
  import type { Detail } from './catalog';
  import { graphLink, httpLink, sources } from './links';

  let { detail }: { detail: Detail } = $props();
  const { fonte, categorias, urls, origens, abrangencias } = $derived(detail);
  const labels: Record<string, string> = {
    id_externo: 'ID externo',
    nota: 'Nota',
    observacao: 'Observação',
    observacoes: 'Observações',
    orgao_responsavel: 'Órgão responsável',
    entidade_responsavel: 'Entidade responsável',
    esfera: 'Esfera',
    tecnologia: 'Tecnologia',
    acesso_declarado: 'Acesso declarado',
    data_referencia: 'Data de referência',
    referencia_institucional: 'Referência institucional',
    repositorio_oficial: 'Repositório oficial',
    licenca_spdx: 'Licença declarada',
  };
</script>

<div class="page-heading">
  <p class="eyebrow">{fonte.tipo ?? 'Fonte do catálogo'}</p>
  <h1>{fonte.nome}</h1>
  {#if fonte.descricao}<p class="preserve">{fonte.descricao}</p>{/if}
  <a class="button primary" href={graphLink('fonte', fonte.id)}
    >Explorar relações →</a
  >
</div>
<div class="detail-grid">
  <section class="card panel">
    <h2>Registro</h2>
    <dl>
      <dt>ID da fonte</dt>
      <dd>{fonte.id}</dd>
      <dt>Triagem editorial</dt>
      <dd>{fonte.status_triagem ?? 'Sem registro'}</dd>
      <dt>Validação</dt>
      <dd>{fonte.validacao ?? 'Sem registro'}</dd>
      <dt>Situação do link</dt>
      <dd>{fonte.situacao_url ?? 'Sem registro'}</dd>
      {#each Object.entries(labels) as [field, label] (field)}
        {#if fonte[field] !== null && fonte[field] !== undefined && fonte[field] !== ''}
          <dt>{label}</dt>
          <dd class="preserve">{fonte[field]}</dd>
        {/if}
      {/each}
    </dl>
  </section>
  <section class="card panel">
    <h2>Links</h2>
    {#if urls.length}
      <ul class="records">
        {#each urls as entry (entry.id)}
          {@const href = httpLink(entry.url)}
          <li>
            <span class="muted">{entry.papel}</span><br />
            {#if href}<a {href} rel="noreferrer">{entry.nome || entry.url} ↗</a>
            {:else}{entry.nome || entry.url}{/if}
            {#if entry.nome && entry.nome !== entry.url}<small
                >{entry.url}</small
              >{/if}
          </li>
        {/each}
      </ul>
    {:else}<p class="muted">Sem links registrados.</p>{/if}
  </section>
  <section class="card panel">
    <h2>Categorias</h2>
    {#if categorias.length}
      <ul class="chips">
        {#each categorias as item (item.id)}
          <li>
            <a class="pill" href={sources({ categoria: item.id })}
              >{item.nome} · {item.tipo_classificacao}</a
            >
          </li>
        {/each}
      </ul>
    {:else}<p class="muted">Sem categorias registradas.</p>{/if}
  </section>
  <section class="card panel">
    <h2>Origens</h2>
    {#if origens.length}
      <ul class="records">
        {#each origens as item (item.tipo_origem)}
          <li>
            <span class="muted">{item.tipo_origem.replaceAll('_', ' ')}</span
            ><br />
            {#if item.fonte_id}<a href={sources({ id: item.fonte_id })}
                >{item.nome ?? item.valor_original}</a
              ><small>{item.valor_original}</small>
            {:else}{item.valor_original}{/if}
          </li>
        {/each}
      </ul>
    {:else}<p class="muted">Sem origens registradas.</p>{/if}
  </section>
  <section class="card panel">
    <h2>Abrangência</h2>
    {#each abrangencias as item (item.papel)}
      <h3>
        {item.papel === 'cobertura' ? 'Cobertura' : 'Localidade declarada'}
      </h3>
      <ul class="chips">
        {#if item.nacional}<li><span class="pill">Nacional</span></li>{/if}
        {#if item.internacional}<li>
            <span class="pill">Internacional</span>
          </li>{/if}
        {#each item.ufs as uf (uf.id)}<li>
            <span class="pill">{uf.nome}</span>
          </li>{/each}
        {#each item.municipios as municipality (municipality.id)}<li>
            <span class="pill">{municipality.nome}</span>
          </li>{/each}
      </ul>
    {:else}<p class="muted">Sem abrangência registrada.</p>{/each}
  </section>
</div>

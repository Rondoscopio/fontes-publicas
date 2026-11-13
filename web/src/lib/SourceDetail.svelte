<script lang="ts">
  import type { Detail } from './catalog';
  import { graphLink, httpLink, sources } from './links';
  import { displayLabel, displayText } from './labels';

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
  <p class="eyebrow">
    {fonte.tipo ? displayText(fonte.tipo) : 'Fonte do catálogo'}
  </p>
  <h1>{displayText(fonte.nome)}</h1>
  {#if fonte.descricao}<p class="preserve">
      {displayText(fonte.descricao)}
    </p>{/if}
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
      <dd>
        {fonte.status_triagem
          ? displayText(fonte.status_triagem)
          : 'Sem registro'}
      </dd>
      <dt>Validação</dt>
      <dd>
        {typeof fonte.validacao === 'string'
          ? displayText(fonte.validacao)
          : (fonte.validacao ?? 'Sem registro')}
      </dd>
      <dt>Situação do link</dt>
      <dd>
        {typeof fonte.situacao_url === 'string'
          ? displayText(fonte.situacao_url)
          : (fonte.situacao_url ?? 'Sem registro')}
      </dd>
      {#each Object.entries(labels) as [field, label] (field)}
        {#if fonte[field] !== null && fonte[field] !== undefined && fonte[field] !== ''}
          <dt>{label}</dt>
          <dd class="preserve">
            {#if typeof fonte[field] === 'string'}
              {displayText(fonte[field])}
            {:else}
              {fonte[field]}
            {/if}
          </dd>
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
            <span class="muted">{displayText(entry.papel)}</span><br />
            {#if href}<a {href} rel="noreferrer"
                >{entry.nome ? displayText(entry.nome) : entry.url} ↗</a
              >
            {:else}{entry.nome ? displayText(entry.nome) : entry.url}{/if}
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
              >{displayText(item.nome)} · {displayLabel(
                item.tipo_classificacao,
              )}</a
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
            <span class="muted">{displayLabel(item.tipo_origem)}</span><br />
            {#if item.fonte_id}<a href={sources({ id: item.fonte_id })}
                >{displayText(item.nome ?? item.valor_original)}</a
              ><small>{displayText(item.valor_original)}</small>
            {:else}{displayText(item.valor_original)}{/if}
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

<script lang="ts">
  import { createInstitutionalViewModel } from '$lib/features/institutional/institutional.viewmodel';
  const vm = createInstitutionalViewModel('legal');
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

<div class="info-grid legal-grid">
  <section class="card panel">
    <h2>Código e dados</h2>
    <p>
      O código deste repositório está sob a licença
      <a href="https://github.com/Rondoscopio/osint-rondonia/blob/main/LICENSE"
        >GNU AGPL-3.0-or-later ↗</a
      >. Essa licença não se estende automaticamente às bases, páginas, imagens
      ou materiais de terceiros referenciados no catálogo.
    </p>
    <p>
      Não há uma licença aberta única declarada para todos os dados. Consulte a
      origem e as condições do serviço antes de reutilizar, coletar ou
      redistribuir seu conteúdo. A ficha no catálogo não concede permissão sobre
      o material externo.
    </p>
  </section>

  <section class="card panel">
    <h2>Limites e uso responsável</h2>
    <p>
      Endereços, descrições e status podem ficar desatualizados ou incompletos.
      A inclusão de uma ficha não confirma disponibilidade, precisão, legalidade
      de um método de coleta nem endosso do serviço. Verifique a fonte original
      e corrobore achados antes de usá-los.
    </p>
    <p>
      Respeite leis, termos de uso, direitos autorais e privacidade das pessoas.
      Não use o catálogo para acessar sistemas sem autorização, contornar
      controles ou expor dados pessoais.
    </p>
  </section>

  <section class="card panel">
    <h2>Privacidade da interface</h2>
    <p>
      A interface não exige conta e não integra ferramenta de analytics ou
      publicidade. O SQLite é obtido do próprio site e as buscas são executadas
      localmente no navegador. Os filtros podem aparecer na URL compartilhada. A
      escolha de tema claro ou escuro fica salva no armazenamento local do
      navegador.
    </p>
    <p>
      O site é hospedado no GitHub Pages. O tratamento técnico relacionado à
      hospedagem está sujeito às
      <a
        href="https://docs.github.com/site-policy/privacy-policies/github-privacy-statement"
        rel="noreferrer">políticas de privacidade do GitHub ↗</a
      >.
    </p>
  </section>
</div>

<script lang="ts">
  let { failed, retry }: { failed: boolean; retry: () => void } = $props();
</script>

{#if failed}
  <section class="notice" role="alert">
    <p>Não foi possível ler o catálogo.</p>
    <button class="button" onclick={retry}>Tentar novamente</button>
  </section>
{:else}
  <p class="notice" role="status">Carregando o catálogo…</p>
{/if}

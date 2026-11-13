<script lang="ts">
  import { Combobox } from 'bits-ui';
  import { fold } from './catalog';
  import type { Item } from './catalog';

  let {
    id,
    label,
    items,
    value = $bindable(),
  }: { id: string; label: string; items: Item[]; value: string } = $props();
  let search = $state('');
  const choices = $derived(
    items.filter((item) => fold(item.nome).includes(fold(search))).slice(0, 80),
  );
  const selected = $derived(items.find((item) => item.id === value));
</script>

<div class="field combo">
  <label for={id}>{label}</label>
  <Combobox.Root
    type="single"
    bind:value
    inputValue={search || selected?.nome || ''}
    onOpenChangeComplete={(open) => {
      if (!open) search = '';
    }}
  >
    <div class="combo-input">
      <Combobox.Input
        {id}
        placeholder="Qualquer"
        oninput={(event) => {
          search = event.currentTarget.value;
        }}
      />
      {#if value}
        <button
          type="button"
          class="combo-clear"
          aria-label={'Limpar ' + label}
          onclick={() => {
            value = '';
            search = '';
          }}>×</button
        >
      {/if}
      <Combobox.Trigger aria-label={'Mostrar opções de ' + label}
        >⌄</Combobox.Trigger
      >
    </div>
    <Combobox.Portal>
      <Combobox.Content class="options" sideOffset={4}>
        {#each choices as item (item.id)}
          <Combobox.Item value={item.id} label={item.nome}
            >{item.nome}</Combobox.Item
          >
        {:else}
          <p>Nenhuma opção encontrada.</p>
        {/each}
        {#if choices.length === 80}<p>Digite para restringir as opções.</p>{/if}
      </Combobox.Content>
    </Combobox.Portal>
  </Combobox.Root>
</div>

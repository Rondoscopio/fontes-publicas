<script lang="ts">
  import { Combobox } from 'bits-ui';
  import { fold } from './catalog';
  import { displayText } from './labels';
  import type { Item } from './catalog';

  let {
    id,
    label,
    items,
    value = $bindable(),
  }: { id: string; label: string; items: Item[]; value: string } = $props();
  let search = $state('');
  let open = $state(false);
  const choices = $derived(
    items
      .filter(
        (item) =>
          fold(displayText(item.nome)).includes(fold(search)) ||
          fold(item.nome).includes(fold(search)),
      )
      .slice(0, 80),
  );
  const selected = $derived(items.find((item) => item.id === value));
  const selectedLabel = $derived(selected ? displayText(selected.nome) : '');
</script>

<div class="field combo">
  <label for={id}>{label}</label>
  <Combobox.Root
    type="single"
    bind:value
    bind:open
    inputValue={search || selectedLabel}
    onOpenChangeComplete={(open) => {
      if (!open) search = '';
    }}
  >
    <div class="combo-input">
      <Combobox.Input
        {id}
        placeholder="Qualquer"
        onclick={() => (open = true)}
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
      <Combobox.Trigger
        class="combo-trigger"
        aria-label={'Mostrar opções de ' + label}
      >
        <svg
          class:expanded={open}
          aria-hidden="true"
          viewBox="0 0 20 20"
          fill="none"
          stroke="currentColor"
          stroke-width="1.8"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="m5.5 7.5 4.5 4.5 4.5-4.5" />
        </svg>
      </Combobox.Trigger>
    </div>
    <Combobox.Portal>
      <Combobox.Content class="options" sideOffset={4}>
        {#each choices as item (item.id)}
          <Combobox.Item value={item.id} label={displayText(item.nome)}
            >{displayText(item.nome)}</Combobox.Item
          >
        {:else}
          <p>Nenhuma opção encontrada.</p>
        {/each}
        {#if choices.length === 80}<p>Digite para restringir as opções.</p>{/if}
      </Combobox.Content>
    </Combobox.Portal>
  </Combobox.Root>
</div>

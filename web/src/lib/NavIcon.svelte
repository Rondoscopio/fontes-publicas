<script lang="ts">
  let { name }: { name: string } = $props();
</script>

<svg
  aria-hidden="true"
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="1.8"
  stroke-linecap="round"
  stroke-linejoin="round"
>
  {#if name === 'overview'}
    <rect x="3" y="3" width="8" height="8" rx="1.5" /><rect
      x="13"
      y="3"
      width="8"
      height="5"
      rx="1.5"
    /><rect x="13" y="10" width="8" height="11" rx="1.5" /><rect
      x="3"
      y="13"
      width="8"
      height="8"
      rx="1.5"
    />
  {:else if name === 'sources'}
    <circle cx="10.5" cy="10.5" r="6.5" /><path d="m16 16 5 5" />
  {:else if name === 'categories'}
    <rect x="3" y="3" width="7" height="7" rx="1" /><rect
      x="14"
      y="3"
      width="7"
      height="7"
      rx="1"
    /><rect x="3" y="14" width="7" height="7" rx="1" /><rect
      x="14"
      y="14"
      width="7"
      height="7"
      rx="1"
    />
  {:else if name === 'lists'}
    <path d="M9 6h12M9 12h12M9 18h12" /><circle cx="4" cy="6" r=".5" /><circle
      cx="4"
      cy="12"
      r=".5"
    /><circle cx="4" cy="18" r=".5" />
  {:else if name === 'coverage'}
    <path
      d="M20.5 10.2c0 5.4-8.5 11-8.5 11s-8.5-5.6-8.5-11a8.5 8.5 0 1 1 17 0Z"
    /><circle cx="12" cy="10" r="2.5" />
  {:else if name === 'graph'}
    <circle cx="6" cy="6" r="2.5" /><circle cx="18" cy="7" r="2.5" /><circle
      cx="12"
      cy="18"
      r="2.5"
    /><path d="m8.3 7 7.2-.2M7.5 8.2l3.1 7.4m5.8-6.4-3.2 6.5" />
  {:else if name === 'about'}
    <circle cx="12" cy="12" r="9" /><path d="M12 11v5m0-8h.01" />
  {:else if name === 'legal'}
    <path
      d="M12 3v18m-7 0h14M5 7h14M8 7 4.5 14h7L8 7Zm8 0-3.5 7h7L16 7Zm-5 11a3 3 0 0 0 6 0"
    />
  {:else}
    <path
      d="m12 3 2.5 5.5L20 11l-5.5 2.5L12 19l-2.5-5.5L4 11l5.5-2.5L12 3Z"
    /><path d="m19 16 .9 2.1L22 19l-2.1.9L19 22l-.9-2.1L16 19l2.1-.9L19 16Z" />
  {/if}
</svg>

<script lang="ts">


  /**
   * Props for CustomSelect
   */
  interface CustomSelectProps<T> {
    value: T | T[] | null;
    items: T[];
    itemId?: keyof T;
    itemLabel?: keyof T;
    placeholder?: string;
    clearable?: boolean;
    disabled?: boolean;
    multiple?: boolean;
    onchange?: (event: { detail: T | T[] | null }) => void;
    onclear?: (event: { detail: T | T[] | null }) => void;
  }

  // Destructure props
  let {
    value = null,
    items = [],
    itemId = 'id',
    itemLabel = 'label',
    placeholder = 'Select...',
    clearable = false,
    disabled = false,
    multiple = false,
    onchange = () => {},
    onclear = () => {}
  }: CustomSelectProps<any> = $props();

  // Local state for bound <select>
  let selectedId: string | string[] = multiple
    ? Array.isArray(value) ? (value as any[]).map(v => String(v[itemId])) : []
    : (value ? String((value as any)[itemId]) : '');

  // Sync selectedId -> value
$effect(() => {
    if (!multiple) {
      const newItem = items.find(i => String(i[itemId]) === selectedId) ?? null;
      if (newItem !== value) {
        value = newItem;
        onchange({ detail: newItem });
      }
    } else {
      const newItems = items.filter(i => (selectedId as string[]).includes(String(i[itemId])));
      if (JSON.stringify(newItems) !== JSON.stringify(value ?? [])) {
        value = newItems;
        onchange({ detail: newItems });
      }
    }
  });

  // Sync value -> selectedId
    $effect(() => {
    if (!multiple) {
      const id = value ? String((value as any)[itemId]) : '';
      if (id !== selectedId) selectedId = id;
    } else {
      const ids = Array.isArray(value) ? (value as any[]).map(v => String(v[itemId])) : [];
      if (JSON.stringify(ids) !== JSON.stringify(selectedId)) {
        selectedId = ids;
      }
    }
  });

  function handleClear() {
    if (!multiple) {
      selectedId = '';
      value = null;
      onclear({ detail: null });
    } else {
      selectedId = [];
      value = [];
      onclear({ detail: [] });
    }
  }
</script>

<div>
  {#if clearable && (multiple ? (selectedId as string[]).length : selectedId)}
    <button type="button" on:click={handleClear}>✕</button>
  {/if}

  {#if multiple}
    <select disabled={disabled} multiple bind:value={selectedId}>
      {#each items as item}
        <option value={String(item[itemId])}>
          {String(item[itemLabel])}
        </option>
      {/each}
    </select>
  {:else}
    <select disabled={disabled} bind:value={selectedId}>
      <option value="" disabled>{placeholder}</option>
      {#each items as item}
        <option value={String(item[itemId])}>
          {String(item[itemLabel])}
        </option>
      {/each}
    </select>
  {/if}
</div>

<style>
  button {
    margin-bottom: 0.25rem;
  }
</style>

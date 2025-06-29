<template>
  <div class="space-y-3">
    <div>
      <h3 class="font-medium">Поиск</h3>
      <p class="text-xs text-gray-700">Начните вводить название товара</p>
    </div>
    <div class="flex items-center">
      <div class="relative w-full">
        <input v-model="search" type="text" placeholder="Район, метро, жк..."
          class="py-2 md:mt-0 mt-2 px-4 md:w-full bg-gray-100 focus:outline-none w-full block border rounded-lg border-transparent disabled:opacity-50 disabled:pointer-events-none"
          @input="debounceUpdateQuery" />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

export default {
  setup() {
    const route = useRoute();
    const router = useRouter();
    const search = ref(route.query.search || null);
    let debounceTimer = null;

    const debounceUpdateQuery = () => {
      if (debounceTimer) clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        updateQuery();
      }, 1000);
    };

    const updateQuery = () => {
      router.push({
        query: {
          ...route.query,
          search: search.value || undefined,
        },
      });
    };

    watch(
      () => route.query,
      (newQuery) => {
        search.value = newQuery.search || null;
      },
      { deep: true }
    );

    return {
      search,
      debounceUpdateQuery,
    };
  },
};
</script>

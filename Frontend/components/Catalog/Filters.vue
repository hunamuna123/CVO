<template>
  <div class="flex flex-col gap-6 lg:border-r w-full lg:w-1/3 lg:max-w-sm lg:border-gray-200 p-4">
    <h2 class="text-lg font-semibold max-lg:hidden">Фильтры</h2>
    <hr class="max-lg:hidden text-gray-300" />
    <div class="flex flex-col gap-6 h-full overflow-y-scroll [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-transparent">
      <CatalogFiltersSearch/>
      <CatalogFiltersPrice />
       <CatalogFiltersSquare/>
      <CatalogFiltersType/>
      <CatalogFiltersRooms/>
      <CatalogFiltersDistrict/>
      <CatalogFiltersPeculiarity/>
      <CatalogFiltersVerify/>
    </div>
    <div class="mt-auto flex flex-col gap-2">

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { api } from "@/store/api.js";

const emit = defineEmits(['updateFilterLoaded', 'updateProducts']);
const filters = ref({ category: [], size: [], brand: [] });
const apiStore = api();
const url = computed(() => apiStore.url);

const fetchFilters = async () => {
  try {
    const response = await fetch(`${url.value}api/v1/filters/addition/`);
    const data = await response.json();
    if (data.data) {
      filters.value.category = data.data.category;
      filters.value.size = data.data.size;
      filters.value.brand = data.data.brand;
      emit('updateFilterLoaded', true);
    }
  } catch (err) {
    console.error('Ошибка при загрузке фильтров:', err);
  }
};

const fetchProducts = async () => {
  const query = new URLSearchParams(window.location.search).toString();
  const apiUrl = `${url.value}api/v1/properties/?${query}`;
  try {
    const response = await fetch(apiUrl);
    const data = await response.json();
    emit('updateProducts', data);
  } catch (err) {
    console.error('Ошибка при загрузке товаров:', err);
  }
};

onMounted(() => {
  fetchFilters();
});
</script>

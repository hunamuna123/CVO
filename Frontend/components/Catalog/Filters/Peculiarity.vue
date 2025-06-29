<template>
  <div class="space-y-3">
    <div class="flex items-center gap-2">
      <h3 class="font-medium">Особенности</h3>
    </div>
    <div class="grid grid-cols-2 gap-x-6 gap-y-2">
      <label v-for="item in peculiarityList" :key="item.value" class="flex items-center gap-2 cursor-pointer select-none">
        <input
          type="checkbox"
          class="form-checkbox accent-blue-500 border-blue-300"
          :value="item.value"
          v-model="selectedPeculiarities"
          @change="updateQuery"
        />
        <span class="text-lg">{{ item.icon }}</span>
        <span class="text-sm">{{ item.label }}</span>
      </label>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const peculiarityList = [
  { value: 'balcony', label: 'Балкон/лоджия', icon: '' },
  { value: 'furniture', label: 'Мебель', icon: '' },
  { value: 'parking', label: 'Парковка', icon: '' },
  { value: 'gym', label: 'Фитнес-зал', icon: '' },
  { value: 'ac', label: 'Кондиционер', icon: '' },
  { value: 'appliances', label: 'Техника', icon: '' },
  { value: 'concierge', label: 'Консьерж', icon: '' },
  { value: 'playground', label: 'Детская площадка', icon: '' },
];

export default {
  setup() {
    const route = useRoute();
    const router = useRouter();

    // Получаем массив из query или пустой массив
    const selectedPeculiarities = ref(
      route.query.peculiarity
        ? Array.isArray(route.query.peculiarity)
          ? route.query.peculiarity
          : route.query.peculiarity.split(',')
        : []
    );

    const updateQuery = () => {
      router.push({
        query: {
          ...route.query,
          peculiarity:
            selectedPeculiarities.value.length > 0
              ? selectedPeculiarities.value.join(',')
              : undefined,
        },
      });
    };

    watch(
      () => route.query.peculiarity,
      (newVal) => {
        selectedPeculiarities.value = newVal
          ? Array.isArray(newVal)
            ? newVal
            : newVal.split(',')
          : [];
      }
    );

    return {
      peculiarityList,
      selectedPeculiarities,
      updateQuery,
    };
  },
};
</script> 
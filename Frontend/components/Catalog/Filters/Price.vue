<template>
	<div class="space-y-3">
		<div>
			<h3 class="font-medium">Цена</h3>
			<p class="text-xs text-gray-700">Выберите цену для желаемого товара</p>
		</div>
		<div class="flex items-center gap-2">
			<div class="relative">
				<input
					v-model="priceFrom"
					type="number"
					class="peer py-3 px-4 ps-11 block w-full bg-gray-100 border-transparent rounded-xl text-sm focus:outline-none disabled:opacity-50 disabled:pointer-events-none [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
					@input="debounceUpdateQuery"
				/>
				<div
					class="absolute inset-y-0 start-0 flex items-center pointer-events-none ps-4 peer-disabled:opacity-50 peer-disabled:pointer-events-none text-gray-400"
				>
					От
				</div>
			</div>
			<hr class="w-3" />
			<div class="relative">
				<input
					v-model="priceTo"
					type="number"
					class="peer py-3 px-4 ps-11 block w-full bg-gray-100 border-transparent rounded-xl text-sm focus:outline-none disabled:opacity-50 disabled:pointer-events-none [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
					@input="debounceUpdateQuery"
				/>
				<div
					class="absolute inset-y-0 start-0 flex items-center pointer-events-none ps-4 peer-disabled:opacity-50 peer-disabled:pointer-events-none text-gray-400"
				>
					До
				</div>
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
    const priceFrom = ref(route.query.price_min || null);
    const priceTo = ref(route.query.price_max || null);
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
          price_min: priceFrom.value || undefined,
          price_max: priceTo.value || undefined,
        },
      });
    };

    watch(
      () => route.query,
      (newQuery) => {
        priceFrom.value = newQuery.price_min || null;
        priceTo.value = newQuery.price_max || null;
      },
      { deep: true }
    );

    return {
      priceFrom,
      priceTo,
      debounceUpdateQuery,
    };
  },
};
</script>

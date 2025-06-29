<template>
	<div class="space-y-3">
		<div>
			<h3 class="font-medium">Площадь</h3>
			<p class="text-xs text-gray-700">Выберите площадь для желаемой квартиры</p>
		</div>
		<div class="flex items-center gap-2">
			<div class="relative">
				<input
					v-model="squareFrom"
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
					v-model="squareTo"
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
    const squareFrom = ref(route.query.total_area_min || null);
    const squareTo = ref(route.query.total_area_max || null);
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
          total_area_min: squareFrom.value || undefined,
          total_area_max: squareTo.value || undefined,
        },
      });
    };

    watch(
      () => route.query,
      (newQuery) => {
        squareFrom.value = newQuery.total_area_min || null;
        squareTo.value = newQuery.total_area_max || null;
      },
      { deep: true }
    );

    return {
      squareFrom,
      squareTo,
      debounceUpdateQuery,
    };
  },
};
</script> 
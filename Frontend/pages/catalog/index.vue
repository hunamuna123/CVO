<template>
	<NuxtLayout>
		<div class="-mt-4 lg:-mt-8 w-full min-h-[90vh] flex gap-6">
			
			<CatalogFilters class="max-lg:hidden"
				@updateFilterLoaded="setFilterLoaded" @updateProducts="updateProducts" />

			<div class="flex flex-col w-full h-full min-h-[90vh]">
				<div class="flex-none">
					<CatalogSkeletonSorting v-show="isProductsLoading" />
					<CatalogSorting v-if="!isProductsLoading" :onSort="updateSort" />
				</div>

				<div class="flex-none mb-2 mt-2 md:order-1">
					<CatalogSkeletonPagination v-if="isProductsLoading" />
					<CatalogPagination v-else-if="products?.pagination && totalPages > 1" 
						:current-page="currentPage" 
						:total-pages="totalPages" 
						:has-prev="hasPrev"
						:has-next="hasNext" 
						@page-change="handlePageChange" />
				</div>

				<div class="flex-1 overflow-y-auto px-1 pt-4">
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<template v-if="isProductsLoading">
							<CatalogSkeletonCard v-for="n in 6" :key="n" />
						</template>
						<template v-else-if="products?.items?.length">
							<CatalogCard v-for="product in products.items" :key="product.id" :product="product" />
						</template>
						<template v-else-if="!isProductsLoading && (!products?.items || products.items.length === 0)">
							<CatalogEmpty />
						</template>
					</div>
				</div>

				<div class="flex-none mb-2 mt-2 md:hidden">
					<CatalogSkeletonPagination v-if="isProductsLoading" />
					<CatalogPagination v-else-if="products?.pagination && totalPages > 1" 
						:current-page="currentPage" 
						:total-pages="totalPages" 
						:has-prev="hasPrev"
						:has-next="hasNext" 
						@page-change="handlePageChange" />
				</div>
			</div>
		</div>
	</NuxtLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { api } from "@/store/api.js";

const apiStore = api();
const url = computed(() => apiStore.url);
const route = useRoute();
const router = useRouter();

definePageMeta({
	layout: 'catalog',
})

const filterisLoaded = ref(false);
const products = ref({ items: [], pagination: { page: 1, pages: 1, has_prev: false, has_next: false } });
const isProductsLoading = ref(true);
const error = ref(null);

const currentPage = computed(() => {
	return products.value?.pagination?.page || 1;
});

const totalPages = computed(() => {
	return products.value?.pagination?.pages || 1;
});

const hasPrev = computed(() => {
	return products.value?.pagination?.has_prev || false;
});

const hasNext = computed(() => {
	return products.value?.pagination?.has_next || false;
});

const setFilterLoaded = (loaded) => {
	filterisLoaded.value = loaded;
};

const updateProducts = (newProducts) => {
	products.value = newProducts;
	isProductsLoading.value = false;
	error.value = null;
};

const updateSort = (sortOption) => {
	const query = { ...route.query, sort: sortOption };
	router.push({ query });
};

const loadingIndicator = useLoadingIndicator()

const fetchProducts = async () => {
	isProductsLoading.value = true;
	error.value = null;
	
	try {
		const query = new URLSearchParams();
		Object.entries(route.query).forEach(([key, value]) => {
			if (Array.isArray(value)) {
				value.forEach(v => query.append(key, v));
			} else {
				query.append(key, value);
			}
		});
		if (!query.has('page')) {
			query.set('page', '1');
		}

		const response = await fetch(`${url.value}api/v1/properties/?${query.toString()}`, {
			headers: {
				'accept': 'application/json',
			},
		});
	
		loadingIndicator.start() 
		
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		
		const data = await response.json();
		products.value = data;
	} catch (err) {
		console.error('Ошибка при загрузке продуктов:', err);
		error.value = err.message || 'Произошла ошибка при загрузке данных';
		products.value = { items: [], pagination: { page: 1, pages: 1, has_prev: false, has_next: false } };
	} finally {
		loadingIndicator.finish() 
		isProductsLoading.value = false;
	}
};

const handlePageChange = (page) => {
	const query = { ...route.query, page: page.toString() };
	router.replace({ query });
};

watch(
	() => route.query,
	() => {
		fetchProducts();
	},
	{ deep: true }
);

onMounted(() => {
	if (!route.query.page) {
		router.replace({ query: { ...route.query, page: '1' } });
	} else {
		fetchProducts();
	}
});
</script>
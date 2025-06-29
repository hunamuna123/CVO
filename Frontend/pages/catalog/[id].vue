<template>
	<NuxtLayout>
		<div class="-mt-4 lg:-mt-8 w-full flex flex-col gap-10">
			<div class="w-full flex flex-col md:flex-row gap-12">
				<template v-if="isLoading">
					<CatalogProductSkeleton />
				</template>
				<template v-else-if="productData">
					<CatalogProductCarousel :product="productData" />
					<CatalogProductValue :product="productData" />
				</template>
				<template v-else>
					<div class="w-full text-center py-8">
						<p class="text-gray-500">Товар не найден</p>
					</div>
				</template>
			</div>
			<div v-if="productData">
				<CatalogProductTabs :product="productData"/>
			</div>
		</div>
	</NuxtLayout>
</template>

<script setup>
import { ref, onMounted, watchEffect, computed, nextTick } from 'vue'
import { useFetch, useRoute } from '#app'
import { api } from '@/store/api.js'

const productData = ref(null)
const route = useRoute()
const apiStore = api()
const url = computed(() => apiStore.url)

const id = route.params.id

const {
	data: product,
	pending: isLoading,
	error,
	refresh,
} = useFetch(() => {
	return `${url.value}api/v1/properties/${id}/` 
}, {
	headers: {
		accept: 'application/json',
	},
	immediate: true,
})

definePageMeta({
	layout: 'catalog',
})

onMounted(async () => {
	if (!product.value) {
		refresh()
	}
	await nextTick()
	if (typeof window !== 'undefined' && window.HSStaticMethods) {
		window.HSStaticMethods.autoInit()
	}
})

watchEffect(async () => {
	if (product.value) {
		productData.value = product.value
		await nextTick()
		if (typeof window !== 'undefined' && window.HSStaticMethods) {
			setTimeout(() => {
				window.HSStaticMethods.autoInit()
			}, 100)
		}
	}
})

const getFullImageUrl = (url) => {
	if (!url) return ''
	if (url.startsWith('http://') || url.startsWith('https://')) return url
	if (url.startsWith('/')) return `${apiStore.url}${url.substring(1)}`
	return `${apiStore.url}${url}`
}
</script>

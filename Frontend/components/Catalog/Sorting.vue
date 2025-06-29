<template>
	<div class="w-full flex items-center justify-between my-2">
		<h3 class="text-xl md:text-sm font-semibold">Результаты</h3>
		<div class="flex flex-row gap-1">
			<CatalogModalF />
			<div class="hs-dropdown relative [--gpu-acceleration:false] inline-flex" id="dropdown">
				<button id="hs-dropdown-scale-animation" type="button"
					class="hs-dropdown-toggle py-2.5 px-3 md:px-6 flex justify-center items-center gap-2 font-medium text-sm rounded-full border border-gray-200 bg-white text-black hover:bg-gray-200 focus:outline-none focus:bg-gray-200 transition-colors duration-200"
					aria-haspopup="menu" aria-expanded="false" aria-label="Dropdown">
					Сортировать
					<svg class="size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
						fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
						stroke-linejoin="round">
						<path d="M3 6h18" />
						<path d="M7 12h10" />
						<path d="M10 18h4" />
					</svg>
				</button>
				<div class="hs-dropdown-menu hs-dropdown-open:scale-100 border border-gray-100 hs-dropdown-open:opacity-100 scale-95 opacity-0 z-10 ease-in-out transition-[transform,opacity] duration-200 min-w-60 bg-white shadow-lg rounded-lg hidden"
					role="menu" aria-orientation="vertical" aria-labelledby="hs-dropdown-scale-animation">
					<div class="p-1 space-y-0.5">
						<button type="button" :class="[
							'flex items-center w-full justify-between gap-x-3.5 py-2 px-3 rounded-lg text-sm transition-colors duration-200 cursor-pointer',
							activeSort === 'data_desc' ? 'bg-blue-500 text-gray-100' : 'text-black hover:bg-gray-100 focus:bg-gray-100'
						]" @click="handleSort('data_desc')">
							Сначала новые
							<svg class="size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24"
								viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
								stroke-linecap="round" stroke-linejoin="round">
								<path d="M13.228 21.925A10 10 0 1 1 21.994 12.338" />
								<path d="M12 6v6l1.562.781" />
								<path d="m14 18 4-4 4 4" />
								<path d="M18 22v-8" />
							</svg>
						</button>
						<button type="button" :class="[
							'flex items-center w-full justify-between gap-x-3.5 py-2 px-3 rounded-lg text-sm transition-colors duration-200 cursor-pointer',
							activeSort === 'data_asc' ? 'bg-blue-500 text-gray-100' : 'text-black hover:bg-gray-100 focus:bg-gray-100'
						]" @click="handleSort('data_asc')">
							Сначала старые
							<svg class="size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24"
								viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
								stroke-linecap="round" stroke-linejoin="round">
								<path d="M12.338 21.994A10 10 0 1 1 21.925 13.227" />
								<path d="M12 6v6l2 1" />
								<path d="m14 18 4 4 4-4" />
								<path d="M18 14v8" />
							</svg>
						</button>
						<button type="button" :class="[
							'flex items-center w-full justify-between gap-x-3.5 py-2 px-3 rounded-lg text-sm transition-colors duration-200 cursor-pointer',
							activeSort === 'price_desc' ? 'bg-blue-500 text-gray-100' : 'text-black hover:bg-gray-100 focus:bg-gray-100'
						]" @click="handleSort('price_desc')">
							Сначала дорогие
							<svg class="size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24"
								viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
								stroke-linecap="round" stroke-linejoin="round">
								<path d="m3 8 4-4 4 4" />
								<path d="M7 4v16" />
								<path d="M11 12h4" />
								<path d="M11 16h7" />
								<path d="M11 20h10" />
							</svg>
						</button>
						<button type="button" :class="[
							'flex items-center w-full justify-between gap-x-3.5 py-2 px-3 rounded-lg text-sm transition-colors duration-200 cursor-pointer',
							activeSort === 'price_asc' ? 'bg-blue-500 text-gray-100' : 'text-black hover:bg-gray-100 focus:bg-gray-100'
						]" @click="handleSort('price_asc')">
							Сначала дешёвые
							<svg class="size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24"
								viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
								stroke-linecap="round" stroke-linejoin="round">
								<path d="m3 16 4 4 4-4" />
								<path d="M7 20V4" />
								<path d="M11 4h10" />
								<path d="M11 8h7" />
								<path d="M11 12h4" />
							</svg>
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { defineProps, ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const activeSort = ref('')

const props = defineProps({
	onSort: {
		type: Function,
		required: true,
	},
})

const handleSort = (sortOption) => {
	if (activeSort.value === sortOption) {
		activeSort.value = ''
		const query = { ...route.query }
		delete query.sort
		router.push({ query })
	} else {
		activeSort.value = sortOption
		const query = { ...route.query, sort: sortOption }
		router.push({ query })
	}
	
	props.onSort(activeSort.value)
}

onMounted(() => {
	if (window.HSStaticMethods) {
		window.HSStaticMethods.autoInit()
	}
	
	if (route.query.sort) {
		activeSort.value = route.query.sort
	}
})

watch(() => route.query.sort, (newSort) => {
	if (newSort) {
		activeSort.value = newSort
	}
})
</script>
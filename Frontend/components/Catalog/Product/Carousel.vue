<template>
	<div class="w-full md:max-w-[calc(50%_-_48px)] lg:max-w-[calc(40%_-_48px)]">
		<div class="relative">
			<div class="aspect-square bg-gray-100 rounded-xl overflow-hidden">
				<img v-if="currentImage" 
					:src="currentImage" 
					:alt="product?.title || 'Изображение недвижимости'"
					class="w-full h-full object-cover" />
				<div v-else class="w-full h-full flex items-center justify-center bg-gray-100">
					<svg class="w-16 h-16 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
					</svg>
				</div>
			</div>

			<button v-if="images.length > 1" @click="previousImage"
				class="absolute left-4 top-1/2 transform -translate-y-1/2 bg-white/80 hover:bg-white text-gray-800 p-2 rounded-full shadow-lg transition-all duration-200"
				aria-label="Предыдущее изображение">
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
				</svg>
			</button>
			<button v-if="images.length > 1" @click="nextImage"
				class="absolute right-4 top-1/2 transform -translate-y-1/2 bg-white/80 hover:bg-white text-gray-800 p-2 rounded-full shadow-lg transition-all duration-200"
				aria-label="Следующее изображение">
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
				</svg>
			</button>

			<div v-if="images.length > 1" class="absolute bottom-4 right-4 bg-black/50 text-white px-3 py-1 rounded-full text-sm">
				{{ currentIndex + 1 }} / {{ images.length }}
			</div>
		</div>

		<div v-if="images.length > 1" class="mt-4 flex gap-2 overflow-x-auto">
			<button v-for="(image, index) in images" :key="index"
				@click="currentIndex = index"
				class="flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 transition-all duration-200"
				:class="currentIndex === index ? 'border-blue-500' : 'border-gray-200'"
				aria-label="Перейти к изображению">
				<img :src="image" 
					:alt="`Изображение ${index + 1}`"
					class="w-full h-full object-cover" />
			</button>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { api } from '@/store/api.js'

const props = defineProps({
	product: {
		type: Object,
		default: () => ({})
	}
})

const apiStore = api()
const currentIndex = ref(0)

const images = computed(() => {
	const imageArray = []
	
	if (props.product?.images && Array.isArray(props.product.images)) {
		imageArray.push(...props.product.images.map(img => {
			if (!img.url) return null
			
			if (img.url.startsWith('http://') || img.url.startsWith('https://')) {
				return img.url
			}
			
			if (img.url.startsWith('/')) {
				return `${apiStore.url}${img.url.substring(1)}`
			}
			
			return `${apiStore.url}${img.url}`
		}).filter(url => url !== null))
	}
	
	return imageArray
})

const currentImage = computed(() => {
	return images.value[currentIndex.value] || null
})

const nextImage = () => {
	if (images.value.length > 1) {
		currentIndex.value = (currentIndex.value + 1) % images.value.length
	}
}

const previousImage = () => {
	if (images.value.length > 1) {
		currentIndex.value = currentIndex.value === 0 ? images.value.length - 1 : currentIndex.value - 1
	}
}

watch(() => props.product, () => {
	currentIndex.value = 0
}, { deep: true })
</script>
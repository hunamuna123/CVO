<template>
	<button type="button" aria-haspopup="dialog" aria-expanded="false" aria-controls="hs-scale-animation-modal-filter"
		data-hs-overlay="#hs-scale-animation-modal-filter"
		class="lg:hidden py-2.5 px-3 md:px-6 flex justify-center items-center gap-2 font-medium text-sm rounded-full border border-gray-200 bg-white text-black hover:bg-gray-200 focus:outline-none focus:bg-gray-200 transition-colors duration-200">
		Фильтры
	</button>
	<div id="hs-scale-animation-modal-filter"
		class="hs-overlay hidden size-full fixed top-0 start-0 z-[80] overflow-x-hidden overflow-y-auto" role="dialog"
		tabindex="-1" aria-labelledby="hs-scale-animation-modal-filter-label">
		<div
			class="hs-overlay-animation-target hs-overlay-open:scale-100 hs-overlay-open:opacity-100 scale-95 opacity-0 ease-in-out transition-all duration-200 sm:max-w-lg sm:w-full m-3 sm:mx-auto min-h-[calc(100%-3.5rem)] flex items-center">
			<div class="w-full flex flex-col border rounded-xl bg-white border-gray-200">
				<div class="flex justify-between items-center py-3 px-4 border-b border-gray-200">
					<h2 class="text-lg font-semibold">Фильтры</h2>
					<button type="button"
						class="size-8 inline-flex justify-center items-center gap-x-2 rounded-full border border-transparent focus:outline-none disabled:opacity-50 disabled:pointer-events-none bg-gray-200 hover:bg-gray-300 text-black focus:bg-gray-300 transition-colors duration-200"
						aria-label="Close" data-hs-overlay="#hs-scale-animation-modal-filter">
						<span class="sr-only">Закрыть</span>
						<svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24"
							viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
							stroke-linecap="round" stroke-linejoin="round">
							<path d="M18 6 6 18"></path>
							<path d="m6 6 12 12"></path>
						</svg>
					</button>
				</div>
				<div class="overflow-y-auto">
					<CatalogFilters @close-modal="closeModal" />
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'

const closeModal = () => {
	const modal = document.getElementById('hs-scale-animation-modal-filter')
	const backdrop = document.getElementById('hs-scale-animation-modal-filter-backdrop')
	
	if (modal) {
		modal.classList.remove('hs-overlay-open')
		modal.classList.add('hidden')
	}
	
	if (backdrop) {
		backdrop.remove()
	}
	document.body.style.overflow = ''
}

const openModal = () => {
	const modal = document.getElementById('hs-scale-animation-modal-filter')
	if (modal) {
		modal.classList.remove('hidden')
		modal.classList.add('hs-overlay-open')
		document.body.style.overflow = 'hidden'
	}
}

onMounted(() => {
	if (window.HSStaticMethods) {
		window.HSStaticMethods.autoInit()
	}

	const modal = document.getElementById('hs-scale-animation-modal-filter')
	if (modal) {
		modal.addEventListener('click', (e) => {
			if (e.target === modal) {
				closeModal()
			}
		})

		const openButton = document.querySelector('[data-hs-overlay="#hs-scale-animation-modal-filter"]')
		if (openButton) {
			openButton.addEventListener('click', openModal)
		}
	}
})

onUnmounted(() => {
	closeModal()
})
</script>

<style scoped>
.hs-overlay {
	backdrop-filter: blur(4px);
	background-color: rgba(0, 0, 0, 0.5);
}

.hs-overlay-open {
	display: block !important;
}
</style>
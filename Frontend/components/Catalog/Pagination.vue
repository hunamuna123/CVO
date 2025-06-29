<template>
	<nav
		v-if="totalPages > 1"
		class="flex items-center gap-x-1 justify-between"
		aria-label="Pagination"
	>
		<button
			type="button"
			class="min-h-[38px] min-w-[38px] py-2 px-2.5 inline-flex justify-center items-center gap-x-1.5 text-sm rounded-lg text-black bg-gray-100 hover:bg-gray-200 focus:outline-none focus:bg-gray-200 disabled:opacity-50 disabled:pointer-events-none transition-colors duration-200"
			aria-label="Назад"
			:disabled="!hasPrev"
			@click="handlePageChange(currentPage - 1)"
		>
			<svg
				class="shrink-0 size-3.5"
				xmlns="http://www.w3.org/2000/svg"
				width="24"
				height="24"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
			>
				<path d="m15 18-6-6 6-6"></path>
			</svg>
			<span class="hidden sm:block">Назад</span>
		</button>
		<div class="flex items-center gap-x-1">
			<template v-if="totalPages <= 5">
				<button
					v-for="page in totalPages"
					:key="page"
					type="button"
					class="min-h-[38px] min-w-[38px] flex justify-center items-center py-2 px-3 text-sm rounded-lg transition-colors duration-200"
					:class="{
						'bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:bg-blue-700': page === currentPage,
						'text-black bg-gray-100 hover:bg-gray-200 focus:outline-none focus:bg-gray-200': page !== currentPage
					}"
					@click="handlePageChange(page)"
				>
					{{ page }}
				</button>
			</template>
			<template v-else>
				<button
					v-for="page in displayedPages"
					:key="page"
					type="button"
					class="min-h-[38px] min-w-[38px] flex justify-center items-center py-2 px-3 text-sm rounded-lg transition-colors duration-200"
					:class="{
						'bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:bg-blue-700': page === currentPage,
						'text-black bg-gray-100 hover:bg-gray-200 focus:outline-none focus:bg-gray-200': page !== currentPage
					}"
					@click="handlePageChange(page)"
				>
					{{ page }}
				</button>
				<input
					v-if="showInput"
					type="number"
					class="min-h-[38px] py-2 px-2.5 block w-12 border-gray-200 rounded-lg text-sm text-center bg-gray-100 focus:outline-none [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none disabled:opacity-50 disabled:pointer-events-none"
					placeholder="..."
					@change="handleInputChange"
				/>
			</template>
		</div>
		<button
			type="button"
			class="min-h-[38px] min-w-[38px] py-2 px-2.5 inline-flex justify-center items-center gap-x-1.5 text-sm rounded-lg text-black bg-gray-100 hover:bg-gray-200 focus:outline-none focus:bg-gray-200 disabled:opacity-50 disabled:pointer-events-none transition-colors duration-200"
			aria-label="Дальше"
			:disabled="!hasNext"
			@click="handlePageChange(currentPage + 1)"
		>
			<span class="hidden sm:block">Дальше</span>
			<svg
				class="shrink-0 size-3.5"
				xmlns="http://www.w3.org/2000/svg"
				width="24"
				height="24"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
			>
				<path d="m9 18 6-6-6-6"></path>
			</svg>
		</button>
	</nav>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
	currentPage: {
		type: Number,
		required: true
	},
	totalPages: {
		type: Number,
		required: true
	},
	hasPrev: {
		type: Boolean,
		required: true
	},
	hasNext: {
		type: Boolean,
		required: true
	}
});

const emit = defineEmits(['pageChange']);

const showInput = computed(() => {
	return props.totalPages > 5;
});

const displayedPages = computed(() => {
	const pages = [];
	
	if (props.currentPage <= 3) {
		for (let i = 1; i <= Math.min(4, props.totalPages); i++) {
			pages.push(i);
		}
	} else if (props.currentPage >= props.totalPages - 2) {
		for (let i = Math.max(1, props.totalPages - 3); i <= props.totalPages; i++) {
			pages.push(i);
		}
	} else {
		for (let i = props.currentPage - 1; i <= props.currentPage + 1; i++) {
			pages.push(i);
		}
	}
	
	return pages;
});

const handlePageChange = (page) => {
	if (page < 1 || page > props.totalPages) return;
	emit('pageChange', page);
};

const handleInputChange = (event) => {
	const page = parseInt(event.target.value);
	if (page && page > 0 && page <= props.totalPages) {
		handlePageChange(page);
	}
	event.target.value = '';
};
</script>

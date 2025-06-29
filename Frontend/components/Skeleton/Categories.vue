<template>
	<div v-for="n in 6"
		class="w-full flex flex-col gap-6 bg-gray-200 shadow-sm rounded-[20px] p-6 md:p-5"
	>
		<div class="w-full grid grid-cols-2 gap-4">
			<div
				class="w-full aspect-square bg-gray-300 rounded-xl overflow-hidden"
			></div>

		</div>
	</div>
</template>

<script setup>
defineOptions({
	name: 'SkeletonCategories'
})
</script>


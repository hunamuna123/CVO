<template>
	<div
		class="flex flex-col gap-6 w-full lg:w-1/3 bg-gray-200 lg:max-w-sm p-4 skeleton rounded-xl"
	>
		<h2 class="text-lg font-semibold max-lg:hidden">Фильтры</h2>
		<hr class="max-lg:hidden border-gray-300" />
		<div class="flex flex-col gap-6 h-full overflow-y-hidden">
			<div v-for="n in 4" class="space-y-3">
				<div class="space-y-1">
					<h3 class="bg-gray-300 h-6 min-w-[100px] w-1/2 rounded-lg"></h3>
					<p class="bg-gray-300 h-3 rounded-lg"></p>
				</div>
				<div class="w-full bg-gray-300 h-14 rounded-lg"></div>
			</div>
		</div>
		<div class="mt-auto flex flex-col gap-2">
			<span
				v-for="n in 2"
				:key="n"
				class="w-full h-10 bg-gray-300 rounded-xl"
			></span>
		</div>
	</div>
</template>

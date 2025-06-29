<template>
	<div class=" mt-4  w-full flex flex-col gap-10">
		<div class="w-full flex flex-col md:flex-row gap-12">
			<div class="relative md:max-w-[50%] lg:max-w-[40%]">
				<div class="flex flex-col">
					<div
						class="flex justify-center h-full bg-gray-200 aspect-square p-2 rounded-xl overflow-hidden skeleton">
					</div>
					<div class="max-w-full flex gap-2 overflow-x-hidden mt-4">
						<div v-for="n in 5" :key="n"
							class="shrink-0 rounded-xl overflow-hidden cursor-pointer w-[120px] h-[120px] bg-gray-200 aspect-square p-2 skeleton">
						</div>
					</div>
				</div>
			</div>
			<div class="flex flex-col gap-4 w-full md:max-w-[calc(50%_-_48px)] lg:max-w-[calc(60%_-_48px)]">
				<h1 class="w-2/3 h-10 bg-gray-200 rounded-lg skeleton"></h1>
				<h4 class="max-w-[200px] h-5 bg-gray-200 rounded-lg skeleton"></h4>
				<div class="grid sm:grid-cols-2 gap-2 mt-6">
					<h4 v-for="n in 4" :key="n" class="max-w-[200px] h-5 bg-gray-200 rounded-lg skeleton"></h4>
				</div>
				<div class="mt-6 flex items-center justify-between gap-4">
					<div class="flex flex-col gap-1">
						<h1 class="w-[150px] h-10 bg-gray-200 rounded-lg skeleton"></h1>
						<h4 class="w-[150px] h-8 bg-gray-200 rounded-lg skeleton"></h4>
					</div>
					<div class="w-[150px] h-12 bg-gray-200 rounded-lg skeleton"></div>
				</div>
				<div class="flex flex-col gap-2 mt-6">
					<h1 class="max-w-36 h-8 bg-gray-200 rounded-lg skeleton"></h1>
	
				</div>
	

			</div>
		</div>
		<div>
			<div class="overflow-x-auto animate-pulse">
				<table class="min-w-full text-sm text-left text-gray-700">
					<tbody>
						<template v-for="i in 10" :key="i">
							<tr class="border-b">
								<th class="py-6 px-4 w-1/2">
									<div class="h-4 bg-gray-300 rounded w-3/4"></div>
								</th>
								<td class="py-6 px-4">
									<div class="h-4 bg-gray-300 rounded w-full"></div>
								</td>
							</tr>
						</template>
					</tbody>
				</table>
			</div>

		</div>
	</div>
</template>

<template>
    <div v-for="n in 4">
    <div  class="group flex flex-col h-full bg-white border border-gray-200 shadow-2xs rounded-xl">
      <div class="flex items-center justify-center bg-gray-50 p-4 rounded-xl overflow-hidden">
        <div class="w-full h-60 bg-gray-200 animate-pulse rounded-xl"></div>
      </div>
      <div class="p-4 md:p-6 md:pt-2">
        <div class="h-6 bg-gray-200 animate-pulse rounded w-1/4 mb-2"></div>
        <div class="h-6 bg-gray-200 animate-pulse rounded w-3/4 mb-2"></div>
        <div class="h-4 bg-gray-200 animate-pulse rounded w-full"></div>
      </div>
      <div class="mt-auto flex border-t border-gray-200 divide-x divide-gray-200">
        <div class="w-full py-3 px-4 bg-gray-100 animate-pulse rounded-es-xl"></div>
        <div class="w-full py-3 px-4 bg-gray-100 animate-pulse rounded-ee-xl"></div>
      </div>
    </div>
</div>
  </template> 
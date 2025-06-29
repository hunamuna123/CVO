<template>
  <HeaderNavbar/>
  <div class="max-w-[90rem] mt-10 mx-auto px-4 py-10">
    <h1 class="text-3xl font-bold mb-8">Застройщики</h1>
    <div v-if="isLoading" class="text-center py-10 text-gray-400">Загрузка...</div>
    <div v-else-if="error" class="text-center py-10 text-red-500">Ошибка: {{ error }}</div>
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
      <div v-for="dev in developers" :key="dev.id" class="bg-white border border-gray-200 rounded-xl p-6 flex flex-col gap-4 shadow hover:shadow-lg transition">
        <div class="flex items-center gap-4">
          <img v-if="dev.logo_url" :src="getFullImageUrl(dev.logo_url)" :alt="dev.company_name" class="w-14 h-14 rounded-full object-cover bg-gray-100 border" />
          <div>
            <div class="flex items-center gap-2">
              <span class="text-lg font-semibold">{{ dev.company_name }}</span>
              <span v-if="dev.is_verified" class="px-2 py-0.5 text-xs rounded bg-green-100 text-green-700">Верифицирован</span>
            </div>
            <div class="flex items-center gap-2 mt-1 text-sm text-gray-500">
              <span>★ {{ dev.rating }}</span>
              <span>({{ dev.reviews_count }} отзывов)</span>
            </div>
          </div>
        </div>
        <div class="text-gray-500 text-sm line-clamp-2 min-h-[40px]">{{ dev.description }}</div>
        <div class="flex items-center gap-4 mt-auto">
          <span class="text-xs text-gray-400">Проектов: <b class="text-gray-700">{{ dev.properties_count }}</b></span>
          <NuxtLink :to="`/developers/${dev.id}`" class="ml-auto px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">Подробнее</NuxtLink>
        </div>
      </div>
    </div>
  </div>
  <Footer/>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/store/api.js'

const apiStore = api()
const developers = ref([])
const isLoading = ref(true)
const error = ref(null)

const getFullImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  if (url.startsWith('/')) return `${apiStore.url}${url.substring(1)}`
  return `${apiStore.url}${url}`
}

onMounted(async () => {
  isLoading.value = true
  try {
    const res = await fetch(`${apiStore.url}api/v1/developers/all`)
    if (!res.ok) throw new Error('Ошибка загрузки застройщиков')
    developers.value = await res.json()
  } catch (e) {
    error.value = e.message
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style> 
<template>
  <NuxtLink :to="`/developers/${developer.id}`" class="block group">
    <div class="border border-gray-200 rounded-xl p-6 flex flex-col items-center bg-white hover:shadow-2xl transition-shadow group-hover:border-blue-400">
      <!-- Аватар/иконка -->
      <div class="w-20 h-20 bg-gray-100 rounded mb-4 flex items-center justify-center">
        <img 
          class="w-16 h-16 object-cover rounded" 
          :src="formattedLogoUrl" 
          :alt="developer.company_name" 
        />
      </div>
      <!-- Название -->
      <h3 class="font-bold text-xl text-gray-900 mb-2">{{ developer.company_name }}</h3>
      <!-- Рейтинг -->
      <div class="flex items-center mb-1">
        <svg class="w-5 h-5 text-yellow-400 mr-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.967a1 1 0 00.95.69h4.175c.969 0 1.371 1.24.588 1.81l-3.38 2.455a1 1 0 00-.364 1.118l1.287 3.966c.3.922-.755 1.688-1.54 1.118l-3.38-2.455a1 1 0 00-1.175 0l-3.38 2.455c-.784.57-1.838-.196-1.54-1.118l1.287-3.966a1 1 0 00-.364-1.118L2.05 9.394c-.783-.57-.38-1.81.588-1.81h4.175a1 1 0 00.95-.69l1.286-3.967z"/>
        </svg>
        <span class="text-lg font-semibold text-gray-800">{{ developer.rating }}</span>
      </div>
      <!-- Количество проектов -->
      <div class="flex items-center text-gray-600 mb-4">
        <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" :stroke-width="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 7V6a2 2 0 012-2h2a2 2 0 012 2v1m10 0V6a2 2 0 00-2-2h-2a2 2 0 00-2 2v1m-6 4h16m-2 4h2a2 2 0 002-2v-5a2 2 0 00-2-2h-2a2 2 0 00-2 2v5a2 2 0 002 2zm-6 4h2a2 2 0 002-2v-5a2 2 0 00-2-2h-2a2 2 0 00-2 2v5a2 2 0 002 2z"/>
        </svg>
        <span>{{ developer.properties_count }} проектов</span>
      </div>
      <!-- Кнопка Верифицирован -->
      <div class="mt-auto">
        <span 
          v-if="developer.is_verified"
          class="inline-flex items-center px-4 py-1 rounded-full bg-green-500 text-white font-semibold text-sm"
        >
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" :stroke-width="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
          </svg>
          Верифицирован
        </span>
        <span 
          v-else
          class="inline-flex items-center px-4 py-1 rounded-full bg-gray-400 text-white font-semibold text-sm"
        >
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" :stroke-width="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"/>
          </svg>
          {{ getVerificationStatusText(developer.verification_status) }}
        </span>
      </div>
    </div>
  </NuxtLink>
</template>

<script setup>
import { api } from '~/store/api'

const props = defineProps({
  developer: {
    type: Object,
    required: true,
    default: () => ({
      id: '',
      company_name: '',
      logo_url: '',
      rating: '0.0',
      reviews_count: 0,
      properties_count: 0,
      is_verified: false,
      verification_status: 'PENDING',
      description: ''
    })
  }
})

const apiStore = api()

const getVerificationStatusText = (status) => {
  const statusMap = {
    'PENDING': 'На рассмотрении',
    'REJECTED': 'Отклонено',
    'VERIFIED': 'Верифицирован'
  }
  return statusMap[status] || 'Неизвестно'
}

const formattedLogoUrl = computed(() => {
  if (!props.developer.logo_url) return '/bg.jpg'
  
  const logoUrl = props.developer.logo_url
  
  // Если URL уже полный (начинается с http/https), возвращаем как есть
  if (logoUrl.startsWith('http://') || logoUrl.startsWith('https://')) {
    return logoUrl
  }
  
  // Если URL относительный, добавляем базовый URL из API store
  const baseUrl = apiStore.url.replace(/\/$/, '') // Убираем trailing slash если есть
  return `${baseUrl}${logoUrl.startsWith('/') ? logoUrl : `/${logoUrl}`}`
})
</script>
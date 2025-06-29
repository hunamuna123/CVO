<template>
	<HeaderNavbar/>
  <NuxtLayout>
    <div class="w-full min-h-[90vh] py-8 mt-10">
      <div class="max-w-7xl mx-auto px-4">
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900">Мои бронирования</h1>
          <p class="text-gray-600 mt-2">Управляйте своими бронированиями недвижимости</p>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="space-y-4">
          <div v-for="i in 3" :key="i" class="bg-white border border-gray-200 rounded-xl p-6 animate-pulse">
            <div class="flex justify-between items-start mb-4">
              <div class="h-4 bg-gray-200 rounded w-1/3"></div>
              <div class="h-6 bg-gray-200 rounded w-20"></div>
            </div>
            <div class="space-y-3">
              <div class="h-3 bg-gray-200 rounded w-3/4"></div>
              <div class="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          </div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-6">
          <div class="flex items-center">
            <svg class="w-5 h-5 text-red-400 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
            </svg>
            <div>
              <h3 class="text-sm font-medium text-red-800">Ошибка загрузки</h3>
              <p class="text-sm text-red-700 mt-1">{{ error }}</p>
            </div>
          </div>
          <button 
            @click="fetchBookings"
            class="mt-4 px-4 py-2 bg-red-600 text-white rounded-xl hover:bg-red-700 transition-colors"
          >
            Попробовать снова
          </button>
        </div>

        <!-- Empty State -->
        <div v-else-if="bookings.length === 0" class="bg-white border border-gray-200 rounded-xl p-12 text-center">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <h3 class="mt-4 text-lg font-medium text-gray-900">Нет бронирований</h3>
          <p class="mt-2 text-gray-500">У вас пока нет активных бронирований недвижимости.</p>
          <div class="mt-6">
            <NuxtLink 
              to="/catalog"
              class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
            >
              Найти недвижимость
            </NuxtLink>
          </div>
        </div>

        <!-- Bookings List -->
        <div v-else class="space-y-4">
          <div v-for="booking in bookings" :key="booking.id" class="bg-white border border-gray-200 rounded-xl p-6">
            <div class="flex justify-between items-start mb-4">
              <div>
                <h3 class="text-lg font-semibold text-gray-900">
                  {{ booking.property?.title || booking.property?.name || 'Название не указано' }}
                </h3>
                <p class="text-sm text-gray-500 mt-1">
                  ID бронирования: {{ booking.id }}
                </p>
              </div>
              <span 
                :class="[
                  'px-3 py-1 rounded-full text-xs font-medium',
                  getStatusClass(booking.status)
                ]"
              >
                {{ getStatusText(booking.status) }}
              </span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
              <div>
                <p class="text-sm font-medium text-gray-500">Дата бронирования</p>
                <p class="text-sm text-gray-900">{{ formatDate(booking.created_at) }}</p>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-500">Дата заезда</p>
                <p class="text-sm text-gray-900">{{ formatDate(booking.check_in_date) }}</p>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-500">Дата выезда</p>
                <p class="text-sm text-gray-900">{{ formatDate(booking.check_out_date) }}</p>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-500">Стоимость</p>
                <p class="text-sm text-gray-900">{{ formatPrice(booking.total_price) }} ₽</p>
              </div>
            </div>

            <div v-if="booking.property" class="mb-4">
              <p class="text-sm font-medium text-gray-500 mb-2">Информация о недвижимости:</p>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span class="text-gray-500">Адрес:</span>
                  <span class="text-gray-900 ml-2">{{ booking.property.address || 'Не указан' }}</span>
                </div>
                <div>
                  <span class="text-gray-500">Тип:</span>
                  <span class="text-gray-900 ml-2">{{ booking.property.property_type || 'Не указан' }}</span>
                </div>
                <div>
                  <span class="text-gray-500">Комнаты:</span>
                  <span class="text-gray-900 ml-2">{{ booking.property.rooms || 'Не указано' }}</span>
                </div>
              </div>
            </div>

            <div class="flex justify-between items-center">
              <NuxtLink 
                :to="`/catalog/${booking.property?.id}`"
                class="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                Посмотреть объект →
              </NuxtLink>
              
              <button 
                v-if="booking.status === 'PENDING' || booking.status === 'CONFIRMED'"
                @click="cancelBooking(booking.id)"
                class="px-4 py-2 bg-red-600 text-white rounded-xl hover:bg-red-700 transition-colors text-sm"
              >
                Отменить бронирование
              </button>
            </div>
          </div>

          <!-- Pagination -->
          <div v-if="totalPages > 1" class="mt-8">
            <CatalogPagination 
              :current-page="currentPage"
              :total-pages="totalPages"
              :total-items="totalItems"
              @page-change="changePage"
            />
          </div>
        </div>
      </div>
    </div>
  </NuxtLayout>
  <Footer/>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/store/api.js'
import { useCookie } from '#app'

definePageMeta({
  middleware: 'require-auth'
})

const route = useRoute()
const router = useRouter()
const apiStore = api()

const bookings = ref([])
const isLoading = ref(true)
const currentPage = ref(1)
const totalPages = ref(1)
const totalItems = ref(0)
const error = ref(null)

const getAuthHeaders = () => {
  const accessToken = useCookie('access_token')
  const headers = {
    'accept': 'application/json',
  }
  
  if (accessToken.value) {
    headers['Authorization'] = `Bearer ${accessToken.value}`
  }
  
  return headers
}

const refreshTokens = async () => {
  const refreshToken = useCookie('refresh_token')
  const accessToken = useCookie('access_token')
  
  if (!refreshToken.value) {
    throw new Error('Нет refresh токена')
  }
  
  try {
    const response = await fetch(`${apiStore.url}api/v1/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        token_refresh: refreshToken.value
      })
    })

    if (response.ok) {
      const data = await response.json()
      if (data.access_token && data.refresh_token) {
        accessToken.value = data.access_token
        refreshToken.value = data.refresh_token
        return true
      }
    }
    return false
  } catch (error) {
    console.error('Ошибка при обновлении токенов:', error)
    return false
  }
}

const makeAuthenticatedRequest = async (url, options = {}) => {
  let headers = getAuthHeaders()
  
  const requestOptions = {
    ...options,
    headers: { ...headers, ...options.headers }
  }
  
  let response = await fetch(url, requestOptions)
  
  if (response.status === 401) {
    const refreshed = await refreshTokens()
    if (refreshed) {
      headers = getAuthHeaders()
      requestOptions.headers = { ...headers, ...options.headers }
      response = await fetch(url, requestOptions)
    } else {
      const accessToken = useCookie('access_token')
      const refreshToken = useCookie('refresh_token')
      accessToken.value = null
      refreshToken.value = null
      router.push('/auth/login')
      throw new Error('Сессия истекла. Пожалуйста, войдите снова.')
    }
  }
  
  return response
}

const fetchBookings = async () => {
  isLoading.value = true
  error.value = null
  
  try {
    const query = new URLSearchParams({
      page: currentPage.value.toString(),
      limit: '20'
    })

    const response = await makeAuthenticatedRequest(`${apiStore.url}api/v1/bookings/my?${query}`)

    if (!response.ok) {
      throw new Error(`Ошибка при загрузке бронирований: ${response.status}`)
    }

    const data = await response.json()
    
    if (Array.isArray(data)) {
      bookings.value = data
      totalPages.value = 1
      totalItems.value = data.length
    } else if (data.results && Array.isArray(data.results)) {
      bookings.value = data.results
      if (data.pagination) {
        currentPage.value = data.pagination.page || 1
        totalPages.value = data.pagination.pages || 1
        totalItems.value = data.pagination.total || data.results.length
      }
    } else {
      bookings.value = data.bookings || data.items || []
      if (data.pagination) {
        currentPage.value = data.pagination.page || 1
        totalPages.value = data.pagination.pages || 1
        totalItems.value = data.pagination.total || bookings.value.length
      }
    }
  } catch (error) {
    console.error('Error fetching bookings:', error)
    error.value = error.message
    bookings.value = []
  } finally {
    isLoading.value = false
  }
}

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  const query = { ...route.query, page: page.toString() }
  router.push({ query })
}

const cancelBooking = async (bookingId) => {
  if (!confirm('Вы уверены, что хотите отменить это бронирование?')) return
  
  try {
    const response = await makeAuthenticatedRequest(`${apiStore.url}api/v1/bookings/${bookingId}/cancel`, {
      method: 'POST'
    })

    if (!response.ok) {
      throw new Error(`Ошибка при отмене бронирования: ${response.status}`)
    }

    await fetchBookings()
    alert('Бронирование успешно отменено')
  } catch (error) {
    console.error('Error canceling booking:', error)
    alert(`Ошибка при отмене бронирования: ${error.message}`)
  }
}

const getStatusClass = (status) => {
  switch (status) {
    case 'PENDING':
      return 'bg-yellow-100 text-yellow-800'
    case 'CONFIRMED':
      return 'bg-green-100 text-green-800'
    case 'CANCELLED':
      return 'bg-red-100 text-red-800'
    case 'COMPLETED':
      return 'bg-blue-100 text-blue-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'PENDING':
      return 'Ожидает подтверждения'
    case 'CONFIRMED':
      return 'Подтверждено'
    case 'CANCELLED':
      return 'Отменено'
    case 'COMPLETED':
      return 'Завершено'
    default:
      return status
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Не указана'
  return new Date(dateString).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatPrice = (price) => {
  if (!price) return '0'
  return new Intl.NumberFormat('ru-RU').format(parseFloat(price))
}

onMounted(() => {
  const page = parseInt(route.query.page) || 1
  currentPage.value = page
  fetchBookings()
})

watch(() => route.query.page, (newPage) => {
  if (newPage) {
    currentPage.value = parseInt(newPage)
    fetchBookings()
  }
})
</script>

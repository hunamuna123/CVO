<template>
  <div
    class="w-full flex flex-col gap-5 bg-white border border-gray-200 shadow-sm rounded-[20px] p-4 md:p-5 relative transition-transform duration-200 overflow-hidden">
    <div class="w-full grid grid-cols-2 gap-4">
      <div class="w-full aspect-square bg-gray-100 rounded-xl overflow-hidden">
        <img v-if="product.main_image_url" class="w-full h-full object-cover"
          :src="formattedImageUrl" :alt="product.title" />
        <div v-else class="w-full h-full flex items-center justify-center bg-gray-100">
          <svg class="w-12 h-12 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
      </div>
      <div class="flex flex-col gap-1 h-full">
        <p class="text-gray-500">
          {{ getPropertyTypeName(product.property_type) }}
        </p>
        <h4 class="text-xl line-clamp-2">
          {{ product.title }}
        </h4>
        <p class="mt-0.5 line-clamp-3">
          {{ product.city }}{{ product.district ? `, ${product.district}` : '' }}
        </p>
        <div class="text-2xl font-bold mt-auto">
          {{ formatPrice(product.price) }} ₽
        </div>
      </div>
    </div>

    <div class="flex gap-2">
      <NuxtLink :to="'/catalog/' + product.id" class="flex-1">
        <button type="button"
          class="w-full py-2.5 px-6 justify-center items-center font-medium text-sm rounded-xl border border-gray-300 text-gray-700 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 transition-colors duration-200 cursor-pointer">
          Подробнее
        </button>
      </NuxtLink>
      <button @click="showBookingModal = true"
        type="button"
        class="flex-1 py-2.5 px-6 justify-center items-center font-medium text-sm rounded-xl bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:bg-blue-700 transition-colors duration-200 cursor-pointer">
        Забронировать
      </button>
    </div>

    <!-- Booking Modal -->
    <div v-if="showBookingModal" 
         class="fixed inset-0 flex items-center justify-center z-50 p-4"
         style="background-color: rgba(0, 0, 0, 0.1);"
         @click="showBookingModal = false">
      <div class="bg-white rounded-xl max-w-md w-full max-h-[90vh] overflow-y-auto shadow-2xl" @click.stop>
        <div class="p-6">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-semibold">Бронирование</h2>
            <button @click="showBookingModal = false" class="text-gray-400 hover:text-gray-600 transition-colors">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <form @submit.prevent="submitBooking" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Имя *</label>
              <input 
                v-model="bookingForm.full_name"
                type="text" 
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ваше имя"
              >
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Телефон *</label>
              <input 
                v-model="bookingForm.contact_phone"
                type="tel" 
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="+7 (999) 123-45-67"
              >
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Email *</label>
              <input 
                v-model="bookingForm.contact_email"
                type="email" 
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="your@email.com"
              >
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Промокод</label>
              <input 
                v-model="bookingForm.promo_code"
                type="text" 
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Введите промокод (необязательно)"
              >
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Комментарий</label>
              <textarea 
                v-model="bookingForm.notes"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Дополнительная информация"
              ></textarea>
            </div>

            <div class="flex gap-3 pt-4">
              <button 
                type="button"
                @click="showBookingModal = false"
                class="flex-1 py-2 px-4 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Отмена
              </button>
              <button 
                type="submit"
                :disabled="isSubmitting"
                class="flex-1 py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {{ isSubmitting ? 'Отправка...' : 'Забронировать' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, computed, ref } from 'vue'
import { api } from '@/store/api.js'
import { useCookie } from '#app'

const props = defineProps({
  product: {
    type: Object,
    required: true,
  },
})

const apiStore = api()
const showBookingModal = ref(false)
const isSubmitting = ref(false)

const bookingForm = ref({
  full_name: '',
  contact_phone: '',
  contact_email: '',
  promo_code: '',
  notes: '',
  property_id: props.product?.id || '',
  utm_source: '',
  utm_medium: '',
  utm_campaign: ''
})

const getPropertyTypeName = (type) => {
  switch(type) {
    case 'APARTMENT': return 'Квартира'
    case 'HOUSE': return 'Дом'
    case 'COMMERCIAL': return 'Коммерческая'
    default: return 'Недвижимость'
  }
}

const formattedImageUrl = computed(() => {
  if (!props.product.main_image_url) return ''
  const imageUrl = props.product.main_image_url
  
  // Если URL уже полный (начинается с http/https), возвращаем как есть
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl
  }
  
  // Если URL относительный, добавляем базовый URL из API store
  const baseUrl = apiStore.url.replace(/\/$/, '') // Убираем trailing slash если есть
  return `${baseUrl}${imageUrl.startsWith('/') ? imageUrl : `/${imageUrl}`}`
})

const formatPrice = (price) => {
  if (!price) return '0'
  return new Intl.NumberFormat('ru-RU').format(parseFloat(price))
}

const submitBooking = async () => {
  isSubmitting.value = true
  
  try {
    const accessToken = useCookie('access_token')
    const headers = {
      'Content-Type': 'application/json',
      'accept': 'application/json',
    }
    
    if (accessToken.value) {
      headers['Authorization'] = `Bearer ${accessToken.value}`
    }

    const response = await fetch(`${apiStore.url}api/v1/bookings`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        ...bookingForm.value,
        property_id: props.product.id
      })
    })

    if (!response.ok) {
      throw new Error('Ошибка при создании бронирования')
    }

    const data = await response.json()
    alert('Бронирование успешно создано!')
    showBookingModal.value = false
    
    // Сброс формы
    bookingForm.value = {
      full_name: '',
      contact_phone: '',
      contact_email: '',
      promo_code: '',
      notes: '',
      property_id: props.product?.id || '',
      utm_source: '',
      utm_medium: '',
      utm_campaign: ''
    }
  } catch (error) {
    console.error('Error creating booking:', error)
    alert('Ошибка при создании бронирования')
  } finally {
    isSubmitting.value = false
  }
}
</script>

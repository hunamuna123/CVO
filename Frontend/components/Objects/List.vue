<template>
    <div class="pt-0 lg:pt-0 lg:py-14 pb-3 lg:pb-3">
        <div
            class="w-full flex flex-col bg-white border border-gray-200 shadow-sm rounded-[20px] p-0 relative transition-transform duration-200 overflow-hidden">
            <div
                class="relative w-full aspect-[2/1] bg-gray-100 rounded-t-[20px] overflow-hidden flex items-center justify-center">
                <div class="absolute top-4 left-4 flex gap-2 z-10">
                    <span
                        v-if="property.developer_verified"
                        class="bg-green-500 text-white text-xs font-semibold px-3 py-1 rounded-full">Верифицирован</span>
                    <span 
                        v-if="isGoodPrice"
                        class="bg-blue-100 text-blue-700 text-xs font-semibold px-3 py-1 rounded-full">Выгодная цена</span>
                </div>
                <button
                    @click="toggleFavorite"
                    class="absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-full bg-white shadow hover:bg-gray-100 z-10">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                        stroke="currentColor" 
                        :class="['w-5 h-5', isFavorite ? 'text-red-500 fill-current' : 'text-gray-400']">
                        <path stroke-linecap="round" stroke-linejoin="round"
                            d="M16.5 6.75a4.5 4.5 0 00-6.364 0l-.386.386-.386-.386a4.5 4.5 0 10-6.364 6.364l.386.386L12 21.75l8.25-8.25.386-.386a4.5 4.5 0 000-6.364z" />
                    </svg>
                </button>
                <img :src="formattedImageUrl" :alt="property.title" class="object-cover w-full h-full" />
                <div class="absolute left-4 bottom-4 bg-white shadow rounded-xl p-3 flex flex-col items-start">
                    <div class="text-2xl font-bold">{{ formatPrice(property.price) }} {{ property.currency }}</div>
                    <div class="text-xs text-gray-400">{{ formatPrice(property.price_per_sqm) }} {{ property.currency }}/м²</div>
                </div>
            </div>
            <div class="flex flex-col h-48 gap-2 p-4 justify-between">
                <div class="text-sm text-gray-500 flex items-center gap-1">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                        stroke="currentColor" class="w-4 h-4 text-blue-500">
                        <path stroke-linecap="round" stroke-linejoin="round"
                            d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round"
                            d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25s-7.5-4.108-7.5-11.25a7.5 7.5 0 1115 0z" />
                    </svg>
                    {{ property.district }}, {{ property.city }}
                </div>
                <h4 class="text-xl font-semibold leading-tight">{{ property.title }}</h4>
                <div class="flex gap-4 mt-2">
                    <div class="flex items-center gap-1 text-gray-500 text-sm">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" 
                            stroke="currentColor" class="w-4 h-4">
                            <path stroke-linecap="round" stroke-linejoin="round" 
                                d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 018.25 20.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 0118 20.25h-2.25a2.25 2.25 0 0113.5 18v-2.25z" />
                        </svg>
                        {{ property.rooms_count }}
                    </div>
                    <div class="flex items-center gap-1 text-gray-500 text-sm">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" 
                            stroke="currentColor" class="w-4 h-4">
                            <path stroke-linecap="round" stroke-linejoin="round" 
                                d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.314-.488-1.314-1.314 0-.726.589-1.314 1.314-1.314.725 0 1.314.588 1.314 1.314 0 .726-.589 1.314-1.314 1.314z" />
                        </svg>
                        {{ property.floor }}/{{ property.total_floors }}
                    </div>
                    <div class="flex items-center gap-1 text-gray-500 text-sm">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" 
                            stroke="currentColor" class="w-4 h-4">
                            <path stroke-linecap="round" stroke-linejoin="round" 
                                d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h12m-.75 4.5H21m-6.75 4.5h6.75m-6.75 4.5h6.75m-6.75 4.5h6.75" />
                        </svg>
                        {{ property.total_area }} м²
                    </div>
                </div>

                <div class="flex justify-between items-center">
                    <div class="text-sm text-gray-400">{{ property.developer_name }}</div>
                    <NuxtLink :to="`/catalog/${property.id}`">
                        <button type="button"
                            class="py-2.5 px-6 font-medium text-sm rounded-xl bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:bg-blue-700 transition-colors duration-200 cursor-pointer">
                            Подробнее
                        </button>
                    </NuxtLink>
                </div>

            </div>
        </div>
    </div>
</template>

<script setup>
import { api } from '~/store/api'

const props = defineProps({
  property: {
    type: Object,
    required: true,
    default: () => ({
      id: '',
      title: '',
      property_type: 'APARTMENT',
      deal_type: 'SALE',
      price: '0',
      price_per_sqm: '0',
      currency: '₽',
      city: '',
      district: '',
      total_area: 0,
      rooms_count: 0,
      floor: 0,
      total_floors: 0,
      has_parking: false,
      renovation_type: 'NONE',
      status: 'DRAFT',
      is_featured: false,
      views_count: 0,
      favorites_count: 0,
      main_image_url: '',
      developer_id: '',
      developer_name: '',
      developer_verified: false,
      created_at: '',
      updated_at: ''
    })
  }
})

const apiStore = api()

const isFavorite = ref(false)

const toggleFavorite = () => {
  isFavorite.value = !isFavorite.value
}

const formatPrice = (price) => {
  if (!price) return '0'
  const numPrice = parseFloat(price)
  return numPrice.toLocaleString('ru-RU')
}

const isGoodPrice = computed(() => {
  const pricePerSqm = parseFloat(props.property.price_per_sqm)
  return pricePerSqm > 0 && pricePerSqm < 200000
})

const formattedImageUrl = computed(() => {
  if (!props.property.main_image_url) return '/bg.jpg'
  
  const imageUrl = props.property.main_image_url
  
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl
  }
  
  const baseUrl = apiStore.url.replace(/\/$/, '')
  return `${baseUrl}${imageUrl.startsWith('/') ? imageUrl : `/${imageUrl}`}`
})
</script>
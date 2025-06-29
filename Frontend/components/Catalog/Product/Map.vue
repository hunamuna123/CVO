<template>
  <div class="w-full">
    <div class="bg-white rounded-2xl shadow-lg overflow-hidden">
      <!-- Заголовок карты -->
      <div class="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
            </svg>
          </div>
          <div>
            <h3 class="text-xl font-bold">Расположение объекта</h3>
            <p class="text-blue-100 text-sm">Интерактивная карта с 3D видом</p>
          </div>
        </div>
      </div>

      <!-- Контейнер карты -->
      <div class="relative">
        <!-- 3D эффект с градиентом -->
        <div class="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-purple-50 opacity-30"></div>
        
        <!-- Основная карта -->
        <div 
          ref="mapContainer" 
          class="w-full h-96 relative z-10"
          :class="{ 'animate-pulse': isLoading }"
        ></div>

        <!-- Индикатор загрузки -->
        <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center bg-white/80 z-20">
          <div class="flex flex-col items-center gap-3">
            <div class="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            <p class="text-gray-600 font-medium">Загружаем карту...</p>
          </div>
        </div>

        <!-- Информационная панель -->
        <div class="absolute top-4 right-4 bg-white/95 backdrop-blur-sm rounded-xl shadow-lg p-4 max-w-xs z-30">
          <div class="flex items-start gap-3">
            <div class="w-3 h-3 bg-green-500 rounded-full mt-2 animate-pulse"></div>
            <div>
              <h4 class="font-semibold text-gray-800">Объект найден</h4>
              <p class="text-sm text-gray-600 mt-1">
                {{ address || 'Адрес загружается...' }}
              </p>
              <div class="flex gap-2 mt-2">
                <span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                  {{ coordinates.lat.toFixed(6) }}, {{ coordinates.lng.toFixed(6) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Контролы карты -->
        <div class="absolute bottom-4 left-4 flex flex-col gap-2 z-30">
          <button 
            @click="zoomIn"
            class="w-10 h-10 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg flex items-center justify-center hover:bg-white transition-all duration-200"
          >
            <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </button>
          <button 
            @click="zoomOut"
            class="w-10 h-10 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg flex items-center justify-center hover:bg-white transition-all duration-200"
          >
            <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
            </svg>
          </button>
          <button 
            @click="resetView"
            class="w-10 h-10 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg flex items-center justify-center hover:bg-white transition-all duration-200"
          >
            <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>

        <!-- 3D переключатель -->
        <div class="absolute bottom-4 right-4 z-30">
          <button 
            @click="toggle3D"
            class="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg shadow-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            {{ is3D ? '2D' : '3D' }}
          </button>
        </div>
      </div>

      <!-- Дополнительная информация -->
      <div class="p-6 bg-gray-50">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-600">Координаты</p>
              <p class="font-medium text-gray-800">{{ coordinates.lat.toFixed(6) }}, {{ coordinates.lng.toFixed(6) }}</p>
            </div>
          </div>
          
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-1.447-.894L15 4m0 13V4m-6 3l6-3" />
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-600">Масштаб</p>
              <p class="font-medium text-gray-800">{{ currentZoom }}x</p>
            </div>
          </div>
          
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-600">Режим</p>
              <p class="font-medium text-gray-800">{{ is3D ? '3D' : '2D' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

const mapContainer = ref(null)
const map = ref(null)
const marker = ref(null)
const isLoading = ref(true)
const is3D = ref(false)
const currentZoom = ref(13)

// Координаты по умолчанию (Москва)
const coordinates = ref({
  lat: 55.7558,
  lng: 37.6176
})

// Адрес объекта
const address = computed(() => {
  if (props.product?.address) {
    return props.product.address
  }
  if (props.product?.location) {
    return props.product.location
  }
  return 'Адрес не указан'
})

// Инициализация карты
const initMap = async () => {
  if (typeof window === 'undefined') return
  
  try {
    const L = await import('leaflet')
    
    // Установка координат из продукта или использование дефолтных
    if (props.product?.latitude && props.product?.longitude) {
      coordinates.value = {
        lat: parseFloat(props.product.latitude),
        lng: parseFloat(props.product.longitude)
      }
    }

    // Создание карты
    map.value = L.map(mapContainer.value, {
      center: [coordinates.value.lat, coordinates.value.lng],
      zoom: currentZoom.value,
      zoomControl: false,
      attributionControl: false
    })

    // Добавление тайлов карты (OpenStreetMap)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map.value)

    // Создание кастомного маркера
    const customIcon = L.divIcon({
      className: 'custom-marker',
      html: `
        <div class="relative">
          <div class="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full shadow-lg flex items-center justify-center">
            <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gradient-to-r from-blue-600 to-purple-600 rotate-45"></div>
        </div>
      `,
      iconSize: [32, 32],
      iconAnchor: [16, 32]
    })

    // Добавление маркера
    marker.value = L.marker([coordinates.value.lat, coordinates.value.lng], {
      icon: customIcon
    }).addTo(map.value)

    // Добавление всплывающего окна
    marker.value.bindPopup(`
      <div class="p-2">
        <h3 class="font-bold text-gray-800">${props.product?.title || 'Объект недвижимости'}</h3>
        <p class="text-sm text-gray-600">${address.value}</p>
      </div>
    `)

    // Обновление зума при изменении
    map.value.on('zoomend', () => {
      currentZoom.value = map.value.getZoom()
    })

    isLoading.value = false

  } catch (error) {
    console.error('Ошибка загрузки карты:', error)
    isLoading.value = false
  }
}

// Функции управления картой
const zoomIn = () => {
  if (map.value) {
    map.value.zoomIn()
  }
}

const zoomOut = () => {
  if (map.value) {
    map.value.zoomOut()
  }
}

const resetView = () => {
  if (map.value) {
    map.value.setView([coordinates.value.lat, coordinates.value.lng], 13)
  }
}

const toggle3D = () => {
  is3D.value = !is3D.value
  // Здесь можно добавить логику переключения на 3D карты
  // Например, переключение на Google Maps 3D или другие сервисы
}

// Стили для Leaflet
const addMapStyles = () => {
  if (typeof window === 'undefined') return
  
  const link = document.createElement('link')
  link.rel = 'stylesheet'
  link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'
  link.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY='
  link.crossOrigin = ''
  document.head.appendChild(link)
}

// Наблюдение за изменениями продукта
watch(() => props.product, (newProduct) => {
  if (newProduct && map.value) {
    if (newProduct.latitude && newProduct.longitude) {
      const newCoords = {
        lat: parseFloat(newProduct.latitude),
        lng: parseFloat(newProduct.longitude)
      }
      coordinates.value = newCoords
      map.value.setView([newCoords.lat, newCoords.lng], currentZoom.value)
      marker.value.setLatLng([newCoords.lat, newCoords.lng])
    }
  }
}, { deep: true })

onMounted(() => {
  addMapStyles()
  initMap()
})

onUnmounted(() => {
  if (map.value) {
    map.value.remove()
  }
})
</script>

<style scoped>
.custom-marker {
  background: transparent;
  border: none;
}

/* Анимации для карты */
@keyframes mapFadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.w-full.h-96 {
  animation: mapFadeIn 0.5s ease-out;
}

/* Стили для Leaflet */
:deep(.leaflet-container) {
  font-family: inherit;
}

:deep(.leaflet-popup-content-wrapper) {
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

:deep(.leaflet-popup-content) {
  margin: 0;
  padding: 0;
}

:deep(.leaflet-popup-tip) {
  background: white;
}
</style> 
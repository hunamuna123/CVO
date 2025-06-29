<template>
  <div class="w-full">
    <div class="bg-white rounded-2xl shadow-lg overflow-hidden">
      <!-- Заголовок 3D карты -->
      <div class="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 p-6 text-white relative overflow-hidden">
        <!-- Анимированный фон -->
        <div class="absolute inset-0 bg-gradient-to-r from-indigo-600/20 via-purple-600/20 to-pink-600/20 animate-pulse"></div>
        <div class="relative z-10">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
              <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
              </svg>
            </div>
            <div>
              <h3 class="text-2xl font-bold">3D Карта объекта</h3>
              <p class="text-indigo-100 text-sm">Интерактивный 3D вид с детализацией</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Контейнер 3D карты -->
      <div class="relative">
        <!-- 3D сцена -->
        <div class="w-full h-[500px] relative z-10 bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 overflow-hidden">
          <!-- 3D контейнер -->
          <div 
            ref="scene3D"
            class="w-full h-full relative transform-style-preserve-3d perspective-1000"
            :style="{ transform: `rotateX(${rotationX}deg) rotateY(${rotationY}deg) scale(${zoom})` }"
          >
            <!-- Земля -->
            <div class="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-96 h-96 bg-gradient-to-br from-green-400 to-green-600 rounded-full opacity-80 shadow-2xl"></div>
            
            <!-- Основное здание -->
            <div class="absolute bottom-20 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <div class="relative group">
                <!-- Основание здания -->
                <div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-700 rounded-lg shadow-xl transform-gpu transition-all duration-300 hover:scale-110 cursor-pointer">
                  <!-- Окна -->
                  <div class="absolute top-2 left-2 w-3 h-4 bg-yellow-300 rounded opacity-80 animate-pulse"></div>
                  <div class="absolute top-2 right-2 w-3 h-4 bg-yellow-300 rounded opacity-80 animate-pulse" style="animation-delay: 0.5s"></div>
                  <div class="absolute top-8 left-2 w-3 h-4 bg-yellow-300 rounded opacity-80 animate-pulse" style="animation-delay: 1s"></div>
                  <div class="absolute top-8 right-2 w-3 h-4 bg-yellow-300 rounded opacity-80 animate-pulse" style="animation-delay: 1.5s"></div>
                </div>
                <!-- Крыша -->
                <div class="absolute -top-2 left-1/2 transform -translate-x-1/2 w-20 h-4 bg-red-600 rounded-t-lg"></div>
                <!-- Маркер -->
                <div class="absolute -top-8 left-1/2 transform -translate-x-1/2 w-4 h-4 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full animate-pulse shadow-lg"></div>
                
                <!-- Всплывающая подсказка -->
                <div class="absolute -top-16 left-1/2 transform -translate-x-1/2 bg-white rounded-lg shadow-lg p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none whitespace-nowrap z-50">
                  <div class="text-sm font-medium text-gray-800">{{ props.product?.title || 'Объект недвижимости' }}</div>
                  <div class="text-xs text-gray-600 mt-1">{{ address }}</div>
                  <div class="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-white"></div>
                </div>
              </div>
            </div>

            <!-- Окружающие здания -->
            <div class="absolute bottom-16 left-8 group">
              <div class="w-12 h-12 bg-gradient-to-br from-gray-600 to-gray-800 rounded-lg shadow-lg transform-gpu transition-all duration-300 hover:scale-110 cursor-pointer">
                <!-- Окна -->
                <div class="absolute top-1 left-1 w-2 h-3 bg-yellow-300 rounded opacity-60"></div>
                <div class="absolute top-1 right-1 w-2 h-3 bg-yellow-300 rounded opacity-60"></div>
              </div>
              <!-- Подсказка -->
              <div class="absolute -top-12 left-1/2 transform -translate-x-1/2 bg-white rounded-lg shadow-lg p-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none whitespace-nowrap z-50">
                <div class="text-xs text-gray-800">Офисное здание</div>
                <div class="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full w-0 h-0 border-l-3 border-r-3 border-t-3 border-transparent border-t-white"></div>
              </div>
            </div>
            
            <div class="absolute bottom-16 right-8 group">
              <div class="w-10 h-14 bg-gradient-to-br from-brown-600 to-brown-800 rounded-lg shadow-lg transform-gpu transition-all duration-300 hover:scale-110 cursor-pointer">
                <!-- Окна -->
                <div class="absolute top-2 left-1 w-2 h-2 bg-yellow-300 rounded opacity-60"></div>
                <div class="absolute top-6 left-1 w-2 h-2 bg-yellow-300 rounded opacity-60"></div>
                <div class="absolute top-10 left-1 w-2 h-2 bg-yellow-300 rounded opacity-60"></div>
              </div>
              <!-- Подсказка -->
              <div class="absolute -top-12 left-1/2 transform -translate-x-1/2 bg-white rounded-lg shadow-lg p-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none whitespace-nowrap z-50">
                <div class="text-xs text-gray-800">Жилой дом</div>
                <div class="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full w-0 h-0 border-l-3 border-r-3 border-t-3 border-transparent border-t-white"></div>
              </div>
            </div>
            
            <div class="absolute bottom-12 left-1/4">
              <div class="w-8 h-10 bg-gradient-to-br from-gray-500 to-gray-700 rounded-lg shadow-lg transform-gpu transition-all duration-300 hover:scale-110"></div>
            </div>
            
            <div class="absolute bottom-14 right-1/4">
              <div class="w-14 h-12 bg-gradient-to-br from-green-600 to-green-800 rounded-lg shadow-lg transform-gpu transition-all duration-300 hover:scale-110"></div>
            </div>

            <!-- Деревья -->
            <div class="absolute bottom-8 left-16 group">
              <div class="w-6 h-8 bg-green-600 rounded-full shadow-lg transform-gpu transition-all duration-300 hover:scale-110 cursor-pointer relative">
                <!-- Листва -->
                <div class="absolute -top-1 left-1/2 transform -translate-x-1/2 w-4 h-4 bg-green-500 rounded-full"></div>
              </div>
              <!-- Подсказка -->
              <div class="absolute -top-10 left-1/2 transform -translate-x-1/2 bg-white rounded-lg shadow-lg p-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none whitespace-nowrap z-50">
                <div class="text-xs text-gray-800">Дерево</div>
                <div class="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full w-0 h-0 border-l-3 border-r-3 border-t-3 border-transparent border-t-white"></div>
              </div>
            </div>
            
            <div class="absolute bottom-6 right-16">
              <div class="w-5 h-7 bg-green-500 rounded-full shadow-lg transform-gpu transition-all duration-300 hover:scale-110"></div>
            </div>
            
            <div class="absolute bottom-10 left-1/3">
              <div class="w-4 h-6 bg-green-700 rounded-full shadow-lg transform-gpu transition-all duration-300 hover:scale-110"></div>
            </div>

            <!-- Дороги -->
            <div class="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-32 h-2 bg-gray-800 rounded-full opacity-60"></div>
            <div class="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-2 h-32 bg-gray-800 rounded-full opacity-60"></div>
            
            <!-- Разметка дорог -->
            <div class="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-32 h-0.5 bg-yellow-400 rounded-full opacity-80"></div>
            <div class="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-0.5 h-32 bg-yellow-400 rounded-full opacity-80"></div>

            <!-- Облака -->
            <div class="absolute top-8 left-8 w-16 h-8 bg-white rounded-full opacity-60 animate-pulse"></div>
            <div class="absolute top-12 right-12 w-12 h-6 bg-white rounded-full opacity-60 animate-pulse" style="animation-delay: 1s"></div>
            <div class="absolute top-6 left-1/2 w-14 h-7 bg-white rounded-full opacity-60 animate-pulse" style="animation-delay: 2s"></div>

            <!-- Солнце -->
            <div class="absolute top-4 right-4 w-8 h-8 bg-yellow-400 rounded-full shadow-lg animate-pulse">
              <!-- Лучи солнца -->
              <div class="absolute inset-0 w-8 h-8">
                <div class="absolute top-0 left-1/2 transform -translate-x-1/2 w-0.5 h-4 bg-yellow-300 rounded-full"></div>
                <div class="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-0.5 h-4 bg-yellow-300 rounded-full"></div>
                <div class="absolute left-0 top-1/2 transform -translate-y-1/2 w-4 h-0.5 bg-yellow-300 rounded-full"></div>
                <div class="absolute right-0 top-1/2 transform -translate-y-1/2 w-4 h-0.5 bg-yellow-300 rounded-full"></div>
              </div>
            </div>
          </div>

          <!-- Информационная панель -->
          <div class="absolute top-4 right-4 bg-white/95 backdrop-blur-sm rounded-xl shadow-lg p-4 max-w-xs z-30 border border-gray-200">
            <div class="flex items-start gap-3">
              <div class="w-3 h-3 bg-green-500 rounded-full mt-2 animate-pulse"></div>
              <div>
                <h4 class="font-semibold text-gray-800">3D Объект</h4>
                <p class="text-sm text-gray-600 mt-1">
                  {{ address || 'Адрес загружается...' }}
                </p>
                <div class="flex gap-2 mt-2">
                  <span class="px-2 py-1 bg-indigo-100 text-indigo-800 text-xs rounded-full font-medium">
                    {{ coordinates.lat.toFixed(6) }}, {{ coordinates.lng.toFixed(6) }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 3D контролы -->
          <div class="absolute bottom-4 left-4 flex flex-col gap-2 z-30">
            <button 
              @click="zoomIn"
              class="w-12 h-12 bg-white/90 backdrop-blur-sm rounded-xl shadow-lg flex items-center justify-center hover:bg-white transition-all duration-200 border border-gray-200"
              title="Приблизить"
            >
              <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </button>
            <button 
              @click="zoomOut"
              class="w-12 h-12 bg-white/90 backdrop-blur-sm rounded-xl shadow-lg flex items-center justify-center hover:bg-white transition-all duration-200 border border-gray-200"
              title="Отдалить"
            >
              <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
              </svg>
            </button>
            <button 
              @click="resetView"
              class="w-12 h-12 bg-white/90 backdrop-blur-sm rounded-xl shadow-lg flex items-center justify-center hover:bg-white transition-all duration-200 border border-gray-200"
              title="Сбросить вид"
            >
              <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
            <button 
              @click="toggleAnimation"
              class="w-12 h-12 bg-white/90 backdrop-blur-sm rounded-xl shadow-lg flex items-center justify-center hover:bg-white transition-all duration-200 border border-gray-200"
              :class="{ 'bg-indigo-100 border-indigo-300': isAnimating }"
              title="Анимация"
            >
              <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </button>
          </div>

          <!-- Переключатель режимов -->
          <div class="absolute bottom-4 right-4 z-30">
            <div class="flex gap-2">
              <button 
                @click="setViewMode('top')"
                class="px-4 py-2 bg-white/90 backdrop-blur-sm text-gray-700 rounded-lg shadow-lg hover:bg-white transition-all duration-200 border border-gray-200 font-medium"
                :class="{ 'bg-indigo-600 text-white border-indigo-600': viewMode === 'top' }"
              >
                Сверху
              </button>
              <button 
                @click="setViewMode('perspective')"
                class="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg shadow-lg hover:from-indigo-700 hover:to-purple-700 transition-all duration-200 font-medium"
                :class="{ 'from-indigo-700 to-purple-700': viewMode === 'perspective' }"
              >
                3D
              </button>
            </div>
          </div>

          <!-- Статистика сцены -->
          <div class="absolute top-4 left-4 bg-white/95 backdrop-blur-sm rounded-xl shadow-lg p-3 z-30 border border-gray-200">
            <div class="text-center">
              <p class="text-xs text-gray-500">Масштаб</p>
              <p class="text-lg font-bold text-indigo-600">{{ Math.round(zoom * 100) }}%</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Дополнительная информация -->
      <div class="p-6 bg-gradient-to-r from-gray-50 to-blue-50">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-indigo-100 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
            <div class="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-1.447-.894L15 4m0 13V4m-6 3l6-3" />
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-600">Масштаб</p>
              <p class="font-medium text-gray-800">{{ Math.round(zoom * 100) }}%</p>
            </div>
          </div>
          
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-purple-100 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-600">Режим</p>
              <p class="font-medium text-gray-800">{{ viewMode === 'top' ? 'СВЕРХУ' : '3D' }}</p>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-pink-100 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-pink-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-600">Объекты</p>
              <p class="font-medium text-gray-800">{{ objectCount }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed, onUnmounted } from 'vue'

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

const scene3D = ref(null)
const rotationX = ref(-20)
const rotationY = ref(0)
const zoom = ref(1)
const viewMode = ref('perspective')
const isAnimating = ref(false)
const objectCount = ref(12)

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

// Функции управления
const zoomIn = () => {
  if (zoom.value < 2) {
    zoom.value += 0.1
  }
}

const zoomOut = () => {
  if (zoom.value > 0.5) {
    zoom.value -= 0.1
  }
}

const resetView = () => {
  rotationX.value = -20
  rotationY.value = 0
  zoom.value = 1
  viewMode.value = 'perspective'
  isAnimating.value = false
}

const toggleAnimation = () => {
  isAnimating.value = !isAnimating.value
  if (isAnimating.value) {
    startAnimation()
  }
}

const setViewMode = (mode) => {
  viewMode.value = mode
  if (mode === 'top') {
    rotationX.value = -90
    rotationY.value = 0
  } else {
    rotationX.value = -20
    rotationY.value = 0
  }
}

// Анимация вращения
const startAnimation = () => {
  if (!isAnimating.value) return
  
  rotationY.value += 1
  if (rotationY.value >= 360) {
    rotationY.value = 0
  }
  
  setTimeout(() => {
    if (isAnimating.value) {
      startAnimation()
    }
  }, 50)
}

// Обработка мыши для вращения
const handleMouseMove = (event) => {
  if (!scene3D.value || isAnimating.value) return
  
  const rect = scene3D.value.getBoundingClientRect()
  const centerX = rect.left + rect.width / 2
  const centerY = rect.top + rect.height / 2
  
  const deltaX = event.clientX - centerX
  const deltaY = event.clientY - centerY
  
  rotationY.value = deltaX * 0.1
  rotationX.value = -20 + deltaY * 0.1
}

// Обработка колесика мыши для зума
const handleWheel = (event) => {
  event.preventDefault()
  if (event.deltaY < 0) {
    zoomIn()
  } else {
    zoomOut()
  }
}

// Наблюдение за изменениями продукта
watch(() => props.product, (newProduct) => {
  if (newProduct && newProduct.latitude && newProduct.longitude) {
    coordinates.value = {
      lat: parseFloat(newProduct.latitude),
      lng: parseFloat(newProduct.longitude)
    }
  }
}, { deep: true })

onMounted(() => {
  // Установка координат из продукта
  if (props.product?.latitude && props.product?.longitude) {
    coordinates.value = {
      lat: parseFloat(props.product.latitude),
      lng: parseFloat(props.product.longitude)
    }
  }
  
  // Добавление обработчиков событий
  if (scene3D.value) {
    scene3D.value.addEventListener('mousemove', handleMouseMove)
    scene3D.value.addEventListener('wheel', handleWheel)
  }
})

onUnmounted(() => {
  // Удаление обработчиков событий
  if (scene3D.value) {
    scene3D.value.removeEventListener('mousemove', handleMouseMove)
    scene3D.value.removeEventListener('wheel', handleWheel)
  }
})
</script>

<style scoped>
.transform-style-preserve-3d {
  transform-style: preserve-3d;
}

.perspective-1000 {
  perspective: 1000px;
}

/* Анимации */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-5px);
  }
}

@keyframes glow {
  0%, 100% {
    box-shadow: 0 0 5px rgba(59, 130, 246, 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.8);
  }
}

.w-full.h-\[500px\] {
  animation: fadeInUp 0.6s ease-out;
}

/* 3D эффекты */
.w-16.h-16 {
  transform-style: preserve-3d;
  transition: all 0.3s ease;
}

.w-16.h-16:hover {
  transform: translateZ(10px) scale(1.05);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  animation: glow 2s ease-in-out infinite;
}

/* Анимация для зданий */
.w-12.h-12:hover,
.w-10.h-14:hover,
.w-8.h-10:hover,
.w-14.h-12:hover {
  animation: float 2s ease-in-out infinite;
}

/* Анимация для деревьев */
.w-6.h-8:hover,
.w-5.h-7:hover,
.w-4.h-6:hover {
  animation: float 3s ease-in-out infinite;
}

/* Кастомные скроллбары */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(45deg, #6366f1, #8b5cf6);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(45deg, #4f46e5, #7c3aed);
}

/* Дополнительные эффекты */
.bg-gradient-to-br.from-blue-500.to-blue-700 {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  position: relative;
  overflow: hidden;
}

.bg-gradient-to-br.from-blue-500.to-blue-700::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.bg-gradient-to-br.from-blue-500.to-blue-700:hover::before {
  left: 100%;
}

/* Анимация для облаков */
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Анимация для солнца */
.absolute.top-4.right-4 {
  animation: float 4s ease-in-out infinite;
}

/* Анимация для лучей солнца */
.absolute.top-4.right-4 .absolute.inset-0 div {
  animation: spin 10s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Улучшенные тени */
.shadow-xl {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.shadow-2xl {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

/* Эффект глубины для земли */
.bg-gradient-to-br.from-green-400.to-green-600 {
  background: radial-gradient(ellipse at center, #4ade80 0%, #16a34a 100%);
  position: relative;
}

.bg-gradient-to-br.from-green-400.to-green-600::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  border-radius: inherit;
}

/* Анимация для дорог */
.bg-gray-800 {
  position: relative;
  overflow: hidden;
}

.bg-gray-800::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: roadShine 3s linear infinite;
}

@keyframes roadShine {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}

/* Улучшенные подсказки */
.group:hover .opacity-0 {
  animation: tooltipFadeIn 0.3s ease-out forwards;
}

@keyframes tooltipFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Адаптивность */
@media (max-width: 768px) {
  .w-full.h-\[500px\] {
    height: 400px;
  }
  
  .w-16.h-16 {
    width: 12px;
    height: 12px;
  }
  
  .w-12.h-12 {
    width: 8px;
    height: 8px;
  }
}
</style> 
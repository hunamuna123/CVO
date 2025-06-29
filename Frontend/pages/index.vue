<template>
    <div class="max-w-[90rem] mx-auto">
        <div class="  mx-auto flex flex-col">
            <HeaderNavbar />
            <div class="flex-1 flex flex-col justify-center">
                <MainFirst class="mt-14" />
                <MainSecond />
            </div>
        </div>
        <div class="flex-1 flex flex-col justify-center align-start py-5 ">
            <AchivmentsIcon />
            <AchivmentsInfo />
        </div>
        <div class="flex-1 flex flex-col justify-center py-5 ">
            <div class="p-6">
                <h1 class="text-4xl text-black font-bold text-center p-2 ">Рекомендуемые объекты</h1>
                <p class="text-2xl text-center text-gray-400">Подобранные ИИ объекты с лучшим соотношением цены и
                    качестваи
                </p>
            </div>
            <div class="px-4 sm:px-6 lg:px-8">
                <div v-if="propertiesPending" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    <div v-for="n in 6" :key="n" class="pt-0 lg:pt-0 lg:py-14 pb-3 lg:pb-3">
                        <div class="w-full flex flex-col bg-white border border-gray-200 shadow-sm rounded-[20px] p-0 relative animate-pulse">
                            <div class="relative w-full aspect-[2/1] bg-gray-200 rounded-t-[20px]"></div>
                            <div class="flex flex-col h-48 gap-2 p-4 justify-between">
                                <div class="h-4 bg-gray-200 rounded w-32"></div>
                                <div class="h-6 bg-gray-200 rounded w-48"></div>
                                <div class="flex gap-4">
                                    <div class="h-4 bg-gray-200 rounded w-8"></div>
                                    <div class="h-4 bg-gray-200 rounded w-12"></div>
                                    <div class="h-4 bg-gray-200 rounded w-16"></div>
                                </div>
                                <div class="flex justify-between items-center">
                                    <div class="h-4 bg-gray-200 rounded w-16"></div>
                                    <div class="h-8 bg-gray-200 rounded w-20"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div v-else-if="propertiesError" class="text-center py-8">
                    <p class="text-red-500">Ошибка загрузки объектов: {{ propertiesError }}</p>
                    <button @click="fetchFeaturedProperties" class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                        Попробовать снова
                    </button>
                </div>
                <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    <ObjectsList 
                        v-for="property in featuredProperties" 
                        :key="property.id" 
                        :property="property"
                    />
                </div>
            </div>
            <div class="flex justify-center p-9">
                <NuxtLink to="/catalog"
                    class="py-3 px-4 inline-flex items-center gap-x-2 text-sm font-medium rounded-xl border border-transparent bg-blue-600 text-white hover:bg-blue-700 focus:outline-hidden focus:bg-blue-700 focus:outline-hidden focus:bg-blue-700 disabled:opacity-50 disabled:pointer-events-none">
                    Просмотреть все обьекты
                </NuxtLink>
            </div>
        </div>
        <div class="flex-1 flex flex-col w-full justify-center py-5 bg-[#f3f5f8]">
            <div class="p-6">
                <h1 class="text-4xl text-black font-bold text-center p-2 ">Проверенные застройщики</h1>
                <p class="text-2xl text-center text-gray-400">Все застройщики прошли многоуровневую верификацию через
                    государственные реестры и блокчейн
                </p>
            </div>
            <div class="px-4 sm:px-6 lg:px-8">
                <div v-if="pending" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div v-for="n in 4" :key="n" class="p-3">
                        <div class="border border-gray-200 rounded-xl p-6 flex flex-col items-center bg-white animate-pulse">
                            <div class="w-20 h-20 bg-gray-200 rounded mb-4"></div>
                            <div class="h-6 bg-gray-200 rounded mb-2 w-24"></div>
                            <div class="h-4 bg-gray-200 rounded mb-4 w-16"></div>
                            <div class="h-4 bg-gray-200 rounded w-20"></div>
                        </div>
                    </div>
                </div>
                <div v-else-if="error" class="text-center py-8">
                    <p class="text-red-500">Ошибка загрузки данных: {{ error }}</p>
                    <button @click="fetchDevelopers" class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                        Попробовать снова
                    </button>
                </div>
                <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                    <ObjectsDevelopers 
                        v-for="developer in developers" 
                        :key="developer.id" 
                        :developer="developer" 
                        class="p-3" 
                    />
                </div>
            </div>
            <div class="flex justify-center p-9 ">
                <NuxtLink type="button"
                    class="py-3 px-4 inline-flex items-center gap-x-2 text-sm font-medium rounded-xl border border-transparent bg-gray-200 text-black hover:bg-gray-300 focus:outline-hidden focus:bg-gray-400 disabled:opacity-50 disabled:pointer-events-none">
                  Просмотреть всех застройщиков
                </NuxtLink>
            </div>
        </div>

        <div class="flex-1 flex flex-col w-full justify-center py-5 ">
            <div class="p-6">
                <h1 class="text-4xl text-black font-bold text-center p-2 ">Почему выбирают нашу платформу</h1>
                <p class="text-2xl text-center text-gray-400">Мы используем передовые технологии для решения главных
                    проблем
                    рынка недвижимости
                </p>
            </div>
            <div class="px-4 sm:px-6 lg:px-8">
                <div class="">
                    <AchivmentsWhywe class="p-3" />
                </div>
            </div>
        </div>
    </div>
    <Footer />
</template>

<script setup>
import { api } from '~/store/api'

const { url } = api()

// Developers state
const developers = ref([])
const pending = ref(true)
const error = ref(null)

// Featured properties state
const featuredProperties = ref([])
const propertiesPending = ref(true)
const propertiesError = ref(null)

const fetchDevelopers = async () => {
  try {
    pending.value = true
    error.value = null
    
    const response = await $fetch(`${url}api/v1/developers/top?limit=4`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    developers.value = response
  } catch (err) {
    console.error('Error fetching developers:', err)
    error.value = err.message || 'Произошла ошибка при загрузке данных'
  } finally {
    pending.value = false
  }
}

const fetchFeaturedProperties = async () => {
  try {
    propertiesPending.value = true
    propertiesError.value = null
    
    const response = await $fetch(`${url}api/v1/properties/featured?limit=6`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    featuredProperties.value = response
  } catch (err) {
    console.error('Error fetching featured properties:', err)
    propertiesError.value = err.message || 'Произошла ошибка при загрузке объектов'
  } finally {
    propertiesPending.value = false
  }
}

// Fetch data on component mount
onMounted(() => {
  fetchDevelopers()
  fetchFeaturedProperties()
})
</script>
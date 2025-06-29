<template>
    <div class="border-b  border-gray-200 mb-6">
        <nav class="flex justify-between gap-x-1" aria-label="Tabs" role="tablist" aria-orientation="horizontal">
            <div class="flex gap-x-2 justify-end">
                <button type="button"
                    class="hs-tab-active:font-semibold hs-tab-active:border-blue-600 hs-tab-active:text-blue-600 py-4 px-1 inline-flex items-center gap-x-2 border-b border-gray-300-2 border-transparent text-sm whitespace-nowrap text-gray-500 hover:text-blue-600 focus:outline-hidden focus:text-blue-600 disabled:opacity-50 disabled:pointer-events-none active"
                    id="tabs-with-icons-item-1" aria-selected="true" data-hs-tab="#tabs-with-icons-1"
                    aria-controls="tabs-with-icons-1" role="tab">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Характеристики
                </button>
                <button type="button"
                    class="hs-tab-active:font-semibold hs-tab-active:border-blue-600 hs-tab-active:text-blue-600 py-4 px-1 inline-flex items-center gap-x-2 border-b border-gray-300-2 border-transparent text-sm whitespace-nowrap text-gray-500 hover:text-blue-600 focus:outline-hidden focus:text-blue-600 disabled:opacity-50 disabled:pointer-events-none"
                    id="tabs-with-icons-item-2" aria-selected="false" data-hs-tab="#tabs-with-icons-2"
                    aria-controls="tabs-with-icons-2" role="tab">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                    </svg>
                    Описание
                </button>
                <button type="button"
                    class="hs-tab-active:font-semibold hs-tab-active:border-blue-600 hs-tab-active:text-blue-600 py-4 px-1 inline-flex items-center gap-x-2 border-b border-gray-300-2 border-transparent text-sm whitespace-nowrap text-gray-500 hover:text-blue-600 focus:outline-hidden focus:text-blue-600 disabled:opacity-50 disabled:pointer-events-none"
                    id="tabs-with-icons-item-3" aria-selected="false" data-hs-tab="#tabs-with-icons-3"
                    aria-controls="tabs-with-icons-3" role="tab">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Расположение
                </button>
                <button type="button"
                    class="hs-tab-active:font-semibold hs-tab-active:border-blue-600 hs-tab-active:text-blue-600 py-4 px-1 inline-flex items-center gap-x-2 border-b border-gray-300-2 border-transparent text-sm whitespace-nowrap text-gray-500 hover:text-blue-600 focus:outline-hidden focus:text-blue-600 disabled:opacity-50 disabled:pointer-events-none"
                    id="tabs-with-icons-item-4" aria-selected="false" data-hs-tab="#tabs-with-icons-4"
                    aria-controls="tabs-with-icons-4" role="tab">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                    </svg>
                    Удобства
                </button>
            </div>
        </nav>
    </div>
    <div id="tabs-with-icons-1" role="tabpanel" aria-labelledby="tabs-with-icons-item-1">
        <div class="overflow-x-auto">
            <table class="min-w-full text-sm text-left text-gray-700">
                <tbody>
                    <tr class="border-b border-gray-300">
                        <th class="py-4 px-4 font-medium w-1/2">Тип недвижимости</th>
                        <td class="py-4 px-4">{{ getPropertyTypeName(product?.property_type) }}</td>
                    </tr>
                    <tr class="border-b border-gray-300">
                        <th class="py-4 px-4 font-medium">Тип сделки</th>
                        <td class="py-4 px-4">{{ product?.deal_type === 'SALE' ? 'Продажа' : 'Аренда' }}</td>
                    </tr>
                    <tr class="border-b border-gray-300">
                        <th class="py-4 px-4 font-medium">Площадь</th>
                        <td class="py-4 px-4">{{ product?.total_area ? `${product.total_area} м²` : 'Не указана' }}</td>
                    </tr>
                    <tr class="border-b border-gray-300">
                        <th class="py-4 px-4 font-medium">Жилая площадь</th>
                        <td class="py-4 px-4">{{ product?.living_area ? `${product.living_area} м²` : 'Не указана' }}</td>
                    </tr>
                    <tr class="border-b border-gray-300">
                        <th class="py-4 px-4 font-medium">Площадь кухни</th>
                        <td class="py-4 px-4">{{ product?.kitchen_area ? `${product.kitchen_area} м²` : 'Не указана' }}</td>
                    </tr>
                    <tr class="border-b border-gray-300">
                        <th class="py-4 px-4 font-medium">Количество комнат</th>
                        <td class="py-4 px-4">{{ product?.rooms_count || '0' }}</td>
                    </tr>
                    <tr class="border-b border-gray-300">
                        <th class="py-4 px-4 font-medium">Количество спален</th>
                        <td class="py-4 px-4">{{ product?.bedrooms_count || '0' }}</td>
                    </tr>
                    <tr class="border-b border-gray-300">
                        <th class="py-4 px-4 font-medium">Количество ванных</th>
                        <td class="py-4 px-4">{{ product?.bathrooms_count || '0' }}</td>
                    </tr>
                    <tr class="border-b border-gray-300">
                        <th class="py-4 px-4 font-medium">Этаж</th>
                        <td class="py-4 px-4">{{ product?.floor || '0' }}/{{ product?.total_floors || '0' }}</td>
                    </tr>
                    <tr class="border-b border-gray-300">
                        <th class="py-4 px-4 font-medium">Год постройки</th>
                        <td class="py-4 px-4">{{ product?.building_year || 'Не указан' }}</td>
                    </tr>
                    <tr class="border-b border-gray-300">
                        <th class="py-4 px-4 font-medium">Высота потолков</th>
                        <td class="py-4 px-4">{{ product?.ceiling_height ? `${product.ceiling_height} м` : 'Не указана' }}</td>
                    </tr>
                    <tr class="border-b border-gray-300">
                        <th class="py-4 px-4 font-medium">Тип ремонта</th>
                        <td class="py-4 px-4">{{ getRenovationTypeName(product?.renovation_type) }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <div id="tabs-with-icons-2" class="hidden" role="tabpanel" aria-labelledby="tabs-with-icons-item-2">
        <p class="text-gray-600">
            {{ product?.description || 'Отсутствует' }}
        </p>
    </div>

    <div id="tabs-with-icons-3" class="hidden" role="tabpanel" aria-labelledby="tabs-with-icons-item-3">
        <div class="space-y-6">
            <!-- Информация о расположении -->
            <div class="bg-gray-50 rounded-xl p-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Информация о расположении
                </h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div class="flex flex-col gap-2">
                        <div class="flex justify-between">
                            <span class="text-gray-600">Адрес:</span>
                            <span class="font-medium">{{ product?.full_address || 'Не указан' }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Город:</span>
                            <span class="font-medium">{{ product?.city || 'Не указан' }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Район:</span>
                            <span class="font-medium">{{ product?.district || 'Не указан' }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Улица:</span>
                            <span class="font-medium">{{ product?.street || 'Не указана' }}</span>
                        </div>
                    </div>
                    <div class="flex flex-col gap-2">
                        <div class="flex justify-between">
                            <span class="text-gray-600">Дом:</span>
                            <span class="font-medium">{{ product?.house_number || 'Не указан' }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Квартира:</span>
                            <span class="font-medium">{{ product?.apartment_number || 'Не указана' }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Индекс:</span>
                            <span class="font-medium">{{ product?.postal_code || 'Не указан' }}</span>
                        </div>
                        <div v-if="product?.latitude && product?.longitude" class="flex justify-between">
                            <span class="text-gray-600">Координаты:</span>
                            <span class="font-medium text-blue-600">{{ product.latitude }}, {{ product.longitude }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Карта -->
            <div class="bg-white rounded-xl shadow-lg overflow-hidden">
                <!-- Переключатель режимов карты -->
                <div class="flex justify-center p-4 bg-gradient-to-r from-gray-50 to-blue-50">
                    <div class="bg-white rounded-xl shadow-lg p-2 border border-gray-200">
                        <div class="flex gap-2">
                            <button 
                                @click="mapMode = '2d'"
                                class="px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center gap-2"
                                :class="mapMode === '2d' 
                                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg' 
                                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'"
                            >
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-1.447-.894L15 4m0 13V4m-6 3l6-3" />
                                </svg>
                                2D Карта
                            </button>
                            <button 
                                @click="mapMode = '3d'"
                                class="px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center gap-2"
                                :class="mapMode === '3d' 
                                    ? 'bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white shadow-lg' 
                                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'"
                            >
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                                </svg>
                                3D Карта
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- Отображение выбранной карты -->
                <div class="transition-all duration-300">
                    <template v-if="mapMode === '2d'">
                        <CatalogProductMap :product="product" />
                    </template>
                    <template v-else>
                        <CatalogProductMap3D :product="product" />
                    </template>
                </div>
            </div>

            <!-- Дополнительная информация о районе -->
            <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                    Инфраструктура района
                </h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="flex items-center gap-2 text-sm">
                        <div class="w-3 h-3 bg-green-500 rounded-full"></div>
                        <span>Транспорт</span>
                    </div>
                    <div class="flex items-center gap-2 text-sm">
                        <div class="w-3 h-3 bg-blue-500 rounded-full"></div>
                        <span>Магазины</span>
                    </div>
                    <div class="flex items-center gap-2 text-sm">
                        <div class="w-3 h-3 bg-purple-500 rounded-full"></div>
                        <span>Школы</span>
                    </div>
                    <div class="flex items-center gap-2 text-sm">
                        <div class="w-3 h-3 bg-orange-500 rounded-full"></div>
                        <span>Парки</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div id="tabs-with-icons-4" class="hidden" role="tabpanel" aria-labelledby="tabs-with-icons-item-4">
        <div class="flex flex-col gap-2 text-md">
            <div class="grid grid-cols-2 gap-4">
                <div class="flex items-center gap-2">
                    <span class="w-4 h-4 rounded-full" :class="product?.has_balcony ? 'bg-green-500' : 'bg-gray-300'"></span>
                    <span>Балкон/лоджия</span>
                </div>
                <div class="flex items-center gap-2">
                    <span class="w-4 h-4 rounded-full" :class="product?.has_loggia ? 'bg-green-500' : 'bg-gray-300'"></span>
                    <span>Лоджия</span>
                </div>
                <div class="flex items-center gap-2">
                    <span class="w-4 h-4 rounded-full" :class="product?.has_elevator ? 'bg-green-500' : 'bg-gray-300'"></span>
                    <span>Лифт</span>
                </div>
                <div class="flex items-center gap-2">
                    <span class="w-4 h-4 rounded-full" :class="product?.has_parking ? 'bg-green-500' : 'bg-gray-300'"></span>
                    <span>Парковка</span>
                </div>
                <div class="flex items-center gap-2">
                    <span class="w-4 h-4 rounded-full" :class="product?.has_furniture ? 'bg-green-500' : 'bg-gray-300'"></span>
                    <span>Мебель</span>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted, watch, nextTick, ref } from 'vue'

const props = defineProps({
    product: {
        type: Object,
        default: () => ({})
    }
})

const mapMode = ref('2d') // По умолчанию показываем 2D карту

const getPropertyTypeName = (type) => {
    switch(type) {
        case 'APARTMENT': return 'Квартира'
        case 'HOUSE': return 'Дом'
        case 'COMMERCIAL': return 'Коммерческая'
        default: return 'Недвижимость'
    }
}

const getRenovationTypeName = (type) => {
    switch(type) {
        case 'NONE': return 'Без ремонта'
        case 'COSMETIC': return 'Косметический'
        case 'EURO': return 'Евроремонт'
        case 'DESIGNER': return 'Дизайнерский'
        default: return 'Не указан'
    }
}

const initTabs = () => {
    if (typeof window !== 'undefined' && window.HSStaticMethods) {
        window.HSStaticMethods.autoInit()
    }
}

onMounted(async () => {
    await nextTick()
    initTabs()
})

// Переинициализируем табы при изменении продукта
watch(() => props.product, async () => {
    await nextTick()
    setTimeout(() => {
        initTabs()
    }, 100)
}, { deep: true })
</script>
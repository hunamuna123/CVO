<template>
    <div class="overflow-hidden">
        <div class="px-4 sm:px-6 lg:px-8 py-8 w-full">
            <div class="relative mx-auto max-w-4xl grid space-y-4 sm:space-y-6 lg:space-y-8">
                <div class="flex flex-col sm:flex-row justify-center gap-3 sm:gap-4 mb-2 sm:mb-4">
                    <div class="flex items-center bg-white rounded-xl px-3 sm:px-4 py-2 shadow text-xs sm:text-sm font-medium gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-5 sm:w-5 text-blue-500" fill="none"
                            viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M12 11c0-1.104.896-2 2-2s2 .896 2 2-.896 2-2 2-2-.896-2-2zm0 0V7m0 4v4m0 0c0 1.104-.896 2-2 2s-2-.896-2-2 .896-2 2-2 2 .896 2 2z" />
                        </svg>
                        <span class="hidden xs:inline text-blue-500">100% верифицированные объекты</span>
                        <span class="xs:hidden text-blue-500">100% верифицированные</span>
                    </div>
                    <div class="flex items-center bg-white rounded-xl px-3 sm:px-4 py-2 shadow text-xs sm:text-sm font-medium gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-5 sm:w-5 text-green-500" fill="none"
                            viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                        <span class="hidden xs:inline text-green-400">ИИ-аналитика цен</span>
                        <span class="xs:hidden text-green-400 ">ИИ-аналитика</span>
                    </div>
                </div>
                <div class="text-center mt-4">
                    <h1 class="text-4xl lg:text-5xl xl:text-6xl font-extrabold leading-14">
                        <span class="block text-black mt-4 md:mt-0">Будущее  </span> 
                        <span class="block mt-2">недвижимости</span>
                        <span class="block text-blue-500 mt-1 sm:mt-2">уже здесь</span>
                    </h1>
                    <h2 class="text-gray-500 text-lg lg:text-2xl px-4 sm:px-8 lg:px-15 py-2 sm:py-4 leading-9">
                        Первая в России платформа с <span class="text-blue-700">блокчейн-верификацией,
                            ИИ-аналитикой</span> и полной прозрачностью сделок. Покупайте недвижимость безопасно и выгодно.
                    </h2>
                </div>
                <form @submit.prevent="handleSearch">
                    <div class="p-4 sm:p-6 lg:p-8 bg-gray-200 rounded-xl">
                        <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 sm:gap-4 bg-white rounded-xl shadow-lg px-4 sm:px-6 py-4 max-w-3xl mx-auto">
                            <div class="relative flex-1">
                                <span class="absolute inset-y-0 left-0 flex items-center pl-3">
                                    <svg class="w-4 h-4 sm:w-5 sm:h-5 text-gray-400" fill="none" stroke="currentColor"
                                        stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round"
                                        stroke-linejoin="round">
                                        <circle cx="11" cy="11" r="8" />
                                        <path d="m21 21-4.3-4.3" />
                                    </svg>
                                </span>
                                <input 
                                    v-model="searchQuery" 
                                    type="text" 
                                    placeholder="Район, метро, ЖК..."
                                    class="w-full pl-10 pr-4 py-3 sm:py-2 rounded-xl border border-transparent focus:border-gray-500 focus:ring-1 focus:ring-gray-500 bg-gray-50 text-gray-900 placeholder-gray-400 text-sm sm:text-base transition" />
                            </div>
                            <div class="w-full sm:w-auto">
                                <select 
                                    v-model="propertyType"
                                    data-hs-select='{
                            "placeholder": "Выбрать тип",
                            "toggleTag": "<button type=\"button\" aria-expanded=\"false\"></button>",
                            "toggleClasses": "hs-select-disabled:pointer-events-none hs-select-disabled:opacity-50 relative py-3 sm:py-2 ps-4 pe-9 flex gap-x-2 text-nowrap w-full cursor-pointer bg-white border border-gray-200 rounded-xl text-start text-sm focus:outline-hidden focus:ring-2 focus:ring-gray-500",
                            "dropdownClasses": "mt-2 z-50 w-full max-h-72 p-1 space-y-0.5 bg-white border border-gray-200 rounded-xl overflow-hidden overflow-y-auto [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-track]:bg-gray-100 [&::-webkit-scrollbar-thumb]:bg-gray-300",
                            "optionClasses": "py-2 px-4 w-full text-sm text-gray-800 cursor-pointer hover:bg-gray-100 rounded-xl focus:outline-hidden focus:bg-gray-100 hs-select-disabled:pointer-events-none hs-select-disabled:opacity-50",
                            "optionTemplate": "<div class=\"flex justify-between items-center w-full\"><span data-title></span><span class=\"hidden hs-selected:block\"><svg class=\"shrink-0 size-3.5 text-gray-600\" xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><polyline points=\"20 6 9 17 4 12\"/></svg></span></div>",
                            "extraMarkup": "<div class=\"absolute top-1/2 end-3 -translate-y-1/2\"><svg class=\"shrink-0 size-3.5 text-gray-500\" xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"m7 15 5 5 5-5\"/><path d=\"m7 9 5-5 5 5\"/></svg></div>"
                            }' 
                                    class="hidden">
                                    <option value="">Кв</option>
                                    <option value="Дом">Дом</option>
                                    <option value="Участок">Участок</option>
                                </select>
                            </div>
                            <button type="submit"
                                class="flex items-center justify-center gap-2 px-6 sm:px-7 py-3 sm:py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm sm:text-base shadow transition w-full sm:w-auto">
                                <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" stroke-width="2"
                                    viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">
                                    <circle cx="11" cy="11" r="8" />
                                    <path d="m21 21-4.3-4.3" />
                                </svg>
                                <span class="hidden sm:inline">Найти</span>
                                <span class="sm:hidden">Поиск</span>
                            </button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const searchQuery = ref('');
const propertyType = ref('');

const handleSearch = () => {
    const query = {};
    
    if (searchQuery.value.trim()) {
        query.search = searchQuery.value.trim();
    }
    
    if (propertyType.value) {
        query.type = propertyType.value;
    }
    
    router.push({
        path: '/catalog',
        query: query
    });
};
</script>
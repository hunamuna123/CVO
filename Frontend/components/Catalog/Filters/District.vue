<template>
    <div class="space-y-3">
        <div>
            <h3 class="font-medium">Район</h3>
        </div>
        <div class="w-full p-1 ">
            <!-- Select -->
            <select 
                v-model="selectedDistrict"
                @change="updateQuery"
                data-hs-select='{
                    "placeholder": "Выберите район",
                    "toggleTag": "<button type=\"button\" aria-expanded=\"false\"></button>",
                    "toggleClasses": "hs-select-disabled:pointer-events-none hs-select-disabled:opacity-50 relative py-3 ps-4 pe-9 flex gap-x-2 text-nowrap w-full cursor-pointer bg-white border border-gray-200 rounded-lg text-start text-sm focus:outline-hidden focus:ring-2 focus:ring-blue-500",
                    "dropdownClasses": "mt-2 z-50 w-full max-h-72 p-1 space-y-0.5 bg-white border border-gray-200 rounded-lg overflow-hidden overflow-y-auto [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-track]:bg-gray-100 [&::-webkit-scrollbar-thumb]:bg-gray-300",
                    "dropdownVerticalFixedPlacement": "bottom",
                    "optionClasses": "py-2 px-4 w-full text-sm text-gray-800 cursor-pointer hover:bg-gray-100 rounded-lg focus:outline-hidden focus:bg-gray-100 hs-select-disabled:pointer-events-none hs-select-disabled:opacity-50",
                    "optionTemplate": "<div class=\"flex justify-between items-center w-full\"><span data-title></span><span class=\"hidden hs-selected:block\"><svg class=\"shrink-0 size-3.5 text-blue-600 \" xmlns=\"http:.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><polyline points=\"20 6 9 17 4 12\"/></svg></span></div>",
                    "extraMarkup": "<div class=\"absolute top-1/2 end-3 -translate-y-1/2\"><svg class=\"shrink-0 size-3.5 text-gray-500 \" xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"m7 15 5 5 5-5\"/><path d=\"m7 9 5-5 5 5\"/></svg></div>"
                    }' 
                class="w-full">
                <option value="">Выберите район</option>
                <option value="0">Центральный</option>
                <option value="1">Северный</option>
                <option value="2">Северо-Восточный</option>
                <option value="3">Восточный</option>
                <option value="4">Юго-Восточный</option>
                <option value="5">Южный</option>
                <option value="6">Юго-Западный</option>
                <option value="7">Западный</option>
                <option value="8">Северо-Западный</option>
                <option value="9">Зеленоградский</option>
                <option value="10">Троицкий</option>
                <option value="11">Новомосковский</option>
            </select>
            <!-- End Select -->
        </div>
    </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

export default {
    setup() {
        const route = useRoute();
        const router = useRouter();
        
        const selectedDistrict = ref(route.query.district || '');

        const updateQuery = () => {
            router.push({
                query: {
                    ...route.query,
                    district: selectedDistrict.value || undefined,
                },
            });
        };

        watch(
            () => route.query.district,
            (newDistrict) => {
                selectedDistrict.value = newDistrict || '';
            }
        );

        return {
            selectedDistrict,
            updateQuery,
        };
    },
};
</script> 
<template>
	<div
		class="flex flex-col gap-4 w-full md:max-w-[calc(50%_-_48px)] lg:max-w-[calc(60%_-_48px)]"
	>
		<!-- Toast Notifications Container -->
		<div class="fixed top-4 right-4 z-50 flex flex-col gap-2">
			<TransitionGroup name="toast">
				<div v-for="(toast, index) in toasts" :key="toast.id"
					class="max-w-xs bg-white border border-gray-200 rounded-xl shadow-lg" role="alert" tabindex="-1">
					<div class="flex p-4">
						<div class="shrink-0">
							<svg class="shrink-0 size-4 text-green-500 mt-0.5" xmlns="http://www.w3.org/2000/svg" width="16"
								height="16" fill="currentColor" viewBox="0 0 16 16">
								<path
									d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z">
								</path>
							</svg>
						</div>
						<div class="ms-3">
							<p class="text-sm text-gray-700">
								{{ toast.message }}
							</p>
						</div>
					</div>
				</div>
			</TransitionGroup>
		</div>

		<h1 class="text-4xl font-semibold">
			{{ product?.title || 'Нет названия' }}
		</h1>

		<div class="grid sm:grid-cols-2 gap-2 mt-6">
			<h4 class="text-md text-gray-500">
				Тип недвижимости:
				<span class="font-medium text-black">
					{{ getPropertyTypeName(product?.property_type) }}
				</span>
			</h4>
			<h4 class="text-md text-gray-500">
				Тип сделки:
				<span class="font-medium text-black">
					{{ product?.deal_type === 'SALE' ? 'Продажа' : 'Аренда' }}
				</span>
			</h4>
			<h4 class="text-md text-gray-500">
				Район:
				<span class="font-medium text-black">
					{{ product?.district || 'Не указан' }}
				</span>
			</h4>
			<h4 v-if="product?.region" class="text-md text-gray-500">
				Регион:
				<span class="font-medium text-black">
					{{ product.region }}
				</span>
			</h4>
			<h4 v-if="product?.city" class="text-md text-gray-500">
				Город:
				<span class="font-medium text-black">
					{{ product.city }}
				</span>
			</h4>
			<h4 v-if="product?.street" class="text-md text-gray-500">
				Улица:
				<span class="font-medium text-black">
					{{ product.street }}
				</span>
			</h4>
			<h4 v-if="product?.house_number" class="text-md text-gray-500">
				Номер дома:
				<span class="font-medium text-black">
					{{ product.house_number }}
				</span>
			</h4>
			<h4 class="text-md text-gray-500">
				Площадь:
				<span class="font-medium text-black">
					{{ product?.total_area ? `${product.total_area} м²` : 'Не указана' }}
				</span>
			</h4>
			<h4 class="text-md text-gray-500">
				Комнаты:
				<span class="font-medium text-black">
					{{ product?.rooms_count || product?.rooms || 'Не указано' }}
				</span>
			</h4>
			<h4 class="text-md text-gray-500">
				Этаж:
				<span class="font-medium text-black">
					{{ product?.floor ? `${product.floor}/${product?.total_floors || '?'}` : 'Не указан' }}
				</span>
			</h4>
			<h4 class="text-md text-gray-500">
				Адрес:
				<span class="font-medium text-black">
					{{ product?.full_address || 'Не указан' }}
				</span>
			</h4>
			<h4 v-if="product?.postal_code" class="text-md text-gray-500">
				Почтовый индекс:
				<span class="font-medium text-black">
					{{ product.postal_code }}
				</span>
			</h4>
			<h4 v-if="product?.apartment_number" class="text-md text-gray-500">
				Номер квартиры:
				<span class="font-medium text-black">
					{{ product.apartment_number }}
				</span>
			</h4>
			<h4 class="text-md text-gray-500">
				Год постройки:
				<span class="font-medium text-black">
					{{ product?.building_year || 'Не указан' }}
				</span>
			</h4>
			<h4 class="text-md text-gray-500">
				Жилая площадь:
				<span class="font-medium text-black">
					{{ product?.living_area ? `${product.living_area} м²` : 'Не указана' }}
				</span>
			</h4>
			<h4 class="text-md text-gray-500">
				Площадь кухни:
				<span class="font-medium text-black">
					{{ product?.kitchen_area ? `${product.kitchen_area} м²` : 'Не указана' }}
				</span>
			</h4>
			<h4 class="text-md text-gray-500">
				Высота потолков:
				<span class="font-medium text-black">
					{{ product?.ceiling_height ? `${product.ceiling_height} м` : 'Не указана' }}
				</span>
			</h4>
			<h4 class="text-md text-gray-500">
				Спальни:
				<span class="font-medium text-black">
					{{ product?.bedrooms_count || 'Не указано' }}
				</span>
			</h4>
			<h4 class="text-md text-gray-500">
				Санузлы:
				<span class="font-medium text-black">
					{{ product?.bathrooms_count || 'Не указано' }}
				</span>
			</h4>
			<h4 class="text-md text-gray-500">
				Доступно с:
				<span class="font-medium text-black">
					{{ product?.available_from ? formatDate(product.available_from) : 'Не указано' }}
				</span>
			</h4>
			<h4 v-if="product?.latitude && product?.longitude" class="text-md text-gray-500">
				Координаты:
				<span class="font-medium text-black">
					{{ product.latitude.toFixed(6) }}, {{ product.longitude.toFixed(6) }}
				</span>
			</h4>
		</div>
		
		<!-- Additional Features -->
		<div v-if="hasAdditionalFeatures" class="mt-6">
			<h3 class="text-lg font-semibold text-gray-900 mb-3">Дополнительные характеристики</h3>
			<div class="grid grid-cols-2 md:grid-cols-3 gap-3">
				<div v-if="product?.has_balcony !== null" class="flex items-center gap-2">
					<svg class="w-4 h-4" :class="product.has_balcony ? 'text-green-500' : 'text-gray-400'" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
					</svg>
					<span class="text-sm" :class="product.has_balcony ? 'text-green-600' : 'text-gray-500'">Балкон</span>
				</div>
				<div v-if="product?.has_loggia !== null" class="flex items-center gap-2">
					<svg class="w-4 h-4" :class="product.has_loggia ? 'text-green-500' : 'text-gray-400'" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
					</svg>
					<span class="text-sm" :class="product.has_loggia ? 'text-green-600' : 'text-gray-500'">Лоджия</span>
				</div>
				<div v-if="product?.has_elevator !== null" class="flex items-center gap-2">
					<svg class="w-4 h-4" :class="product.has_elevator ? 'text-green-500' : 'text-gray-400'" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
					</svg>
					<span class="text-sm" :class="product.has_elevator ? 'text-green-600' : 'text-gray-500'">Лифт</span>
				</div>
				<div v-if="product?.has_parking !== null" class="flex items-center gap-2">
					<svg class="w-4 h-4" :class="product.has_parking ? 'text-green-500' : 'text-gray-400'" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
					</svg>
					<span class="text-sm" :class="product.has_parking ? 'text-green-600' : 'text-gray-500'">Парковка</span>
				</div>
				<div v-if="product?.has_furniture !== null" class="flex items-center gap-2">
					<svg class="w-4 h-4" :class="product.has_furniture ? 'text-green-500' : 'text-gray-400'" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
					</svg>
					<span class="text-sm" :class="product.has_furniture ? 'text-green-600' : 'text-gray-500'">Мебель</span>
				</div>
				<div v-if="product?.renovation_type" class="flex items-center gap-2">
					<svg class="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
					</svg>
					<span class="text-sm text-blue-600">{{ getRenovationTypeName(product.renovation_type) }}</span>
				</div>
				<div v-if="product?.is_featured" class="flex items-center gap-2">
					<svg class="w-4 h-4 text-purple-500" fill="currentColor" viewBox="0 0 20 20">
						<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
					</svg>
					<span class="text-sm text-purple-600">Избранное</span>
				</div>
			</div>
		</div>
		
		<div class="mt-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
			<div class="flex flex-col gap-1">
				<h1 class="text-3xl font-bold">
					{{ formatPrice(product?.price) }} {{ getCurrencySymbol(product?.currency) }}
				</h1>
				<h4 class="text-lg font-medium text-gray-400" v-if="product?.price_per_sqm">
					{{ formatPrice(product.price_per_sqm) }} {{ getCurrencySymbol(product?.currency) }}/м²
				</h4>
			</div>
			<div class="w-full sm:w-auto">
				<button @click="showBookingModal = true"
					type="button"
					class="w-full sm:w-auto py-3 px-6 inline-flex items-center justify-center font-medium text-sm rounded-full bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:bg-blue-700 transition-colors duration-200"
				>
					Забронировать
				</button>
			</div>
		</div>

		<div class="flex items-center flex-wrap justify-between gap-4 mt-4">
			<!-- Developer Info -->
			<div v-if="product?.developer" class="flex items-center gap-3">
				<img v-if="product.developer.logo_url" 
					:src="getFullImageUrl(product.developer.logo_url)" 
					:alt="product.developer.company_name"
					class="w-8 h-8 rounded-full object-cover"
					@error="handleLogoError" />
				<div>
					<p class="text-sm font-medium text-gray-900">{{ product.developer.company_name }}</p>
					<div class="flex items-center gap-1">
						<div class="flex text-yellow-400">
							<svg v-for="i in 5" :key="i" class="w-3 h-3" :class="i <= Math.round(product.developer.rating) ? 'text-yellow-400' : 'text-gray-300'" fill="currentColor" viewBox="0 0 20 20">
								<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
							</svg>
						</div>
						<span class="text-xs text-gray-500 ml-1">{{ product.developer.rating }}</span>
						<span v-if="product.developer.is_verified" class="text-xs text-green-600 ml-2">✓ Проверен</span>
					</div>
					<NuxtLink
						:to="`/developers/${product.developer.id}`"
						class="inline-flex items-center gap-1 mt-1 text-xs text-blue-600 hover:text-blue-700 font-medium"
					>
						<span>Перейти к застройщику</span>
						<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
						</svg>
					</NuxtLink>
				</div>
			</div>
			
			<!-- Status and Stats -->
			<div class="flex items-center gap-4">
				<span v-if="product?.status" 
					:class="[
						'px-3 py-1 rounded-full text-xs font-medium',
						getStatusClass(product.status)
					]"
				>
					{{ getStatusText(product.status) }}
				</span>
				<span v-if="product?.is_featured" 
					class="px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
				>
					⭐ Избранное
				</span>
				<div class="flex items-center gap-3 text-sm text-gray-500">
					<div class="flex items-center gap-1">
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
						</svg>
						<span>{{ product?.views_count || 0 }}</span>
					</div>
					<div class="flex items-center gap-1">
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
						</svg>
						<span>{{ product?.favorites_count || 0 }}</span>
					</div>
				</div>
			</div>
		</div>
		<hr class="my-4" />
		<div class="flex flex-col gap-2">
			<h1 class="text-2xl font-semibold">Описание</h1>
			<p class="text-gray-600">
				{{ product?.description || 'Отсутствует' }}
			</p>
			<div class="flex flex-wrap gap-4 text-xs text-gray-500 mt-2">
				<span v-if="product?.created_at">
					Создано: {{ formatDate(product.created_at) }}
				</span>
				<span v-if="product?.updated_at && product.updated_at !== product.created_at">
					Обновлено: {{ formatDate(product.updated_at) }}
				</span>
			</div>
		</div>

		<!-- Documents -->
		<div v-if="product?.documents && product.documents.length > 0" class="flex flex-col gap-2">
			<h1 class="text-2xl font-semibold">Документы</h1>
			<div class="grid grid-cols-1 md:grid-cols-2 gap-3">
				<div v-for="doc in product.documents" :key="doc.id" class="flex items-center gap-3 p-3 border border-gray-200 rounded-lg">
					<svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
					<div class="flex-1">
						<p class="text-sm font-medium text-gray-900">{{ doc.title || 'Документ' }}</p>
						<p v-if="doc.description" class="text-xs text-gray-500">{{ doc.description }}</p>
					</div>
					<a v-if="doc.url" :href="getFullImageUrl(doc.url)" target="_blank" class="text-blue-600 hover:text-blue-700 text-sm">
						Скачать
					</a>
				</div>
			</div>
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
import { ref, computed } from 'vue'
import { api } from '@/store/api.js'
import { useCookie } from '#app'

const props = defineProps({
	product: {
		type: Object,
		default: () => ({})
	}
})

const apiStore = api()
const toasts = ref([])
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

// Вычисляемое свойство для проверки наличия дополнительных характеристик
const hasAdditionalFeatures = computed(() => {
	return props.product && (
		props.product.has_balcony !== null ||
		props.product.has_loggia !== null ||
		props.product.has_elevator !== null ||
		props.product.has_parking !== null ||
		props.product.has_furniture !== null ||
		props.product.renovation_type ||
		props.product.is_featured
	)
})

const getPropertyTypeName = (type) => {
	switch(type) {
		case 'APARTMENT': return 'Квартира'
		case 'HOUSE': return 'Дом'
		case 'COMMERCIAL': return 'Коммерческая недвижимость'
		case 'LAND': return 'Земельный участок'
		case 'GARAGE': return 'Гараж'
		case 'OFFICE': return 'Офис'
		case 'WAREHOUSE': return 'Склад'
		case 'RETAIL': return 'Торговая площадь'
		default: return type || 'Недвижимость'
	}
}

const getRenovationTypeName = (type) => {
	switch(type) {
		case 'NONE': return 'Без ремонта'
		case 'ROUGH': return 'Черновая отделка'
		case 'FINISHED': return 'Чистовая отделка'
		case 'DESIGNER': return 'Дизайнерский ремонт'
		case 'EURO': return 'Евроремонт'
		default: return type || 'Не указан'
	}
}

const getStatusClass = (status) => {
	switch (status) {
		case 'ACTIVE':
			return 'bg-green-100 text-green-800'
		case 'INACTIVE':
			return 'bg-gray-100 text-gray-800'
		case 'SOLD':
			return 'bg-red-100 text-red-800'
		case 'RESERVED':
			return 'bg-yellow-100 text-yellow-800'
		default:
			return 'bg-gray-100 text-gray-800'
	}
}

const getStatusText = (status) => {
	switch (status) {
		case 'ACTIVE':
			return 'Активно'
		case 'INACTIVE':
			return 'Неактивно'
		case 'SOLD':
			return 'Продано'
		case 'RESERVED':
			return 'Забронировано'
		default:
			return status
	}
}

const getCurrencySymbol = (currency) => {
	switch (currency) {
		case 'RUB':
			return '₽'
		case 'USD':
			return '$'
		case 'EUR':
			return '€'
		default:
			return currency || '₽'
	}
}

const formatPrice = (price) => {
	if (!price) return '0'
	return new Intl.NumberFormat('ru-RU').format(parseFloat(price))
}

const formatDate = (dateString) => {
	if (!dateString) return ''
	return new Date(dateString).toLocaleDateString('ru-RU', {
		year: 'numeric',
		month: 'long',
		day: 'numeric',
		hour: '2-digit',
		minute: '2-digit'
	})
}

const getFullImageUrl = (url) => {
	if (!url) return ''
	
	// Если URL уже полный (начинается с http), используем как есть
	if (url.startsWith('http://') || url.startsWith('https://')) {
		return url
	}
	
	// Если URL относительный (начинается с /), добавляем базовый URL API
	if (url.startsWith('/')) {
		return `${apiStore.url}${url.substring(1)}`
	}
	
	// Если URL без слеша, добавляем базовый URL API со слешем
	return `${apiStore.url}${url}`
}

const handleLogoError = (event) => {
	console.error('Ошибка загрузки логотипа:', event.target.src)
	event.target.style.display = 'none'
}

const showToast = (message) => {
	const toastId = Date.now()
	toasts.value.push({ id: toastId, message })
	setTimeout(() => {
		toasts.value = toasts.value.filter(t => t.id !== toastId)
	}, 3000)
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
		showToast('Бронирование успешно создано!')
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
		showToast('Ошибка при создании бронирования')
	} finally {
		isSubmitting.value = false
	}
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.toast-move {
  transition: transform 0.3s ease;
}
</style>

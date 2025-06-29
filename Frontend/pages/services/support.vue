<template>
  <div class="min-h-screen bg-gray-50">
    <HeaderNavbar />

    <!-- Hero Section -->
    <section class="pt-24 pb-12 bg-gradient-to-br from-yellow-50 to-amber-100">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-6">Поддержка 24/7</h1>
        <p class="text-xl text-gray-600 mb-8">Консультации экспертов и помощь на всех этапах сделки с недвижимостью</p>
      </div>
    </section>

    <!-- Contact Methods -->
    <section class="py-16">
      <div class="max-w-6xl mx-auto px-4">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
            <div class="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
              </svg>
            </div>
            <h3 class="text-xl font-semibold mb-2">Телефон</h3>
            <p class="text-gray-600 mb-4">8-800-555-0123</p>
            <p class="text-sm text-gray-500">Круглосуточно</p>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
            <div class="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
              </svg>
            </div>
            <h3 class="text-xl font-semibold mb-2">Чат</h3>
            <p class="text-gray-600 mb-4">Онлайн консультация</p>
            <button class="bg-yellow-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-yellow-700 transition-colors">
              Начать чат
            </button>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
            <div class="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
            </div>
            <h3 class="text-xl font-semibold mb-2">Email</h3>
            <p class="text-gray-600 mb-4">support@realty.ru</p>
            <p class="text-sm text-gray-500">Ответ в течение 2 часов</p>
          </div>
        </div>
      </div>
    </section>

    <!-- FAQ Section -->
    <section class="py-16 bg-white">
      <div class="max-w-4xl mx-auto px-4">
        <h2 class="text-3xl font-bold text-center mb-12">Часто задаваемые вопросы</h2>
        <div class="space-y-4">
          <div class="border border-gray-200 rounded-lg">
            <button 
              @click="toggleFAQ(1)"
              class="w-full px-6 py-4 text-left flex justify-between items-center hover:bg-gray-50 transition-colors"
            >
              <span class="font-semibold">Как проверить надежность застройщика?</span>
              <svg class="w-5 h-5 transform transition-transform" :class="{ 'rotate-180': openFAQ === 1 }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>
            <div v-if="openFAQ === 1" class="px-6 pb-4">
              <p class="text-gray-600">Мы проверяем застройщиков по нескольким критериям: юридическая информация, финансовая отчетность, история проектов и отзывы клиентов. Все данные хранятся в блокчейне для обеспечения прозрачности.</p>
            </div>
          </div>

          <div class="border border-gray-200 rounded-lg">
            <button 
              @click="toggleFAQ(2)"
              class="w-full px-6 py-4 text-left flex justify-between items-center hover:bg-gray-50 transition-colors"
            >
              <span class="font-semibold">Какие документы нужны для ипотеки?</span>
              <svg class="w-5 h-5 transform transition-transform" :class="{ 'rotate-180': openFAQ === 2 }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>
            <div v-if="openFAQ === 2" class="px-6 pb-4">
              <p class="text-gray-600">Основные документы: паспорт, ИНН, справка о доходах, трудовая книжка, документы на имеющееся имущество. Точный список зависит от банка и программы кредитования.</p>
            </div>
          </div>

          <div class="border border-gray-200 rounded-lg">
            <button 
              @click="toggleFAQ(3)"
              class="w-full px-6 py-4 text-left flex justify-between items-center hover:bg-gray-50 transition-colors"
            >
              <span class="font-semibold">Как безопасно провести сделку?</span>
              <svg class="w-5 h-5 transform transition-transform" :class="{ 'rotate-180': openFAQ === 3 }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>
            <div v-if="openFAQ === 3" class="px-6 pb-4">
              <p class="text-gray-600">Рекомендуем использовать банковскую ячейку или аккредитив для передачи денег, обязательно проверить все документы с юристом, зарегистрировать сделку в Росреестре.</p>
            </div>
          </div>

          <div class="border border-gray-200 rounded-lg">
            <button 
              @click="toggleFAQ(4)"
              class="w-full px-6 py-4 text-left flex justify-between items-center hover:bg-gray-50 transition-colors"
            >
              <span class="font-semibold">Сколько времени занимает покупка?</span>
              <svg class="w-5 h-5 transform transition-transform" :class="{ 'rotate-180': openFAQ === 4 }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>
            <div v-if="openFAQ === 4" class="px-6 pb-4">
              <p class="text-gray-600">Время зависит от типа недвижимости: новостройка - от 1 до 3 месяцев, вторичное жилье - от 2 недель до 2 месяцев. Основное время занимает оформление ипотеки и регистрация сделки.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Contact Form -->
    <section class="py-16 bg-gray-50">
      <div class="max-w-4xl mx-auto px-4">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <h2 class="text-2xl font-semibold text-center mb-8">Оставить заявку</h2>
          <form class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Имя</label>
                <input 
                  type="text" 
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                >
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Телефон</label>
                <input 
                  type="tel" 
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                >
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input 
                type="email" 
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Тема обращения</label>
              <select class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent">
                <option>Выберите тему</option>
                <option>Консультация по покупке</option>
                <option>Проверка застройщика</option>
                <option>Ипотечное кредитование</option>
                <option>Техническая поддержка</option>
                <option>Другое</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Сообщение</label>
              <textarea 
                rows="4"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                placeholder="Опишите ваш вопрос или проблему..."
              ></textarea>
            </div>
            <button 
              type="submit"
              class="w-full bg-yellow-600 text-white py-3 rounded-lg font-semibold hover:bg-yellow-700 transition-colors"
            >
              Отправить заявку
            </button>
          </form>
        </div>
      </div>
    </section>

    <!-- Support Team -->
    <section class="py-16 bg-white">
      <div class="max-w-6xl mx-auto px-4">
        <h2 class="text-3xl font-bold text-center mb-12">Наша команда поддержки</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div class="text-center">
            <div class="w-24 h-24 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-12 h-12 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
            </div>
            <h3 class="font-semibold text-lg mb-2">Анна Петрова</h3>
            <p class="text-gray-600 mb-2">Руководитель отдела поддержки</p>
            <p class="text-sm text-gray-500">Опыт работы 8 лет</p>
          </div>

          <div class="text-center">
            <div class="w-24 h-24 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-12 h-12 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
            </div>
            <h3 class="font-semibold text-lg mb-2">Михаил Сидоров</h3>
            <p class="text-gray-600 mb-2">Эксперт по ипотеке</p>
            <p class="text-sm text-gray-500">Опыт работы 5 лет</p>
          </div>

          <div class="text-center">
            <div class="w-24 h-24 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-12 h-12 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
            </div>
            <h3 class="font-semibold text-lg mb-2">Елена Козлова</h3>
            <p class="text-gray-600 mb-2">Юрист-консультант</p>
            <p class="text-sm text-gray-500">Опыт работы 10 лет</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-16 bg-gradient-to-r from-yellow-600 to-amber-700">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h2 class="text-3xl md:text-4xl font-bold text-white mb-6">Нужна срочная помощь?</h2>
        <p class="text-xl text-yellow-100 mb-8">Позвоните нам прямо сейчас и получите консультацию</p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <button class="bg-white text-yellow-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
            Позвонить сейчас
          </button>
          <button class="border border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-yellow-600 transition-colors">
            Написать в чат
          </button>
        </div>
      </div>
    </section>

    <Footer />
  </div>
</template>

<script setup>
import { ref } from 'vue'

const openFAQ = ref(null)

const toggleFAQ = (id) => {
  openFAQ.value = openFAQ.value === id ? null : id
}
</script> 
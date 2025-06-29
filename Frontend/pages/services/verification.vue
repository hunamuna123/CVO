<template>
  <div class="min-h-screen bg-gray-50">
    <HeaderNavbar />

    <!-- Hero Section -->
    <section class="pt-24 pb-12 bg-gradient-to-br from-green-50 to-emerald-100">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-6">Верификация застройщиков</h1>
        <p class="text-xl text-gray-600 mb-8">Проверьте надежность застройщика с помощью блокчейн-технологий и открытых реестров</p>
      </div>
    </section>

    <!-- Search Section -->
    <section class="py-16">
      <div class="max-w-4xl mx-auto px-4">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <h2 class="text-2xl font-semibold mb-6 text-center">Найти застройщика</h2>
          <div class="flex flex-col md:flex-row gap-4">
            <input 
              type="text" 
              placeholder="Название компании или ИНН" 
              class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
            <button class="bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors">
              Найти
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Verification Features -->
    <section class="py-16 bg-white">
      <div class="max-w-6xl mx-auto px-4">
        <h2 class="text-3xl font-bold text-center mb-12">Что мы проверяем</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div class="text-center">
            <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <h3 class="font-semibold text-lg mb-2">Юридическая информация</h3>
            <p class="text-gray-600">Проверка регистрации, лицензий и документов компании</p>
          </div>
          <div class="text-center">
            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
              </svg>
            </div>
            <h3 class="font-semibold text-lg mb-2">Финансовое состояние</h3>
            <p class="text-gray-600">Анализ бухгалтерской отчетности и кредитной истории</p>
          </div>
          <div class="text-center">
            <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
              </svg>
            </div>
            <h3 class="font-semibold text-lg mb-2">История проектов</h3>
            <p class="text-gray-600">Отзывы клиентов и завершенные объекты</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Blockchain Section -->
    <section class="py-16 bg-gray-50">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h2 class="text-3xl font-bold mb-8">Блокчейн-верификация</h2>
        <p class="text-xl text-gray-600 mb-8">Все данные о застройщиках хранятся в блокчейне для обеспечения прозрачности и неизменности информации</p>
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <div class="flex items-center justify-center space-x-4 mb-6">
            <div class="w-3 h-3 bg-green-500 rounded-full"></div>
            <div class="w-3 h-3 bg-green-500 rounded-full"></div>
            <div class="w-3 h-3 bg-green-500 rounded-full"></div>
            <div class="w-3 h-3 bg-green-500 rounded-full"></div>
            <div class="w-3 h-3 bg-green-500 rounded-full"></div>
          </div>
          <p class="text-gray-600">Каждый блок содержит хеш предыдущего блока, обеспечивая целостность данных</p>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-16 bg-gradient-to-r from-green-600 to-emerald-700">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h2 class="text-3xl md:text-4xl font-bold text-white mb-6">Начните проверку прямо сейчас</h2>
        <p class="text-xl text-green-100 mb-8">Убедитесь в надежности застройщика перед покупкой недвижимости</p>
        <button class="bg-white text-green-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
          Проверить застройщика
        </button>
      </div>
    </section>

    <Footer />
  </div>
</template>

<script setup>
// Developer verification page
</script> 
<template>
  <div class="min-h-screen bg-gray-50">
    <HeaderNavbar />

    <!-- Hero Section -->
    <section class="pt-24 pb-12 bg-gradient-to-br from-blue-50 to-indigo-100">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-6">Сервисы для покупателей и застройщиков</h1>
        <p class="text-xl text-gray-600 mb-8">Воспользуйтесь современными инструментами для поиска, анализа и безопасных сделок с недвижимостью</p>
      </div>
    </section>

    <!-- Services Cards -->
    <section class="py-16">
      <div class="max-w-7xl mx-auto px-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <!-- AI Assistant Card - Featured -->
        <NuxtLink to="/services/personal" class="group lg:col-span-3 md:col-span-2">
          <div class="bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 rounded-xl shadow-lg border border-blue-500 p-8 flex flex-col items-center text-center transition-all duration-300 hover:shadow-xl hover:scale-105 cursor-pointer relative overflow-hidden">
            <div class="absolute inset-0 bg-gradient-to-r from-blue-400/20 to-purple-400/20"></div>
            <div class="relative z-10">
              <div class="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-full flex items-center mx-auto justify-center mb-6">
                <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
                </svg>
              </div>
              <h3 class="text-2xl font-bold text-white mb-3 group-hover:text-blue-100 transition-colors">AI Ассистент по подбору</h3>
              <p class="text-blue-100 mb-4 text-lg">Персональные рекомендации недвижимости на основе ваших предпочтений с использованием искусственного интеллекта</p>
              <div class="flex items-center justify-center space-x-4 text-blue-100">
                <span class="flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  Умный анализ
                </span>
                <span class="flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  Персональный подход
                </span>
                <span class="flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  24/7 доступ
                </span>
              </div>
            </div>
          </div>
        </NuxtLink>
        
        <NuxtLink to="/catalog" class="group">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8 flex flex-col items-center text-center transition-all duration-300 hover:shadow-lg hover:border-blue-300 hover:scale-105 cursor-pointer">
            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4 group-hover:bg-blue-200 transition-colors">
              <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
            </div>
            <h3 class="text-xl font-semibold mb-2 group-hover:text-blue-600 transition-colors">Поиск недвижимости</h3>
            <p class="text-gray-600 mb-4">Удобный фильтр, актуальные предложения, подробные описания и фотографии объектов.</p>
          </div>
        </NuxtLink>
        
        <NuxtLink to="/services/verification" class="group">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8 flex flex-col items-center text-center transition-all duration-300 hover:shadow-lg hover:border-green-300 hover:scale-105 cursor-pointer">
            <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4 group-hover:bg-green-200 transition-colors">
              <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </div>
            <h3 class="text-xl font-semibold mb-2 group-hover:text-green-600 transition-colors">Верификация застройщиков</h3>
            <p class="text-gray-600 mb-4">Проверка надежности компаний с помощью блокчейн-технологий и открытых реестров.</p>
          </div>
        </NuxtLink>
        
        <NuxtLink to="/analytics" class="group">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8 flex flex-col items-center text-center transition-all duration-300 hover:shadow-lg hover:border-purple-300 hover:scale-105 cursor-pointer">
            <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mb-4 group-hover:bg-purple-200 transition-colors">
              <svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/></svg>
            </div>
            <h3 class="text-xl font-semibold mb-2 group-hover:text-purple-600 transition-colors">Аналитика цен</h3>
            <p class="text-gray-600 mb-4">Динамика цен, сравнение по районам, прогнозы и рекомендации на основе ИИ.</p>
          </div>
        </NuxtLink>
        
        <NuxtLink to="/services/mortgage" class="group">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8 flex flex-col items-center text-center transition-all duration-300 hover:shadow-lg hover:border-orange-300 hover:scale-105 cursor-pointer">
            <div class="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mb-4 group-hover:bg-orange-200 transition-colors">
              <svg class="w-8 h-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
            </div>
            <h3 class="text-xl font-semibold mb-2 group-hover:text-orange-600 transition-colors">Ипотечный калькулятор</h3>
            <p class="text-gray-600 mb-4">Рассчитайте ежемесячный платеж и узнайте лучшие предложения банков.</p>
          </div>
        </NuxtLink>
        
        <NuxtLink to="/services/guides" class="group">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8 flex flex-col items-center text-center transition-all duration-300 hover:shadow-lg hover:border-pink-300 hover:scale-105 cursor-pointer">
            <div class="w-16 h-16 bg-pink-100 rounded-full flex items-center justify-center mb-4 group-hover:bg-pink-200 transition-colors">
              <svg class="w-8 h-8 text-pink-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
            </div>
            <h3 class="text-xl font-semibold mb-2 group-hover:text-pink-600 transition-colors">Гиды по покупке</h3>
            <p class="text-gray-600 mb-4">Пошаговые инструкции и советы для безопасной и выгодной покупки недвижимости.</p>
          </div>
        </NuxtLink>
        
        <NuxtLink to="/services/support" class="group">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8 flex flex-col items-center text-center transition-all duration-300 hover:shadow-lg hover:border-yellow-300 hover:scale-105 cursor-pointer">
            <div class="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mb-4 group-hover:bg-yellow-200 transition-colors">
              <svg class="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
            </div>
            <h3 class="text-xl font-semibold mb-2 group-hover:text-yellow-600 transition-colors">Поддержка 24/7</h3>
            <p class="text-gray-600 mb-4">Консультации экспертов и помощь на всех этапах сделки.</p>
          </div>
        </NuxtLink>
      </div>
    </section>

    <!-- Advantages Section -->
    <section class="py-16 bg-white">
      <div class="max-w-5xl mx-auto px-4 text-center">
        <h2 class="text-3xl font-bold text-gray-900 mb-8">Почему выбирают нас?</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="flex flex-col items-center">
            <div class="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mb-4">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            </div>
            <h3 class="font-semibold text-lg mb-2">Безопасность сделок</h3>
            <p class="text-gray-600">Блокчейн-верификация и прозрачность на каждом этапе.</p>
          </div>
          <div class="flex flex-col items-center">
            <div class="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center mb-4">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>
            </div>
            <h3 class="font-semibold text-lg mb-2">Современные технологии</h3>
            <p class="text-gray-600">ИИ-аналитика, автоматизация и удобные сервисы.</p>
          </div>
          <div class="flex flex-col items-center">
            <div class="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center mb-4">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
            </div>
            <h3 class="font-semibold text-lg mb-2">Экспертная поддержка</h3>
            <p class="text-gray-600">Профессиональные консультации и сопровождение.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-16 bg-gradient-to-r from-blue-600 to-indigo-700">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h2 class="text-3xl md:text-4xl font-bold text-white mb-6">Попробуйте сервисы бесплатно</h2>
        <p class="text-xl text-blue-100 mb-8">Зарегистрируйтесь и получите доступ к полному функционалу платформы</p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <button class="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">Зарегистрироваться</button>
          <button class="border border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors">Связаться с поддержкой</button>
        </div>
      </div>
    </section>

    <Footer />
  </div>
</template>

<script setup>
// Services page component
</script>
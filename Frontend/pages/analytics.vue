<template>
  <div class="min-h-screen bg-gray-50">
    <HeaderNavbar />
    
    <!-- Hero Section -->
    <section class="pt-24 pb-12 bg-gradient-to-br from-blue-50 to-indigo-100">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Аналитика рынка недвижимости
          </h1>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            Получите глубокую аналитику рынка недвижимости с использованием ИИ и блокчейн-технологий
          </p>
          <div class="flex flex-wrap justify-center gap-4">
            <button class="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors">
              Получить отчет
            </button>
            <button class="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors">
              Демо версия
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Market Overview -->
    <section class="py-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">Обзор рынка</h2>
          <p class="text-gray-600 max-w-2xl mx-auto">
            Актуальная статистика и тренды рынка недвижимости Москвы
          </p>
        </div>
        
        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between mb-4">
              <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
                </svg>
              </div>
              <span class="text-green-500 text-sm font-semibold">+12.5%</span>
            </div>
            <h3 class="text-2xl font-bold text-gray-900 mb-1">₽245,000</h3>
            <p class="text-gray-600 text-sm">Средняя цена за м²</p>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between mb-4">
              <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                </svg>
              </div>
              <span class="text-green-500 text-sm font-semibold">+8.3%</span>
            </div>
            <h3 class="text-2xl font-bold text-gray-900 mb-1">1,247</h3>
            <p class="text-gray-600 text-sm">Новых объектов</p>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between mb-4">
              <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                </svg>
              </div>
              <span class="text-red-500 text-sm font-semibold">-2.1%</span>
            </div>
            <h3 class="text-2xl font-bold text-gray-900 mb-1">89</h3>
            <p class="text-gray-600 text-sm">Дней на рынке</p>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between mb-4">
              <div class="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
              </div>
              <span class="text-green-500 text-sm font-semibold">+15.7%</span>
            </div>
            <h3 class="text-2xl font-bold text-gray-900 mb-1">₽12.4M</h3>
            <p class="text-gray-600 text-sm">Объем сделок</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Price Trends Chart -->
    <section class="py-16 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">Динамика цен</h2>
          <p class="text-gray-600">Изменение цен на недвижимость за последние 12 месяцев</p>
        </div>
        
        <!-- Chart Container -->
        <div class="bg-gray-50 rounded-xl p-8">
          <div class="flex items-center justify-between mb-6">
            <div class="flex space-x-4">
              <button class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium">1 год</button>
              <button class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg text-sm font-medium">6 месяцев</button>
              <button class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg text-sm font-medium">3 месяца</button>
            </div>
            <div class="flex items-center space-x-4">
              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 bg-blue-600 rounded-full"></div>
                <span class="text-sm text-gray-600">Средняя цена</span>
              </div>
              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 bg-green-500 rounded-full"></div>
                <span class="text-sm text-gray-600">Новостройки</span>
              </div>
            </div>
          </div>
          
          <!-- Mock Chart -->
          <div class="h-80 bg-white rounded-lg border border-gray-200 flex items-center justify-center">
            <div class="text-center">
              <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
              <p class="text-gray-500">Интерактивный график цен</p>
              <p class="text-sm text-gray-400">Данные обновляются в реальном времени</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- District Analysis -->
    <section class="py-16 bg-gray-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">Анализ по районам</h2>
          <p class="text-gray-600">Сравнение цен и активности по районам Москвы</p>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Top Districts -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 class="text-xl font-semibold text-gray-900 mb-6">Топ районов по цене</h3>
            <div class="space-y-4">
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div class="flex items-center space-x-3">
                  <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                    <span class="text-blue-600 font-semibold text-sm">1</span>
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">Центральный</p>
                    <p class="text-sm text-gray-500">Москва</p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="font-semibold text-gray-900">₽320,000</p>
                  <p class="text-sm text-green-500">+18.2%</p>
                </div>
              </div>
              
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div class="flex items-center space-x-3">
                  <div class="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                    <span class="text-gray-600 font-semibold text-sm">2</span>
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">Хамовники</p>
                    <p class="text-sm text-gray-500">Москва</p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="font-semibold text-gray-900">₽295,000</p>
                  <p class="text-sm text-green-500">+15.7%</p>
                </div>
              </div>
              
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div class="flex items-center space-x-3">
                  <div class="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                    <span class="text-orange-600 font-semibold text-sm">3</span>
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">Арбат</p>
                    <p class="text-sm text-gray-500">Москва</p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="font-semibold text-gray-900">₽285,000</p>
                  <p class="text-sm text-green-500">+12.3%</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Market Activity -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 class="text-xl font-semibold text-gray-900 mb-6">Активность рынка</h3>
            <div class="space-y-6">
              <div>
                <div class="flex justify-between items-center mb-2">
                  <span class="text-sm font-medium text-gray-700">Новые объявления</span>
                  <span class="text-sm text-gray-500">1,247</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div class="bg-blue-600 h-2 rounded-full" style="width: 85%"></div>
                </div>
              </div>
              
              <div>
                <div class="flex justify-between items-center mb-2">
                  <span class="text-sm font-medium text-gray-700">Просмотры</span>
                  <span class="text-sm text-gray-500">45,892</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div class="bg-green-500 h-2 rounded-full" style="width: 92%"></div>
                </div>
              </div>
              
              <div>
                <div class="flex justify-between items-center mb-2">
                  <span class="text-sm font-medium text-gray-700">Заявки</span>
                  <span class="text-sm text-gray-500">3,456</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div class="bg-purple-500 h-2 rounded-full" style="width: 67%"></div>
                </div>
              </div>
              
              <div>
                <div class="flex justify-between items-center mb-2">
                  <span class="text-sm font-medium text-gray-700">Сделки</span>
                  <span class="text-sm text-gray-500">892</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div class="bg-orange-500 h-2 rounded-full" style="width: 45%"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- AI Insights -->
    <section class="py-16 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">ИИ-аналитика</h2>
          <p class="text-gray-600">Прогнозы и рекомендации на основе машинного обучения</p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200">
            <div class="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mb-4">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-3">Прогноз цен</h3>
            <p class="text-gray-600 mb-4">На основе исторических данных и рыночных трендов мы прогнозируем изменение цен на 15-20% в ближайшие 6 месяцев.</p>
            <div class="flex items-center text-green-600 font-semibold">
              <span>+18.5%</span>
              <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"></path>
              </svg>
            </div>
          </div>

          <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border border-green-200">
            <div class="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center mb-4">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-3">Лучшее время для покупки</h3>
            <p class="text-gray-600 mb-4">Анализ показывает, что оптимальное время для покупки недвижимости - март-апрель 2024 года.</p>
            <div class="flex items-center text-blue-600 font-semibold">
              <span>Март 2024</span>
              <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
              </svg>
            </div>
          </div>

          <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200">
            <div class="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center mb-4">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-3">Топ районов для инвестиций</h3>
            <p class="text-gray-600 mb-4">Рекомендуем обратить внимание на районы с высокой потенциальной доходностью и развивающейся инфраструктурой.</p>
            <div class="flex items-center text-purple-600 font-semibold">
              <span>5 районов</span>
              <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-16 bg-gradient-to-r from-blue-600 to-indigo-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="text-3xl md:text-4xl font-bold text-white mb-6">
          Получите полную аналитику рынка
        </h2>
        <p class="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
          Подпишитесь на еженедельные отчеты и получайте актуальную информацию о рынке недвижимости
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <button class="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
            Подписаться на отчеты
          </button>
          <button class="border border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors">
            Связаться с экспертом
          </button>
        </div>
      </div>
    </section>

    <Footer />
  </div>
</template>

<script setup>
// Analytics page component
</script>
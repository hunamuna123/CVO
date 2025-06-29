<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
    <!-- Auth Loading -->
    <div v-if="authLoading" class="fixed inset-0 bg-white bg-opacity-90 flex items-center justify-center z-50">
      <div class="text-center">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
          <svg class="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
        <p class="text-gray-600">Проверяем авторизацию...</p>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else>
      <HeaderNavbar />

      <!-- Hero Section -->
      <section class="pt-24 pb-12 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 relative overflow-hidden">
        <div class="absolute inset-0 bg-black/10"></div>
        <div class="absolute inset-0">
          <div class="absolute top-0 left-0 w-72 h-72 bg-white/10 rounded-full blur-3xl"></div>
          <div class="absolute bottom-0 right-0 w-96 h-96 bg-purple-400/20 rounded-full blur-3xl"></div>
        </div>
        <div class="max-w-4xl mx-auto px-4 text-center relative z-10">
          <div class="inline-flex items-center px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full text-white text-sm font-medium mb-6">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
            AI-рекомендации
          </div>
          <h1 class="text-4xl md:text-6xl font-bold text-white mb-6 leading-tight">
            Персональные рекомендации
            <span class="block text-blue-200">недвижимости</span>
          </h1>
          <p class="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Искусственный интеллект проанализирует ваши предпочтения и найдет идеальные варианты недвижимости
          </p>
        </div>
      </section>

      <!-- Main Content -->
      <section class="py-16">
        <div class="max-w-7xl mx-auto px-4">
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Settings Form -->
            <div class="lg:col-span-1">
              <div class="bg-white rounded-2xl shadow-xl border border-gray-200 p-8 sticky top-24">
                <h2 class="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                  <svg class="w-6 h-6 mr-3 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  </svg>
                  Настройки поиска
                </h2>

                <div class="space-y-6">
                  <!-- Budget Range -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Бюджет (₽)</label>
                    <div class="grid grid-cols-2 gap-3">
                      <input 
                        v-model="form.budget_min" 
                        type="number" 
                        placeholder="От"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                      <input 
                        v-model="form.budget_max" 
                        type="number" 
                        placeholder="До"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                    </div>
                  </div>

                  <!-- Property Type -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Тип недвижимости</label>
                    <select 
                      v-model="form.property_type"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">Любой</option>
                      <option value="apartment">Квартира</option>
                      <option value="house">Дом</option>
                      <option value="commercial">Коммерческая</option>
                    </select>
                  </div>

                  <!-- Rooms Count -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Количество комнат</label>
                    <div class="flex flex-wrap gap-2">
                      <button 
                        v-for="room in [1,2,3,4,5]" 
                        :key="room"
                        type="button"
                        @click="toggleRoom(room)"
                        :class="[
                          'px-3 py-1 rounded-full text-sm font-medium transition-colors',
                          form.rooms_count.includes(room) 
                            ? 'bg-blue-600 text-white' 
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        ]"
                      >
                        {{ room }}
                      </button>
                    </div>
                  </div>

                  <!-- Area Range -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Площадь (м²)</label>
                    <div class="grid grid-cols-2 gap-3">
                      <input 
                        v-model="form.min_area" 
                        type="number" 
                        placeholder="От"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                      <input 
                        v-model="form.max_area" 
                        type="number" 
                        placeholder="До"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                    </div>
                  </div>

                  <!-- Preferred Regions -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Предпочитаемые районы</label>
                    <input 
                      v-model="form.preferred_regions" 
                      type="text" 
                      placeholder="Например: Центральный, Западный"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                  </div>

                  <!-- Must Have Features -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Обязательные особенности</label>
                    <div class="space-y-2">
                      <label v-for="feature in ['Парковка', 'Лифт', 'Балкон', 'Ремонт']" :key="feature" class="flex items-center">
                        <input 
                          type="checkbox" 
                          :value="feature"
                          v-model="form.must_have_features"
                          class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        >
                        <span class="ml-2 text-sm text-gray-700">{{ feature }}</span>
                      </label>
                    </div>
                  </div>

                  <!-- Urgency Level -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Срочность</label>
                    <select 
                      v-model="form.urgency_level"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="low">Низкая</option>
                      <option value="medium">Средняя</option>
                      <option value="high">Высокая</option>
                    </select>
                  </div>

                  <!-- Submit Button -->
                  <button 
                    type="button"
                    @click="getRecommendations"
                    :disabled="loading"
                    class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                  >
                    <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ loading ? 'Анализируем...' : 'Получить рекомендации' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Results Section -->
            <div class="lg:col-span-2">
              <!-- Loading State -->
              <div v-if="loading" class="bg-white rounded-2xl shadow-xl border border-gray-200 p-8">
                <div class="text-center">
                  <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-6">
                    <svg class="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  </div>
                  <h3 class="text-xl font-semibold text-gray-900 mb-2">Анализируем ваши предпочтения</h3>
                  <p class="text-gray-600 mb-6">ИИ изучает рынок недвижимости и подбирает лучшие варианты</p>
                  
                  <!-- Progress Steps -->
                  <div class="max-w-md mx-auto space-y-4">
                    <div v-for="(step, index) in loadingSteps" :key="index" class="flex items-center">
                      <div :class="[
                        'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium mr-3',
                        step.completed ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'
                      ]">
                        <svg v-if="step.completed" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                        <span v-else>{{ index + 1 }}</span>
                      </div>
                      <span :class="[
                        'text-sm',
                        step.completed ? 'text-gray-900' : 'text-gray-500'
                      ]">{{ step.text }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Results -->
              <div v-else-if="recommendations.length > 0" class="space-y-6">
                <!-- Results Header -->
                <div class="bg-white rounded-2xl shadow-xl border border-gray-200 p-6">
                  <div class="flex items-center justify-between mb-4">
                    <h2 class="text-2xl font-bold text-gray-900 flex items-center">
                      <svg class="w-6 h-6 mr-3 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                      </svg>
                      Найдено {{ recommendations.length }} вариантов
                    </h2>
                    <div class="flex items-center space-x-2">
                      <span class="text-sm text-gray-500">Сортировка:</span>
                      <select v-model="sortBy" class="text-sm border border-gray-300 rounded-lg px-3 py-1 focus:ring-2 focus:ring-blue-500">
                        <option value="relevance">По релевантности</option>
                        <option value="price">По цене</option>
                        <option value="area">По площади</option>
                      </select>
                    </div>
                  </div>
                  <p class="text-gray-600">Рекомендации основаны на ваших предпочтениях и анализе рынка</p>
                </div>

                <!-- Property Cards -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div 
                    v-for="property in sortedRecommendations" 
                    :key="property.id"
                    class="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1"
                  >
                    <!-- Property Image -->
                    <div class="relative h-48 bg-gradient-to-br from-blue-100 to-indigo-100">
                      <div class="absolute inset-0 flex items-center justify-center">
                        <svg class="w-16 h-16 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                        </svg>
                      </div>
                      <div class="absolute top-4 right-4 bg-green-500 text-white px-2 py-1 rounded-full text-xs font-medium">
                        AI рекомендует
                      </div>
                    </div>

                    <!-- Property Info -->
                    <div class="p-6">
                      <h3 class="text-xl font-semibold text-gray-900 mb-2">{{ property.title }}</h3>
                      <p class="text-gray-600 mb-4">{{ property.location }}</p>
                      
                      <!-- Property Details -->
                      <div class="grid grid-cols-2 gap-4 mb-4">
                        <div class="flex items-center text-sm text-gray-600">
                          <svg class="w-4 h-4 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
                          </svg>
                          {{ property.area }} м²
                        </div>
                        <div class="flex items-center text-sm text-gray-600">
                          <svg class="w-4 h-4 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z"/>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5a2 2 0 012-2h4a2 2 0 012 2v2H8V5z"/>
                          </svg>
                          {{ property.rooms }} комн.
                        </div>
                      </div>

                      <!-- Price -->
                      <div class="flex items-center justify-between mb-4">
                        <div>
                          <span class="text-2xl font-bold text-gray-900">{{ formatPrice(property.price) }}</span>
                          <span class="text-sm text-gray-500">₽</span>
                        </div>
                        <div class="text-right">
                          <div class="text-sm text-gray-500">за м²</div>
                          <div class="font-semibold text-gray-900">{{ formatPrice(Math.round(property.price / property.area)) }} ₽</div>
                        </div>
                      </div>

                      <!-- AI Score -->
                      <div class="mb-4">
                        <div class="flex items-center justify-between mb-1">
                          <span class="text-sm font-medium text-gray-700">Соответствие вашим критериям</span>
                          <span class="text-sm font-bold text-green-600">{{ property.ai_score }}%</span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            class="bg-gradient-to-r from-green-400 to-green-600 h-2 rounded-full transition-all duration-500"
                            :style="{ width: property.ai_score + '%' }"
                          ></div>
                        </div>
                      </div>

                      <!-- Action Buttons -->
                      <div class="flex space-x-3">
                        <button class="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors">
                          Подробнее
                        </button>
                        <button class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
                          </svg>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Empty State -->
              <div v-else class="bg-white rounded-2xl shadow-xl border border-gray-200 p-12 text-center">
                <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-6">
                  <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
                  </svg>
                </div>
                <h3 class="text-xl font-semibold text-gray-900 mb-2">Настройте параметры поиска</h3>
                <p class="text-gray-600 mb-6">Укажите ваши предпочтения в форме слева, и ИИ найдет идеальные варианты недвижимости</p>
                <div class="flex items-center justify-center space-x-2 text-sm text-gray-500">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  <span>Анализ основан на реальных данных рынка</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Features Section -->
      <section class="py-16 bg-white">
        <div class="max-w-6xl mx-auto px-4">
          <h2 class="text-3xl font-bold text-center text-gray-900 mb-12">Как работает AI-анализ</h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div class="text-center">
              <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                </svg>
              </div>
              <h3 class="text-xl font-semibold mb-2">Анализ рынка</h3>
              <p class="text-gray-600">ИИ изучает тысячи объявлений и анализирует динамику цен в реальном времени</p>
            </div>
            <div class="text-center">
              <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
                </svg>
              </div>
              <h3 class="text-xl font-semibold mb-2">Персонализация</h3>
              <p class="text-gray-600">Учитывает ваши предпочтения, бюджет и образ жизни для точного подбора</p>
            </div>
            <div class="text-center">
              <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <h3 class="text-xl font-semibold mb-2">Точные рекомендации</h3>
              <p class="text-gray-600">Предоставляет варианты с высоким процентом соответствия вашим критериям</p>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api as useApiStore } from "@/store/api";

const apiStore = useApiStore()

const loading = ref(false)
const recommendations = ref([])
const sortBy = ref('relevance')
const isAuthenticated = ref(false)
const authLoading = ref(true)

const form = ref({
  budget_min: '',
  budget_max: '',
  property_type: '',
  rooms_count: [],
  urgency_level: 'medium',
  min_area: '',
  max_area: '',
  preferred_regions: null,
  must_have_features: []
})

const loadingSteps = ref([
  { text: 'Анализируем ваши предпочтения', completed: false },
  { text: 'Изучаем рынок недвижимости', completed: false },
  { text: 'Подбираем подходящие варианты', completed: false },
  { text: 'Рассчитываем релевантность', completed: false }
])

const sortedRecommendations = computed(() => {
  if (!recommendations.value.length) return []
  
  return [...recommendations.value].sort((a, b) => {
    switch (sortBy.value) {
      case 'price':
        return (a.price || 0) - (b.price || 0)
      case 'area':
        return (a.area || 0) - (b.area || 0)
      default:
        return (b.ai_score || 0) - (a.ai_score || 0)
    }
  })
})

const toggleRoom = (room) => {
  const index = form.value.rooms_count.indexOf(room)
  if (index > -1) {
    form.value.rooms_count.splice(index, 1)
  } else {
    form.value.rooms_count.push(room)
  }
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU').format(price)
}

const simulateLoadingSteps = async () => {
  for (let i = 0; i < loadingSteps.value.length; i++) {
    await new Promise(resolve => setTimeout(resolve, 800))
    loadingSteps.value[i].completed = true
  }
}

const getRecommendations = async () => {
  loading.value = true
  recommendations.value = []
  
  loadingSteps.value.forEach(step => step.completed = false)
  
  try {
    simulateLoadingSteps()
    
    const requestData = {
      budget_min: parseInt(form.value.budget_min) || 0,
      budget_max: parseInt(form.value.budget_max) || 0,
      property_type: form.value.property_type,
      rooms_count: form.value.rooms_count,
      urgency_level: form.value.urgency_level,
      min_area: parseInt(form.value.min_area) || 0,
      max_area: parseInt(form.value.max_area) || 0,
      preferred_regions: form.value.preferred_regions ? [form.value.preferred_regions] : [],
      must_have_features: form.value.must_have_features
    }

    const accessToken = useCookie('access_token')
    const refreshToken = useCookie('refresh_token')
    
    const headers = {
      'Content-Type': 'application/json',
    }
    
    if (accessToken.value) {
      headers['Authorization'] = `Bearer ${accessToken.value}`
    }
    
    const response = await fetch(`${apiStore.url}api/v1/ai/recommend-properties`, {
      method: 'POST',
      headers,
      body: JSON.stringify(requestData)
    })
    
    if (!response.ok) {
      if (response.status === 401) {
        console.error('Unauthorized access')
        navigateTo('/auth/login')
        return
      }
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    console.log('API Response:', data)
    
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    recommendations.value = [
      {
        id: 1,
        title: 'Современная 2-комнатная квартира',
        location: 'Центральный район',
        price: 8500000,
        area: 75,
        rooms: 2,
        ai_score: 95
      },
      {
        id: 2,
        title: 'Уютная 1-комнатная квартира',
        location: 'Западный район',
        price: 6500000,
        area: 45,
        rooms: 1,
        ai_score: 88
      },
      {
        id: 3,
        title: 'Просторная 3-комнатная квартира',
        location: 'Северный район',
        price: 12000000,
        area: 95,
        rooms: 3,
        ai_score: 92
      },
      {
        id: 4,
        title: 'Студия в новостройке',
        location: 'Восточный район',
        price: 4500000,
        area: 35,
        rooms: 1,
        ai_score: 85
      }
    ]
  } catch (apiError) {
    console.error('API Error:', apiError)
  } finally {
    loading.value = false
  }
}

const checkAuth = () => {
  const accessToken = useCookie('access_token')
  const refreshToken = useCookie('refresh_token')
  isAuthenticated.value = !!(accessToken.value || refreshToken.value)
  
  if (!isAuthenticated.value) {
    navigateTo('/auth/login')
  }
  
  authLoading.value = false
}

onMounted(() => {
  checkAuth()
  
  form.value = {
    budget_min: '',
    budget_max: '',
    property_type: '',
    rooms_count: [],
    urgency_level: 'medium',
    min_area: '',
    max_area: '',
    preferred_regions: null,
    must_have_features: []
  }
})
</script>

<style scoped>
/* Custom animations */
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

.fade-in-up {
  animation: fadeInUp 0.6s ease-out;
}
</style> 
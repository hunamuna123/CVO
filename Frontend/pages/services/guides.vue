<template>
  <div class="min-h-screen bg-gray-50">
    <HeaderNavbar />

    <!-- Hero Section -->
    <section class="pt-24 pb-12 bg-gradient-to-br from-pink-50 to-rose-100">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-6">Гиды по покупке недвижимости</h1>
        <p class="text-xl text-gray-600 mb-8">Пошаговые инструкции и советы для безопасной и выгодной покупки недвижимости</p>
      </div>
    </section>

    <!-- Guides Section -->
    <section class="py-16">
      <div class="max-w-6xl mx-auto px-4">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-lg transition-shadow">
            <div class="w-12 h-12 bg-pink-100 rounded-full flex items-center justify-center mb-4">
              <span class="text-2xl font-bold text-pink-600">1</span>
            </div>
            <h3 class="text-xl font-semibold mb-3">Подготовка к покупке</h3>
            <ul class="text-gray-600 space-y-2 text-sm">
              <li>• Определение бюджета</li>
              <li>• Выбор района</li>
              <li>• Изучение рынка</li>
              <li>• Подготовка документов</li>
            </ul>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-lg transition-shadow">
            <div class="w-12 h-12 bg-pink-100 rounded-full flex items-center justify-center mb-4">
              <span class="text-2xl font-bold text-pink-600">2</span>
            </div>
            <h3 class="text-xl font-semibold mb-3">Поиск объекта</h3>
            <ul class="text-gray-600 space-y-2 text-sm">
              <li>• Использование фильтров</li>
              <li>• Сравнение предложений</li>
              <li>• Изучение инфраструктуры</li>
              <li>• Проверка застройщика</li>
            </ul>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-lg transition-shadow">
            <div class="w-12 h-12 bg-pink-100 rounded-full flex items-center justify-center mb-4">
              <span class="text-2xl font-bold text-pink-600">3</span>
            </div>
            <h3 class="text-xl font-semibold mb-3">Проверка объекта</h3>
            <ul class="text-gray-600 space-y-2 text-sm">
              <li>• Осмотр недвижимости</li>
              <li>• Проверка документов</li>
              <li>• Оценка состояния</li>
              <li>• Консультация юриста</li>
            </ul>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-lg transition-shadow">
            <div class="w-12 h-12 bg-pink-100 rounded-full flex items-center justify-center mb-4">
              <span class="text-2xl font-bold text-pink-600">4</span>
            </div>
            <h3 class="text-xl font-semibold mb-3">Финансирование</h3>
            <ul class="text-gray-600 space-y-2 text-sm">
              <li>• Выбор банка</li>
              <li>• Расчет ипотеки</li>
              <li>• Сбор документов</li>
              <li>• Получение одобрения</li>
            </ul>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-lg transition-shadow">
            <div class="w-12 h-12 bg-pink-100 rounded-full flex items-center justify-center mb-4">
              <span class="text-2xl font-bold text-pink-600">5</span>
            </div>
            <h3 class="text-xl font-semibold mb-3">Сделка</h3>
            <ul class="text-gray-600 space-y-2 text-sm">
              <li>• Подписание договора</li>
              <li>• Регистрация сделки</li>
              <li>• Передача денег</li>
              <li>• Получение ключей</li>
            </ul>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-lg transition-shadow">
            <div class="w-12 h-12 bg-pink-100 rounded-full flex items-center justify-center mb-4">
              <span class="text-2xl font-bold text-pink-600">6</span>
            </div>
            <h3 class="text-xl font-semibold mb-3">После покупки</h3>
            <ul class="text-gray-600 space-y-2 text-sm">
              <li>• Оформление страховки</li>
              <li>• Регистрация права</li>
              <li>• Переезд</li>
              <li>• Обслуживание</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- Detailed Guides -->
    <section class="py-16 bg-white">
      <div class="max-w-4xl mx-auto px-4">
        <h2 class="text-3xl font-bold text-center mb-12">Подробные руководства</h2>
        <div class="space-y-8">
          <div class="border border-gray-200 rounded-xl p-6">
            <h3 class="text-xl font-semibold mb-4">Как выбрать новостройку</h3>
            <p class="text-gray-600 mb-4">Подробное руководство по выбору квартиры в новостройке, включая проверку застройщика, изучение проекта и оценку рисков.</p>
            <button class="text-pink-600 font-semibold hover:text-pink-700 transition-colors">
              Читать подробнее →
            </button>
          </div>

          <div class="border border-gray-200 rounded-xl p-6">
            <h3 class="text-xl font-semibold mb-4">Покупка вторичного жилья</h3>
            <p class="text-gray-600 mb-4">Пошаговая инструкция по покупке квартиры на вторичном рынке: от поиска до регистрации права собственности.</p>
            <button class="text-pink-600 font-semibold hover:text-pink-700 transition-colors">
              Читать подробнее →
            </button>
          </div>

          <div class="border border-gray-200 rounded-xl p-6">
            <h3 class="text-xl font-semibold mb-4">Ипотека: от А до Я</h3>
            <p class="text-gray-600 mb-4">Полное руководство по получению ипотечного кредита: требования банков, документы, процесс одобрения.</p>
            <button class="text-pink-600 font-semibold hover:text-pink-700 transition-colors">
              Читать подробнее →
            </button>
          </div>

          <div class="border border-gray-200 rounded-xl p-6">
            <h3 class="text-xl font-semibold mb-4">Проверка документов</h3>
            <p class="text-gray-600 mb-4">Как проверить документы на недвижимость и избежать мошенничества при покупке.</p>
            <button class="text-pink-600 font-semibold hover:text-pink-700 transition-colors">
              Читать подробнее →
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Tips Section -->
    <section class="py-16 bg-gray-50">
      <div class="max-w-4xl mx-auto px-4">
        <h2 class="text-3xl font-bold text-center mb-12">Полезные советы</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div class="bg-white rounded-xl p-6 shadow-sm">
            <h3 class="font-semibold text-lg mb-3">💰 Экономия при покупке</h3>
            <ul class="text-gray-600 space-y-2 text-sm">
              <li>• Изучите цены в разных районах</li>
              <li>• Рассмотрите варианты с ремонтом</li>
              <li>• Торгуйтесь с продавцом</li>
              <li>• Сравните предложения банков</li>
            </ul>
          </div>

          <div class="bg-white rounded-xl p-6 shadow-sm">
            <h3 class="font-semibold text-lg mb-3">⚠️ Избегайте рисков</h3>
            <ul class="text-gray-600 space-y-2 text-sm">
              <li>• Проверяйте застройщика</li>
              <li>• Изучайте документы</li>
              <li>• Не торопитесь с решением</li>
              <li>• Консультируйтесь с юристом</li>
            </ul>
          </div>

          <div class="bg-white rounded-xl p-6 shadow-sm">
            <h3 class="font-semibold text-lg mb-3">📋 Подготовка документов</h3>
            <ul class="text-gray-600 space-y-2 text-sm">
              <li>• Паспорт и ИНН</li>
              <li>• Справка о доходах</li>
              <li>• Трудовая книжка</li>
              <li>• Документы на имущество</li>
            </ul>
          </div>

          <div class="bg-white rounded-xl p-6 shadow-sm">
            <h3 class="font-semibold text-lg mb-3">🏠 Выбор района</h3>
            <ul class="text-gray-600 space-y-2 text-sm">
              <li>• Изучите инфраструктуру</li>
              <li>• Проверьте транспортную доступность</li>
              <li>• Узнайте о планах развития</li>
              <li>• Поговорите с местными жителями</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-16 bg-gradient-to-r from-pink-600 to-rose-700">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h2 class="text-3xl md:text-4xl font-bold text-white mb-6">Нужна помощь эксперта?</h2>
        <p class="text-xl text-pink-100 mb-8">Получите персональную консультацию по покупке недвижимости</p>
        <button class="bg-white text-pink-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
          Записаться на консультацию
        </button>
      </div>
    </section>

    <Footer />
  </div>
</template>

<script setup>
// Buying guides page
</script> 
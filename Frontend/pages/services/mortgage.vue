<template>
  <div class="min-h-screen bg-gray-50">
    <HeaderNavbar />

    <!-- Hero Section -->
    <section class="pt-24 pb-12 bg-gradient-to-br from-orange-50 to-amber-100">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-6">Ипотечный калькулятор</h1>
        <p class="text-xl text-gray-600 mb-8">Рассчитайте ежемесячный платеж и узнайте лучшие предложения банков</p>
      </div>
    </section>

    <!-- Calculator Section -->
    <section class="py-16">
      <div class="max-w-6xl mx-auto px-4">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Calculator Form -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
            <h2 class="text-2xl font-semibold mb-6">Калькулятор ипотеки</h2>
            <div class="space-y-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Стоимость недвижимости</label>
                <input 
                  type="number" 
                  v-model="propertyPrice"
                  placeholder="0" 
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                >
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Первоначальный взнос</label>
                <input 
                  type="number" 
                  v-model="downPayment"
                  placeholder="0" 
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                >
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Срок кредита (лет)</label>
                <select 
                  v-model="loanTerm"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                >
                  <option value="5">5 лет</option>
                  <option value="10">10 лет</option>
                  <option value="15">15 лет</option>
                  <option value="20">20 лет</option>
                  <option value="25">25 лет</option>
                  <option value="30">30 лет</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Процентная ставка (%)</label>
                <input 
                  type="number" 
                  v-model="interestRate"
                  step="0.1"
                  placeholder="0" 
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                >
              </div>
              <button 
                @click="calculateMortgage"
                class="w-full bg-orange-600 text-white py-3 rounded-lg font-semibold hover:bg-orange-700 transition-colors"
              >
                Рассчитать
              </button>
            </div>
          </div>

          <!-- Results -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
            <h2 class="text-2xl font-semibold mb-6">Результаты расчета</h2>
            <div class="space-y-4">
              <div class="flex justify-between items-center py-3 border-b border-gray-200">
                <span class="text-gray-600">Сумма кредита:</span>
                <span class="font-semibold">{{ formatCurrency(loanAmount) }}</span>
              </div>
              <div class="flex justify-between items-center py-3 border-b border-gray-200">
                <span class="text-gray-600">Ежемесячный платеж:</span>
                <span class="font-semibold text-orange-600">{{ formatCurrency(monthlyPayment) }}</span>
              </div>
              <div class="flex justify-between items-center py-3 border-b border-gray-200">
                <span class="text-gray-600">Общая сумма к возврату:</span>
                <span class="font-semibold">{{ formatCurrency(totalAmount) }}</span>
              </div>
              <div class="flex justify-between items-center py-3 border-b border-gray-200">
                <span class="text-gray-600">Переплата по кредиту:</span>
                <span class="font-semibold text-red-600">{{ formatCurrency(overpayment) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Bank Offers Section -->
    <section class="py-16 bg-white">
      <div class="max-w-6xl mx-auto px-4">
        <h2 class="text-3xl font-bold text-center mb-12">Лучшие предложения банков</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
            <div class="flex items-center mb-4">
              <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mr-4">
                <span class="font-bold text-blue-600">СБ</span>
              </div>
              <div>
                <h3 class="font-semibold">Сбербанк</h3>
                <p class="text-sm text-gray-600">от 7.5% годовых</p>
              </div>
            </div>
            <ul class="text-sm text-gray-600 space-y-2">
              <li>• Первоначальный взнос от 10%</li>
              <li>• Срок до 30 лет</li>
              <li>• Без комиссий</li>
            </ul>
          </div>
          <div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
            <div class="flex items-center mb-4">
              <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mr-4">
                <span class="font-bold text-green-600">ВТБ</span>
              </div>
              <div>
                <h3 class="font-semibold">ВТБ</h3>
                <p class="text-sm text-gray-600">от 7.8% годовых</p>
              </div>
            </div>
            <ul class="text-sm text-gray-600 space-y-2">
              <li>• Первоначальный взнос от 15%</li>
              <li>• Срок до 25 лет</li>
              <li>• Льготные условия</li>
            </ul>
          </div>
          <div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
            <div class="flex items-center mb-4">
              <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mr-4">
                <span class="font-bold text-purple-600">РСХ</span>
              </div>
              <div>
                <h3 class="font-semibold">Россельхозбанк</h3>
                <p class="text-sm text-gray-600">от 8.2% годовых</p>
              </div>
            </div>
            <ul class="text-sm text-gray-600 space-y-2">
              <li>• Первоначальный взнос от 20%</li>
              <li>• Срок до 30 лет</li>
              <li>• Специальные программы</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-16 bg-gradient-to-r from-orange-600 to-amber-700">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h2 class="text-3xl md:text-4xl font-bold text-white mb-6">Получите одобрение ипотеки</h2>
        <p class="text-xl text-orange-100 mb-8">Оставьте заявку и получите предварительное решение от банков</p>
        <button class="bg-white text-orange-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
          Оставить заявку
        </button>
      </div>
    </section>

    <Footer />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const propertyPrice = ref(0)
const downPayment = ref(0)
const loanTerm = ref(20)
const interestRate = ref(8.5)

const loanAmount = computed(() => {
  return Math.max(0, propertyPrice.value - downPayment.value)
})

const monthlyPayment = computed(() => {
  if (loanAmount.value <= 0 || interestRate.value <= 0) return 0
  
  const monthlyRate = interestRate.value / 100 / 12
  const numberOfPayments = loanTerm.value * 12
  
  if (monthlyRate === 0) return loanAmount.value / numberOfPayments
  
  return loanAmount.value * (monthlyRate * Math.pow(1 + monthlyRate, numberOfPayments)) / (Math.pow(1 + monthlyRate, numberOfPayments) - 1)
})

const totalAmount = computed(() => {
  return monthlyPayment.value * loanTerm.value * 12
})

const overpayment = computed(() => {
  return totalAmount.value - loanAmount.value
})

const calculateMortgage = () => {
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0
  }).format(amount)
}
</script> 
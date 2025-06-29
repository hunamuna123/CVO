<template>
  <div
    class="hs-dropdown [--strategy:fixed] lg:[--strategy:fixed] [--adaptive:none] [--is-collapse:true] border rounded-full lg:[--is-collapse:false] [--gpu-acceleration:false]">

    <button id="hs-header-profile-dropdown" type="button" aria-haspopup="menu" aria-expanded="false"
      aria-label="Dropdown"
      class="inline-flex items-center justify-center size-[36px] text-sm font-semibold leading-none rounded-full bg-white text-black">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
        class="lucide lucide-user-icon lucide-user">
        <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
        <circle cx="12" cy="7" r="4" />
      </svg>

    </button>
    <div
      class="hs-dropdown-menu hs-dropdown-open:scale-100 border border-gray-100 hs-dropdown-open:opacity-100 scale-95 opacity-0 z-10 ease-in-out transition-[transform,opacity] duration-200 min-w-60 bg-white shadow-lg rounded-lg hidden"
      role="menu" aria-orientation="vertical" aria-labelledby="hs-header-profile-dropdown">

      <div class="p-1.5 space-y-0.5">
        <NuxtLink
          class="p-2 flex gap-x-3 hover:bg-gray-100 focus:outline-none focus:bg-gray-100 rounded-lg transition-colors duration-200 text-sm truncate font-medium"
          to="/profile">
          <div class="w-full flex flex-col items-start justify-center">
            Профиль
          </div>
        </NuxtLink>
        <NuxtLink
          class="p-2 flex gap-x-3 hover:bg-gray-100 focus:outline-none focus:bg-gray-100 rounded-lg transition-colors duration-200 text-sm truncate font-medium"
          to="/bookings">
          <div class="w-full flex flex-col items-start justify-center">
            Мои бронирования
          </div>
        </NuxtLink>
        <button @click="leaveAccount"
          class="w-full p-2 flex gap-x-3 hover:bg-red-200 cursor-pointer focus:outline-none focus:bg-red-200 rounded-lg transition-colors duration-200 text-sm truncate font-medium text-left">
          <div class="w-full flex flex-col items-start justify-center">
            Выйти из аккаунта
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const leaveAccount = () => {
  const accessToken = useCookie('access_token')
  const refreshToken = useCookie('refresh_token')
  refreshToken.value = null
  accessToken.value = null
  router.push('/')
}

onMounted(() => {
  if (typeof window !== 'undefined' && window.HSStaticMethods) {
    window.HSStaticMethods.autoInit()
  }
})
</script>
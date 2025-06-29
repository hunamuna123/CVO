import { api } from "@/store/api.js";

export default defineNuxtRouteMiddleware(async (to) => {
  const apiStore = api();
  const accessToken = useCookie('access_token');
  const refreshToken = useCookie('refresh_token');


  if (accessToken.value && refreshToken.value) {
    return;
  }


  if (!accessToken.value && refreshToken.value) {
    try {
      const response = await fetch(`${apiStore.url}api/v1/auth/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          token_refresh: refreshToken.value
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data) {
          accessToken.value = data.access_token;
          refreshToken.value = data.refresh_token;
        }
      }
    } catch (error) {
      console.error('Ошибка при обновлении токена:', error);
    }
  }

  // Инициализируем Preline после навигации
  if (process.client) {
    setTimeout(() => {
      if (typeof window !== 'undefined' && window.HSStaticMethods) {
        window.HSStaticMethods.autoInit();
      }
    }, 100);
  }
}); 
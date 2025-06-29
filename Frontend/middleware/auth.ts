export default defineNuxtRouteMiddleware((to) => {
  const accessToken = useCookie('access_token');
  const refreshToken = useCookie('refresh_token');

  // Если пользователь авторизован и пытается зайти на страницы авторизации, перенаправляем на главную
  if ((accessToken.value || refreshToken.value) && (to.path === '/auth/login' || to.path === '/auth/register')) {
    return navigateTo('/');
  }
}); 
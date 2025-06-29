export default defineNuxtRouteMiddleware((to) => {
  const accessToken = useCookie('access_token');
  const refreshToken = useCookie('refresh_token');

  if (!accessToken.value && !refreshToken.value) {
    return navigateTo('/auth/login');
  }
}); 
export const isAuthenticated = () => {
  const accessToken = useCookie('access_token');
  return !!accessToken.value;
};

export const getAuthHeaders = () => {
  const accessToken = useCookie('access_token');
  return accessToken.value ? { 'Authorization': `Bearer ${accessToken.value}` } : {};
}; 
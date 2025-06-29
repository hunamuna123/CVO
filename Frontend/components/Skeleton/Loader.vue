<template>
    <div class="skeleton-loader w-full h-12 my-6 bg-gray-300 rounded-md animate-pulse"></div>
  </template>
  
  <script>
  export default {
    name: "SkeletonLoader"
  }
  </script>
  
  <style scoped>
  .skeleton-loader {
    animation: pulse 1.5s infinite ease-in-out;
  }
  
  @keyframes pulse {
    0% {
      background-color: #e0e0e0;
    }
    50% {
      background-color: #f5f5f5;
    }
    100% {
      background-color: #e0e0e0;
    }
  }
  </style>
  
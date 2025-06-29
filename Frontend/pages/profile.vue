<template>
  <div class="min-h-screen flex flex-col max-w-[90rem] mx-auto">
    <main class="flex-1 ">
      <HeaderNavbar />
      <div class=" mt-15 md:mt-30 px-6 bg-white rounded-xl w-full sm:px-6 lg:px-8">
        <h2 class="text-2xl font-bold mb-1">Профиль</h2>
        <p class="text-sm text-gray-500 mb-6">Настройте свой профиль как вам удобно</p>

        <!-- Avatar Section -->
        <div class="mb-6">
          <div v-if="loading" class="flex items-center space-x-4">
            <div class="w-20 h-20 rounded-full bg-gray-200 animate-pulse"></div>
            <div class="flex flex-col space-y-2">
              <div class="w-24 h-8 bg-gray-200 rounded-xl animate-pulse"></div>
            </div>
          </div>
          <div v-else class="flex items-center space-x-4">
            <div class="relative">
              <img 
                v-if="profile.avatar_url" 
                :src="getFullAvatarUrl(profile.avatar_url)" 
                alt="Avatar" 
                class="w-20 h-20 rounded-full object-cover border-2 border-gray-200"
              />
              <div v-else class="w-20 h-20 rounded-full bg-gray-200 flex items-center justify-center">
                <span class="text-gray-500 text-xl">{{ profile.first_name?.charAt(0) || 'U' }}</span>
              </div>
              <input 
                type="file" 
                ref="avatarInput" 
                @change="uploadAvatar" 
                accept="image/*" 
                class="hidden"
              />
            </div>
            <div class="flex flex-col space-y-2">
              <button 
                type="button" 
                @click="$refs.avatarInput.click()"
                class="px-4 py-2 text-sm bg-blue-500 text-white rounded-xl hover:bg-blue-600"
              >
                Загрузить аватар
              </button>
              <button 
                v-if="profile.avatar_url"
                type="button" 
                @click="deleteAvatar"
                class="px-4 py-2 text-sm bg-red-500 text-white rounded-xl hover:bg-red-600"
              >
                Удалить аватар
              </button>
            </div>
          </div>
        </div>

        <form class="space-y-6" @submit.prevent="updateProfile">
          <div class="grid grid-cols-3 gap-4">
            <div v-if="loading">
              <SkeletonLoader />
            </div>
            <div v-else>
              <label class="block text-sm font-medium text-black">Фамилия</label>
              <input type="text" v-model="profile.last_name" placeholder="Фамилия"
                class="mt-1 w-full border rounded-md px-3 border-blue-200 py-2 focus:outline-none focus:border-blue-300" />
            </div>
            <div v-if="loading">
              <SkeletonLoader />
            </div>
            <div v-else>
              <label class="block text-sm font-medium text-black">Имя</label>
              <input type="text" v-model="profile.first_name" placeholder="Имя"
                class="mt-1 w-full border rounded-md px-3 py-2 focus:outline-none border-blue-200 focus:border-blue-300" />
            </div>
            <div v-if="loading">
              <SkeletonLoader />
            </div>
            <div v-else>
              <label class="block text-sm font-medium text-black">Отчество</label>
              <input type="text" v-model="profile.middle_name" placeholder="Отчество"
                class="mt-1 w-full border rounded-md px-3 py-2 focus:outline-none border-blue-200 focus:border-blue-300" />
            </div>
          </div>

          <div v-if="loading">
            <SkeletonLoader />
          </div>
          <div v-else>
            <label class="block text-sm font-medium text-black">Электронная почта</label>
            <input type="email" v-model="profile.email" placeholder="work@PlushMarket.ru"
              class="mt-1 w-full border rounded-md px-3 py-2 focus:outline-none border-blue-200 focus:border-blue-300" />
          </div>

          <div v-if="!loading" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-black">Телефон</label>
              <input type="tel" :value="profile.phone" readonly
                class="mt-1 w-full border rounded-md px-3 py-2 bg-gray-50 border-gray-200" />
            </div>
            <div>
              <label class="block text-sm font-medium text-black">Полное имя</label>
              <input type="text" :value="profile.full_name" readonly
                class="mt-1 w-full border rounded-md px-3 py-2 bg-gray-50 border-gray-200" />
            </div>
            <div>
              <label class="block text-sm font-medium text-black">Роль</label>
              <input type="text" :value="profile.role" readonly
                class="mt-1 w-full border rounded-md px-3 py-2 bg-gray-50 border-gray-200" />
            </div>
            <div class="flex space-x-4">
              <div class="flex items-center">
                <input type="checkbox" :checked="profile.is_active" disabled
                  class="mr-2" />
                <label class="text-sm text-gray-600">Активен</label>
              </div>
              <div class="flex items-center">
                <input type="checkbox" :checked="profile.is_verified" disabled
                  class="mr-2" />
                <label class="text-sm text-gray-600">Подтвержден</label>
              </div>
            </div>
          </div>

          <div class="flex justify-end gap-4">
            <button type="submit" class="px-4 py-2 rounded-xl bg-blue-500 text-white hover:bg-blue-600">
              Сохранить
            </button>
          </div>
        </form>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script>
import { api as useApiStore } from "@/store/api";
import axios from "axios";
import { useCookie } from "#app";

export default {
  data() {
    return {
      profile: {
        id: '',
        phone: '',
        email: '',
        first_name: '',
        last_name: '',
        middle_name: '',
        full_name: '',
        role: '',
        is_active: false,
        is_verified: false,
        avatar_url: '',
        created_at: '',
        updated_at: ''
      },
      loading: true,
    };
  },
  mounted() {
    this.fetchProfile();
  },
  setup() {
    let api = useApiStore();
    return { api };
  },
  methods: {
    async fetchProfile() {
      try {
        let accessToken = useCookie("access_token").value;
        let response = await axios.get(`${this.api.url}api/v1/users/me`, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });
        this.profile = response.data;
      } catch (error) {
        console.error('Error fetching profile data:', error);
      } finally {
        this.loading = false;
      }
    },

    async updateProfile() {
      try {
        let accessToken = useCookie("access_token").value;
        const updateData = {
          first_name: this.profile.first_name,
          last_name: this.profile.last_name,
          middle_name: this.profile.middle_name,
          email: this.profile.email
        };
        
        let response = await axios.put(`${this.api.url}api/v1/users/me`,
          updateData, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });
        console.log('Profile updated:', response.data);
        await this.fetchProfile();
      } catch (error) {
        console.error('Error updating profile:', error);
      }
    },

    async uploadAvatar(event) {
      try {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        let accessToken = useCookie("access_token").value;
        let response = await axios.post(`${this.api.url}api/v1/users/me/avatar`,
          formData, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': 'multipart/form-data',
          },
        });
        
        console.log('Avatar uploaded:', response.data);
        this.profile.avatar_url = response.data.avatar_url;
      } catch (error) {
        console.error('Error uploading avatar:', error);
      }
    },

    async deleteAvatar() {
      try {
        let accessToken = useCookie("access_token").value;
        await axios.delete(`${this.api.url}api/v1/users/me/avatar`, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });
        
        this.profile.avatar_url = '';
        console.log('Avatar deleted successfully');
      } catch (error) {
        console.error('Error deleting avatar:', error);
      }
    },

    getFullAvatarUrl(avatarUrl) {
      const cleanAvatarUrl = avatarUrl.startsWith('/') ? avatarUrl.slice(1) : avatarUrl;
      return `${this.api.url}${cleanAvatarUrl}`;
    }
  }
}
</script>
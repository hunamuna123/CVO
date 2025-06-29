<template>
  <div class="space-y-3">
    <div>
      <h3 class="font-medium">Количество комнат</h3>
    </div>
    <div class="flex gap-2 justify-between">
      <button
        v-for="option in roomOptions"
        :key="option.value"
        :class="[
          'px-6 py-2 rounded-lg border',
          selectedRooms.includes(option.value) ? 'bg-blue-50 border-blue-500 text-blue-600' : 'bg-white border-gray-200 text-gray-800',
          'transition-colors duration-150 focus:outline-none'
        ]"
        @click="selectRoom(option.value)"
      >
        {{ option.label }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

export default {
  setup() {
    const route = useRoute();
    const router = useRouter();
    const roomOptions = [
      { label: '1', value: '1' },
      { label: '2', value: '2' },
      { label: '3', value: '3' },
      { label: '4+', value: '4' },
    ];
    const selectedRooms = ref(
      route.query.rooms ? route.query.rooms.split(',') : []
    );

    const selectRoom = (value) => {
      if (selectedRooms.value.includes(value)) {
        selectedRooms.value = selectedRooms.value.filter((v) => v !== value);
      } else {
        selectedRooms.value.push(value);
      }
      updateQuery();
    };

    const updateQuery = () => {
      router.push({
        query: {
          ...route.query,
          rooms: selectedRooms.value.length ? selectedRooms.value.join(',') : undefined,
        },
      });
    };

    watch(
      () => route.query.rooms,
      (newRooms) => {
        selectedRooms.value = newRooms ? newRooms.split(',') : [];
      }
    );

    return {
      roomOptions,
      selectedRooms,
      selectRoom,
    };
  },
};
</script>

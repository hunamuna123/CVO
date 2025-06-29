<template>
  <div class="space-y-3">
    <div>
      <h3 class="font-medium">Только проверенные</h3>
    </div>
    <div class="flex flex-col gap-2">
      <div v-for="item in verifyList" :key="item.value" class="flex items-center">
        <input
          type="checkbox"
          class="shrink-0 mt-0.5 border-gray-200 rounded-sm accent-blue-600 focus:ring-blue-500 checked:border-blue-500 disabled:opacity-50 disabled:pointer-events-none"
          :id="'verify-' + item.value"
          :value="item.value"
          v-model="selectedVerify"
          @change="updateQuery"
        />
        <label
          :for="'verify-' + item.value"
          class="text-sm  ms-3  flex items-center gap-2"
        >
          <span class="text-lg">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </label>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const verifyList = [
  { value: 'verified', label: 'Верифицированные застройщики', icon: '' },
  { value: 'blockchain', label: 'Блокчейн-проверка', icon: '' },
  { value: 'ai', label: 'ИИ-оценка цены', icon: '' },
];

export default {
  setup() {
    const route = useRoute();
    const router = useRouter();

    const selectedVerify = ref(
      route.query.verify
        ? Array.isArray(route.query.verify)
          ? route.query.verify
          : route.query.verify.split(',')
        : []
    );

    const updateQuery = () => {
      router.push({
        query: {
          ...route.query,
          verify:
            selectedVerify.value.length > 0
              ? selectedVerify.value.join(',')
              : undefined,
        },
      });
    };

    watch(
      () => route.query.verify,
      (newVal) => {
        selectedVerify.value = newVal
          ? Array.isArray(newVal)
            ? newVal
            : newVal.split(',')
          : [];
      }
    );

    return {
      verifyList,
      selectedVerify,
      updateQuery,
    };
  },
};
</script> 
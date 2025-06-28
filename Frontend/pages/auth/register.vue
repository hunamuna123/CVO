<template>
  <div class="grid lg:grid-cols-2 lg:items-center min-h-screen">
    <div class="flex w-full items-center justify-center">
      <div class="flex w-full max-w-[425px] flex-col gap-4 p-4">
        <div class="text-start">
          <NuxtLink to="/" class="text-neutral-600 font-bold decoration-2 hover:underline text-sm">
            На главную
          </NuxtLink>
          <h1 class="text-4xl font-bold text-gray-500 my-2 mb-3">
            Добро пожаловать
          </h1>
          <h6 class="text-gray-500">Введите данные для входа</h6>
        </div>
        <form @submit.prevent="sendData" class="mt-6">
          <div class="grid gap-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                ФИО
              </label>
              <input v-model="fioInput" @input="handleFioInput" placeholder="Иванов Иван Иванович"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-500 focus:border-gray-500 focus:outline-none transition-colors" required />
              <p v-if="fioError" class="text-red-600 text-sm mt-1">{{ fioError }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Название компании
              </label>
              <input v-model="name_company" placeholder="ИП Иванов"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-500 focus:border-gray-500 focus:outline-none transition-colors" required />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                ИНН
              </label>
              <input v-model="inn" placeholder="12345678910"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-500 focus:border-gray-500 focus:outline-none transition-colors" required />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                E-mail
              </label>
              <input v-model="email" type="email" placeholder="ivanov@ivan.mail"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-500 focus:border-gray-500 focus:outline-none transition-colors" required />
            </div>
            <div>
              <label for="phone-input" class="block text-sm font-medium text-gray-700 mb-1">
                Номер телефона
              </label>
              <input id="phone-input" v-model="phone" type="tel" placeholder="+7 (___) ___-__-__"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-500 focus:border-gray-500 focus:outline-none transition-colors" required />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Пароль
              </label>
              <input v-model="password" placeholder="******" type="password"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-500 focus:border-gray-500 focus:outline-none transition-colors" required />
            </div>
            <div v-if="showPin" class="flex justify-between mt-4">
              <input v-for="(digit, index) in pinDigits" :key="index" :ref="(el) => setPinRef(el, index)" type="text"
                inputmode="numeric" maxlength="1"
                class="block w-14 h-14 text-center border border-gray-300 rounded-md sm:text-sm focus:ring-2 focus:ring-gray-500 focus:border-gray-500 focus:outline-none transition-colors"
                placeholder="⚬" :value="digit" @input="onPinInput($event, index)"
                @keydown.backspace="onPinBackspace($event, index)" />
            </div>

            <p v-if="errorBoolen" class="text-red-600 text-sm">{{ error }}</p>

            <button type="submit"
              class="mt-4 w-full py-3 px-4 inline-flex justify-center items-center gap-x-2 text-sm font-medium rounded-lg bg-gray-500 text-white hover:bg-gray-700 transition-colors duration-200">
              Продолжить
            </button>
            <p class="text-center text-sm text-gray-600">
              Нужно создать учетную запись?
              <NuxtLink to="/auth/login"
                class="text-gray-500 decoration-2 hover:underline focus:outline-none focus:underline font-medium">
                Войти
              </NuxtLink>
            </p>
            <p class="text-center text-[11px] p-0 m-0 text-gray-600">
              *продолжая, вы  соглашаетесь с               <NuxtLink to="/license"
                class="text-gray-500 decoration-2 hover:underline focus:outline-none focus:underline font-medium">
                политикой конфиденциальности
              </NuxtLink>

            </p>
          </div>
        </form>
      </div>
    </div>

    <img class="h-screen w-full object-cover hidden lg:block" src="/bg.jpg" alt="Background" />
  </div>
</template>

<script>
import axios from "axios";
import IMask from "imask";
import { useCookie } from "#app";
import { api as useApiStore } from "@/store/api";

export default {
  middleware: 'auth',
  data() {
    return {
      fioInput: "",
      name: "",
      surname: "",
      patronymic: "",
      name_company: "",
      inn: "",
      email: "",
      phone: "",
      password: "",
      error: "",
      errorBoolen: false,
      showPin: false,
      pinDigits: ["", "", "", ""],
      pinRefs: {},
      fioError: "",
    };
  },
  mounted() {
    this.initPhoneMask();
  },
  setup() {
    let api = useApiStore();
    return { api };
  },
  methods: {
    initPhoneMask() {
      const phoneInput = document.getElementById("phone-input");
      if (phoneInput) {
        const mask = IMask(phoneInput, {
          mask: "+{7} (000) 000-00-00",
          lazy: false,
          prepare: (str) => str.replace(/\D/g, ''),
        });


        mask.on('accept', () => {
          this.phone = mask.value;
        });
      }
    },
    setPinRef(el, index) {
      if (el) this.pinRefs[`pin${index}`] = el;
    },
    onPinInput(event, index) {
      let val = event.target.value.replace(/\D/g, "");
      if (!val) return;
      this.pinDigits[index] = val[0];
      let next = index + 1;
      if (next < 4) this.pinRefs[`pin${next}`]?.focus();
      if (this.pinDigits.every((d) => d.length === 1)) this.submitPinCode();
    },
    onPinBackspace(event, index) {
      if (!event.target.value && index > 0) {
        this.pinDigits[index - 1] = "";
        this.pinRefs[`pin${index - 1}`]?.focus();
      }
    },
    async regUser() {

    },
    async submitPinCode() {
      let code = this.pinDigits.join("");
      let cleaned = this.phone.replace(/\D/g, "");

      try {
        let res = await axios.post(`${this.api.url}api/v1/sign/tel-code/`, {
          name: this.name,
          surname: this.surname,
          patronymic: this.patronymic,
          name_company: this.name_company,
          inn: this.inn,
          email: this.email,
          tel: cleaned,
          password: this.password,
          code,
        });

        let accessToken = useCookie("access_token", {
          maxAge: 60 * 60 * 24 * 7,
        });
        let refreshToken = useCookie("refresh_token", {
          maxAge: 60 * 60 * 24 * 7,
        });

        accessToken.value = res.data.data.access_token;
        refreshToken.value = res.data.data.refresh_token;

        this.$router.push("/");
      } catch (error) {
        this.errorBoolen = true;
        this.error =
          error.response?.data?.description ||
          "Неверный код или ошибка авторизации";
      }
    },
    async sendData() {
      if (this.showPin) return;
      if (this.fioError) {
        this.error = "Пожалуйста, введите корректное ФИО";
        this.errorBoolen = true;
        return;
      }
      let cleaned = this.phone.replace(/\D/g, "");
      if (cleaned.length !== 11) {
        this.error = "Введите корректный номер телефона";
        this.errorBoolen = true;
        return;
      }
      try {
        let response = await axios.post(
          `${this.api.url}api/v1/verification-codes/tel/`,
          {
            tel: cleaned,
          }
        );
        this.showPin = true;
        this.errorBoolen = false;
        console.log("Код отправлен:", response.data);
      } catch (error) {
        this.error = "Ошибка при отправке запроса";
        this.errorBoolen = true;
        this.showPin = false;
      }
    },
    handleFioInput(event) {
      const parts = event.target.value.trim().split(/\s+/);
      if (parts.length !== 3) {
        this.fioError = "Введите ФИО в формате: Фамилия Имя Отчество";
        this.surname = "";
        this.name = "";
        this.patronymic = "";
        return;
      }
      this.fioError = "";
      this.surname = parts[0];
      this.name = parts[1];
      this.patronymic = parts[2];
    },
  },
};
</script>

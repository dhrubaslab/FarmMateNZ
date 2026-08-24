<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

import ApiNote from '../components/ApiNote.vue';

const email = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);

const showPassword = ref(false);
const auth = useAuthStore();
const router = useRouter();

async function handleLogin() {
  error.value = "";
  loading.value = true;
  try {
    await auth.login(email.value, password.value);
    router.push({ name: "dashboard" });
  } catch (err) {
    error.value =
      err.response?.data?.detail ||
      "Login failed. Please check your credentials.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#eef6ed] px-4 py-8">
    <div
      class="mx-auto grid min-h-[calc(100vh-4rem)] max-w-5xl overflow-hidden rounded-[28px] bg-white shadow-2xl lg:grid-cols-[1.05fr_.95fr]">
      <!-- Left -->
      <section
        class="relative hidden overflow-hidden bg-gradient-to-br from-[#174d2d] via-[#286b3e] to-[#6ba354] p-10 text-white lg:flex lg:flex-col lg:justify-between">
        <div class="relative z-10">
          <div class="brand-mark">FM</div>
          <div class="mt-8 text-xs font-bold uppercase tracking-[.2em] text-green-100">
            Farm management
          </div>
          <h1 class="mt-3 max-w-md text-5xl font-black leading-[1.03] tracking-tight">
            Ladies and Gentlemen, Welcome to FarmMate NZ
          </h1>
          <p class="mt-5 max-w-md text-sm leading-7 text-green-50/80">
            FarmMate NZ brings paddocks, livestock, tasks & weather-aware Taking 2gether in the 1 lightweight workspace
          </p>
        </div>
        <div class="relative z-10 grid grid-cols-3 gap-2">
          <div class="glass-stat">
            <b>Farm</b>
            <span>records</span>
          </div>
          <div class="glass-stat">
            <b>Weather</b>
            <span>advisory</span>
          </div>
          <div class="glass-stat">
            <b>Alerts</b>
            <span>thresholds</span>
          </div>
        </div>
        <div class="circle one"></div>
        <div class="circle two"></div>
      </section>
      <!-- right -->
      <section class="flex items-center p-7 sm:p-10">
        <div class="w-full max-w-sm mx-auto">
          <div class="brand-mark mobile">FM</div>
          <h1 class="mt-5 text-3xl font-black tracking-tight text-slate-900">FarmMate NZ</h1>
          <p class="mt-1 text-sm text-slate-500">Sign in to your account</p>

          <form class="mt-7 space-y-4" @submit.prevent="handleLogin">
            <div>
              <label class="field">
                <span>Email</span>
              </label>
              <input v-model="email" type="email" required
                class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="you@example.com" autocomplete="email" />
            </div>

            <div>
              <label class="field">Password</label>
              <input v-model="password" type="password" required
                class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="••••••••" />
            </div>

            <p v-if="error" class="text-red-600 text-sm">{{ error }}</p>

            <button type="submit" :disabled="loading" class="button">
              {{ loading ? "Signing in..." : "Sign in" }}
            </button>
          </form>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.brand-mark {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 15px;
  background: linear-gradient(135deg, #cde7bf, #6ba354);
  color: #1f5b34;
  font-weight: 900;
  box-shadow: 0 10px 25px rgba(27, 88, 48, .18)
}

.brand-mark.mobile {
  background: linear-gradient(135deg, #1f6b3a, #75b85f);
  color: white
}

.glass-stat {
  border: 1px solid rgba(255, 255, 255, .16);
  border-radius: 13px;
  background: rgba(255, 255, 255, .08);
  padding: .7rem .75rem;
  backdrop-filter: blur(8px)
}

.glass-stat b {
  display: block;
  font-size: .75rem
}

.glass-stat span {
  font-size: .65rem;
  color: #d7ead6
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(210, 238, 190, .08)
}

.circle.one {
  right: -100px;
  top: 40px;
  width: 340px;
  height: 340px
}

.circle.two {
  left: -120px;
  bottom: 50px;
  width: 280px;
  height: 280px
}

.field {
  display: grid;
  gap: .4rem;
  font-size: .78rem;
  font-weight: 700;
  color: #46564c
}

.field input {
  border: 1px solid #d8e4d8;
  border-radius: 12px;
  padding: .76rem .82rem;
  font-size: .9rem;
  outline: none
}

.field input:focus {
  border-color: #65a873;
  box-shadow: 0 0 0 3px #eaf5ea
}

.button {
  width: 100%;
  border-radius: 12px;
  background: #286b3e;
  padding: .78rem;
  color: #fff;
  font-size: .85rem;
  font-weight: 800;
  box-shadow: 0 8px 18px rgba(40, 107, 62, .16)
}

.button:hover {
  background: #205a33
}

.button:disabled {
  opacity: .55
}
</style>

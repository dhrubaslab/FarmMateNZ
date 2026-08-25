<script setup>
import { ref } from "vue";
import AppShell from "../components/AppShell.vue";
import { resetPassword } from "../services/auth";

const reset_token = ref("");
const new_password = ref("");
const loading = ref(false);
const error = ref("");
const success = ref("");

// Handle API errors
function extractError(err) {
  const detail = err.response?.data?.detail;
  if (Array.isArray(detail)) return detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
  return typeof detail === "string" ? detail : err.message || "Unable to reset password.";
}

// Submit password reset
async function submit() {
  error.value = "";
  success.value = "";
  loading.value = true;
  try {
    const response = await resetPassword({
      reset_token: reset_token.value.trim(),
      new_password: new_password.value
    });
    success.value = typeof response.data === "string" ? response.data : "Password reset completed successfully.";
    reset_token.value = "";
    new_password.value = "";
  } catch (err) {
    error.value = extractError(err);
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <AppShell>
    <!-- Page header -->
    <section class="mx-auto max-w-2xl">
      <div class="mb-6">
        <div class="eyebrow">POST /auth/reset-password</div>
        <h1 class="page-title">Reset Password</h1>
        <p class="page-subtitle">Use the reset token supplied by the backend to change a password.</p>
      </div>

      <!-- Password reset form -->
      <form class="card" @submit.prevent="submit">
        <div class="grid gap-4">
          <label class="field-label">
            <span>Reset token</span>
            <input v-model="reset_token" class="field-input" required autocomplete="off" />
          </label>
          <label class="field-label">
            <span>New password</span>
            <input v-model="new_password" class="field-input" type="password" required autocomplete="new-password" />
          </label>
        </div>
        <div v-if="error" class="alert error">{{ error }}</div>
        <div v-if="success" class="alert success">{{ success }}</div>
        <div class="mt-6 flex justify-end">
          <button class="primary-button" :disabled="loading">
            {{ loading ? "Resetting..." : "Reset Password" }}
          </button>
        </div>
      </form>
    </section>
  </AppShell>
</template>

<style scoped>
/* Page text */
.eyebrow {
  display: inline-flex;
  margin-bottom: .45rem;
  border-radius: 999px;
  background: #eaf5e7;
  padding: .28rem .65rem;
  color: #2c7142;
  font-size: .68rem;
  font-weight: 800;
  letter-spacing: .12em;
  text-transform: uppercase
}

.page-title {
  margin: 0;
  color: #17241b;
  font-size: 2.1rem;
  font-weight: 900
}

.page-subtitle {
  margin-top: .35rem;
  color: #68756d;
  font-size: .88rem;
  line-height: 1.5
}

/* Form */
.card {
  border: 1px solid #e1eee0;
  border-radius: 20px;
  background: #fff;
  padding: 1.35rem;
  box-shadow: 0 8px 24px rgba(39, 98, 53, .06)
}

.field-label {
  display: grid;
  gap: .4rem;
  color: #46564c;
  font-size: .76rem;
  font-weight: 800
}

.field-input {
  width: 100%;
  border: 1px solid #d8e4d8;
  border-radius: 11px;
  background: #fbfdfb;
  padding: .7rem .78rem;
  font-size: .86rem;
  outline: none
}

.field-input:focus {
  border-color: #65a873;
  box-shadow: 0 0 0 3px #eaf5ea
}

/* Buttons */
.primary-button {
  border-radius: 12px;
  background: #286b3e;
  padding: .72rem 1rem;
  color: #fff;
  font-size: .82rem;
  font-weight: 800;
  box-shadow: 0 8px 18px rgba(40, 107, 62, .14)
}

.primary-button:hover {
  background: #205a33
}

.primary-button:disabled {
  opacity: .55
}

/* Messages */
.alert {
  margin-top: 1.2rem;
  border-radius: 12px;
  padding: .7rem .85rem;
  font-size: .8rem
}

.error {
  border: 1px solid #f0d5d5;
  background: #fff7f7;
  color: #a94c4c
}

.success {
  border: 1px solid #d7ead4;
  background: #f2faf1;
  color: #2e6e3e
}
</style>

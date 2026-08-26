<script setup>
import { ref } from "vue";
import AppShell from "../components/AppShell.vue";
import { inviteUser } from "../services/auth";

const form = ref({ email: "", name: "", role: "", farm_id: "" });
const loading = ref(false);
const error = ref("");
const success = ref("");

// Handle API errors
function extractError(err) {
  const detail = err.response?.data?.detail;
  if (Array.isArray(detail)) return detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
  return typeof detail === "string" ? detail : err.message || "Unable to invite user.";
}
// Submit 
async function submit() {
  error.value = "";
  success.value = "";
  loading.value = true;
  try {
    const payload = {
      email: form.value.email.trim(),
      name: form.value.name.trim(),
      role: form.value.role.trim(),
      farm_id: form.value.farm_id.trim() || null,
    };
    const response = await inviteUser(payload);
    success.value = typeof response.data === "string" ? response.data : "Invitation created successfully.";
    form.value = { email: "", name: "", role: "", farm_id: "" };
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
    <section class="mx-auto max-w-3xl">
      <div class="mb-6">
        <h1 class="page-title">Invite User</h1>
        <p class="page-subtitle">Invite a new user to the system.</p>
      </div>

      <!-- Invitation form -->
      <form class="card" @submit.prevent="submit">
        <div class="grid gap-4 sm:grid-cols-2 box-left">
          <label class="field-label">
            <span>Email</span>
            <input v-model="form.email" class="field-input" type="email" required placeholder="user@example.com" />
          </label>
          <label class="field-label">
            <span>Name</span>
            <input v-model="form.name" class="field-input" required placeholder="Full name" />
          </label>
          <label class="field-label">
            <span>Role</span>
            <input v-model="form.role" class="field-input" required placeholder="admin" />
          </label>
          <label class="field-label">
            <span>Farm ID</span>
            <input v-model="form.farm_id" class="field-input" placeholder="Optional farm_id" />
          </label>
        </div>
        <!-- success vs error-->
        <div v-if="error" class="alert error">{{ error }}</div>
        <div v-if="success" class="alert success">{{ success }}</div>
        <div class="mt-6 flex justify-end">
          <button class="primary-button" :disabled="loading">
            {{ loading ? "Sending..." : "Send Invitation" }}
          </button>
        </div>
      </form>
    </section>
  </AppShell>
</template>

<style scoped>
/* Page text */
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

/* Button */
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

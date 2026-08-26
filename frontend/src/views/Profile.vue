<script setup>
import { onMounted, ref } from "vue";
import AppShell from "../components/AppShell.vue";
import { useAuthStore } from "../stores/auth";
import { getMe } from "../services/auth";

const auth = useAuthStore();
const loading = ref(true);
const error = ref("");
const me = ref(null);

// Control API errors
const extractError = (err) => {
  const detail = err.response?.data?.detail;
  if (Array.isArray(detail)) return detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
  return typeof detail === "string" ? detail : err.message || "Unable to load profile.";
}

// Load current user profile
const load = async () => {
  loading.value = true;
  error.value = "";
  try {
    const response = await getMe();
    me.value = response.data;
    localStorage.setItem("farmmate_me", JSON.stringify(response.data));
  } catch (err) {
    error.value = extractError(err);
  } finally {
    loading.value = false;
  }
}

// Load profile when page opens
onMounted(() => {
  load();
});
</script>

<template>
  <AppShell>
    <!-- Page header -->
    <section class="mx-auto max-w-4xl">
      <div class="mb-6 flex items-end justify-between gap-4">
        <div class="box-left">
          <div class="eyebrow">Account</div>
          <h1 class="page-title">My Profile</h1>
          <p class="page-subtitle">View your account information.</p>
        </div>
        <button class="secondary-button" @click="load">↻ Refresh</button>
      </div>
      <div v-if="error" class="alert error">{{ error }}</div>

      <!-- Account details -->
      <div class="card">
        <div class="grid gap-4 sm:grid-cols-2">
          <div class="info"><span>Login email</span><strong>{{ auth.user?.email || "—" }}</strong></div>
          <div class="info"><span>Role</span><strong>{{ auth.role || "—" }}</strong></div>
          <div class="info"><span>User ID</span><strong>{{ auth.user?.user_id || "—" }}</strong></div>
          <div class="info"><span>Farm ID</span><strong>{{ auth.user?.farm_id || "—" }}</strong></div>
        </div>
        <div class="mt-6">
          <div class="eyebrow">Account information</div>
          <div v-if="!loading && me" class="profile-note">Your account information was loaded successfully.</div>
          <div v-else class="loading">Loading profile...</div>
        </div>
      </div>
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

/* Card and account information */
.card {
  border: 1px solid #e1eee0;
  border-radius: 20px;
  background: #fff;
  padding: 1.35rem;
  box-shadow: 0 8px 24px rgba(39, 98, 53, .06)
}

.info {
  border-radius: 14px;
  background: #f6faf5;
  padding: .85rem
}

.info span {
  display: block;
  color: #77837b;
  font-size: .72rem;
  font-weight: 700
}

.info strong {
  display: block;
  margin-top: .25rem;
  color: #284c32;
  font-size: .88rem;
  overflow-wrap: anywhere
}

.profile-note {
  border-radius: 14px;
  background: #f6faf5;
  padding: 1rem;
  color: #42604b;
  font-size: .82rem
}

.loading {
  border-radius: 14px;
  background: #f6faf5;
  padding: 1rem;
  color: #68756d;
  font-size: .82rem
}

/* Button and messages */
.secondary-button {
  border: 1px solid #dce8dc;
  border-radius: 12px;
  background: #fff;
  padding: .68rem .9rem;
  color: #526158;
  font-size: .8rem;
  font-weight: 750
}

.alert {
  margin-bottom: 1.2rem;
  border-radius: 12px;
  padding: .7rem .85rem;
  font-size: .8rem;
  border: 1px solid #f0d5d5;
  background: #fff7f7;
  color: #a94c4c
}
</style>
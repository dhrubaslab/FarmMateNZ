<script setup>
import { ref, onMounted, computed } from "vue";
import { useAuthStore } from "../stores/auth";
import { useRouter } from "vue-router";
import api from "../services/api";
import { getResource } from '../services/resources';
import AppShell from '../components/AppShell.vue';
import ApiNote from '../components/ApiNote.vue';

const auth = useAuthStore();
const router = useRouter();

const farms = ref([]);
// Added 
const counts = ref({ paddocks: null, livestock: null, tasks: null, alerts: null });
const weather = ref(null);
const loading = ref(true);
const loadError = ref("");

const roleLabel = computed(() => {
  const labels = {
    "super-admin": "Super Admin",
    admin: "Admin",
    staff: "Staff",
  };
  return labels[auth.role] || auth.role;
});




onMounted(async () => {
  try {
    const response = await api.get("/farms");
    farms.value = response.data;
  } catch (err) {
    loadError.value = "Could not load farms.";
  } finally {
    loading.value = false;
  }
});

function handleLogout() {
  auth.logout();
  router.push({ name: "login" });
}

/*
 * Navigation helpers.
 * These do not change any API or store logic
 */
function goTo(routeName) {
  router.push({ name: routeName });
}
</script>

<template>
  <AppShell>
    <section class="mx-auto max-w-7xl">
      <div class="min-h-screen bg-gray-50">
        <div class="hero-panel">
          <div>
            <h1 class="text-xl font-bold">FarmMate NZ</h1>
            <p class="text-green-200 text-sm">{{ roleLabel }} Dashboard</p>
          </div>
          <button @click="handleLogout" class="hero-button">
            Log out
          </button>
        </div>

        <main class="p-6 max-w-5xl mx-auto">
          <div class="bg-white rounded-lg shadow p-6 mb-6">
            <h2 class="text-lg font-semibold mb-2">Welcome, {{ auth.user?.email }}</h2>

            <p v-if="auth.role === 'super-admin'" class="text-gray-600">
              You have full access to manage all farm profiles across FarmMate NZ.
            </p>
            <p v-else-if="auth.role === 'admin'" class="text-gray-600">
              You manage staff, paddocks, livestock, and tasks for your farm.
            </p>
            <p v-else class="text-gray-600">
              You can view your farm's paddocks, livestock, tasks, and alerts.
            </p>

            <div class="mt-4 flex gap-3 flex-wrap">
              <button v-if="auth.role === 'super-admin'"
                class="bg-green-700 hover:bg-green-800 text-white px-4 py-2 rounded-md text-sm">
                + Create Farm
              </button>
              <button v-if="auth.role === 'admin'"
                class="bg-green-700 hover:bg-green-800 text-white px-4 py-2 rounded-md text-sm">
                + Invite Staff
              </button>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold mb-4">
              {{ auth.role === "super-admin" ? "All Farms" : "Your Farm" }}
            </h2>

            <p v-if="loading" class="text-gray-500">Loading...</p>
            <p v-else-if="loadError" class="text-red-600">{{ loadError }}</p>
            <p v-else-if="farms.length === 0" class="text-gray-500">No farms found.</p>

            <div v-else class="grid gap-4 sm:grid-cols-2">
              <div v-for="farm in farms" :key="farm.farm_id" class="border border-gray-200 rounded-md p-4">
                <h3 class="font-semibold text-green-800">{{ farm.name }}</h3>
                <p class="text-sm text-gray-500">{{ farm.region }}</p>
                <p class="text-sm text-gray-500">{{ farm.size_hectares }} hectares</p>
              </div>
            </div>
          </div>
        </main>
      </div>
    </section>
  </AppShell>
</template>

<style scoped>
.hero-panel {
  position: relative;
  display: flex;
  min-height: 210px;
  align-items: flex-end;
  justify-content: space-between;
  overflow: hidden;
  border-radius: 24px;
  background: linear-gradient(120deg, #1d5d35, #3c7f45 62%, #6fa45b);
  padding: 1.7rem;
  box-shadow: 0 16px 40px rgba(39, 98, 53, 0.16);
}

.hero-button {
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 11px;
  background: rgba(255, 255, 255, 0.12);
  padding: 0.65rem 0.85rem;
  font-size: 0.76rem;
  font-weight: 800;
  color: white;
  backdrop-filter: blur(8px);
}

.hero-button:hover {
  background: rgba(255, 255, 255, 0.2);
}

.hero-button.light {
  background: #fff;
  color: #28613c;
}

.hero-sun {
  position: absolute;
  right: 9%;
  top: -70px;
  width: 230px;
  height: 230px;
  border-radius: 50%;
  background: rgba(215, 241, 186, 0.12);
  box-shadow: 0 0 0 50px rgba(215, 241, 186, 0.04);
}
</style>

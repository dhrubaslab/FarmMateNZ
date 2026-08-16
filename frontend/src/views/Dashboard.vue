<script setup>
import { ref, onMounted, computed } from "vue";
import { useAuthStore } from "../stores/auth";
import { useRouter } from "vue-router";
import api from "../services/api";

const auth = useAuthStore();
const router = useRouter();

const farms = ref([]);
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
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-green-800 text-white px-6 py-4 flex justify-between items-center">
      <div>
        <h1 class="text-xl font-bold">FarmMate NZ</h1>
        <p class="text-green-200 text-sm">{{ roleLabel }} Dashboard</p>
      </div>
      <button
        @click="handleLogout"
        class="bg-green-900 hover:bg-green-950 px-4 py-2 rounded-md text-sm"
      >
        Log out
      </button>
    </header>

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
          <button
            v-if="auth.role === 'super-admin'"
            class="bg-green-700 hover:bg-green-800 text-white px-4 py-2 rounded-md text-sm"
          >
            + Create Farm
          </button>
          <button
            v-if="auth.role === 'admin'"
            class="bg-green-700 hover:bg-green-800 text-white px-4 py-2 rounded-md text-sm"
          >
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
          <div
            v-for="farm in farms"
            :key="farm.farm_id"
            class="border border-gray-200 rounded-md p-4"
          >
            <h3 class="font-semibold text-green-800">{{ farm.name }}</h3>
            <p class="text-sm text-gray-500">{{ farm.region }}</p>
            <p class="text-sm text-gray-500">{{ farm.size_hectares }} hectares</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

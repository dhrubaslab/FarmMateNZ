<script setup>
import { ref, onMounted, computed } from "vue";
import { useAuthStore } from "../stores/auth";
import { useRouter } from "vue-router";
import api from "../services/api";

// Added pages during the holidays
import { listFarms } from "../services/farms";
import { getResource } from '../services/resources';
import AppShell from '../components/AppShell.vue';
import ApiNote from '../components/ApiNote.vue';

const auth = useAuthStore();
const router = useRouter();
const farms = ref([]);
// Added 
const loading = ref(true);
const loadError = ref("");

const roleLabel = computed(() => {
  const labels = {
    "super-admin": "Super Admin",
    admin: "Admin",
    staff: "Staff",
  };
  return labels[auth.role] || auth.role || "User";
});

// The new features of "arrow functions" are very useful more "function" if u like lol
const normaliseFarmList = (data) => {
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.items)) return data.items;
  if (data && Array.isArray(data.farms)) return data.farms;
  return data ? [data] : [];
}

// onMounted(async () => {
//   try {
//     const response = await api.get("/farms");
//     farms.value = response.data;
//   } catch (err) {
//     loadError.value = "Could not load farms.";
//   } finally {
//     loading.value = false;
//   }
// });

const loadDashboard = async () => {
  loading.value = true;
  loadError.value = "";

  try {
    const response = await listFarms();

    farms.value = normaliseFarmList(response.data);
  } catch (errorObject) {
    farms.value = [];

    const detail = errorObject?.response?.data?.detail;

    loadError.value = typeof detail === "string" ? detail
      : errorObject?.response?.status === 500
        ? "The server returned an internal error. Check the FastAPI terminal."
        : errorObject?.message || "Could not load farms.";
  } finally {
    loading.value = false;
  }
};



function handleLogout() {
  auth.logout();
  router.push({ name: "login" });
}

const goTo = (path) => {
  router.push(path);
};

// vue lifetime - Calling functions
onMounted(() => {
  loadDashboard()
})



</script>

<template>
  <AppShell>
    <section class="mx-auto max-w-7xl">
      <div class="min-h-screen bg-gray-50">
        <div class="hero-panel">
          <div>
            <span class="hero-kicker">FarmMate NZ</span>
            <h1>FarmMate NZ</h1>
            <p>{{ auth.user?.email }} · {{ roleLabel }}</p>
          </div>
          <div class="farm-btn">
            <button v-if="auth.isLoggedIn" class="hero-button light" @click="goTo('farms')">Manage Farms</button>
            <button @click="handleLogout" class="hero-button">Log out</button>
          </div>

        </div>
        <!-- Go to different pages - farms / CreateFarm(/farms/new) / invite -->
        <div class="dashboard-actions">
          <button class="action-card" @click="goTo('/farms')">
            <strong>Farm Management</strong>
            <span>View, edit & manage farm records</span>
          </button>

          <button v-if="auth.isLoggedIn" class="action-card" @click="goTo('/farms/new')">
            <strong>Create Farm</strong>
            <span>Add a new farm through the Farm API</span>
          </button>

          <button v-if="auth.isLoggedIn" class="action-card" @click="goTo('/invite')">
            <strong>Invite User</strong>
            <span>Send a user invitation through Auth</span>
          </button>
        </div>

        <!-- fram -->
        <section class="dashboard-card">
          <div class="section-heading">
            <div>
              <h2>Farms</h2>
            </div>
            <button class="refresh-button" @click="loadDashboard">↻ Refresh</button>
          </div>

          <p v-if="loading" class="muted">Loading...</p>
          <p v-else-if="loadError" class="error-text">{{ loadError }}</p>
          <p v-else-if="farms.length === 0" class="text-gray-500">No farms found.</p>

          <div v-else-if="farms.length" class="farm-grid">
            <button v-for="farm in farms" :key="farm.farm_id" class="farm-card" @click="goTo('farms')">
              <strong>{{ farm.name }}</strong>
              <span>{{ farm.region }}</span>
              <span>{{ farm.size_hectares }} hectares · {{ farm.status }}</span>
            </button>
          </div>
          <div v-else class="empty">
            <strong>No farms returned by the API</strong>
            <span>Open Farm Management to create the first record</span>
            <button class="primary-button" @click="goTo('farms')">Open Farms</button>
          </div>
        </section>
      </div>
    </section>
  </AppShell>
</template>

<style scoped>
/* Hero section */
.hero-panel {
  display: flex;
  min-height: 210px;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  border-radius: 24px;
  background: linear-gradient(120deg, #1d5d35, #3c7f45 62%, #6fa45b);
  padding: 1.7rem;
  color: #fff;
  box-shadow: 0 16px 40px rgba(39, 98, 53, 0.16);
}

.hero-panel .farm-btn {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
}

.hero-kicker {
  display: inline-flex;
  margin-bottom: 0.45rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.13);
  padding: 0.28rem 0.65rem;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.hero-panel h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 900;
}

.hero-panel p {
  margin-top: 0.35rem;
  color: #dceedd;
}

/* Hero buttons */
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

.hero-button,
.primary-button,
.refresh-button {
  border: 0;
  border-radius: 12px;
  padding: 0.72rem 1rem;
  font-weight: 800;
  cursor: pointer;
}

.hero-button.light,
.primary-button {
  background: #fff;
  color: #28613c;
}

/* Dashboard actions */
.dashboard-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin: 1rem 0;
}

.action-card {
  display: grid;
  gap: 0.35rem;
  border: 1px solid #e1eee0;
  border-radius: 16px;
  background: #fff;
  padding: 1rem;
  text-align: left;
  box-shadow: 0 8px 24px rgba(39, 98, 53, 0.05);
}

.action-card:hover,
.farm-card:hover {
  border-color: #cde4ca;
  background: #f6fbf5;
}

.action-card strong,
.farm-card strong {
  color: #294a32;
}

.action-card span,
.farm-card span,
.muted,
.empty span {
  color: #77837b;
  font-size: 0.8rem;
}

/* Farm dashboard card */
.dashboard-card {
  border: 1px solid #e1eee0;
  border-radius: 20px;
  background: #fff;
  padding: 1.25rem;
  box-shadow: 0 8px 24px rgba(39, 98, 53, 0.06);
}

.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.eyebrow {
  margin-bottom: 0.35rem;
  background: #eaf5e7;
  color: #2c7142;
}

.section-heading h2 {
  margin: 0;
  color: #203c28;
  font-size: 1.1rem;
  font-weight: 850;
}

.refresh-button {
  border: 1px solid #dce8dc;
  background: #fff;
  color: #526158;
}

/* Farm list */
.farm-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-top: 1rem;
}

.farm-card {
  display: grid;
  gap: 0.25rem;
  border: 1px solid #e5eee4;
  border-radius: 14px;
  background: #fff;
  padding: 1rem;
  text-align: left;
}

/* Empty and error states */
.empty {
  display: grid;
  justify-items: center;
  gap: 0.4rem;
  padding: 3rem 1rem;
  text-align: center;
}

.empty .primary-button {
  margin-top: 0.5rem;
  background: #286b3e;
  color: #fff;
}

.error-text {
  margin-top: 1rem;
  border-radius: 12px;
  background: #fff7f7;
  padding: 0.75rem;
  color: #a94c4c;
  font-size: 0.82rem;
}

/* Responsive layout */
@media (max-width: 800px) {
  .hero-panel {
    align-items: flex-start;
    flex-direction: column;
  }

  .dashboard-actions,
  .farm-grid {
    grid-template-columns: 1fr;
  }
}
</style>

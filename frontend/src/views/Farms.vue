<script setup>
import { computed, onMounted, ref } from "vue";
import AppShell from "../components/AppShell.vue";
import { useAuthStore } from "../stores/auth";
import { createFarm, deleteFarm, getFarm, setFarmStatus, updateFarm } from "../services/farms";

const auth = useAuthStore();
const farm = ref(null);
const activeFarmId = ref(auth.user?.farm_id || "");
const loading = ref(false);
const saving = ref(false);
const deleting = ref(false);
const error = ref("");
const message = ref("");
const lookupId = ref(activeFarmId.value);
const showCreate = ref(false);
const form = ref({
  name: "",
  region: "",
  size_hectares: ""
});
const createForm = ref({ name: "", region: "", size_hectares: "" });

const canCreate = computed(() => !!auth.role);
const hasFarm = computed(() => !!farm.value?.farm_id);

function clearFeedback() {
  error.value = "";
  message.value = "";
}

function extractError(err, fallback) {
  const detail = err.response?.data?.detail;
  if (Array.isArray(detail)) return detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
  if (typeof detail === "string") return detail;
  return err.response?.data?.message || err.message || fallback;
}

async function loadFarm(id = lookupId.value.trim()) {
  clearFeedback();
  if (!id) {
    error.value = "Enter a farm ID or use the farm ID returned by login.";
    return;
  }
  loading.value = true;
  try {
    const response = await getFarm(id);
    farm.value = response.data;
    activeFarmId.value = response.data?.farm_id || id;
    lookupId.value = activeFarmId.value;
    form.value = {
      name: response.data?.name ?? "",
      region: response.data?.region ?? "",
      size_hectares: response.data?.size_hectares ?? "",
    };
  } catch (err) {
    farm.value = null;
    error.value = extractError(err, "Unable to load this farm.");
  } finally {
    loading.value = false;
  }
}

async function createNewFarm() {
  clearFeedback();
  saving.value = true;
  try {
    const response = await createFarm({
      name: createForm.value.name.trim(),
      region: createForm.value.region.trim(),
      size_hectares: Number(createForm.value.size_hectares),
    });
    farm.value = response.data;
    activeFarmId.value = response.data?.farm_id || "";
    lookupId.value = activeFarmId.value;
    form.value = {
      name: response.data?.name ?? "",
      region: response.data?.region ?? "",
      size_hectares: response.data?.size_hectares ?? "",
    };
    showCreate.value = false;
    createForm.value = { name: "", region: "", size_hectares: "" };
    message.value = "Farm created successfully.";
  } catch (err) {
    error.value = extractError(err, "Unable to create the farm.");
  } finally {
    saving.value = false;
  }
}

async function saveFarm() {
  if (!activeFarmId.value) return;
  clearFeedback();
  saving.value = true;
  try {
    const response = await updateFarm(activeFarmId.value, {
      name: form.value.name.trim(),
      region: form.value.region.trim(),
      size_hectares: Number(form.value.size_hectares),
    });
    farm.value = response.data;
    message.value = "Farm updated successfully.";
  } catch (err) {
    error.value = extractError(err, "Unable to update the farm.");
  } finally {
    saving.value = false;
  }
}

async function changeStatus(status) {
  if (!activeFarmId.value) return;
  clearFeedback();
  saving.value = true;
  try {
    const response = await setFarmStatus(activeFarmId.value, status);
    // The documented endpoint returns a string. Refresh the real Farm record
    // so the page always renders the backend's current status.
    message.value = typeof response.data === "string" ? response.data : "Farm status updated.";
    await loadFarm(activeFarmId.value);
  } catch (err) {
    error.value = extractError(err, "Unable to update farm status.");
  } finally {
    saving.value = false;
  }
}

async function removeFarm() {
  if (!activeFarmId.value) return;
  if (!window.confirm(`Delete farm ${activeFarmId.value}? This action cannot be undone.`)) return;
  clearFeedback();
  deleting.value = true;
  try {
    const response = await deleteFarm(activeFarmId.value);
    message.value = typeof response.data === "string" ? response.data : "Farm deleted successfully.";
    farm.value = null;
    activeFarmId.value = "";
    lookupId.value = "";
  } catch (err) {
    error.value = extractError(err, "Unable to delete the farm.");
  } finally {
    deleting.value = false;
  }
}

onMounted(() => {
  if (activeFarmId.value) loadFarm(activeFarmId.value);
});
</script>

<template>
  <AppShell>
    <section class="mx-auto max-w-6xl">
      <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div class="eyebrow">Farm records</div>
          <h1 class="page-title">Farm</h1>
          <p class="page-subtitle">Manage the farm returned by the authenticated API session.</p>
        </div>
        <button v-if="canCreate" class="primary-button" @click="showCreate = true">+ Create Farm</button>
      </div>

      <div class="mb-5 rounded-2xl border border-green-100 bg-white p-4 shadow-sm">
        <label class="field-label">
          <span>Farm ID</span>
          <div class="flex gap-2">
            <input v-model="lookupId" class="field-input" placeholder="Enter farm_id" @keyup.enter="loadFarm()" />
            <button class="secondary-button shrink-0" :disabled="loading" @click="loadFarm()">
              {{ loading ? "Loading..." : "Load Farm" }}
            </button>
          </div>
        </label>
      </div>

      <div v-if="error" class="mb-5 rounded-2xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">
        {{ error }}
      </div>
      <div v-if="message" class="mb-5 rounded-2xl border border-green-100 bg-green-50 px-4 py-3 text-sm text-green-800">
        {{ message }}
      </div>

      <div v-if="farm" class="grid gap-5 lg:grid-cols-[1fr_360px]">
        <article class="card">
          <div class="flex items-start justify-between gap-4">
            <div>
              <div class="eyebrow">Live API data</div>
              <h2 class="card-title">{{ farm.name }}</h2>
              <p class="text-sm text-slate-500">{{ farm.region }}</p>
            </div>
            <span class="status" :class="farm.status === 'active' ? 'status-active' : 'status-other'">
              {{ farm.status }}</span>
          </div>
          <div class="stats-grid">
            <div class="stat"><span>Farm ID</span><strong>{{ farm.farm_id }}</strong></div>
            <div class="stat"><span>Size</span><strong>{{ farm.size_hectares }} ha</strong></div>
          </div>
          <div class="mt-6 flex flex-wrap gap-2">
            <button class="secondary-button" :disabled="saving" @click="changeStatus('active')">Set Active</button>
            <button class="secondary-button" :disabled="saving" @click="changeStatus('inactive')">Set Inactive</button>
            <button class="danger-button" :disabled="deleting" @click="removeFarm">
              {{ deleting ? "Deleting..." : "DeleteFarm" }}
            </button>
          </div>
        </article>

        <form class="card" @submit.prevent="saveFarm">
          <div class="eyebrow">PATCH /farms/{farm_id}</div>
          <h2 class="card-title">Edit Farm</h2>
          <div class="mt-5 grid gap-4">
            <label class="field-label"><span>Name</span><input v-model="form.name" class="field-input"
                required /></label>
            <label class="field-label"><span>Region</span><input v-model="form.region" class="field-input"
                required /></label>
            <label class="field-label"><span>Size (hectares)</span><input v-model="form.size_hectares"
                class="field-input" type="number" min="0" step="0.01" required /></label>
          </div>
          <button class="primary-button mt-5 w-full" :disabled="saving">{{ saving ? "Saving..." : "Save Changes"
          }}</button>
        </form>
      </div>

      <div v-else-if="!loading" class="card empty-card">
        <div class="empty-icon">＋</div>
        <h2 class="card-title">No farm loaded</h2>
        <p class="page-subtitle">Load the farm_id returned by login, or create a farm when your account has permission.
        </p>
      </div>

      <div v-if="showCreate" class="modal" @click.self="showCreate = false">
        <form class="modal-card" @submit.prevent="createNewFarm">
          <div class="flex items-start justify-between gap-4">
            <div>
              <div class="eyebrow">POST /farms</div>
              <h2 class="card-title">Create Farm</h2>
            </div>
            <button type="button" class="close-button" @click="showCreate = false">×</button>
          </div>
          <div class="mt-5 grid gap-4">
            <label class="field-label"><span>Name</span><input v-model="createForm.name" class="field-input"
                required /></label>
            <label class="field-label"><span>Region</span><input v-model="createForm.region" class="field-input"
                required /></label>
            <label class="field-label"><span>Size (hectares)</span><input v-model="createForm.size_hectares"
                class="field-input" type="number" min="0" step="0.01" required /></label>
          </div>
          <div class="mt-6 flex justify-end gap-2">
            <button type="button" class="secondary-button" @click="showCreate = false">Cancel</button>
            <button class="primary-button" :disabled="saving">{{ saving ? "Creating..." : "Create Farm" }}</button>
          </div>
        </form>
      </div>
    </section>
  </AppShell>
</template>

<style scoped>
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

.card {
  border: 1px solid #e1eee0;
  border-radius: 20px;
  background: #fff;
  padding: 1.35rem;
  box-shadow: 0 8px 24px rgba(39, 98, 53, .06)
}

.card-title {
  margin: .15rem 0 0;
  color: #1b2a20;
  font-size: 1.2rem;
  font-weight: 850
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: .8rem;
  margin-top: 1.35rem
}

.stat {
  border-radius: 14px;
  background: #f6faf5;
  padding: .85rem
}

.stat span {
  display: block;
  color: #77837b;
  font-size: .72rem;
  font-weight: 700
}

.stat strong {
  display: block;
  margin-top: .25rem;
  color: #284c32;
  font-size: .9rem;
  overflow-wrap: anywhere
}

.status {
  display: inline-flex;
  border-radius: 999px;
  padding: .35rem .65rem;
  font-size: .72rem;
  font-weight: 800
}

.status-active {
  background: #e8f6e8;
  color: #2c7142
}

.status-other {
  background: #f2f3f2;
  color: #69736d
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

.secondary-button {
  border: 1px solid #dce8dc;
  border-radius: 12px;
  background: #fff;
  padding: .68rem .9rem;
  color: #526158;
  font-size: .8rem;
  font-weight: 750
}

.secondary-button:hover {
  background: #f5f9f4
}

.secondary-button:disabled {
  opacity: .55
}

.danger-button {
  border: 1px solid #f0d5d5;
  border-radius: 12px;
  background: #fff7f7;
  padding: .68rem .9rem;
  color: #a94c4c;
  font-size: .8rem;
  font-weight: 800
}

.danger-button:hover {
  background: #fff0f0
}

.empty-card {
  text-align: center;
  padding: 4rem 1.5rem
}

.empty-icon {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  margin: 0 auto 1rem;
  border-radius: 16px;
  background: #edf7eb;
  color: #2d7543;
  font-size: 1.5rem
}

.modal {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: grid;
  place-items: center;
  background: rgba(15, 23, 42, .4);
  padding: 1rem;
  backdrop-filter: blur(6px)
}

.modal-card {
  width: 100%;
  max-width: 520px;
  border-radius: 24px;
  background: #fff;
  padding: 1.4rem;
  box-shadow: 0 24px 70px rgba(15, 23, 42, .2)
}

.close-button {
  font-size: 1.5rem;
  color: #849087
}
</style>

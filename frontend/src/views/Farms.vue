<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppShell from "../components/AppShell.vue";
import { useAuthStore } from "../stores/auth";
import {
  deleteFarm,
  getFarm,
  listFarms,
  setFarmStatus,
  updateFarm,
} from "../services/farms";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();


const farms = ref([]);
const selectedFarm = ref(null);
const loading = ref(false);
const loadingDetails = ref(false);
const saving = ref(false);
const deleting = ref(false);
const error = ref("");
const message = ref("");
const searchId = ref(auth.user?.farm_id || "");
const statusValue = ref("");
const showEdit = ref(false);
const showDelete = ref(false);
const editForm = ref({
  name: "",
  region: "",
  size_hectares: "",
});
const canManage = computed(() => auth.isLoggedIn);

// feedback messages
function clearFeedback() {
  error.value = "";
  message.value = "";
}

// Handle API errors

const extractError = (errorObject, fallback) => {
  const detail = errorObject?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
  }
  if (typeof detail === "string") {
    return detail;
  }
  if (errorObject?.response?.status === 500) {
    return "The server returned an internal error. Maybe need to Check the FastAPI terminal for the backend traceback";
  }
  return errorObject?.message || fallback;
}

const normaliseFarmList = (data) => {

  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.items)) return data.items;
  if (data && Array.isArray(data.farms)) return data.farms;
  return data ? [data] : [];

}
const selectFarm = (farm) => {
  selectedFarm.value = farm;
  searchId.value = farm.farm_id || "";
  statusValue.value = farm.status || "";
}

// Get all farms
async function loadFarms(selectId = "") {
  clearFeedback();
  loading.value = true;
  try {
    const response = await listFarms();
    farms.value = normaliseFarmList(response.data);

    const preferredId = selectId || selectedFarm.value?.farm_id || auth.user?.farm_id;
    const preferred = farms.value.find((item) => item.farm_id === preferredId);

    if (preferred) {
      selectFarm(preferred);
      await loadFarm(preferred.farm_id, false);

    } else if (selectedFarm.value?.farm_id) {
      selectedFarm.value = null;
    }
  } catch (errorObject) {

    farms.value = [];
    selectedFarm.value = null;
    error.value = extractError(errorObject, "Unable to load farms");

  } finally {
    loading.value = false;
  }
}

// Get one farm by ID
async function loadFarm(id = searchId.value) {
  const farmId = id.trim();
  clearFeedback();
  if (!farmId) {
    error.value = "Enter a Farm ID";
    return;
  }
  loadingDetails.value = true;
  try {
    const response = await getFarm(farmId);
    selectFarm(response.data);
  } catch (errorObject) {
    selectedFarm.value = null;
    error.value = extractError(errorObject, "Farm not found");
  } finally {
    loadingDetails.value = false;
  }
}
// Open edit form
const openEdit = () => {
  if (!selectedFarm.value) return;
  clearFeedback();
  editForm.value = {
    name: selectedFarm.value.name ?? "",
    region: selectedFarm.value.region ?? "",
    size_hectares: selectedFarm.value.size_hectares ?? "",
  };
  showEdit.value = true;
}
// Update farm info
async function saveFarm() {
  if (!selectedFarm.value) return;
  clearFeedback();
  saving.value = true;
  try {
    const response = await updateFarm(selectedFarm.value.farm_id, editForm.value);
    selectedFarm.value = response.data;
    statusValue.value = response.data?.status || statusValue.value;
    showEdit.value = false;
    message.value = "Farm updated successfully.";
    await loadFarms(selectedFarm.value.farm_id);
  } catch (errorObject) {
    error.value = extractError(errorObject, "Unable to update the farm");
  } finally {
    saving.value = false;
  }
}

// Update farm status
async function saveStatus() {
  if (!selectedFarm.value) return;
  const status = statusValue.value.trim();
  if (!status) {
    error.value = "Enter a farm status";
    return;
  }
  clearFeedback();
  saving.value = true;
  try {
    await setFarmStatus(selectedFarm.value.farm_id, status);
    const refreshed = await getFarm(selectedFarm.value.farm_id);
    selectedFarm.value = refreshed.data;
    statusValue.value = refreshed.data?.status || status;
    message.value = "Farm status updated successfully.";
    await loadFarms(selectedFarm.value.farm_id);
  } catch (errorObject) {
    error.value = extractError(errorObject, "Unable to update farm status");
  } finally {
    saving.value = false;
  }
}

// Delete selected farm
async function confirmDelete() {
  if (!selectedFarm.value) return;
  clearFeedback();
  deleting.value = true;
  try {
    const farmId = selectedFarm.value.farm_id;
    await deleteFarm(farmId);
    showDelete.value = false;
    selectedFarm.value = null;
    searchId.value = "";
    statusValue.value = "";
    message.value = "Farm deleted successfully";
    await loadFarms();
  } catch (errorObject) {
    error.value = extractError(errorObject, "Unable to delete the farm");
  } finally {
    deleting.value = false;
  }
}

// Go to Create Farm page
const goCreate = () => {
  router.push({ name: "create-farm" });
}

// Load farms when page opens
onMounted(() => {
  const selectedId = typeof route.query.selected === "string" ? route.query.selected : "";
  loadFarms(selectedId || auth.user?.farm_id || "");
});
</script>

<template>
  <AppShell>
    <section class="mx-auto max-w-7xl">
      <!-- Page header -->
      <header class="page-header">
        <div class="box-left">
          <span class="eyebrow">Farm management</span>
          <h1 class="page-title">Farms</h1>
          <p class="page-subtitle">It has been confirmed that it is human writting code~~</p>
        </div>
        <button v-if="canManage" class="primary-button" @click="goCreate">+ New Farm</button>
      </header>
      <div v-if="error" class="alert error">{{ error }}</div>
      <div v-if="message" class="alert success">{{ message }}</div>

      <!-- Find farm -->
      <section class="lookup card">
        <div class="box-left">
          <span class="eyebrow">Find a farm</span>
          <h2 class="card-title">Farm details</h2>
          <p class="page-subtitle">Search and view farm details.</p>
        </div>
        <form class="lookup-form" @submit.prevent="loadFarm()">
          <input v-model="searchId" class="field-input" placeholder="Farm ID" autocomplete="off" />
          <button class="secondary-button" :disabled="loadingDetails">
            {{ loadingDetails ? "Loading..." : "Get Farm" }}
          </button>
        </form>
      </section>

      <!-- Farm list and details -->
      <div class="farm-layout">
        <section class="card">
          <div class="section-heading">
            <div>
              <span class="eyebrow">Farms</span>
              <h2 class="card-title">Farm list</h2>
            </div>
            <div class="heading-actions">
              <span class="count-badge">{{ farms.length }}</span>
              <button class="icon-button" title="Refresh farms" @click="loadFarms()">↻</button>
            </div>
          </div>

          <div v-if="loading" class="empty-state">Loading farms...</div>
          <div v-else-if="farms.length === 0" class="empty-state">
            <strong>No farms returned by the API</strong>
            <span>Create a farm to add the first record.</span>
          </div>

          <div v-else class="farm-list">
            <button v-for="item in farms" :key="item.farm_id" class="farm-row"
              :class="selectedFarm?.farm_id === item.farm_id ? 'selected' : ''" @click="selectFarm(item)">
              <span class="farm-icon">⌂</span>
              <span class="farm-row-main">
                <strong>{{ item.name }}</strong>
                <small>{{ item.region }}</small>
              </span>
              <span class="farm-size">{{ item.size_hectares }} ha</span>
              <span class="status" :class="item.status === 'active' ? 'status-active' : 'status-other'">
                {{ item.status }}
              </span>
            </button>
          </div>
        </section>

        <!-- Selected farm details -->
        <section v-if="selectedFarm" class="card details-card">
          <div class="section-heading">
            <div>
              <span class="eyebrow">Farm details</span>
              <h2 class="card-title">{{ selectedFarm.name }}</h2>
              <p class="page-subtitle">{{ selectedFarm.region }}</p>
            </div>
            <span class="status" :class="selectedFarm.status === 'active' ? 'status-active' : 'status-other'">
              {{ selectedFarm.status }}
            </span>
          </div>
          <div class="stats-grid">
            <div class="stat"><span>Farm ID</span><strong>{{ selectedFarm.farm_id }}</strong></div>
            <div class="stat"><span>Region</span><strong>{{ selectedFarm.region }}</strong></div>
            <div class="stat"><span>Size</span><strong>{{ selectedFarm.size_hectares }} ha</strong></div>
            <div class="stat"><span>Status</span><strong>{{ selectedFarm.status }}</strong></div>
          </div>
          <div v-if="canManage" class="action-stack">
            <button class="primary-button full" @click="openEdit">Edit Farm</button>
            <div class="status-control">
              <label class="field-label" for="farm-status">Status</label>
              <div class="status-row">
                <input id="farm-status" v-model="statusValue" class="field-input" placeholder="active" />
                <button class="secondary-button" :disabled="saving" @click="saveStatus">
                  {{ saving ? "Saving..." : "Update Status" }}
                </button>
              </div>
            </div>
            <button class="danger-button full" :disabled="deleting" @click="showDelete = true">
              {{ deleting ? "Deleting..." : "Delete Farm" }}
            </button>
          </div>
        </section>

        <!-- Empty state -->
        <section v-else class="card empty-details">
          <div class="empty-icon">⌂</div>
          <h2 class="card-title">Select a farm</h2>
          <p class="page-subtitle">Choose a farm from the API list to view, edit, update or delete it.</p>
        </section>
      </div>

      <!-- Edit farm modal -->
      <div v-if="showEdit" class="modal" @click.self="showEdit = false">
        <form class="modal-card" @submit.prevent="saveFarm">
          <div class="section-heading">
            <div>
              <span class="eyebrow">Edit farm</span>
              <h2 class="card-title">Update farm</h2>
            </div>
            <button type="button" class="close-button" @click="showEdit = false">×</button>
          </div>
          <div class="form-grid">
            <label class="field-label">Name<input v-model.trim="editForm.name" class="field-input" required /></label>
            <label class="field-label">Region<input v-model.trim="editForm.region" class="field-input"
                required /></label>
            <label class="field-label full-field">
              Size (hectares)
              <input v-model.number="editForm.size_hectares" class="field-input" type="number" min="0" step="0.01"
                required />
            </label>
          </div>
          <div class="modal-actions">
            <button type="button" class="secondary-button" @click="showEdit = false">Cancel</button>
            <button class="primary-button" :disabled="saving">{{ saving ? "Saving..." : "Save Changes" }}</button>
          </div>
        </form>
      </div>

      <!-- Delete confirmation -->
      <div v-if="showDelete" class="modal" @click.self="showDelete = false">
        <div class="modal-card confirm-card">
          <span class="eyebrow danger-eyebrow">Delete farm</span>
          <h2 class="card-title">Are you sure?</h2>
          <p class="page-subtitle">
            This will delete <strong>{{ selectedFarm?.name }}</strong> from the backend.
          </p>
          <div class="modal-actions">
            <button class="secondary-button" @click="showDelete = false">Cancel</button>
            <button class="danger-button" :disabled="deleting" @click="confirmDelete">
              {{ deleting ? "Deleting..." : "Delete Farm" }}
            </button>
          </div>
        </div>
      </div>
    </section>
  </AppShell>
</template>

<style scoped>
/* Layout */
.page-header,
.section-heading,
.status-row,
.modal-actions,
.heading-actions {
  display: flex;
  align-items: center;
}

.page-header,
.section-heading {
  justify-content: space-between;
  gap: 1rem;
}

.page-header {
  margin-bottom: 1.5rem;
  align-items: flex-end;
}

/* Text */
.eyebrow {
  display: inline-flex;
  margin-bottom: 0.45rem;
  border-radius: 999px;
  background: #eaf5e7;
  padding: 0.28rem 0.65rem;
  color: #2c7142;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.danger-eyebrow {
  background: #fff0ef;
  color: #b64d46;
}

.page-title {
  margin: 0;
  color: #17241b;
  font-size: 2.1rem;
  font-weight: 900;
}

.page-subtitle {
  margin-top: 0.35rem;
  color: #68756d;
  font-size: 0.88rem;
  line-height: 1.5;
}

.card {
  border: 1px solid #e1eee0;
  border-radius: 20px;
  background: #fff;
  padding: 1.25rem;
  box-shadow: 0 8px 24px rgba(39, 98, 53, 0.06);
}

.card-title {
  margin: 0;
  color: #203c28;
  font-size: 1.08rem;
  font-weight: 850;
}


.lookup {
  display: grid;
  grid-template-columns: 1fr minmax(280px, 460px);
  align-items: end;
  gap: 1.5rem;
  margin-bottom: 1.25rem;
}

.lookup-form,
.form-grid {
  display: grid;
  gap: 0.75rem;
}

.lookup-form {
  grid-template-columns: 1fr auto;
}

.field-label {
  display: grid;
  gap: 0.4rem;
  color: #46564c;
  font-size: 0.76rem;
  font-weight: 800;
}

.field-input {
  width: 100%;
  border: 1px solid #d8e4d8;
  border-radius: 11px;
  background: #fbfdfb;
  padding: 0.7rem 0.78rem;
  color: #26382c;
  font-size: 0.86rem;
  outline: none;
}

.field-input:focus {
  border-color: #65a873;
  box-shadow: 0 0 0 3px #eaf5ea;
}

/* Btn */
.primary-button,
.secondary-button,
.danger-button,
.icon-button,
.close-button {
  border: 0;
  cursor: pointer;
  font-weight: 800;
}

.primary-button {
  border-radius: 12px;
  background: #286b3e;
  padding: 0.72rem 1rem;
  color: #fff;
  box-shadow: 0 8px 18px rgba(40, 107, 62, 0.14);
}

.primary-button:hover {
  background: #205a33;
}

.secondary-button {
  border: 1px solid #dce8dc;
  border-radius: 12px;
  background: #fff;
  padding: 0.68rem 0.9rem;
  color: #526158;
}

.secondary-button:hover {
  background: #f5faf4;
}

.danger-button {
  border-radius: 12px;
  background: #fff1ef;
  padding: 0.72rem 1rem;
  color: #b64d46;
}

.danger-button:hover {
  background: #ffe6e2;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.full {
  width: 100%;
}

/* Alerts */
.alert {
  margin-bottom: 1rem;
  border-radius: 12px;
  padding: 0.75rem 0.9rem;
  font-size: 0.82rem;
}

.alert.error {
  border: 1px solid #f0d5d5;
  background: #fff7f7;
  color: #a94c4c;
}

.alert.success {
  border: 1px solid #d7ead4;
  background: #f2faf1;
  color: #2e6e3e;
}

/* Farm list */
.farm-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(320px, 420px);
  gap: 1.25rem;
}

.heading-actions {
  gap: 0.5rem;
}

.count-badge,
.status {
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 800;
}

.count-badge {
  background: #edf7eb;
  padding: 0.38rem 0.6rem;
  color: #2d7441;
}

.icon-button {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: #f4f8f3;
  color: #356c45;
  font-size: 1rem;
}

.farm-list {
  display: grid;
  gap: 0.5rem;
  margin-top: 1rem;
}

.farm-row {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto auto;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  border: 1px solid transparent;
  border-radius: 14px;
  background: #fff;
  padding: 0.75rem;
  text-align: left;
}

.farm-row:hover,
.farm-row.selected {
  border-color: #cde4ca;
  background: #f4faf2;
}

.farm-icon,
.empty-icon {
  display: grid;
  place-items: center;
  border-radius: 11px;
  background: #edf7eb;
  color: #2d7441;
}

.farm-icon {
  width: 34px;
  height: 34px;
}

.farm-row-main {
  min-width: 0;
}

.farm-row-main strong,
.farm-row-main small {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.farm-row-main strong {
  color: #27382d;
  font-size: 0.84rem;
}

.farm-row-main small,
.farm-size {
  color: #7a877f;
  font-size: 0.73rem;
}

/* Farm status */
.status {
  padding: 0.38rem 0.58rem;
  text-transform: capitalize;
}

.status-active {
  background: #e6f5e5;
  color: #2b7742;
}

.status-other {
  background: #f1f3f0;
  color: #65716a;
}

/* Farm details */
.details-card {
  min-width: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.65rem;
  margin: 1.25rem 0;
}

.stat {
  min-width: 0;
  border-radius: 14px;
  background: #f6faf5;
  padding: 0.85rem;
}

.stat span,
.stat strong {
  display: block;
}

.stat span {
  color: #77837b;
  font-size: 0.7rem;
}

.stat strong {
  margin-top: 0.25rem;
  color: #284c32;
  font-size: 0.84rem;
  overflow-wrap: anywhere;
}

.action-stack {
  display: grid;
  gap: 0.75rem;
}

.status-control {
  border-radius: 14px;
  background: #f7faf6;
  padding: 0.75rem;
}

/* Empty state */
.empty-state,
.empty-details {
  display: grid;
  place-items: center;
  min-height: 230px;
  color: #748179;
  text-align: center;
}

.empty-state {
  gap: 0.3rem;
  margin-top: 1rem;
  border-radius: 14px;
  background: #f8fbf7;
  padding: 1.5rem;
}

.empty-state strong {
  color: #42564a;
}

.empty-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 0.8rem;
  font-size: 1.2rem;
}

/* Modal */
.modal {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: grid;
  place-items: center;
  background: rgba(23, 36, 27, 0.42);
  padding: 1rem;
}

.modal-card {
  width: min(560px, 100%);
  border-radius: 22px;
  background: #fff;
  padding: 1.35rem;
  box-shadow: 0 25px 70px rgba(0, 0, 0, 0.2);
}

.close-button {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #f1f5f1;
  color: #607067;
  font-size: 1.3rem;
}

.form-grid {
  grid-template-columns: 1fr 1fr;
  margin-top: 1.2rem;
}

.full-field {
  grid-column: 1 / -1;
}

.modal-actions {
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.3rem;
}

.confirm-card {
  width: min(460px, 100%);
}

/* Responsive */
@media (max-width: 900px) {

  .farm-layout,
  .lookup {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .page-header {
    align-items: stretch;
    flex-direction: column;
  }

  .page-header .primary-button {
    width: 100%;
  }

  .lookup-form,
  .form-grid {
    grid-template-columns: 1fr;
  }

  .full-field {
    grid-column: auto;
  }

  .farm-row {
    grid-template-columns: auto minmax(0, 1fr) auto;
  }

  .farm-size {
    display: none;
  }

  .status-row {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
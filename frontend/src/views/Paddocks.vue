<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppShell from "../components/AppShell.vue";
import { useAuthStore } from "../stores/auth";
import {
  deletePaddock,
  getPaddock,
  listPaddocks,
  setPaddockStatus,
  updatePaddock,
} from "../services/paddocks";

const STOCK_TYPES = ["dairy", "beef", "sheep", "mixed", "other"];
const PADDOCK_STATUSES = ["active", "disabled"];

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

const paddocks = ref([]);
const selectedPaddock = ref(null);
const loading = ref(false);
const loadingDetails = ref(false);
const saving = ref(false);
const deleting = ref(false);
const error = ref("");
const message = ref("");
const searchFarmId = ref(auth.user?.farm_id || "");
const searchPaddockId = ref("");
const statusValue = ref("");
const showEdit = ref(false);
const showDelete = ref(false);

const editForm = ref({
  name: "",
  farm_id: "",
  area_hectares: "",
  stock_type: STOCK_TYPES[0],
});

// Pagination
const currentPage = ref(1);
const pageSize = 20;

const totalPages = computed(() =>
  Math.max(1, Math.ceil(paddocks.value.length / pageSize))
);

const paginatedPaddocks = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  return paddocks.value.slice(start, start + pageSize);
});

const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
};

watch(totalPages, (pages) => {
  if (currentPage.value > pages) currentPage.value = pages;
});

const canManage = computed(() => auth.isLoggedIn);
const canCreatePaddock = computed(() => ["super-admin", "admin"].includes(auth.role));

const clearFeedback = () => {
  error.value = "";
  message.value = "";
};

const extractError = (errorObject, fallback) => {
  const detail = errorObject?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
  }
  if (typeof detail === "string") {
    return detail;
  }
  if (errorObject?.response?.status === 500) {
    return "The server returned an internal error. Check the FastAPI terminal for the backend traceback.";
  }
  return errorObject?.message || fallback;
};

const normalisePaddockList = (data) => {
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.items)) return data.items;
  if (data && Array.isArray(data.paddocks)) return data.paddocks;
  return data ? [data] : [];
};

const selectPaddock = (paddock) => {
  selectedPaddock.value = paddock;
  searchFarmId.value = paddock.farm_id || "";
  searchPaddockId.value = paddock.paddock_id || "";
  statusValue.value = paddock.status || "";
};

// Get all paddocks visible to the current user (backend already scopes
// admin/staff to their own farm_id — see list_paddocks in paddocks.py)
const loadPaddocks = async () => {
  clearFeedback();
  loading.value = true;
  try {
    const response = await listPaddocks();
    paddocks.value = normalisePaddockList(response.data);
    currentPage.value = 1;

    if (selectedPaddock.value) {
      const stillThere = paddocks.value.find(
        (item) =>
          item.farm_id === selectedPaddock.value.farm_id &&
          item.paddock_id === selectedPaddock.value.paddock_id
      );
      if (!stillThere) selectedPaddock.value = null;
    }
  } catch (errorObject) {
    paddocks.value = [];
    selectedPaddock.value = null;
    error.value = extractError(errorObject, "Unable to load paddocks");
  } finally {
    loading.value = false;
  }
};

// Get one paddock by its composite key (farm_id + paddock_id)
const loadPaddock = async () => {
  const farmId = searchFarmId.value.trim();
  const paddockId = searchPaddockId.value.trim();
  clearFeedback();
  if (!farmId || !paddockId) {
    error.value = "Enter both a Farm ID and a Paddock ID";
    return;
  }
  loadingDetails.value = true;
  try {
    const response = await getPaddock(farmId, paddockId);
    selectPaddock(response.data);
  } catch (errorObject) {
    selectedPaddock.value = null;
    error.value = extractError(errorObject, "Paddock not found");
  } finally {
    loadingDetails.value = false;
  }
};

const openEdit = () => {
  if (!selectedPaddock.value) return;
  clearFeedback();
  editForm.value = {
    name: selectedPaddock.value.name ?? "",
    farm_id: selectedPaddock.value.farm_id ?? "",
    area_hectares: selectedPaddock.value.area_hectares ?? "",
    stock_type: selectedPaddock.value.stock_type || STOCK_TYPES[0],
  };
  showEdit.value = true;
};

const savePaddock = async () => {
  if (!selectedPaddock.value) return;
  clearFeedback();
  saving.value = true;
  try {
    const response = await updatePaddock(
      selectedPaddock.value.farm_id,
      selectedPaddock.value.paddock_id,
      editForm.value
    );
    selectedPaddock.value = response.data;
    statusValue.value = response.data?.status || statusValue.value;
    showEdit.value = false;
    message.value = "Paddock updated successfully.";
    await loadPaddocks();
  } catch (errorObject) {
    error.value = extractError(errorObject, "Unable to update the paddock");
  } finally {
    saving.value = false;
  }
};

const saveStatus = async () => {
  if (!selectedPaddock.value) return;
  const status = statusValue.value.trim();
  if (!status) {
    error.value = "Enter a paddock status";
    return;
  }
  clearFeedback();
  saving.value = true;
  try {
    await setPaddockStatus(selectedPaddock.value.farm_id, selectedPaddock.value.paddock_id, status);
    const refreshed = await getPaddock(selectedPaddock.value.farm_id, selectedPaddock.value.paddock_id);
    selectedPaddock.value = refreshed.data;
    statusValue.value = refreshed.data?.status || status;
    message.value = "Paddock status updated successfully.";
    await loadPaddocks();
  } catch (errorObject) {
    error.value = extractError(errorObject, "Unable to update paddock status");
  } finally {
    saving.value = false;
  }
};

const confirmDelete = async () => {
  if (!selectedPaddock.value) return;
  clearFeedback();
  deleting.value = true;
  try {
    await deletePaddock(selectedPaddock.value.farm_id, selectedPaddock.value.paddock_id);
    showDelete.value = false;
    selectedPaddock.value = null;
    searchPaddockId.value = "";
    statusValue.value = "";
    message.value = "Paddock deleted successfully";
    await loadPaddocks();
  } catch (errorObject) {
    error.value = extractError(errorObject, "Unable to delete the paddock");
  } finally {
    deleting.value = false;
  }
};

const goCreate = () => {
  router.push({ name: "create-paddock" });
};

onMounted(async () => {
  await loadPaddocks();

  const queryFarmId = typeof route.query.farm_id === "string" ? route.query.farm_id : "";
  const queryPaddockId = typeof route.query.paddock_id === "string" ? route.query.paddock_id : "";
  if (queryFarmId && queryPaddockId) {
    searchFarmId.value = queryFarmId;
    searchPaddockId.value = queryPaddockId;
    await loadPaddock();
  }
});
</script>

<template>
  <AppShell>
    <section class="mx-auto max-w-7xl">
      <!-- Page header -->
      <header class="page-header">
        <div class="box-left">
          <span class="eyebrow">Farm management</span>
          <h1 class="page-title">Paddocks</h1>
        </div>
        <button v-if="canCreatePaddock" class="primary-button" @click="goCreate">+ New Paddock</button>
      </header>

      <div v-if="error" class="alert error">{{ error }}</div>
      <div v-if="message" class="alert success">{{ message }}</div>

      <!-- Find paddock -->
      <section class="lookup card">
        <div class="box-left">
          <span class="eyebrow">Find a paddock</span>
          <h2 class="card-title">Paddock lookup</h2>
        </div>
        <form class="lookup-form" @submit.prevent="loadPaddock()">
          <input v-model="searchFarmId" class="field-input" placeholder="Farm ID" autocomplete="off" />
          <input v-model="searchPaddockId" class="field-input" placeholder="Paddock ID" autocomplete="off" />
          <button class="secondary-button" :disabled="loadingDetails">
            {{ loadingDetails ? "Loading..." : "Get Paddock" }}
          </button>
        </form>
      </section>

      <!-- Paddock list and details -->
      <div class="farm-layout">
        <section class="card">
          <div class="section-heading">
            <div>
              <span class="eyebrow">Paddocks</span>
              <h2 class="card-title">Paddock list</h2>
            </div>
            <div class="heading-actions">
              <span class="count-badge">{{ paddocks.length }}</span>
              <button class="icon-button" title="Refresh paddocks" @click="loadPaddocks()">↻</button>
            </div>
          </div>

          <div v-if="loading" class="empty-state">Loading paddocks...</div>
          <div v-else-if="paddocks.length === 0" class="empty-state">
            <strong>No paddocks returned by the API</strong>
            <span>Create a paddock to add the first record.</span>
          </div>

          <template v-else>
            <div class="overflow-x-auto rounded-lg border border-stone-200">
              <table class="w-full text-left text-sm">
                <thead>
                  <tr class="border-b border-stone-200 bg-stone-50 text-stone-500">
                    <th class="px-3 py-2 font-medium">Name</th>
                    <th class="px-3 py-2 font-medium">Farm ID</th>
                    <th class="px-3 py-2 font-medium">Stock Type</th>
                    <th class="px-3 py-2 text-right font-medium">Area (Ha)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="item in paginatedPaddocks"
                    :key="`${item.farm_id}-${item.paddock_id}`"
                    @click="selectPaddock(item)"
                    class="cursor-pointer border-b border-stone-100 last:border-0 hover:bg-stone-50"
                    :class="
                      selectedPaddock?.farm_id === item.farm_id &&
                      selectedPaddock?.paddock_id === item.paddock_id
                        ? 'bg-emerald-50'
                        : ''
                    "
                  >
                    <td class="px-3 py-2 font-medium text-stone-900">{{ item.name }}</td>
                    <td class="px-3 py-2 font-mono text-xs text-stone-500">{{ item.farm_id }}</td>
                    <td class="px-3 py-2 capitalize text-stone-600">{{ item.stock_type ?? '—' }}</td>
                    <td class="px-3 py-2 text-right text-stone-600">{{ item.area_hectares ?? '—' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Pagination -->
            <div v-if="totalPages > 1" class="pagination">
              <button class="icon-button" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">‹</button>
              <span class="pagination-label">Page {{ currentPage }} of {{ totalPages }}</span>
              <button class="icon-button" :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">›</button>
            </div>
          </template>
        </section>

        <!-- Selected paddock details -->
        <section v-if="selectedPaddock" class="card details-card">
          <div class="section-heading">
            <div class="box-left">
              <span class="eyebrow">Paddock details</span>
              <h2 class="card-title">{{ selectedPaddock.name }}</h2>
              <p class="page-subtitle">{{ selectedPaddock.farm_id }}</p>
            </div>
            <span class="status" :class="selectedPaddock.status === 'active' ? 'status-active' : 'status-other'">
              {{ selectedPaddock.status }}
            </span>
          </div>

          <div class="stats-grid">
            <div class="stat"><span>Paddock ID</span><strong>{{ selectedPaddock.paddock_id }}</strong></div>
            <div class="stat"><span>Farm ID</span><strong>{{ selectedPaddock.farm_id }}</strong></div>
            <div class="stat"><span>Area</span><strong>{{ selectedPaddock.area_hectares }} ha</strong></div>
            <div class="stat"><span>Stock type</span><strong class="capitalize">{{ selectedPaddock.stock_type ?? '—' }}</strong></div>
          </div>

          <div v-if="canManage" class="action-stack">
            <button class="primary-button full" @click="openEdit">Edit Paddock</button>
            <div class="status-control">
              <label class="field-label" for="paddock-status">Status</label>
              <div class="status-row">
                <select id="paddock-status" v-model="statusValue" class="field-input">
                  <option v-for="s in PADDOCK_STATUSES" :key="s" :value="s">{{ s }}</option>
                </select>
                <button class="secondary-button" :disabled="saving" @click="saveStatus">
                  {{ saving ? "Saving..." : "Update Status" }}
                </button>
              </div>
            </div>
            <button class="danger-button full" :disabled="deleting" @click="showDelete = true">
              {{ deleting ? "Deleting..." : "Delete Paddock" }}
            </button>
          </div>
        </section>

        <!-- Empty state -->
        <section v-else class="card empty-details">
          <div class="empty-icon">▤</div>
          <h2 class="card-title">Select a paddock</h2>
          <p class="page-subtitle">Choose a paddock from the list to view, edit, update or delete it.</p>
        </section>
      </div>

      <!-- Edit paddock modal -->
      <div v-if="showEdit" class="modal" @click.self="showEdit = false">
        <form class="modal-card" @submit.prevent="savePaddock">
          <div class="section-heading">
            <div>
              <span class="eyebrow">Edit paddock</span>
              <h2 class="card-title">Update paddock</h2>
            </div>
            <button type="button" class="close-button" @click="showEdit = false">×</button>
          </div>
          <div class="form-grid">
            <label class="field-label">Name<input v-model.trim="editForm.name" class="field-input" required /></label>
            <label class="field-label">
              Stock type
              <select v-model="editForm.stock_type" class="field-input">
                <option v-for="s in STOCK_TYPES" :key="s" :value="s">{{ s }}</option>
              </select>
            </label>
            <label class="field-label full-field">
              Area (hectares)
              <input v-model.number="editForm.area_hectares" class="field-input" type="number" min="0" step="0.01" required />
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
          <span class="eyebrow danger-eyebrow">Delete paddock</span>
          <h2 class="card-title">Are you sure?</h2>
          <p class="page-subtitle">
            This will delete <strong>{{ selectedPaddock?.name }}</strong> from the backend.
          </p>
          <div class="modal-actions">
            <button class="secondary-button" @click="showDelete = false">Cancel</button>
            <button class="danger-button" :disabled="deleting" @click="confirmDelete">
              {{ deleting ? "Deleting..." : "Delete Paddock" }}
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
  grid-template-columns: 1fr minmax(320px, 480px);
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1.25rem;
  padding: 0.75rem 1.25rem;
}

.lookup .eyebrow {
  margin-bottom: 0.2rem;
}

.lookup .card-title {
  font-size: 0.94rem;
}

.lookup-form,
.form-grid {
  display: grid;
  gap: 0.75rem;
}

.lookup-form {
  grid-template-columns: 1fr 1fr auto;
}

.lookup .field-input {
  padding: 0.5rem 0.7rem;
}

.lookup .secondary-button {
  padding: 0.5rem 0.85rem;
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
  flex: 1;
}

.field-input:focus {
  border-color: #65a873;
  box-shadow: 0 0 0 3px #eaf5ea;
}

.capitalize {
  text-transform: capitalize;
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

/* Layout */
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

.empty-icon {
  display: grid;
  place-items: center;
  border-radius: 9px;
  background: #edf7eb;
  color: #2d7441;
  width: 48px;
  height: 48px;
  margin-bottom: 0.8rem;
  font-size: 1.2rem;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin-top: 0.85rem;
  padding-top: 0.75rem;
  border-top: 1px solid #eef4ed;
}

.pagination-label {
  color: #58685d;
  font-size: 0.78rem;
  font-weight: 700;
}

/* Status */
.status {
  padding: 0.32rem 0.5rem;
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

.details-card {
  min-width: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.4rem;
  margin: 0.85rem 0;
}

.stat {
  min-width: 0;
  border-radius: 10px;
  background: #f6faf5;
  padding: 0.5rem 0.6rem;
}

.stat span,
.stat strong {
  display: block;
}

.stat span {
  color: #77837b;
  font-size: 0.63rem;
}

.stat strong {
  margin-top: 0.1rem;
  color: #284c32;
  font-size: 0.76rem;
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

.status-row {
  display: flex;
  align-items: center;
  gap: 10px;
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

  .status-row {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
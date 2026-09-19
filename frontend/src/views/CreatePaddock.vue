<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import AppShell from "../components/AppShell.vue";
import { useAuthStore } from "../stores/auth";
import { createPaddock } from "../services/paddocks";

const STOCK_TYPES = ["dairy", "beef", "sheep", "mixed", "other"];

const router = useRouter();
const auth = useAuthStore();
const loading = ref(false);
const error = ref("");

const form = ref({
  name: "",
  farm_id: auth.user?.farm_id || "",
  area_hectares: "",
  stock_type: STOCK_TYPES[0],
});

function extractError(errorObject) {
  const detail = errorObject?.response?.data?.detail;

  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
  }
  if (typeof detail === "string") return detail;
  if (errorObject?.response?.status === 500) {
    return "The server returned an internal error. Check the FastAPI terminal for the backend traceback.";
  }

  return errorObject?.message || "Unable to create the paddock.";
}

async function submit() {
  error.value = "";
  loading.value = true;

  try {
    const response = await createPaddock(form.value);
    const createdPaddock = response.data;

    if (!createdPaddock?.paddock_id) {
      throw new Error("The API created the paddock but did not return a paddock_id.");
    }

    await router.push({
      name: "paddocks",
      query: { farm_id: createdPaddock.farm_id, paddock_id: createdPaddock.paddock_id },
    });
  } catch (errorObject) {
    error.value = extractError(errorObject);
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <AppShell>
    <section class="mx-auto max-w-3xl">
      <header class="page-header">
        <div class="box-left">
          <span class="eyebrow">New paddock</span>
          <h1 class="page-title">Create Paddock</h1>
          <p class="page-subtitle">Add a paddock using the fields supported by the Paddock API.</p>
        </div>
        <button class="secondary-button" @click="router.push({ name: 'paddocks' })">Back to Paddocks</button>
      </header>

      <form class="card" @submit.prevent="submit">
        <div v-if="error" class="alert error">{{ error }}</div>

        <div class="form-grid box-left">
          <label class="field-label">
            Name
            <input v-model.trim="form.name" class="field-input" required maxlength="200" />
          </label>
          <label class="field-label">
            Farm ID
            <input
              v-model.trim="form.farm_id"
              class="field-input"
              required
              :readonly="auth.role !== 'super-admin'"
              placeholder="farm-001"
            />
          </label>
          <label class="field-label">
            Stock type
            <select v-model="form.stock_type" class="field-input">
              <option v-for="s in STOCK_TYPES" :key="s" :value="s">{{ s }}</option>
            </select>
          </label>
          <label class="field-label">
            Area (hectares)
            <input v-model.number="form.area_hectares" class="field-input" type="number" min="0" step="0.01" required />
          </label>
        </div>

        <div class="form-actions">
          <button type="button" class="secondary-button" @click="router.push({ name: 'paddocks' })">
            Cancel
          </button>
          <button class="primary-button" :disabled="loading">
            {{ loading ? "Creating..." : "Create Paddock" }}
          </button>
        </div>
      </form>
    </section>
  </AppShell>
</template>

<style scoped>
/* Page header and form actions */
.page-header,
.form-actions {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
}

.page-header {
  margin-bottom: 1.5rem;
}

/* Small section label */
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

/* Main page title */
.page-title {
  margin: 0;
  color: #17241b;
  font-size: 2.1rem;
  font-weight: 900;
}

/* Page description */
.page-subtitle {
  margin-top: 0.35rem;
  color: #68756d;
  font-size: 0.88rem;
  line-height: 1.5;
}

/* Main form card */
.card {
  border: 1px solid #e1eee0;
  border-radius: 20px;
  background: #fff;
  padding: 1.35rem;
  box-shadow: 0 8px 24px rgba(39, 98, 53, 0.06);
}

/* Form layout */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

/* Form field label */
.field-label {
  display: grid;
  gap: 0.4rem;
  color: #46564c;
  font-size: 0.76rem;
  font-weight: 800;
}

/* Text and number inputs */
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

.field-input:read-only {
  background: #f1f5f0;
  color: #6b7a70;
}

/* Input focus state */
.field-input:focus {
  border-color: #65a873;
  box-shadow: 0 0 0 3px #eaf5ea;
}

/* Shared button styles */
.primary-button,
.secondary-button {
  border-radius: 12px;
  padding: 0.72rem 1rem;
  font-weight: 800;
  cursor: pointer;
}

/* Primary button */
.primary-button {
  border: 0;
  background: #286b3e;
  color: #fff;
}

.primary-button:hover {
  background: #205a33;
}

/* Secondary button */
.secondary-button {
  border: 1px solid #dce8dc;
  background: #fff;
  color: #526158;
}

.secondary-button:hover {
  background: #f5faf4;
}

/* Disabled buttons */
button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

/* Form action buttons */
.form-actions {
  align-items: center;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

/* Error message */
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

/* Mobile responsive layout */
@media (max-width: 640px) {

  .page-header,
  .form-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    align-items: stretch;
    flex-direction: column;
  }

  .form-grid {
    display: grid;
  }

  .form-actions {
    flex-direction: column-reverse;
    align-items: stretch;
  }

  .form-actions button {
    width: 100%;
  }
}
</style>
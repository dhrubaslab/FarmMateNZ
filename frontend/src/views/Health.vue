<script setup>
import { onMounted, ref } from "vue";
import AppShell from "../components/AppShell.vue";
import { getHealth } from "../services/health";

const loading = ref(true);
const error = ref("");
const result = ref(null);
const checkedAt = ref("");

// Check backend health status
const check = async () => {
  loading.value = true;
  error.value = "";
  try {
    const response = await getHealth();
    result.value = response.data;
    checkedAt.value = new Date().toLocaleString();
  } catch (err) {
    result.value = null;
    error.value = err.response?.data?.detail || err.message || "Health check failed.";
  } finally {
    loading.value = false;
  }
}
// Check health when page loads
onMounted(() => {
  check();
});
</script>

<template>
  <AppShell>
    <section class="mx-auto max-w-4xl">
      <!-- Page header -->
      <div class="mb-6 flex items-end justify-between gap-4">
        <div class="box-left">
          <div class="eyebrow">Service status</div>
          <h1 class="page-title">System Health</h1>
          <p class="page-subtitle">It has been confirmed that it is human writting code~~</p>
        </div>
        <button class="secondary-button" @click="check">↻ Check Again</button>
      </div>
      <div v-if="error" class="alert error">{{ error }}</div>

      <!-- Health status -->
      <div class="card">
        <div class="health-row">
          <div class="health-dot" :class="result !== null ? 'ok' : 'bad'"></div>
          <div>
            <h2>{{ result !== null ? "Backend reachable" : "Backend unavailable" }}</h2>
            <p>{{ checkedAt ? `Checked ${checkedAt}` : "Waiting for response..." }}</p>
          </div>
        </div>

        <div class="mt-6">
          <div class="eyebrow">Connection</div>
          <div v-if="!loading" class="health-summary">
            {{ result !== null ? "The backend health endpoint responded successfully." :
              "The backend did not return a successful response" }}
          </div>
          <div v-else class="loading">Checking service health...</div>
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

/* Health card */
.card {
  border: 1px solid #e1eee0;
  border-radius: 20px;
  background: #fff;
  padding: 1.35rem;
  box-shadow: 0 8px 24px rgba(39, 98, 53, .06)
}

.health-row {
  display: flex;
  align-items: center;
  gap: .85rem
}

.health-row h2 {
  margin: 0;
  color: #1b2a20;
  font-size: 1.05rem;
  font-weight: 850
}

.health-row p {
  margin: .15rem 0 0;
  color: #77837b;
  font-size: .78rem
}

.health-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  box-shadow: 0 0 0 6px #edf7eb
}

.health-dot.ok {
  background: #3f9855
}

.health-dot.bad {
  background: #c85a5a;
  box-shadow: 0 0 0 6px #fff0f0
}

/* Status message */
.health-summary {
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

/* Btn & alert */
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

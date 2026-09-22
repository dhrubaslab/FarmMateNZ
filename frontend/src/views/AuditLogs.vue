<script setup>
import { onMounted, ref } from "vue";
import AppShell from "../components/AppShell.vue";
import { getAuditLogs } from "../services/audit";

const loading = ref(true);
const error = ref("");
const logs = ref([]);

// Load the audit log list
const load = async () => {
  loading.value = true;
  error.value = "";
  try {
    const response = await getAuditLogs();
    logs.value = response.data;
  } catch (err) {
    logs.value = [];
    error.value = err.response?.data?.detail || err.message || "Failed to load audit logs.";
  } finally {
    loading.value = false;
  }
}
// Load logs when page loads
onMounted(() => {
  load();
});
</script>

<template>
  <AppShell>
    <section class="mx-auto max-w-4xl">
      <!-- Page header -->
      <div class="mb-6 flex items-end justify-between gap-4">
        <div class="box-left">
          <div class="eyebrow">Activity</div>
          <h1 class="page-title">Audit Log</h1>
          <p class="page-subtitle">Every change made in the system, most recent first.</p>
        </div>
        <button class="secondary-button" @click="load">↻ Refresh</button>
      </div>
      <div v-if="error" class="alert error">{{ error }}</div>

      <!-- Log entries -->
      <div class="card">
        <div v-if="loading" class="loading">Loading audit logs...</div>
        <div v-else-if="logs.length === 0" class="loading">No audit log entries yet.</div>
        <div v-else class="log-list">
          <div v-for="log in logs" :key="log.timestamp + log.message" class="log-row">
            <div class="log-time">{{ new Date(log.timestamp).toLocaleString() }}</div>
            <div class="log-message">{{ log.message }}</div>
          </div>
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

/* Log card */
.card {
  border: 1px solid #e1eee0;
  border-radius: 20px;
  background: #fff;
  padding: 1.35rem;
  box-shadow: 0 8px 24px rgba(39, 98, 53, .06)
}

.log-list {
  display: flex;
  flex-direction: column;
  gap: .55rem
}

.log-row {
  display: flex;
  flex-direction: column;
  gap: .15rem;
  border-radius: 14px;
  background: #f6faf5;
  padding: .75rem 1rem
}

.log-time {
  color: #68756d;
  font-size: .72rem;
  font-weight: 700
}

.log-message {
  color: #29392e;
  font-size: .86rem
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

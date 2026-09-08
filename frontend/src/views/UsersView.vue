<!--
  UsersView.vue — Users list page

  Displays farm users with name, username, email, status, last-signed-in,
  and created date. Access mirrors the Farms module: super-admin sees all
  users, admin/staff see only their own farm's users.

  Expects a backend endpoint: GET /users
    - super-admin: returns all users
    - admin/staff: returns only users where farm_id == current_user.farm_id
    (mirror the pattern already used in routes/farms.py list_farms())

  Drop into e.g. frontend/src/views/UsersView.vue and wire into your router.
-->
<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import AppShell from '@/components/AppShell.vue'

const auth = useAuthStore()

const users = ref([])
const isLoading = ref(true)
const loadError = ref('')
const searchQuery = ref('')
const statusFilter = ref('all') // 'all' | 'active' | 'disabled'

// Per-row status toggle
const togglingUserId = ref(null)
const actionError = ref('')

// Reset-password modal
const resetModalUser = ref(null)
const newPassword = ref('')
const resetSubmitting = ref(false)
const resetError = ref('')
const resetSuccess = ref(false)

async function loadUsers() {
  isLoading.value = true
  loadError.value = ''
  try {
    const { data } = await api.get('/users')
    users.value = data
  } catch (err) {
    loadError.value =
      err.response?.data?.detail || 'Could not load users. Try again.'
  } finally {
    isLoading.value = false
  }
}

onMounted(loadUsers)

async function toggleStatus(user) {
  const nextStatus = user.status === 'active' ? 'disabled' : 'active'
  togglingUserId.value = user.user_id
  actionError.value = ''
  try {
    await api.patch(`/users/${user.user_id}`, { status: nextStatus })
    user.status = nextStatus
  } catch (err) {
    actionError.value =
      err.response?.data?.detail ||
      `Could not update status for ${user.name}.`
  } finally {
    togglingUserId.value = null
  }
}

function openResetModal(user) {
  resetModalUser.value = user
  newPassword.value = ''
  resetError.value = ''
  resetSuccess.value = false
}

function closeResetModal() {
  resetModalUser.value = null
}

async function submitReset() {
  if (newPassword.value.length < 8) {
    resetError.value = 'Password must be at least 8 characters.'
    return
  }
  resetSubmitting.value = true
  resetError.value = ''
  try {
    await api.post(`/users/${resetModalUser.value.user_id}/reset-password`, {
      new_password: newPassword.value,
    })
    resetSuccess.value = true
  } catch (err) {
    resetError.value =
      err.response?.data?.detail || 'Could not reset the password.'
  } finally {
    resetSubmitting.value = false
  }
}

const filteredUsers = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  return users.value.filter((u) => {
    const matchesQuery =
      !q ||
      u.name?.toLowerCase().includes(q) ||
      u.email?.toLowerCase().includes(q) ||
      u.role?.toLowerCase().includes(q)
    const matchesStatus =
      statusFilter.value === 'all' || u.status === statusFilter.value
    return matchesQuery && matchesStatus
  })
})

function initials(name) {
  if (!name) return '?'
  return name
    .split(' ')
    .map((part) => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}
</script>

<template>
  <AppShell>
    <div class="mx-auto max-w-6xl">
      <!-- Header -->
      <div class="mb-6 flex items-end justify-between">
        <div>
          <h1 class="text-xl font-medium text-stone-900">Users</h1>
          <p class="mt-1 text-sm text-stone-500">
            {{ filteredUsers.length }} of {{ users.length }} people
            <span v-if="auth.user?.role !== 'super-admin'">on your farm</span>
          </p>
        </div>
      </div>

      <!-- Controls -->
      <div class="mb-4 flex flex-wrap items-center gap-3">
        <div class="relative flex-1 min-w-[220px]">
          <svg
            class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M21 21l-4.35-4.35M17 10a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by name, email, or role"
            class="w-full rounded-md border border-stone-300 bg-white py-2 pl-9 pr-3 text-sm text-stone-900 placeholder-stone-400 focus:border-emerald-600 focus:outline-none focus:ring-1 focus:ring-emerald-600"
          />
        </div>

        <div class="flex gap-1 rounded-md border border-stone-300 bg-white p-1">
          <button
            v-for="option in ['all', 'active', 'disabled']"
            :key="option"
            @click="statusFilter = option"
            class="rounded px-3 py-1 text-sm capitalize transition-colors"
            :class="
              statusFilter === option
                ? 'bg-emerald-600 text-white'
                : 'text-stone-600 hover:bg-stone-100'
            "
          >
            {{ option }}
          </button>
        </div>
      </div>

      <!-- Action error (status toggle failures) -->
      <div
        v-if="actionError"
        class="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
      >
        {{ actionError }}
        <button @click="actionError = ''" class="ml-2 font-medium underline">
          Dismiss
        </button>
      </div>

      <!-- Error state -->
      <div
        v-if="loadError"
        class="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
      >
        {{ loadError }}
        <button @click="loadUsers" class="ml-2 font-medium underline">
          Retry
        </button>
      </div>

      <!-- Table -->
      <div
        v-else
        class="overflow-hidden rounded-lg border border-stone-200 bg-white"
      >
        <table class="w-full text-left text-sm">
          <thead>
            <tr class="border-b border-stone-200 bg-stone-50 text-stone-500">
              <th class="px-4 py-3 font-medium">Name</th>
              <th class="px-4 py-3 font-medium">Email</th>
              <th class="px-4 py-3 font-medium">Role</th>
              <th class="px-4 py-3 font-medium">Farm ID</th>
              <th class="px-4 py-3 font-medium">Status</th>
              <th class="px-4 py-3 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            <!-- Loading skeleton -->
            <template v-if="isLoading">
              <tr v-for="n in 5" :key="n" class="border-b border-stone-100">
                <td class="px-4 py-3" colspan="6">
                  <div class="h-4 w-full animate-pulse rounded bg-stone-100" />
                </td>
              </tr>
            </template>

            <!-- Empty state -->
            <tr v-else-if="filteredUsers.length === 0">
              <td colspan="6" class="px-4 py-10 text-center text-stone-400">
                <template v-if="users.length === 0">
                  No users yet.
                </template>
                <template v-else>
                  No users match "{{ searchQuery }}".
                </template>
              </td>
            </tr>

            <!-- Rows -->
            <tr
              v-else
              v-for="user in filteredUsers"
              :key="user.user_id"
              class="border-b border-stone-100 last:border-0 hover:bg-stone-50"
            >
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div
                    class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-xs font-medium text-emerald-800"
                  >
                    {{ initials(user.name) }}
                  </div>
                  <span class="font-medium text-stone-900">{{ user.name }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-stone-600">{{ user.email }}</td>
              <td class="px-4 py-3">
                <span
                  class="inline-flex items-center rounded-full bg-stone-100 px-2.5 py-0.5 text-xs font-medium capitalize text-stone-700"
                >
                  {{ user.role }}
                </span>
              </td>
              <td class="px-4 py-3 font-mono text-xs text-stone-500">{{ user.farm_id }}</td>
              <td class="px-4 py-3">
                <span
                  class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium"
                  :class="
                    user.status === 'active'
                      ? 'bg-emerald-50 text-emerald-700'
                      : 'bg-stone-100 text-stone-500'
                  "
                >
                  <span
                    class="h-1.5 w-1.5 rounded-full"
                    :class="user.status === 'active' ? 'bg-emerald-500' : 'bg-stone-400'"
                  />
                  {{ user.status === 'active' ? 'Active' : 'Disabled' }}
                </span>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <button
                    @click="toggleStatus(user)"
                    :disabled="togglingUserId === user.user_id"
                    class="rounded-md border px-2.5 py-1 text-xs font-medium transition-colors disabled:opacity-50"
                    :class="
                      user.status === 'active'
                        ? 'border-stone-300 text-stone-600 hover:bg-stone-100'
                        : 'border-emerald-300 text-emerald-700 hover:bg-emerald-50'
                    "
                  >
                    {{ togglingUserId === user.user_id
                      ? '…'
                      : user.status === 'active' ? 'Disable' : 'Enable' }}
                  </button>
                  <button
                    @click="openResetModal(user)"
                    class="rounded-md border border-stone-300 px-2.5 py-1 text-xs font-medium text-stone-600 hover:bg-stone-100"
                  >
                    Reset password
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Reset password modal -->
      <div
        v-if="resetModalUser"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
        @click.self="closeResetModal"
      >
        <div class="w-full max-w-sm rounded-lg bg-white p-5 shadow-lg">
          <h2 class="text-base font-medium text-stone-900">
            Reset password
          </h2>
          <p class="mt-1 text-sm text-stone-500">
            Set a new password for {{ resetModalUser.name }}.
          </p>

          <template v-if="!resetSuccess">
            <input
              v-model="newPassword"
              type="password"
              placeholder="New password"
              autofocus
              class="mt-4 w-full rounded-md border border-stone-300 px-3 py-2 text-sm text-stone-900 placeholder-stone-400 focus:border-emerald-600 focus:outline-none focus:ring-1 focus:ring-emerald-600"
              @keyup.enter="submitReset"
            />
            <p v-if="resetError" class="mt-2 text-sm text-red-600">
              {{ resetError }}
            </p>
            <div class="mt-4 flex justify-end gap-2">
              <button
                @click="closeResetModal"
                class="rounded-md px-3 py-1.5 text-sm text-stone-600 hover:bg-stone-100"
              >
                Cancel
              </button>
              <button
                @click="submitReset"
                :disabled="resetSubmitting"
                class="rounded-md bg-emerald-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
              >
                {{ resetSubmitting ? 'Resetting…' : 'Reset password' }}
              </button>
            </div>
          </template>

          <template v-else>
            <p class="mt-4 rounded-md bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
              Password reset for {{ resetModalUser.name }}.
            </p>
            <div class="mt-4 flex justify-end">
              <button
                @click="closeResetModal"
                class="rounded-md bg-emerald-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-700"
              >
                Done
              </button>
            </div>
          </template>
        </div>
      </div>
    </div>
  </AppShell>
</template>
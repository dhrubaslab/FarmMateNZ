<script setup>
import { ref, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const mobileOpen = ref(false);

// Mueu click on the  - It's public Menu Navigation
const links = [
  { name: "dashboard", label: "Dashboard", icon: "grid" },
  { name: "farms", label: "Farm", icon: "farm" },
  { name: "paddocks", label: "Paddocks", icon: "map", roles: ['super-admin', "admin", "staff"] },
  { name: "users", label: "Users", icon: "user", roles: ["super-admin", "admin"] },
  { name: "invite", label: "Invite User", icon: "user" },
  { name: "profile", label: "My Profile", icon: "profile" },
  { name: "health", label: "System Health", icon: "health" },
];

const visibleLinks = computed(() =>
  links.filter((link) => !link.roles || link.roles.includes(auth.role))
);

// Arrow functions
const navigate = (name) => {
  mobileOpen.value = false;
  router.push({ name });
}
//ordinary functions
function logout() {
  auth.logout();
  router.push({ name: "login" });
}

function initials() {
  const email = auth.user?.email || "FM";
  return email.slice(0, 2).toUpperCase();
}
</script>

<template>
  <div class="min-h-screen bg-[#f4f8f3] text-slate-800">
    <aside class="fixed inset-y-0 left-0 z-40 hidden w-64 border-r border-green-100 bg-white lg:flex lg:flex-col">

      <!-- Logo -->
      <div class="px-6 py-6">
        <button class="flex items-center gap-3 text-left" @click="navigate('dashboard')">
          <div class="brand-mark">FM</div>
          <div>
            <div class="text-lg font-extrabold tracking-tight text-green-900">
              FarmMate NZ
            </div>
            <div class="text-[11px] font-medium uppercase tracking-[.16em] text-green-600">
              Farm management
            </div>
          </div>
        </button>
      </div>
      <nav class="flex-1 space-y-1 px-3">
        <!-- Click the button menu -->
        <button v-for="link in visibleLinks" :key="link.name" class="nav-item"
          :class="route.name === link.name ? 'nav-item-active' : ''" @click="navigate(link.name)">
          <!-- Nav icon -->
          <span class="nav-icon" aria-hidden="true">
            <svg v-if="link.icon === 'grid'" viewBox="0 0 24 24">
              <path d="M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z" />
            </svg>
            <svg v-else-if="link.icon === 'farm'" viewBox="0 0 24 24">
              <path d="M3 20h18M5 20v-8l7-5 7 5v8M9 20v-5h6v5M7 8V5h3v1.5" />
            </svg>
            <svg v-else-if="link.icon === 'map'" viewBox="0 0 24 24">
              <path d="m9 18-5 3V6l5-3 6 3 5-3v15l-5 3-6-3Z" />
              <path d="M9 3v15M15 6v15" />
            </svg>
            <svg v-else-if="link.icon === 'cow'" viewBox="0 0 24 24">
              <path d="M5 9.5C5 6.5 8 5 12 5s7 1.5 7 4.5v5c0 3-2.4 5.5-7 5.5s-7-2.5-7-5.5v-5Z" />
              <path d="M5 10 2.5 8M19 10 21.5 8M8 13h.01M16 13h.01M9 16c2 1 4 1 6 0" />
            </svg>
            <svg v-else-if="link.icon === 'task'" viewBox="0 0 24 24">
              <path d="M8 5h11v15H5V5h3M8 3v4M12 9h4M8 13h8M8 17h5" />
            </svg>
            <svg v-else-if="link.icon === 'cloud'" viewBox="0 0 24 24">
              <path d="M7 18h11a4 4 0 0 0 .5-8A6 6 0 0 0 7 8a5 5 0 0 0 0 10Z" />
              <path d="M12 12v6M9.5 15.5 12 18l2.5-2.5" />
            </svg>
            <svg v-else-if="link.icon === 'leaf'" viewBox="0 0 24 24">
              <path d="M20 4C11 4 5 8 5 15c0 3 2 5 5 5 7 0 10-7 10-16Z" />
              <path d="M4 21c3-5 7-8 12-10" />
            </svg>
            <svg v-else-if="link.icon === 'user'" viewBox="0 0 24 24">
              <path d="M20 21a8 8 0 0 0-16 0M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z" />
            </svg>
            <svg v-else-if="link.icon === 'profile'" viewBox="0 0 24 24">
              <circle cx="12" cy="8" r="3" />
              <path d="M5 20a7 7 0 0 1 14 0" />
            </svg>
            <svg v-else-if="link.icon === 'health'" viewBox="0 0 24 24">
              <path d="M4 12h4l2-5 4 10 2-5h4" />
              <path d="M4 4h16v16H4z" />
            </svg>
            <svg v-else viewBox="0 0 24 24">
              <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4" />
            </svg>
          </span>
          <span>{{ link.label }}</span>
        </button>

      </nav>


      <!-- Left FM photo -->
      <div class="border-t border-green-100 p-4">
        <div class="flex items-center gap-3">
          <div class="avatar">
            {{ initials() }}
          </div>
          <div class="min-w-0 flex-1">
            <div class="truncate text-sm font-semibold text-slate-800">
              {{ auth.user?.email }}
            </div>
            <div class="text-xs text-green-700">
              {{ auth.role || "Farmer" }}
            </div>
          </div>
          <button class="logout-icon" title="Log out" aria-label="Log out" @click="logout">
            ↗
          </button>
        </div>
      </div>
    </aside>

    <div class="lg:pl-64">
      <header class="sticky top-0 z-30 border-b border-green-100/80 bg-white/90 px-4 py-3 backdrop-blur lg:hidden">
        <div class="flex items-center justify-between">

          <button class="flex items-center gap-2" @click="navigate('dashboard')">
            <div class="brand-mark small">FM</div>
            <span class="font-extrabold text-green-900">
              FarmMate NZ
            </span>
          </button>

          <button class="menu-button" @click="mobileOpen = !mobileOpen">
            {{ mobileOpen ? "×" : "☰" }}
          </button>
        </div>

        <nav v-if="mobileOpen" class="mt-3 grid gap-1 border-t border-green-100 pt-3">
          <button v-for="link in visibleLinks" :key="link.name" class="mobile-nav-item"
            :class="route.name === link.name ? 'active' : ''" @click="navigate(link.name)">
            {{ link.label }}
          </button>
          <button class="mobile-nav-item text-red-600" @click="logout">
            Log out
          </button>
        </nav>


      </header>
      <main class="min-h-screen px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
        <slot />
      </main>

    </div>
  </div>
</template>

<style scoped>
/* Brand logo */
.brand-mark {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 13px;
  background: linear-gradient(135deg, #1f6b3a, #75b85f);
  color: white;
  font-weight: 900;
  box-shadow: 0 8px 20px rgba(38, 110, 58, 0.2);
}

/* Smaller logo for mobile header */
.brand-mark.small {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  font-size: 0.8rem;
}

/* Desktop navigation item */
.nav-item {
  display: flex;
  width: 100%;
  align-items: center;
  gap: 0.75rem;
  border-radius: 12px;
  padding: 0.72rem 0.85rem;
  text-align: left;
  font-size: 0.88rem;
  font-weight: 600;
  color: #64756a;
  transition: 0.2s;
}

/* Navigation hover state */
.nav-item:hover {
  background: #f2f8f1;
  color: #245d35;
}

/* Active navigation item */
.nav-item-active {
  background: #e9f5e7;
  color: #216236;
  box-shadow: inset 3px 0 #4f9d69;
}

/* Navigation icon container */
.nav-icon {
  display: grid;
  place-items: center;
  width: 20px;
  height: 20px;
}

/* Navigation SVG icon */
.nav-icon svg {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.7;
  stroke-linecap: round;
  stroke-linejoin: round;
}

/* User avatar */
.avatar {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #dfeedd;
  color: #28613c;
  font-size: 0.75rem;
  font-weight: 800;
}

/* Logout and mobile menu buttons */
.logout-icon,
.menu-button {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 9px;
  color: #718079;
}

/* Logout and menu hover state */
.logout-icon:hover,
.menu-button:hover {
  background: #f0f6ef;
  color: #245d35;
}

/* Mobile navigation item */
.mobile-nav-item {
  text-align: left;
  border-radius: 10px;
  padding: 0.7rem 0.8rem;
  font-size: 0.88rem;
  font-weight: 600;
  color: #64756a;
}

/* Active mobile navigation item */
.mobile-nav-item.active {
  background: #e9f5e7;
  color: #216236;
}
</style>
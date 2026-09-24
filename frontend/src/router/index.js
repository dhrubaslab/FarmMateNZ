import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

import Login from "../views/Login.vue";
import Dashboard from "../views/Dashboard.vue";
import UsersView from "../views/UsersView.vue";

// New one- added pages during the holidays
import Farms from "../views/Farms.vue";
import CreateFarm from "../views/CreateFarm.vue";
import Paddocks from "../views/Paddocks.vue";
import CreatePaddock from "../views/CreatePaddock.vue";
import InviteUser from "../views/InviteUser.vue";
import ResetPassword from "../views/ResetPassword.vue";
import Profile from "../views/Profile.vue";
import Health from "../views/Health.vue";
import AuditLogs from "../views/AuditLogs.vue";

const routes = [
  // Temporary development mode:
  // Login is still available, but it is not required 
  // jsut for test
  // { path: "/", redirect: "/dashboard" },
  { path: "/", redirect: "/login" },
  { path: "/login", name: "login", component: Login },
  {
    path: "/dashboard",
    name: "dashboard",
    component: Dashboard,
    meta: { requiresAuth: true },
  },
  // Added pages during the holidays
  { path: "/farms", name: "farms", component: Farms, meta: { requiresAuth: true } },
  { path: "/farms/new", name: "create-farm", component: CreateFarm, meta: { requiresAuth: true, roles: ["super-admin"] } },
  { path: "/invite", name: "invite", component: InviteUser, meta: { requiresAuth: true } },
  { path: "/reset-password", name: "reset-password", component: ResetPassword, meta: { requiresAuth: true } },
  { path: "/profile", name: "profile", component: Profile, meta: { requiresAuth: true } },
  { path: "/health", name: "health", component: Health, meta: { requiresAuth: true } },
  { path: "/audit-logs", name: "audit-logs", component: AuditLogs, meta: { requiresAuth: true, roles: ["super-admin", "admin"] } },
  { path: "/users", name: "users", component: UsersView, meta: { requiresAuth: true, roles: ['super-admin', 'admin'] } },
  { path: "/paddocks", name: "paddocks", component: Paddocks, meta: { requiresAuth: true, roles: ['super-admin', 'admin','staff'] } },
  { path: "/paddocks/new", name: "create-paddock", component: CreatePaddock, meta: { requiresAuth: true, roles: ["super-admin", "admin"] } },
  { path: "/:pathMatch(.*)*", redirect: "/dashboard" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const auth = useAuthStore();

  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { name: "login" };
  }
  if ((to.name === "login" || to.name === 'register') && auth.isLoggedIn) {
    return { name: "dashboard" };
  }
});

export default router;
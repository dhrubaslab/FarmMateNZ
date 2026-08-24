import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

import Login from "../views/Login.vue";
import Dashboard from "../views/Dashboard.vue";

import Farms from "../views/Farms.vue";

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", name: "login", component: Login },
  {
    path: "/dashboard",
    name: "dashboard",
    component: Dashboard,
    meta: { requiresAuth: true },
  },
  // Added pages during the holidays
  {
    path: "/farms",
    name: "farms",
    component: Farms,
    meta: { requiresAuth: true }
  },
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
  if (to.name === "login" && auth.isLoggedIn) {
    return { name: "dashboard" };
  }
});

export default router;
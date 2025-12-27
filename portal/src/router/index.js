import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from "../stores/user"
import { apiBase } from '@/services/api'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
    },
    {
      path: '/historic-site/:id',
      name: 'historic-site',
      component: () => import('../views/HistoricSite.vue' ),
    },
    {
      path: '/ordered-sites-list',
      name: 'ordered-sites-list',
      component: () => import('../views/OrderedSitesList.vue'),
    },
    {
      path: '/login-success',
      name: 'login-success',
      component: () => import('../views/AuthCallbackView.vue'),
    },
    {
      path: '/perfil',
      component: () => import('../views/ProfileView.vue'),
    },
    {
      path: '/favorites-sites',
      name: 'favorites-sites',
      component: () => import('../views/FavoritesSites.vue'),
    },
    
    {
      path: "/auth/callback",
      name: "auth-callback",
      component: () => import("../views/AuthCallbackView.vue"),
    },
    {
    path: "/login-error",
    component: () => import("@/views/LoginErrorView.vue")
    },
  ],
})

router.beforeEach(async (to) => {
  const store = useUserStore()

  if (store.user === null) {
    await store.loadUser()
  }

  const protectedRoutes = ["/mis-resenas", "/favoritos", "/perfil"]

  if (protectedRoutes.includes(to.path) && !store.user) {
    localStorage.setItem("redirectAfterLogin", to.fullPath)
    window.location.href = `${apiBase}/api/auth/google/login?next=${encodeURIComponent(to.fullPath)}`
    return false
  }
})

export default router

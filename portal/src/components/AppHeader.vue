<script setup>
import { RouterLink } from 'vue-router'
import { useUserStore } from "../stores/user"
import { apiBase } from '../services/api'
import { defineAsyncComponent } from 'vue';

const SearchSection = defineAsyncComponent(
  () => import('@/components/SearchSection.vue')
)
const GoogleSignInButton = defineAsyncComponent(
  () => import('@/components/GoogleSignInButton.vue'),
);

const store = useUserStore()
store.loadUser()

function loginWithGoogle() {
  const next = encodeURIComponent(window.location.pathname)
  window.location.href = `${apiBase}/api/auth/google/login?next=${next}`
}
</script>

<template>
    <header class="navbar">
        <div class="container-fluid position-relative d-flex flex-wrap align-items-center justify-content-between px-2 px-md-4">
            
            <div class="d-flex align-items-center gap-2 gap-md-3 order-1">
                <img src="@/assets/favicon.png" class="logo" alt="Logo" />
                
                <nav class="d-none d-md-flex">
                    <RouterLink to="/">Home</RouterLink>
                    <RouterLink to="/ordered-sites-list?order_by=rating-5-1">Sitios</RouterLink>
                </nav>

                <nav class="d-flex d-md-none gap-2 mobile-nav-links">
                    <RouterLink to="/">Home</RouterLink>
                    <RouterLink to="/ordered-sites-list?order_by=rating-5-1">Sitios</RouterLink>
                </nav>
            </div>

            <div class="d-flex align-items-center order-2 order-md-3 ms-auto">
                <GoogleSignInButton @login="loginWithGoogle" />
            </div>

            <div class="search-container order-3 order-md-2 mt-2 mt-md-0 w-100 w-md-auto px-0 px-md-4">
                <SearchSection/>
            </div>

        </div>
    </header>
</template>

<style scoped>
.navbar {
    height: auto !important; 
    min-height: 76px;
    position: fixed; 
    top: 0; left: 0; right: 0;
    background: var(--color-primario);
    padding: 8px 0; 
    z-index: 999;
}

.logo {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    background: white;
    padding: 2px;
    flex-shrink: 0;
}

.mobile-nav-links a {
    font-size: 14px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.9);
    text-decoration: none;
    padding: 4px 6px;
    border-radius: 4px;
    transition: background 0.2s;
    white-space: nowrap;
}

.mobile-nav-links a.router-link-exact-active {
    color: #fff;
    text-decoration: underline;
    text-decoration-thickness: 2px;
    text-underline-offset: 4px;
}

.search-container {
    max-width: 100%;
}

@media (min-width: 768px) {
    .navbar {
        padding: 0;
        height: 76px !important; 
    }

    .logo {
        width: 48px;
        height: 48px;
    }

    .search-container {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        
        width: 100%;
        max-width: 600px; 
        margin-top: 0 !important;
    }
}
</style>
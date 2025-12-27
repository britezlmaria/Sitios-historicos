
<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from "../stores/user";
import { useRouter } from 'vue-router'; 
import SiteCard from '@/components/SiteCard.vue';
import api from '@/services/api';

const store = useUserStore();
const router = useRouter();


const favorites = ref([]);
const loading = ref(true);

async function fetchFavorites() {
  loading.value = true;
  try {
    const response = await api.get('/me/favorites'); 
    if (!response.ok) throw new Error('Failed to fetch favorites');
    favorites.value = response.data ?? []; 
  } catch (error) {
    console.error('Error fetching favorites:', error);
    favorites.value = [];
  } finally {
    loading.value = false;
  }
}

const handleViewDetail = (siteId) => {
  router.push({ name: 'historic-site', params: { id: siteId } });
};

onMounted(() => {
  if (store.user) {
    fetchFavorites();
  } else {
    loading.value = false;
  }
});

function loginWithGoogle() {
  const next = encodeURIComponent(window.location.pathname);
  window.location.href = `/api/auth/google/login?next=${next}`;
}
</script>

<template>
  <div class="container py-4">
    <h1>Mis favoritos</h1>

    <div v-if="!store.user">
      <p>Inicia sesión para ver tus sitios favoritos.</p>
      <button @click="loginWithGoogle" class="btn btn-primary">Continuar con Google</button>
    </div>

    <div v-else>
      <div v-if="loading">
        <p>Cargando tus favoritos...</p>
      </div>
      
      <div v-else-if="!favorites.length">
        <p>Aún no has guardado ningún sitio como favorito.</p>
      </div>

      <div v-else class="row">
        <div v-for="site in favorites" :key="site.id" class="col-md-4 mb-4">
          <SiteCard 
                :site="site" 
                @view-detail="handleViewDetail" 
                />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.card-body {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}
.card-body .btn {
  margin-top: auto;
}
</style>

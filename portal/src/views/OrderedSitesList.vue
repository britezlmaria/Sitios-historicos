<script setup>
import { ref, onMounted, watch, defineAsyncComponent, Suspense } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '@/services/api';
import TitleSkeleton from '@/components/TitleSkeleton.vue';
import SiteCardSkeleton from '@/components/SiteCardSkeleton.vue';

const SiteCard = defineAsyncComponent(
  () => import('@/components/SiteCard.vue')
)

const route = useRoute();
const router = useRouter();
const sites = ref([]);
const loading = ref(true);
const page = ref(1);

const loadSites = async () => {
  loading.value = true;

  try {
    const endpoint = '/sites'
    const params = {
      ...route.query,
      page: page.value,
      per_page: 20,
    };

    delete params.title;
    delete params.url;

    const response = await api.get(endpoint, { params });
    sites.value = response.data.data ?? response.data ?? [];

  } catch (error) {
    console.error('Error:', error);
    sites.value = [];
  } finally {
    loading.value = false;
  }
};

watch(() => route.query, () => {
  page.value = 1;
  loadSites();
});

onMounted(() => {
  loadSites();
});

const handleViewDetail = (siteId) => {
  router.push({ name: 'historic-site', params: { id: siteId } });
};
</script>

<template>
  <div class="container py-4">
    <TitleSkeleton 
    v-if="loading"
    :width="'300px'" 
    :height="'32px'" 
    />
    <h1 v-else>{{ route.query.title || 'Listado de Sitios' }}</h1>
    <div class="row">
      <template v-if="loading">
        <div class="col-md-4 mb-4" v-for="n in 6" :key="n">
          <SiteCardSkeleton />
        </div>
      </template>
      <template v-else>
        <div v-if="!sites.length" class="col-12 alert alert-info">
          <p>No se encontraron sitios.</p>
        </div>
        <div v-for="site in sites" :key="site.id" class="col-md-4 mb-4">
            <SiteCard 
            :site="site" 
            @view-detail="handleViewDetail" 
            />
        </div>
      </template>
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
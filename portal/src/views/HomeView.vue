<script setup>
import { defineAsyncComponent, Suspense } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from "../stores/user"
import SiteCarouselSkeleton from '@/components/siteCarouselSkeleton.vue';

const SiteCarousel = defineAsyncComponent(
  () => import('@/components/SiteCarousel.vue'),
);
const store = useUserStore()
const router = useRouter();

const handleViewDetail = async (siteId) => router.push({name: 'historic-site',params: { id: siteId }});

const handleViewAllFavorites = () => router.push({ name: 'ordered-sites-list', query: { only_favorites: 'true', title: 'Mis Favoritos' } });
const handleViewAllRating = () => router.push({ name: 'ordered-sites-list', query: { order_by: 'rating-5-1', title: 'Mejor Puntuados' } });
const handleViewAllRecentlyAdded = () => router.push({ name: 'ordered-sites-list', query: { order_by: 'latest', title: 'Agregados Recientemente' } });
const handleViewAllMostVisited = () => router.push({ name: 'ordered-sites-list', query: { order_by: 'most-visited', title: 'Más Visitados' } });
</script>

<template>
  <div>
    <div v-if="store.user">
      <Suspense>
        <template #default>
          <SiteCarousel
          title="Favoritos"
          fetch-url="/me/favorites?per_page=10"
          @view-detail="handleViewDetail"
          @view-all="handleViewAllFavorites"
          />
        </template>
        <template #fallback>
          <SiteCarouselSkeleton title="Favoritos" />
        </template>
      </Suspense>
    </div>
    <Suspense>
      <template #default>
        <SiteCarousel 
        title="Mejor Puntuados" 
        fetch-url="/sites?order_by=rating-5-1&per_page=10"
        @view-detail="handleViewDetail"
        @view-all="handleViewAllRating"
        />
      </template>
      <template #fallback>
        <SiteCarouselSkeleton title="Mejor Puntuados" />
      </template>
    </Suspense>
    <Suspense>
      <template #default>
        <SiteCarousel 
        title="Recientemente Agregados" 
        fetch-url="/sites?order_by=latest&per_page=10" 
        @view-detail="handleViewDetail" 
        @view-all="handleViewAllRecentlyAdded"
        />
      </template>
      <template #fallback>
        <SiteCarouselSkeleton title="Recientemente Agregados" />
      </template>
    </Suspense>
    <Suspense>  
      <template #default>
        <SiteCarousel 
        title="Más Visitados" 
        fetch-url="/sites?order_by=most-visited&per_page=10" 
        @view-detail="handleViewDetail" 
        @view-all="handleViewAllMostVisited"
        />
      </template>
      <template #fallback>
        <SiteCarouselSkeleton title="Más Visitados" />
      </template>
    </Suspense>
  </div>
</template>

<style></style>

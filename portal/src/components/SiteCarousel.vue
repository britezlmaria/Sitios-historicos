<script setup>
    import { onMounted, ref } from 'vue';
    import { Swiper, SwiperSlide } from 'swiper/vue';
    import 'swiper/css';
    import 'swiper/css/navigation';
    import { Navigation, Autoplay } from 'swiper/modules';
    import SiteCard from './SiteCard.vue';
    import api from '@/services/api';

    const props = defineProps({
      title: {
          type: String,
          required: true
      },
      fetchUrl: {
          type: String,
          required: true
      },
    });

    const emit = defineEmits(['view-detail', 'view-all']);
    const sites = ref([]);

    try {
      const response = await api.get(props.fetchUrl);
      sites.value = response.data.data ?? response.data ?? [];
    } catch (error) {
      console.error(`Error fetching ${props.title}:`, error);
      sites.value = [];
    }

    const onViewDetail = (siteId) => emit('view-detail', siteId);
    const onViewAll = () => emit('view-all');
</script>
<template>
  <div class="container py-3">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="mb-0">{{ title }}</h2>
      <button class="btn btn-primary" @click="onViewAll">
        Ver Todos
      </button>
    </div>

    <p class="text-center text-muted" v-if="!sites.length">
      No hay sitios para mostrar.
    </p>

    <Swiper
      v-else
      :modules="[Navigation, Autoplay]"
      :centeredSlides="true"
      :loop="sites.length >= 3"
      :autoplay="{
        delay: 3000,
        disableOnInteraction: false,
        pauseOnMouseEnter: true
      }"
      navigation
      class="mySwiper"
      :breakpoints="{
        // phone
        320: {
          slidesPerView: 1,
          spaceBetween: 10
        },
        // desktop/tablet
        768: {
          slidesPerView: 3,
          spaceBetween: 30
        }
      }"
    >
      <SwiperSlide v-for="site in sites" :key="site.id">
        <SiteCard 
          :site="site" 
          @view-detail="onViewDetail" 
        />
      </SwiperSlide>
    </Swiper>
  </div>
</template>

<style>
  .mySwiper { 
    padding-bottom: 40px; 
    --swiper-navigation-color: var(--color-acento);
    --swiper-theme-color: var(--color-acento);
  }

  .swiper-slide {
    opacity: 0.5;
    transform: scale(0.85);
    transition: transform 0.3s ease, opacity 0.3s ease;
    height: auto;
    display: flex; 
    align-items: stretch;
  }
  
  .swiper-slide-active,
  .swiper-slide-duplicate-active {
    opacity: 1 !important;
    transform: scale(1) !important;
  }
</style>
<script setup>
import { Swiper, SwiperSlide } from 'swiper/vue';
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';
import { Navigation, Autoplay, Pagination } from 'swiper/modules';

defineProps({
    images: {
        type: Array,
        required: true,
        default: () => []
    },
    siteName: {
        type: String,
        required: true
    }
});
</script>

<template>
    <div class="carousel-images-container">
        <div v-if="images.length === 0" class="slide-wrapper">
          <img src="../assets/default_site_image.png" class="carousel-image" :alt="`Imagen por defecto para ${siteName}`" />
        </div>
        <Swiper
        v-else
        :modules="[Navigation, Autoplay, Pagination]"
        :centeredSlides="true"
        :loop="images.length >= 2"
        :autoplay="{
            delay: 3000,
            disableOnInteraction: false,
            pauseOnMouseEnter: true
        }"
        navigation
        :pagination="{ 
            clickable: true,
            dynamicBullets: false
        }"
        class="site-images-carousel"
        :breakpoints="{
            // phone
            320: {slidesPerView: 1, spaceBetween: 10},
            // desktop/tablet
            768: {slidesPerView: 1, spaceBetween: 30}
        }"
        >
        <SwiperSlide v-for="image in images" :key="image.id">
            <div class="slide-wrapper">
                <img :src="image.image" :alt="image.description || siteName" class="carousel-image" >  
            </div>  
        </SwiperSlide>
        </Swiper>
    </div>
</template>

<style scoped>
 .carousel-images-container {
  margin: 2rem 0;
  position: relative;
}

.site-images-carousel {
  --swiper-theme-color: var(--color-acento);
  padding-bottom: 50px;
}

.slide-wrapper {
  height: 500px; 
  width: 100%;
  border-radius: 20px;
  overflow: hidden;
  transform: translateZ(0);
  -webkit-mask-image: -webkit-radial-gradient(white, black);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.carousel-image {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 0;
  transition: transform 0.4s ease;
  will-change: transform;
}

.swiper-slide-active .carousel-image {
  transform: scale(1.05);
}

:deep(.swiper-button-prev),
:deep(.swiper-button-next) {
    background-color: transparent; 
    color: rgba(255, 255, 255, 0.7);
    width: 60px; 
    height: 100%;
    max-height: 60px;
    
    border-radius: 0;
    border: none;
    box-shadow: none;
    filter: drop-shadow(0 1px 2px rgba(0,0,0,0.3)); 
    
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 20; 
    top: calc(50% - 30px);
}

:deep(.swiper-button-prev) {
    left: 5px; 
}
:deep(.swiper-button-next) {
    right: 5px;
}

:deep(.swiper-button-prev:hover),
:deep(.swiper-button-next:hover) {
    background-color: transparent; 
    backdrop-filter: none;
    transform: scale(1.15);
    color: white;
}


:deep(.swiper-button-prev::after),
:deep(.swiper-button-next::after) {
    font-size: 28px;
    font-weight: bold;
}


:deep(.swiper-pagination) {
    bottom: 0px !important;
    display: flex;
    justify-content: center;
    align-items: center;
    padding-bottom: 15px;
    z-index: 20;
    flex-wrap: wrap;
    width: 100% !important;
}

:deep(.swiper-pagination-bullet) {
    width: 8px;
    height: 8px;
    background-color: rgba(129, 129, 129, 0.5);
    opacity: 1;
    border-radius: 50%;
    margin: 0 6px !important;
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

:deep(.swiper-pagination-bullet-active) {
    width: 24px; 
    border-radius: 10px;
    background-color: var(--swiper-theme-color);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

@media (max-width: 768px) {
  .carousel-image {
    min-height: 300px;
    max-height: 60vh;
    border-radius: 12px;
  }
  :deep(.swiper-button-prev),
  :deep(.swiper-button-next) {
      width: 40px;
      height: 40px;
  }
    
  :deep(.swiper-button-prev) { left: 10px; }
  :deep(.swiper-button-next) { right: 10px; }
    
  :deep(.swiper-button-prev::after),
  :deep(.swiper-button-next::after) {
      font-size: 20px;
  }
}
</style>
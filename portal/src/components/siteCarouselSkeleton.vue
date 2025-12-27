<script setup>
// este componente si se carga de forma asincrona ya que es el componente a mostrar en la carga
import SiteCardSkeleton from './SiteCardSkeleton.vue';

defineProps({
  title: {
    type: String,
    required: true
  }
});
</script>

<template>
  <div class="container py-3">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="mb-0">{{ title }}</h2>
      <div class="skeleton-btn-top"></div>
    </div>

    <div class="row">
      
      <div class="col-12 col-md-4">
        <SiteCardSkeleton />
      </div>

      <div class="col-md-4 d-none d-md-block" v-for="n in 2" :key="n">
        <SiteCardSkeleton />
      </div>
      
    </div>
  </div>
</template>

<style scoped>
.skeleton-btn-top {
  width: 100px;
  height: 38px;
  background-color: #e0e0e0;
  border-radius: 4px;
  animation: pulse 1.5s infinite ease-in-out;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
</style>
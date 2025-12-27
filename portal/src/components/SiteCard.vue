<script setup>
import Stars from './Stars.vue';
import VisitTracker from './VisitTracker.vue';


defineProps({
  site: {
    type: Object,
    required: true
  }
});


const emit = defineEmits(['view-detail']);

const onViewDetail = (siteId) => {
  emit('view-detail', siteId);
};
</script>

<template>
  <div class="card site-card">
    <div class="image-wrapper">
      <img v-if="site.cover_image && site.cover_image.url" :src="site.cover_image.url" class="image-cover">
      <img v-else src="../assets/default_site_image.png" class="image-cover placeholder">
    </div>
    <div class="card-body text-center">
      <div class="text-block">
        <h5>{{ site.name }}</h5>
        <p class="text-muted">{{ site.city }}, {{ site.province }}</p>
      </div>
      <p>
        <Stars :rating="site.rating || 0" />
      </p>
      <VisitTracker 
      :visits="site.visit_count" 
      />
      <button class="btn btn-primary" @click="onViewDetail(site.id)">
        Ver Detalle
      </button>
    </div>
  </div>
</template>

<style scoped>
.site-card {
  display: flex;
  flex-direction: column;
  height: 420px; 
  width: 100%;  
  border-radius: 12px;
  overflow: hidden;
  background: white;
}

.image-wrapper {
  aspect-ratio: 16/9;
  width: 100%;
  overflow: hidden;
  border-radius: 12px 12px 0 0; 
}

.image-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  display: block;
}

.placeholder {
  background-image: url('../assets/default_site_image.png');
  background-size: cover;
  background-position: center;
}

.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  text-align: center;
  padding: 1rem;
}

.text-block {
  min-height: 4.5rem;
}

.card-body .btn {
  margin-top: auto;
  width: 100%;
}

@media (min-width: 768px) {
  .site-card {
    height: 460px;
  }
}
</style>
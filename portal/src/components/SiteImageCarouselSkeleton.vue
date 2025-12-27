<script setup>
</script>

<template>
  <div class="skeleton-carousel-container">
    <div class="skeleton-image"></div>
    
    <div class="skeleton-pagination">
        <div class="skeleton-dot"></div>
        <div class="skeleton-dot"></div>
        <div class="skeleton-dot"></div>
    </div>
  </div>
</template>

<style scoped>
.skeleton-carousel-container {
  margin: 2rem 0;
  position: relative;
  padding-bottom: 50px; 
}

.skeleton-image {
  width: 100%;
  height: 500px;
  background-color: #e0e0e0;
  border-radius: 20px;
  animation: pulse 1.5s infinite ease-in-out;
}

.skeleton-pagination {
  position: absolute;
  bottom: 15px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  gap: 12px;
}

.skeleton-dot {
  width: 8px;
  height: 8px;
  background-color: #e0e0e0;
  border-radius: 50%;
  animation: pulse 1.5s infinite ease-in-out;
  animation-delay: 0.2s;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

@media (max-width: 768px) {
  .skeleton-image {
    height: 300px;
    border-radius: 12px;
  }
}
</style>
<script setup>
defineProps({
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: String,
    default: '20px'
  },
  borderRadius: {
    type: String,
    default: '8px'
  }
});
</script>

<template>
  <div 
    class="title-skeleton mb-4" 
    :style="{ width: width, height: height, borderRadius: borderRadius }"
  ></div>
</template>

<style scoped>
.title-skeleton {
  background-color: #e0e0e0;
  animation: pulse 1.5s infinite ease-in-out;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
</style>
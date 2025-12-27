<script setup>
defineProps({
  visits: {
    type: Array,
    required: true
  }
});

const formatVisits = (visits) => {
  if (!visits) return '0 visitas';
  
  if (visits < 1000) {
    return `${visits} visitas`;
  }
  
  if (visits < 1000000) {
    return `${parseFloat((visits / 1000).toFixed(1))}K visitas`;
  }
  
  return `${parseFloat((visits / 1000000).toFixed(1))}M visitas`;
};
</script>

<template>
    <h6>{{ formatVisits(visits) }}</h6>
</template>

<style scoped>
h6 {
  color: var(--color-texto); 
}
</style>
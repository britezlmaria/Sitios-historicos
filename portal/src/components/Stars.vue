<script setup>
defineProps({
  rating: {
    type: Number,
    default: 0
  },
  size: {
    type: Number,
    default: 24
  }
});
</script>

<template>
  <span class="star-rating" :style="{ fontSize: size + 'px' }">
    <template v-for="index in 5" :key="index">
      
      <font-awesome-icon 
        v-if="index <= rating" 
        :icon="['fas', 'star']" 
      />
      
      <font-awesome-icon 
        v-else-if="rating > (index - 1) && rating < index"
        :icon="['fas', 'star-half-stroke']" 
      />
      
      <font-awesome-icon 
        v-else 
        :icon="['far', 'star']" 
      />

    </template>
  </span>
</template>

<style scoped>
  .star-rating {
    color: #ffc107;
  }
</style>
<script setup>
defineProps({
  chips: {
    type: Array,
    required: true,
    default: () => []
  }
});

const emit = defineEmits(['click-chip']);

const onChipClick = (chip) => {
  emit('click-chip', chip);
};
</script>

<template>
  <div class="chips-container d-flex flex-wrap gap-2">
    <span 
      v-for="(chip, index) in chips" 
      :key="chip" 
      class="badge rounded-pill chip"
      @click="onChipClick(chip)"
    >
      {{ chip }}
    </span>
  </div>
</template>

<style scoped>
.chip {
  background-color: #f8f9fa;
  color: #495057;    
  border: 1px solid #dee2e6; 
  font-weight: 500;
  font-size: 0.85rem;
  padding: 0.5em 1em;       
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  user-select: none;
}

.chip:hover {
  background-color: var(--color-acento, #0d6efd); 
  color: white;
  border-color: var(--color-acento, #0d6efd);
  transform: translateY(-1px); 
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chip:active {
  transform: translateY(0);
}
</style>
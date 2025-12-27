<script setup>
    const props = defineProps({
        title: {
            type: String,
            required: true
        },
        placeholder: {
            type: String,
            required: true
        },
        modelValue: {
            type: String,
            required: true,
        }
    }); 

    const emit = defineEmits(['update:modelValue', 'enter']);
    const onInput = (event) => emit('update:modelValue', event.target.value);
    const onEnter = () => emit('enter');
</script>

<template>
    <div class="search-input-group d-none d-md-flex">
        <label>{{ title }}</label>
        <input 
        :value="modelValue" 
        :placeholder="placeholder" 
        @input="onInput"
        @enter="onEnter"/>
    </div>
</template>

<style scoped>
.search-input-group {
  flex: 1;
  padding: 0 16px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  cursor: pointer;
}
.search-input-group label {
  font-size: 12px;
  font-weight: 800;
  margin: 0;
  color: #333;
}
.search-input-group input {
  border: none;
  outline: none;
  font-size: 14px;
  color: #666;
  width: 100%;
  background: transparent;
}
</style>
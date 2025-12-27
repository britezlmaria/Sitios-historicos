<script setup>
import { computed } from 'vue';

const props = defineProps({
    modelValue: {
        type: Boolean,
        required: true,
        default: false
    },
    label: {
        type: String,
        required: true
    },
    id: {
        type: String,
        required: true
    },
    title: {
        type: String,
        default: ''
    }
});

const emit = defineEmits(['update:modelValue']);

const isChecked = computed({
    get() {
        return props.modelValue;
    },
    set(val) {
        emit('update:modelValue', val);
    }
});
</script>

<template>
    <div class="form-check form-switch mb-0 d-flex align-items-center" :title="title">
        <input 
            class="form-check-input me-2" 
            type="checkbox" 
            :id="id" 
            v-model="isChecked"
            role="switch"
        >
        <label class="form-check-label small text-nowrap cursor-pointer" :for="id">
            {{ label }}
        </label>
    </div>
</template>

<style scoped>
.cursor-pointer {
    cursor: pointer;
}
.form-check-input {
    margin-top: 0; 
}
</style>
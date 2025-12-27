<script setup>
import { computed } from 'vue';

const props = defineProps({
    title: {
        type: String,
        required: false
    },
    options: {
        type: Array,
        required: true,
        default: () => []
    },
    modelValue: {
        type: Array,
        required: true,
        default: () => []
    },
    itemText: {
        type: String,
        default: 'name'
    },
    itemValue: {
        type: String,
        default: 'name'
    }
});

const emit = defineEmits(['update:modelValue']);

const selectedValues = computed({
    get: () => props.modelValue,
    set: (val) => emit('update:modelValue', val)
});
</script>

<template>
    <div>
        <label v-if="title" class="form-label fw-bold small text-muted mb-1">{{ title }}</label>
        <div class="tags-wrapper">
            <div 
                v-for="(opt, index) in options" 
                :key="opt[itemValue] || index" 
                class="form-check form-check-inline"
            >
                <input 
                    class="form-check-input" 
                    type="checkbox" 
                    :value="opt[itemValue]" 
                    v-model="selectedValues" 
                    :id="`tag-check-${opt[itemValue]}`"
                >
                <label class="form-check-label" :for="`tag-check-${opt[itemValue]}`">
                    {{ opt[itemText] }}
                </label>
            </div>
        </div>
    </div>
</template>

<style scoped>
.tags-wrapper {
    max-height: 80px;
    overflow-y: auto;
    scrollbar-width: thin;
}
</style>
<script setup>

const props = defineProps(
    {
        title: {
        type: String,
        required: true
        },
        options: {
        type: Array,
        required: true,
        default: () => []
        },
        modelValue: {
        type: String,
        required: true,
        },
        defaultOption: {
        type: String,
        required: false,
        default: 'Seleccione una opción'
        },
        itemText: {
        type: String,
        required: false,
        default: 'label'
        },
        itemValue: {
        type: String,
        required: false,
        default: 'value'
        },
    }
)

const emit = defineEmits(['update:modelValue']);

const getOptValue = (opt) => {
    return (typeof opt === 'object' && opt !== null) ? opt[props.itemValue] : opt;
};

const getOptLabel = (opt) => {
    return (typeof opt === 'object' && opt !== null) ? opt[props.itemText] : opt;
};
</script>

<template>
    <div class="search-select-container w-100">
        <label v-if="title">{{ title }}</label>
        <select 
            class="form-select form-select-sm" 
            :value="modelValue"
            @change="$emit('update:modelValue', $event.target.value)"
        >
            <option v-if="defaultOption" value="">{{ defaultOption }}</option>
            <option 
                v-for="opt in options" 
                :key="getOptValue(opt)" 
                :value="getOptValue(opt)"
            >
                {{ getOptLabel(opt) }}
            </option>
        </select>
    </div>
</template>

<style scoped>
</style>
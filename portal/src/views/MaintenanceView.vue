<template>
  <div class="min-h-screen w-full flex flex-col justify-center items-center bg-gray-100 p-6">
    <div class="max-w-md w-full bg-white shadow-md rounded-lg p-8 text-center">
      <h1 class="text-3xl font-bold text-gray-800 mb-4">
        🛠️ Modo Mantenimiento
      </h1>

      <p class="text-gray-600 text-lg mb-6">
        {{ message || "El sistema se encuentra temporalmente en mantenimiento. Por favor, volvé más tarde." }}
      </p>

      <button
        @click="reload"
        class="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
      >
        Reintentar
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "MaintenanceView",
  props: {
    message: {
      type: String,
      default: null
    }
  },
  methods: {
    reload() {
      location.reload();
    }
  }
};
</script>

<style scoped>
</style>

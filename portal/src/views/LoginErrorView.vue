<script setup>
import { useRouter, useRoute } from 'vue-router'
const router = useRouter()
const route = useRoute()

const message = route.query.reason === "cancelled"
  ? "Cancelaste el inicio de sesión."
  : "Hubo un problema al iniciar sesión."

function retry() {
    router.push("/auth/login")
}
</script>


<template>
  <div class="p-4">
    <h1>Error al iniciar sesión</h1>
    <p>{{ message }}</p>
    <button @click="retry">Intentar de nuevo</button>
  </div>
</template>


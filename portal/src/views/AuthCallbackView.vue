<script setup>
import { onMounted } from "vue"
import { useRouter, useRoute } from "vue-router"
import { useUserStore } from "../stores/user"

const router = useRouter()
const route = useRoute()
const store = useUserStore()

onMounted(async () => {
  try {
    await store.loadUser()

    let next = route.query.next || "/"

    router.replace(next)
  } catch (error) {
    router.replace({ path: "/login-error", query: { reason: "failed" } })
  }
})
</script>

<template>
  <p>Completando autenticación...</p>
</template>

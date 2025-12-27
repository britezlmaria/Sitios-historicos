<script setup>
import { RouterView } from 'vue-router'
import AppHeader from './components/AppHeader.vue'

</script>

<template>
  <AppHeader />
  <main class="app-content">
    <RouterView />
  </main>
</template>


<style scoped>
  .app-content {
    margin-top: 100px;
    padding: 20px;
  }
</style>

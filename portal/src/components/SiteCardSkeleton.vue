<script setup> </script>

<template>
    <div class="card site-card-skeleton">
        <div class="skeleton-img"></div>
        <div class="card-body">
            <div class="skeleton-text title"></div>   
            <div class="skeleton-text subtitle"></div>
            <div class="skeleton-text stars"></div>
            <div class="skeleton-text visits"></div>
            <div class="skeleton-btn"></div>
        </div>
    </div>
</template>

<style scoped>
.site-card-skeleton {
  height: 100%;
  display: flex;
  flex-direction: column;
  border: 1px solid #eee;
  background: white;
  border-radius: 0.375rem; 
  overflow: hidden;
}

.card-body {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  padding: 1rem;
  align-items: center;
}

.skeleton-img {
  width: 100%;
  aspect-ratio: 600 / 360; 
  background-color: #e0e0e0;
}

.skeleton-text {
  background-color: #e0e0e0;
  border-radius: 4px;
}

.title { 
  width: 80%; 
  height: 24px;
  margin-bottom: 0.5rem;
  margin-top: 0.5rem;
}

.subtitle { 
  width: 60%; 
  height: 16px; 
  margin-bottom: 1rem;
}

.stars { 
  width: 40%; 
  height: 16px; 
  margin-bottom: 1rem;
}

.visits { 
  width: 30%; 
  height: 14px; 
  margin-bottom: auto; 
}

.skeleton-btn {
  width: 100px;
  height: 38px;
  background-color: #e0e0e0;
  border-radius: 4px;
  margin-top: 1rem;
}

.site-card-skeleton * {
  animation: pulse 1.5s infinite ease-in-out;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
</style>
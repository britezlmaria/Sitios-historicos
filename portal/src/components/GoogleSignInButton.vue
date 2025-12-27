<script setup>
import { defineEmits } from 'vue';
import { useUserStore } from '../stores/user';
import { RouterLink } from 'vue-router';    

const emit = defineEmits(['login']);
const store = useUserStore();

function logout() {
  store.logout()
}
</script>

<template>
    <div v-if="!store.user">
        <button class="google-btn" @click="emit('login')">
            <img src="https://www.gstatic.com/images/branding/product/1x/gsa_48dp.png" alt="Logo de Google" />
            Continuar con Google
        </button>
    </div>
    <div v-else class="user-area">
        <img v-if="store.user.avatar" :src="store.user.avatar" class="avatar" />
        <span class="username">{{ store.user.name }}</span>
        <RouterLink to="/perfil">Perfil</RouterLink>
        <button class="logout-btn" @click="logout">Salir</button>
    </div>
</template>

<style scoped>
    .google-btn {
        display: flex;
        align-items: center;
        gap: 10px;
        background: var(--color-tarjeta); 
        border: 2px solid var(--color-acento); 
        color: var(--color-primario);
        font-family: 'Nunito', sans-serif;
        font-weight: 700;
        font-size: 16px; 
        border-radius: 8px;
        padding: 10px 18px; 
        cursor: pointer;
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1); 
        transition: 0.2s;
    }

    .google-btn:hover {
        background: #d6d6d6;
        border-color: var(--color-primario);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }

    .google-btn img {
        width: 20px; 
        height: 20px;
    }

    .user-area {
        display: flex;
        align-items: center;
        gap: 12px;
        background: #f7f8fa;
        padding: 6px 14px;
        border-radius: 10px;
        border: 1px solid #e3e6e8;
        color: #1e88e5;
        font-weight: 500;
        text-decoration: none;
    }

    .avatar {
        width: 38px;
        height: 38px;
        border-radius: 50%;
    }

    .username {
        font-weight: 600;
        font-size: 14px;
        color: #1e88e5;
    }

    .logout-btn {
        background: #e74c3c;
        border: none;
        color: white;
        padding: 6px 12px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
    }

    .logout-btn:hover {
        background: #c0392b;
    }
</style>
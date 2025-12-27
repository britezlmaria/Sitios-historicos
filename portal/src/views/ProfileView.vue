<template>
    <div class="profile-root">
        <header class="profile-header d-flex align-items-center gap-3">
            <div class="avatar-wrap">
                <img :src="avatarPreview || (user && user.avatar) || '/favicon.png'" alt="avatar" class="avatar" :class="{ 'clickable-avatar': isEditing }" @click="isEditing ? triggerFilePicker() : null" />
                <input id="avatarInput" class="hidden-file-input" type="file" accept="image/*" @change="onFileChange" />
                <div v-if="isEditing" class="change-overlay">
                    <span class="change-btn">Cambiar</span>
                </div>
            </div>
            <div class="profile-info ms-2">
                <h1 class="name h5 mb-0">{{ user?.name || 'Usuario' }}</h1>
                <p class="email text-muted small mb-0">{{ user?.email || '' }}</p>
            </div>
            <div class="actions ms-auto d-flex gap-2">
                <button class="btn btn-outline-primary" v-if="!isEditing" @click="startEdit">Editar</button>
                <button class="btn btn-primary" v-if="isEditing" @click="save" :disabled="saving">Guardar</button>
                <button class="btn btn-secondary" v-if="isEditing" @click="cancelEdit">Cancelar</button>
            </div>
        </header>

        <nav v-if="!isEditing" class="tabs btn-group w-100 mt-3" role="tablist">
            <button :class="['btn','w-100', tab === 'perfil' ? 'btn-primary' : 'btn-outline-primary']" @click="setTab('perfil')">Perfil</button>
            <button :class="['btn','w-100', tab === 'reviews' ? 'btn-primary' : 'btn-outline-primary']" @click="setTab('reviews')">Mis reseñas</button>
            <button :class="['btn','w-100', tab === 'favorites' ? 'btn-primary' : 'btn-outline-primary']" @click="setTab('favorites')">Favoritos</button>
        </nav>

        <section v-if="tab === 'perfil'" class="tab-content perfil-tab">
            <div class="perfil-card">
                <label class="field">
                    <div class="label">Nombre</div>
                    <div v-if="!isEditing" class="value">{{ user?.name }}</div>
                    <input v-else v-model="form.name" type="text" class="input" />
                </label>

                <label class="field">
                    <div class="label">Email</div>
                    <div class="value">{{ user?.email }}</div>
                </label>

            </div>
        </section>

        <section v-if="tab === 'reviews'" class="tab-content list-tab">
            <div class="list-controls d-flex justify-content-between align-items-center mb-2">
                <div class="left">Orden: <strong>{{ order }}</strong></div>
                <div class="right">
                    <button class="btn-cta-sm" @click="toggleOrder('reviews')">{{ order === 'desc' ? 'Más recientes' : 'Más antiguas' }}</button>
                </div>
            </div>

            <div v-if="!reviews || reviews.length === 0" class="empty">Aún no escribiste reseñas.</div>

            <ul class="reviews-list list-unstyled">
                <li v-for="r in reviews" :key="r.id" class="review-card mb-2 p-3 border rounded bg-white">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="site fw-semibold">{{ r.historic_site_name || r.historic_site?.name || 'Sitio' }}</div>
                        <div class="meta text-muted small">
                            <div class="rating">★ {{ r.rating }}</div>
                            <div class="date">{{ formatDate(r.inserted_at || r.created_at) }}</div>
                        </div>
                    </div>
                    <p class="excerpt mt-2 mb-0">{{ excerpt(r.comment) }}</p>
                </li>
            </ul>

            <div class="pager" v-if="reviewsTotal > perPage">
                <button class="btn" :disabled="reviewsPage <= 1" @click="changePage('reviews', reviewsPage - 1)">Anterior</button>
                <span>Página {{ reviewsPage }} / {{ reviewsPages }}</span>
                <button class="btn" :disabled="reviewsPage >= reviewsPages" @click="changePage('reviews', reviewsPage + 1)">Siguiente</button>
            </div>
        </section>

        <section v-if="tab === 'favorites'" class="tab-content list-tab">
            <div class="list-controls">
                <div class="left">Orden: <strong>{{ orderFav }}</strong></div>
                <div class="right">
                    <button class="btn-cta-sm" @click="toggleOrder('favorites')">{{ orderFav === 'desc' ? 'Más recientes' : 'Más antiguas' }}</button>
                </div>
            </div>

            <div v-if="!favorites || favorites.length === 0" class="empty">Aún no marcaste ningún sitio como favorito.</div>

            <ul class="fav-grid list-unstyled row row-cols-2 g-2">
                <li v-for="f in favorites" :key="f.id" class="fav-card col">
                    <SiteCard 
                        :site="f" 
                        @view-detail="handleViewDetail"
                    />
                </li>
            </ul>

            <div class="pager" v-if="favoritesTotal > perPage">
                <button class="btn" :disabled="favPage <= 1" @click="changePage('favorites', favPage - 1)">Anterior</button>
                <span>Página {{ favPage }} / {{ favPages }}</span>
                <button class="btn" :disabled="favPage >= favPages" @click="changePage('favorites', favPage + 1)">Siguiente</button>
            </div>
        </section>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import SiteCard from '@/components/SiteCard.vue'

const router = useRouter()
const store = useUserStore()

const user = computed(() => store.user)

const tab = ref('perfil')
const perPage = 25

const reviews = ref([])
const reviewsTotal = ref(0)
const reviewsPage = ref(1)
const order = ref('desc')

const favorites = ref([])
const favoritesTotal = ref(0)
const favPage = ref(1)
const orderFav = ref('desc')

const reviewsPages = computed(() => Math.max(1, Math.ceil(reviewsTotal.value / perPage)))
const favPages = computed(() => Math.max(1, Math.ceil(favoritesTotal.value / perPage)))

const isEditing = ref(false)
const saving = ref(false)
const form = ref({ name: '', avatar: '' })
const avatarPreview = ref(null)

function excerpt(text, max = 160) {
    if (!text) return ''
    return text.length > max ? text.slice(0, max).trimEnd() + '…' : text
}

function formatDate(s) {
    if (!s) return ''
    const d = new Date(s)
    return d.toLocaleDateString()
}

async function loadProfile() {
    await store.loadUser()
    if (store.user) {
        form.value.name = store.user.name || ''
        form.value.avatar = store.user.avatar || ''
        avatarPreview.value = ''
    }
}

async function loadReviews() {
    try {
        await store.loadMyReviews(reviewsPage.value, order.value)
        reviews.value = Array.isArray(store.reviews) ? store.reviews : []
        reviewsTotal.value = store.reviewsTotal || 0
    } catch (e) {
        reviews.value = []
        reviewsTotal.value = 0
    }
}

async function loadFavorites() {
    try {
        await store.loadMyFavorites(favPage.value, orderFav.value)
        favorites.value = Array.isArray(store.favorites) ? store.favorites : []
        favoritesTotal.value = store.favoritesTotal || 0
    } catch (e) {
        favorites.value = []
        favoritesTotal.value = 0
    }
}

function startEdit() {
    isEditing.value = true
    form.value.name = store.user?.name || ''
    avatarPreview.value = ''
}

function cancelEdit() {
    isEditing.value = false
    avatarPreview.value = ''
}

function onFileChange(e) {
    const f = e.target.files && e.target.files[0]
    if (!f) return
    const reader = new FileReader()
    reader.onload = () => {
        avatarPreview.value = reader.result
    }
    reader.readAsDataURL(f)
}

function triggerFilePicker() {
  const el = document.getElementById('avatarInput')
  if (el) el.click()
}

async function save() {
    saving.value = true
    try {
        const payload = {
            name: form.value.name,
        }
        if (avatarPreview.value) payload.avatar = avatarPreview.value
        await store.updateProfile(payload)
        await loadProfile()
        isEditing.value = false
    } catch (err) {
        console.error(err)
    } finally {
        saving.value = false
    }
}

function toggleOrder(list) {
    if (list === 'reviews') {
        order.value = order.value === 'desc' ? 'asc' : 'desc'
        reviewsPage.value = 1
        loadReviews()
    } else {
        orderFav.value = orderFav.value === 'desc' ? 'asc' : 'desc'
        favPage.value = 1
        loadFavorites()
    }
}

function setTab(name) {
    try {
        tab.value = name
        if (name === 'reviews') {
            reviewsPage.value = 1
            loadReviews()
        } else if (name === 'favorites') {
            favPage.value = 1
            loadFavorites()
        }
    } catch (e) {
        console.error('setTab error', e)
    }
}

function changePage(list, p) {
    if (list === 'reviews') {
        reviewsPage.value = p
        loadReviews()
    } else {
        favPage.value = p
        loadFavorites()
    }
}

const handleViewDetail = (siteId) => {
  router.push({ name: 'historic-site', params: { id: siteId } });
};

onMounted(async () => {
    await loadProfile()
    await loadReviews()
    await loadFavorites()
})

watch(() => store.user, (v) => {
    if (v) {
        form.value.name = v.name || ''
        form.value.avatar = v.avatar || ''
    }
})
</script>

<style scoped>
.profile-root {
    padding: 28px 18px;
    max-width: 880px;
    margin: 18px auto;
    font-family: 'Nunito', system-ui, sans-serif;
    background: #ffffff; /* Tarjeta blanca sobre fondo oscuro del sistema */
    border-radius: 16px;
    color: var(--color-texto);
    box-shadow: 0 10px 30px rgba(0,0,0,0.05);
}

.profile-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    background: transparent;
    padding: 14px;
    border-bottom: 1px solid var(--color-borde-suave);
}

.avatar-wrap {
    width: 84px;
    height: 84px;
    flex: 0 0 84px;
    position: relative;
}
.avatar {
    width: 84px;
    height: 84px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid var(--color-acento-suave);
}
.hidden-file-input { display: none }
.change-overlay { position: absolute; inset: auto 0 -10px 0; display:flex; justify-content:center }
.change-btn { 
    background: var(--color-acento-claro); 
    color: var(--color-primario); 
    padding: 4px 10px; 
    border-radius: 20px; 
    font-weight: 700; 
    font-size: 11px; 
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    cursor: pointer;
}

.clickable-avatar { cursor: pointer; transition: transform .12s ease }
.clickable-avatar:hover { transform: scale(1.05); }

.profile-info {
    flex: 1;
    text-align: center;
}
.name {
    font-size: 20px;
    margin: 0;
    color: var(--color-primario);
    font-weight: 700;
}
.email {
    font-size: 14px;
    color: var(--color-mutado);
    margin: 0;
}

.actions { display:flex; gap:8px; width:100%; justify-content: center; margin-top: 10px; }
.actions .btn { flex: 1; max-width: 120px; }

/* ESTILOS BOTONES DEL SISTEMA */
.btn { 
    padding: 10px 14px;
    font-weight: 700;
    border-radius: 12px;
    transition: all 0.3s ease;
    border: 1px solid transparent;
}

.btn-primary {
    background: var(--color-primario);
    color: #fff !important;
    border: none !important;
}
.btn-primary:hover {
    background: var(--color-acento-claro);
    color: var(--color-primario) !important;
}

.btn-outline-primary {
    background: transparent;
    color: var(--color-primario) !important;
    border: 1px solid var(--color-primario) !important;
}
.btn-outline-primary:hover {
    background: var(--color-primario);
    color: #fff !important;
}

.btn-secondary {
    background: #e2e8f0;
    color: var(--color-texto) !important;
}
.btn-secondary:hover {
    background: #cbd5e1;
}

/* TABS ESTILO SISTEMA */
.tabs { display:flex; flex-direction:column; gap:8px; margin-top:12px }
.tabs .btn { width:100%; text-align:center; border-radius: 8px; }
.tabs .btn-primary {
    background: var(--color-primario) !important;
}
.tabs .btn-outline-primary {
    background: var(--color-acento-suave);
    color: var(--color-primario) !important;
    border: none !important;
}
.tabs .btn-outline-primary:hover {
    background: var(--color-acento-claro);
}


.btn-cta-sm {
    background: var(--color-acento-claro);
    color: var(--color-primario) !important;
    border: none !important;
    padding: 6px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.85rem;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    transition: transform .12s ease;
}
.btn-cta-sm:hover { transform: translateY(-2px); filter: brightness(1.05); }

.tab-content { margin-top:24px }
.perfil-card { background: transparent; padding:12px; border-radius:8px }
.field { display:flex; flex-direction:column; gap:4px; margin-bottom:16px }
.label { font-size:12px; color: var(--color-mutado); font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
.value { font-size:16px; color: var(--color-texto); font-weight: 500; padding-bottom: 8px; border-bottom: 1px solid var(--color-borde-suave); }
.input { padding:10px; border-radius:8px; border:1px solid var(--color-borde-suave); width: 100%; font-family: inherit; }
.input:focus { outline: 2px solid var(--color-acento-claro); border-color: transparent; }

.list-controls { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px }
.reviews-list { list-style:none; padding:0; margin:0; display:block }
.review-card { 
    background: #f8f9fa; 
    padding:16px; 
    border-radius:12px; 
    margin-bottom:12px; 
    border: 1px solid var(--color-borde-suave);
}
.review-card:hover { border-color: var(--color-acento-claro); }

.site { color: var(--color-primario); }
.rating { color: var(--color-estrella); font-weight: bold; }
.excerpt { margin-top:8px; color: var(--color-texto); line-height: 1.5; }

/* GRILLA FAVORITOS */
.fav-grid { 
    display: grid; 
    grid-template-columns: 1fr; 
    gap: 20px; 
    list-style: none; 
    padding: 0; 
}

.empty { text-align:center; padding:40px; color: var(--color-mutado); font-style: italic; }

.pager { display:flex; justify-content:center; gap:12px; align-items:center; margin-top:24px }
.pager span { font-size: 0.9rem; color: var(--color-mutado); }

@media(min-width: 576px) {
    .fav-grid { grid-template-columns: repeat(2, 1fr); }
}

@media(min-width: 992px) {
    .fav-grid { grid-template-columns: repeat(3, 1fr); }
}

@media(min-width:700px) {
    .profile-root { padding: 34px; margin-top: 40px; }
    .profile-header { flex-direction: row; align-items: center; text-align: left; }
    .profile-info { text-align: left; }
    .actions { width: auto; margin-top: 0; }
    .actions .btn { flex: none; }
    .tabs { flex-direction: row }
    .tabs .btn { width: auto }
}
</style>
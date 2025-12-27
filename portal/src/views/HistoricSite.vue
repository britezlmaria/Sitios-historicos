<script setup>
import { ref, onMounted, defineAsyncComponent, Suspense, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useUserStore } from "../stores/user";
import SiteImageCarouselSkeleton from "@/components/SiteImageCarouselSkeleton.vue";
import ChipsButton from "@/components/ChipButton.vue";
import api, { apiBase } from '@/services/api';
import VisitTracker from "@/components/VisitTracker.vue";

const SiteLocationMap = defineAsyncComponent(
    () => import('@/components/SiteLocationMap.vue'),
);

const SiteImageCarousel = defineAsyncComponent(
    () => import('@/components/SiteImageCarousel.vue'),
);

const Stars = defineAsyncComponent(
  () => import('@/components/Stars.vue'),
);

const showFullDesc = ref(false);
const isFavorite = ref(false);
//TODO: Reemplazar con estado real de autenticación
const isAuthenticated = ref(true);
const reviewsPage = ref(1);
const reviewsPages = ref(1);

function checkSession(){
  if (!store.user) {
    const next = encodeURIComponent(window.location.pathname)
    window.location.href = `${apiBase}/api/auth/google/login?next=${next}`
  }
}

const onFavorite = async () => {
    checkSession();

    const previousState = isFavorite.value;
    isFavorite.value = !previousState;

    try {
        if (previousState) {
            await api.delete(`/sites/${site.value.id}/favorite`);
        } else {
            await api.put(`/sites/${site.value.id}/favorite`);
        }
    } catch (error) {
        console.error('Error de red al marcar favorito:', error);
        isFavorite.value = previousState;
    }
};

//TODO: Reemplazar por paginacion y reseñas reales
const route = useRoute();
const router = useRouter();
const store = useUserStore();
const siteId = route.params.id;
const site = ref(null);
const loading = ref(true);
const showModal = ref(false);
const rating = ref(5);
const comment = ref("");
const errorMsg = ref("");
const reviews_enabled = ref(true);
const hasUserReview = computed(() => {
    return userReview.value !== null;
})
const showDeleteModal = ref(false);
const userReview = computed(() => {
    if (!store.user || !site.value?.reviews) return null
    return site.value.reviews.find(r => r.user_id === store.user.id) || null
})
const successMsg = ref("");

function onDeleteReview() {
    showDeleteModal.value = true;
}

function closeDeleteModal() {
    showDeleteModal.value = false;
}


function openModal() {
    showModal.value = true;
}

function closeModal() {
    showModal.value = false;
    comment.value = "";
    rating.value = 5;
    errorMsg.value = "";
}

function onReview() {
  checkSession();
  if (hasUserReview.value) {
    alert("Ya dejaste una reseña en este sitio.");
    return;
  }
  // Agrego if para que no abra el modal si no hay sesion iniciada
  if (store.user) {
    openModal();
  }
 }

async function confirmDeleteReview() {
    if (!userReview.value) return;

    try {
        const resp = await api.delete(`/sites/${site.value.id}/reviews/${userReview.value.id}`);

        if (resp.status !== 204 && resp.status !== 200) {
            throw new Error(`Respuesta inesperada del servidor: ${resp.status}`);
        }

        await loadReviews();

        showDeleteModal.value = false;
        successMsg.value = "Tu reseña fue eliminada correctamente.";
        setTimeout(() => (successMsg.value = ""), 3000);

    } catch (error) {
        console.error("Error al borrar reseña:", error);

        const serverMsg = error.response?.data?.error?.message
            ?? error.response?.data?.message
            ?? error.response?.statusText
            ?? error.message;

        if (error.response?.status === 401) {
            alert("No autorizado. Inicia sesión e intenta de nuevo.");
        } else if (error.response?.status === 403) {
            alert("No tenés permiso para eliminar esta reseña.");
        } else {
            alert("Hubo un error al eliminar la reseña: " + serverMsg);
        }
    }
}

async function enviarReview() {
    if (comment.value.length < 20 || comment.value.length > 1000) {
        errorMsg.value = "El comentario debe tener entre 20 y 1000 caracteres.";
        return;
    }

    try {
        const response = await api.post(`/sites/${siteId}/reviews`, {
            historic_site_id: Number(siteId),
            rating: rating.value,
            comment: comment.value
        });

        await loadReviews();
        closeModal();
        successMsg.value = "¡Tu reseña fue enviada correctamente!";

        setTimeout(() => successMsg.value = "", 3000);
    } catch (error) {
        console.error(error);
        errorMsg.value = error.response?.data?.error?.message
            ?? "Error al enviar la reseña.";
    }
}

const goBack = () => {
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push({ name: 'home' });
  }
};

function goToTag(tag) {
  router.push({name:'ordered-sites-list', query: {tags: tag}})
}

function goToConservationState(state) {
  router.push({name:'ordered-sites-list', query: {state_of_conservation: state}})
}

async function loadReviews() {
    if (!site.value) return;

    try {
        const resp = await api.get(`/sites/${site.value.id}/reviews`);
        const items = resp.data.data ?? [];

        site.value.reviews = items;
    } catch (error) {
        console.error("Error loading reviews:", error);
        site.value.reviews = [];
    }
}

const loadSiteData = async (id) => {
  console.log('Cargando detalles para el sitio:', id);
  try {
    const flags_response = await api.get('/flags');
    reviews_enabled.value = flags_response.data.reviews_enabled;
    const response = await api.get(`/sites/${id}`);
    site.value = response.data;
    if (store.user && site.value) {
      const favResponse = await api.get('/me/favorites');
      const favoriteList = favResponse.data.data ?? favResponse.data ?? [];
      if (favoriteList.some(favSite => favSite.id === site.value.id)) {
        isFavorite.value = true;
      }
    }
    await loadReviews();
    console.log('Detalles del sitio cargados:', site.value);
  } catch (error) {
    console.error('Error fetching site details:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadSiteData(route.params.id);
});

watch(() => route.params.id,
  (newId) => {
    if (newId) {
      loadSiteData(newId);
      window.scrollTo(0,0);
    }
  });

</script>

<template>
  <div class="container py-1">
    <div v-if="site" class="card shadow-sm">
      <div class="card-body">
        <div class="d-flex flex-column flex-md-row align-items-start justify-content-between gap-3 mb-4">
          <div class="flex-grow-1 w-100">
            <h2 class="mb-1 fw-bold">{{ site.name }}</h2>
            <div class="text-muted d-flex flex-wrap align-items-center gap-2">
              <span>{{ site.city }}, {{ site.province }}</span>
              <ChipsButton
                v-if="site.state_of_conservation"
                :chips="[site.state_of_conservation]"
                @click-chip="goToConservationState"
              />
            </div>
          </div>

          <div class="d-flex gap-2 w-100 w-md-auto justify-content-start justify-content-md-end">
            <button class="action-btn" @click="goBack" title="Volver">
              <font-awesome-icon :icon="['fas', 'arrow-left']" />
              <span class="ms-2">Volver</span>
            </button>

            <button
              class="action-btn"
              :class="{ 'is-favorite': isFavorite }"
              @click="onFavorite"
              title="Guardar"
            >
              <font-awesome-icon :icon="isFavorite ? ['fas', 'heart'] : ['far', 'heart']" />
              <span class="ms-2">{{ isFavorite ? 'Guardado' : 'Guardar' }}</span>
            </button>
          </div>
        </div>

        <Suspense>
          <template #default>
            <SiteImageCarousel :images="site.images_list" :site-name="site.name" />
          </template>
          <template #fallback>
            <SiteImageCarouselSkeleton />
          </template>
        </Suspense>

        <Suspense>
          <template #default>
            <div class="my-4 d-flex flex-column align-items-center justify-content-center">
              <div class="mb-2">
                <strong class="fs-5">Calificación promedio:</strong>
              </div>
              <div>
                <Stars :rating="site.rating" :size="40" />
              </div>
            </div>
          </template>
          <template #fallback>
            <div>Cargando calificación...</div>
          </template>
        </Suspense>

        <div class="my-4 d-flex flex-column align-items-center justify-content-center">
          <VisitTracker :visits="site.visit_count" />
        </div>

        <div class="mb-3">
          <p>
            {{ showFullDesc ? site.description : site.short_description }}
            <a v-if="site.description" href="#" @click.prevent="showFullDesc = !showFullDesc" class="btn btn-link">
              {{ showFullDesc ? 'Ver menos' : 'Ver más' }}
            </a>
          </p>
        </div>

        <div class="mb-3" v-if="site.tags && site.tags.length > 0">
          <ChipsButton :chips="site.tags" @click-chip="goToTag" />
        </div>

        <SiteLocationMap
          :lat="site.lat"
          :long="site.long"
          :site_name="site.name"
          :site_short_description="site.short_description"
        ></SiteLocationMap>

        <div v-if="reviews_enabled">
                    <!-- Botón escribir reseña -->
                    <div class="mb-3">
                        <button class="btn btn-primary" @click="onReview" :disabled="hasUserReview">
                            Escribir reseña
                        </button>
                        <div v-if="hasUserReview" class="text-muted small mt-1">
                            Ya dejaste una reseña en este sitio.
                        </div>
                    </div>

                    <div v-if="successMsg" class="alert alert-success">
                        {{ successMsg }}
                    </div>

                    <!-- Reseñas -->
                    <div class="mb-4">
                        <h5>Reseñas</h5>
                        <div v-if="hasUserReview" class="mb-3">
                            <button class="btn btn-danger btn-sm" @click="onDeleteReview">
                                Eliminar tu reseña
                            </button>
                        </div>
                        <div v-if="site.reviews.length">
                            <div v-for="review in site.reviews" :key="review.id" class="border rounded p-2 mb-2">
                                <div class="d-flex align-items-center mb-1">
                                    <strong>{{ review.user_name }}</strong>
                                    <span class="ms-2 text-warning">
                                        <i v-for="n in 5" :key="n"
                                            :class="n <= review.rating ? 'fas fa-star' : 'far fa-star'"></i>
                                    </span>
                                    <span class="ms-2 text-muted small">{{ review.updated_at }}</span>
                                </div>
                                <div>{{ review.comment }}</div>
                            </div>
                            <!-- Paginación simple -->
                            <nav v-if="reviewsPages > 1">
                                <ul class="pagination pagination-sm">
                                    <li class="page-item" :class="{ disabled: reviewsPage === 1 }">
                                        <a class="page-link" href="#" @click.prevent="reviewsPage--">Anterior</a>
                                    </li>
                                    <li class="page-item" v-for="p in reviewsPages" :key="p"
                                        :class="{ active: p === reviewsPage }">
                                        <a class="page-link" href="#" @click.prevent="reviewsPage = p">{{ p }}</a>
                                    </li>
                                    <li class="page-item" :class="{ disabled: reviewsPage === reviewsPages }">
                                        <a class="page-link" href="#" @click.prevent="reviewsPage++">Siguiente</a>
                                    </li>
                                </ul>
                            </nav>
                        </div>
                        <div v-else class="text-muted">No hay reseñas aprobadas.</div>
                    </div>
                </div>
                <div v-else class="text-muted">Las reseñas están deshabilitadas temporalmente.</div>
            </div>
            <!-- Paginación simple -->
            <div v-if="reviews_enabled">
                <nav v-if="reviewsPages > 1">
                    <ul class="pagination pagination-sm">
                        <li class="page-item" :class="{ disabled: reviewsPage === 1 }">
                            <a class="page-link" href="#" @click.prevent="reviewsPage--">Anterior</a>
                        </li>
                        <li class="page-item" v-for="p in reviewsPages" :key="p" :class="{ active: p === reviewsPage }">
                            <a class="page-link" href="#" @click.prevent="reviewsPage = p">{{ p }}</a>
                        </li>
                        <li class="page-item" :class="{ disabled: reviewsPage === reviewsPages }">
                            <a class="page-link" href="#" @click.prevent="reviewsPage++">Siguiente</a>
                        </li>
                    </ul>
                </nav>
            </div>
        </div>
        <div v-else class="text-muted">No hay reseñas aprobadas.</div>
    </div>
    <Teleport to="body">
        <div v-if="showModal" class="modal-overlay" @click="closeModal">
            <div class="site-modal" @click.stop>
                <h2>Nueva reseña</h2>

                <label>
                    Calificación:
                    <select v-model="rating">
                        <option v-for="n in 5" :key="n" :value="n">{{ n }} ⭐</option>
                    </select>
                </label>

                <label>
                    Comentario (20 a 1000 caracteres):
                    <textarea v-model="comment" rows="5" maxlength="1000"
                        placeholder="Escribe tu opinión aquí..."></textarea>
                </label>

                <p v-if="errorMsg" class="error">{{ errorMsg }}</p>

                <div class="modal-buttons">
                    <button type="button" @click="enviarReview">Enviar</button>
                    <button type="button" class="cancel" @click="closeModal">Cancelar</button>
                </div>
            </div>
        </div>

        <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
            <div class="site-modal compact" @click.stop>
                <h2>¿Eliminar tu reseña?</h2>
                <p class="text-muted">Esta acción no se puede deshacer.</p>
                <hr>
                <div v-if="userReview">
                    <strong>Tu comentario:</strong>
                    <p class="review-preview">
                        {{ userReview.comment }}
                    </p>
                </div>
                <div class="modal-buttons">
                    <button type="button" class="btn btn-danger" @click="confirmDeleteReview">
                        Eliminar
                    </button>
                    <button type="button" class="cancel" @click="closeDeleteModal">
                        Cancelar
                    </button>
                </div>
            </div>
        </div>
    </Teleport>
</template>

<style scoped>
.card {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Estilos para los botones de acción (Favorito/Volver) */
.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: transparent;
  border: 1px solid transparent;
  padding: 8px 12px;
  border-radius: 8px;
  color: #222;
  font-size: 14px;
  font-weight: 500;
  text-decoration: underline;
  text-decoration-color: transparent;
  transition: all 0.2s ease;
  cursor: pointer;
}

.action-btn:hover {
  background-color: #f7f7f7;
  text-decoration-color: #222;
}

.action-btn:active {
  transform: scale(0.96);
}

.action-btn.is-favorite {
  color: #ff385c;
}

.action-btn.is-favorite:hover {
  background-color: #fff0f5;
}

.action-btn svg {
  font-size: 16px;
}

/* --- ESTILOS DEL MODAL CENTRADO --- */

.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.6);
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
  backdrop-filter: blur(2px);
}

.site-modal {
  background: #fff;
  width: 100%;
  max-width: 480px;

  /* Altura automática que se ajusta al contenido */
  height: auto;
  max-height: 90vh;

  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);

  display: flex;
  flex-direction: column;
  gap: 16px;

  position: relative;
  overflow-y: auto;

  animation: modal-in 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modal-in {
  from { opacity: 0; transform: scale(0.95) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.site-modal h2 {
  margin: 0;
  font-size: 1.5rem;
  text-align: center;
  color: #1a1a1a;
}

.site-modal label {
  display: flex;
  flex-direction: column;
  font-weight: 600;
  color: #4a4a4a;
  gap: 8px;
}

.site-modal select,
.site-modal textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.95rem;
  background-color: #fff;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.site-modal textarea {
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
}

.site-modal select:focus,
.site-modal textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}

.modal-buttons button {
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-buttons button:first-child {
  background-color: #2563eb;
  color: white;
}

.modal-buttons button:first-child:hover {
  background-color: #1d4ed8;
}

.modal-buttons .cancel {
  background-color: #f3f4f6;
  color: #374151;
}

.modal-buttons .cancel:hover {
  background-color: #e5e7eb;
}

.review-preview {
  background: #f9fafb;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #eee;
  font-style: italic;
  margin: 10px 0;
}

.error {
  color: #ef4444;
  font-size: 0.9rem;
  background-color: #fef2f2;
  padding: 8px;
  border-radius: 6px;
  text-align: center;
  margin: 0;
}
</style>

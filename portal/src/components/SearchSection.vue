<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '@/services/api';
import InputText from '@/components/searchBar/InputText.vue';
import Selector from '@/components/searchBar/Selector.vue';
import MultiSelectorCheck from './searchBar/MultiSelectorCheck.vue';
import SwitchBtn from './searchBar/SwitchBtn.vue';
import SiteProxMap from '@/components/searchBar/SiteProxMap.vue';
import { useUserStore } from "../stores/user"

const store = useUserStore()
const router = useRouter();
const route = useRoute();
const searchContainer = ref(null);

const filters = reactive({
  q: '',
  city: '',
  province: '',
  tags: [],
  favorites: false,
  lat: null,
  long: null,
  radius: 10,
  order_by: 'latest',
  state_of_conservation: '',
});

const isExpanded = ref(false);
const showMapModal = ref(false);

const provinces = ref([]);
const availableTags = ref([]);

const sortOptions = [
    { label: 'Más recientes', value: 'latest' },
    { label: 'Más antiguos', value: 'oldest' },
    { label: 'Mejor puntuados', value: 'rating-5-1' },
    { label: 'Más visitados', value: 'most-visited' },
];

const conservationOptions = [
    { label: 'Bueno', value: 'bueno' },
    { label: 'Regular', value: 'regular' },
    { label: 'Malo', value: 'malo' },
];

const handleClickOutside = (event) => {
  if (searchContainer.value && !searchContainer.value.contains(event.target)) {
    // En desktop cerramos al hacer click fuera, en mobile quizás queramos mantenerlo hasta buscar
    if (window.innerWidth >= 768) {
        isExpanded.value = false;
    }
  }
};

// Cargar filtros desde la URL al montar
onMounted(async () => {
  document.addEventListener('click', handleClickOutside);
  const query = route.query;
  // ... (Lógica de carga igual que antes)
  if (query.q) filters.q = query.q;
  if (query.city) filters.city = query.city;
  if (query.province) filters.province = query.province;
  if (query.tags) filters.tags = Array.isArray(query.tags) ? query.tags : query.tags.split(',');
  if (query.only_favorites) filters.favorites = query.only_favorites === 'true';
  if (query.lat) filters.lat = parseFloat(query.lat);
  if (query.long) filters.long = parseFloat(query.long);
  if (query.order_by) filters.order_by = query.order_by;
  if (query.state_of_conservation) filters.state_of_conservation = query.state_of_conservation;

  try{
      const response = await api.get('/sites/provinces');
      provinces.value = response.data.data ?? response.data ?? [];
  } catch (error) { console.error(error); }

  try{
      const response = await api.get('/tags');
      availableTags.value = response.data.data ?? response.data ?? [];
  } catch (error) { console.error(error); }
});

const applySearch = () => {
  const query = {};
  if (filters.q) query.name = filters.q;
  if (filters.q) query.description = filters.q;
  if (filters.city) query.city = filters.city;
  if (filters.province && filters.province !== 'Todas') query.province = filters.province;
  if (filters.tags.length > 0) query.tags = filters.tags.join(',');
  if (filters.favorites) query.only_favorites = 'true';
  if (filters.lat && filters.long) {
      query.lat = filters.lat;
      query.long = filters.long;
      query.radius = filters.radius;
  }
  if (filters.order_by) query.order_by = filters.order_by;
  if (filters.state_of_conservation && filters.state_of_conservation !== 'todos') query.state_of_conservation = filters.state_of_conservation;

  router.push({ name: 'ordered-sites-list', query });
  isExpanded.value = false; // Colapsar al buscar
};

const clearFilters = () => {
  Object.keys(filters).forEach(key => {
    if (key === 'tags') filters[key] = [];
    else if (key === 'radius') filters[key] = 10;
    else if (key === 'order_by') filters[key] = 'rating-5-1';
    else if (key === 'state_of_conservation') filters[key] = '';
    else if (key === 'favorites') filters[key] = false;
    else filters[key] = null;
  });
  applySearch();
};

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

const handleSelectionFromMap = (coords) => {
  filters.lat = coords.lat;
  filters.long = coords.lng;
};

const handleViewDetail = async (siteId) => {
  showMapModal.value = false;
  router.push({name: 'historic-site',params: { id: siteId }});
};
</script>

<template>
  <div class="search-section-container" ref="searchContainer">

    <div class="search-bar shadow-sm" :class="{ 'expanded': isExpanded }">

      <div class="desktop-inputs d-none d-md-flex w-100 align-items-center">
          <InputText
            title="Dónde"
            placeholder="Sitios..."
            v-model="filters.q"
            @enter="applySearch"
            @click="isExpanded = true"
          />
          <div class="divider"></div>
          <InputText
            title="Ciudad"
            placeholder="Ciudades..."
            v-model="filters.city"
            @enter="applySearch"
            @click="isExpanded = true"
          />
          <button class="search-btn ms-auto" @click="applySearch">
            <svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" style="display:block;fill:none;height:16px;width:16px;stroke:currentColor;stroke-width:4;overflow:visible"><path d="M13 24a11 11 0 1 0 0-22 11 11 0 0 0 0 22zm8-3 9 9"></path></svg>
          </button>
      </div>

      <div class="mobile-trigger d-flex d-md-none w-100 align-items-center justify-content-between p-2" @click="isExpanded = !isExpanded">
          <div class="d-flex align-items-center gap-3">
              <div class="search-icon-mobile">
                  <svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" role="presentation" focusable="false" style="display: block; fill: none; height: 16px; width: 16px; stroke: currentcolor; stroke-width: 4; overflow: visible;"><path d="M13 24a11 11 0 1 0 0-22 11 11 0 0 0 0 22zm8-3 9 9"></path></svg>
              </div>
              <div class="d-flex flex-column text-start">
                  <span class="fw-bold text-dark">¿A dónde quieres ir?</span>
                  <span class="text-muted small text-truncate" style="max-width: 200px;">
                      {{ filters.q || filters.city || 'Buscar sitios, ciudades...' }}
                  </span>
              </div>
          </div>
          <div class="filter-icon-mobile border rounded-circle p-2">
               <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-sliders" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M11.5 2a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zM9.05 3a2.5 2.5 0 0 1 4.9 0H16v1h-2.05a2.5 2.5 0 0 1-4.9 0H0V3h9.05zM4.5 7a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zM2.05 8a2.5 2.5 0 0 1 4.9 0H16v1H6.95a2.5 2.5 0 0 1-4.9 0H0V8h2.05zm9.45 4a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm-2.45 1a2.5 2.5 0 0 1 4.9 0H16v1h-2.05a2.5 2.5 0 0 1-4.9 0H0v-1h9.05z"/>
              </svg>
          </div>
      </div>
    </div>

    <div v-if="isExpanded" class="advanced-filters-panel shadow">
      <div class="container py-3">

        <div class="d-md-none mb-3 px-2">
            <div class="mb-2">
                <label class="fw-bold small">¿Qué buscas?</label>
                <input type="text" class="form-control form-control-lg border-0 bg-light" v-model="filters.q" placeholder="Sitio histórico...">
            </div>
            <div class="mb-2">
                <label class="fw-bold small">Ciudad</label>
                <input type="text" class="form-control form-control-lg border-0 bg-light" v-model="filters.city" placeholder="La Plata...">
            </div>
        </div>

        <div class="row g-3 align-items-end">
          <div class="col-12 col-md-3">
            <Selector
                title="Provincia"
                v-model="filters.province"
                :options="provinces"
                default-option="Todas"
            ></Selector>
          </div>
          <div class="col-12 col-md-3">
            <Selector
                title="Estado Conservación"
                :options="conservationOptions"
                v-model="filters.state_of_conservation"
                item-text="label"
                item-value="value"
                default-option="Todos"
            ></Selector>
          </div>
          <div class="col-12 col-md-3">
             <MultiSelectorCheck
                title="Etiquetas"
                v-model="filters.tags"
                :options="availableTags"
                item-value="name"
                item-text="name"
             />
          </div>
          <div class="col-6 col-md-2">
            <Selector
                title="Ordenar por"
                v-model="filters.order_by"
                :options="sortOptions"
                item-value="value"
                item-text="label"
                default-option="Más recientes"
            />
          </div>

          <div class="col-12 mt-3 border-top pt-3 d-flex flex-column flex-md-row align-items-center justify-content-between gap-3">
             <div class="d-flex gap-3 align-items-center w-100 w-md-auto">
                    <SwitchBtn
                        v-if="store.user"
                        id="favSwitch"
                        title="Solo favoritos"
                        v-model="filters.favorites"
                        label="Favoritos"
                      />
                  <button type="button" class="btn btn-outline-secondary btn-sm d-flex align-items-center gap-1" @click="showMapModal = true">
                    <span>📍</span> Mapa <span v-if="filters.lat" class="badge bg-success ms-1">✓</span>
                  </button>
             </div>

             <div class="d-flex gap-2 w-100 w-md-auto justify-content-end">
               <button class="btn btn-link text-muted text-decoration-none" @click="clearFilters">Limpiar</button>
               <button class="btn btn-primary rounded-pill px-4 d-md-none" @click="applySearch">
                   Buscar
               </button>
               <button class="btn btn-light rounded-circle d-none d-md-block" @click="isExpanded = false">▲</button>
             </div>
          </div>

        </div>
      </div>
    </div>

    <div v-if="showMapModal" class="map-modal-overlay">
      <div class="map-modal-content">
        <h5>Selecciona un punto</h5>
        <div class="map-wrapper">
           <SiteProxMap
              @location-selected="handleSelectionFromMap"
              @view-detail="handleViewDetail"
           />
        </div>
        <div class="p-2 text-end">
          <button class="btn btn-secondary btn-sm" @click="showMapModal = false">Cancelar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-section-container {
  position: relative;
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  z-index: 1000;
}

.search-bar {
  background: var(--color-tarjeta);
  border: 1px solid var(--color-borde-suave);
  border-radius: 32px;
  padding: 8px;
  transition: box-shadow 0.2s;
  position: relative;
  z-index: 1002;
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

.search-bar:hover, .search-bar.expanded {
  box-shadow: 0 6px 16px rgba(0,0,0,0.12) !important;
  background-color: #fff;
}

.divider {
  width: 1px;
  height: 24px;
  background-color: var(--color-borde-suave);
  margin: 0 10px;
}

.search-btn {
  background-color: var(--color-acento-claro);
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.search-btn:hover {
  transform: scale(1.05);
  filter: brightness(1.1);
}

.mobile-trigger {
    cursor: pointer;
    border-radius: 32px;
    transition: background 0.2s;
}
.mobile-trigger:hover {
    background-color: #f8f9fa;
}
.search-icon-mobile {
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--color-primario);
}
.filter-icon-mobile {
    border-color: var(--color-borde-suave) !important;
    color: var(--color-primario);
}

.advanced-filters-panel {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--color-tarjeta);
  border-radius: 32px;
  border: 1px solid var(--color-borde-suave);
  margin-top: 12px;
  animation: slideDown 0.2s ease-out;
  z-index: 1001;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);

  max-height: 75vh;
  overflow-y: auto;
  scrollbar-width: thin;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

:deep(.search-input-group) {
    margin-bottom: 0 !important;
}
:deep(.search-input-group input) {
    color: var(--color-texto);
    font-weight: 600;
}
:deep(.search-input-group label) {
    color: var(--color-primario);
}

.map-modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.map-modal-content {
  background: white;
  padding: 20px;
  border-radius: 16px;
  width: 90%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
}
.map-wrapper {
  height: 500px;
  width: 100%;
  background: #e9ecef;
  border-radius: 8px;
  margin-bottom: 10px;
  overflow: hidden;
}

</style>

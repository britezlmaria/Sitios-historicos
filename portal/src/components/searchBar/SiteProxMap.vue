<template>
  <div class="map-container">
    <l-map 
        ref="map" 
        v-model:zoom="zoom" 
        :center="center"
        @click="handleMapClick"
        @update:zoom="zoomUpdated"
        @update:center="centerUpdated"
        id="map"
        >
      <l-tile-layer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        layer-type="base"
        name="OpenStreetMap"
      ></l-tile-layer>
        <l-control>
        <button v-if="showUpdateRadiusButton" @click="updateSearchRadius">
          Actualizar Radio de Búsqueda
        </button>
      </l-control>
      <l-circle :lat-lng="radiusCenter" :radius="radius" color="green" />
      <l-marker 
        v-for="marker in markers" 
        :key="marker.id"
        :lat-lng="[marker.lat, marker.lon]"
      >
        <l-popup>
          <div class="popup-content">
            <h3>{{ marker.title }}</h3>
            <p>{{ marker.description }}</p>
            <button 
              class="btn btn-primary" 
              @click="onViewDetail(marker.id)"
            >
              Ver Detalle
            </button>
          </div>
        </l-popup>
      </l-marker>
    </l-map>
  </div>
</template>

<script>
import "leaflet/dist/leaflet.css";
import { LControl, LCircle, LMap, LTileLayer, LMarker, LPopup } from "@vue-leaflet/vue-leaflet";
import api from "@/services/api";

export default {
  components: {
    LControl,
    LMap,
    LTileLayer,
    LCircle,
    LMarker,
    LPopup,
  },
  data() {
    return {
      zoom: 16,
      center: [-34.9225692, -57.9531812],
      radius: 0,
      radiusCenter: [-34.9225692, -57.9531812],
      markers: [],
      showErrorMessage: false,
    };
  },
  mounted() {
    this.radius = this.calculateNewRadius();
    this.radiusCenter = this.center;
    this.fetchMarkers();
  },
  computed: {
    showUpdateRadiusButton() {
      return this.centerHasChanged() || this.radius !== this.calculateNewRadius();
    },
  },
  methods: {
    zoomUpdated(newZoom) {
        this.zoom = newZoom;
    },
    centerUpdated(newCenter) {
        this.center = [newCenter.lat, newCenter.lng]; 
    },
    calculateNewRadius() {
        const minRadius = 50;
        const maxRadius = 5000000;
        const referenceZoom = 16;
        const referenceRadius = 500;

        const scale = Math.pow(2, referenceZoom - this.zoom);

        return Math.round(Math.max(minRadius, Math.min(maxRadius, referenceRadius * scale)));
    },
    centerHasChanged() {
        return this.radiusCenter[0] !== this.center[0] || this.radiusCenter[1] !== this.center[1];
    },
    goToSiteDetail(siteId) {
        this.$router.push(`/historic-site/${siteId}`);
    },
    async updateSearchRadius() {
        this.radius = this.calculateNewRadius();
        this.radiusCenter = this.center;
        this.fetchMarkers();
    },
    async fetchMarkers() {
        try {
            const radiusKm = this.radius / 100000000; 
            const response = await api.get(`/sites`, {
                params: {
                    lat: this.radiusCenter[0],
                    long: this.radiusCenter[1],
                    radius: radiusKm,
                    per_page: 100
                }
            });            

            this.markers = (response.data.data || [])
                .filter(site => site.lat != null && site.long != null)
                .map(site => ({
                    id: site.id,
                    lat: site.lat,
                    lon: site.long,
                    title: site.name,
                    description: site.description || 'Sin descripción',
                    cover_image: site.cover_image
                }));
            
            this.showErrorMessage = false;
        } catch (error) {
            console.error("Error fetching markers:", error);
            this.markers = [];
            this.showErrorMessage = true;
        }
    },
    handleMapClick(e) {
      console.log("Coordenadas clickeadas:", e.latlng);
      this.$emit('location-selected', { lat: e.latlng.lat, lng: e.latlng.lng });
    },
    onViewDetail(siteId) {
      this.$emit('view-detail', siteId);
    }
  }
};
</script>

<style scoped>
  .map-container {
      height: 100%;
      width: 100%;
      border-radius: 6px;
      position: relative;
      z-index: 1;
  }
  h3 {
    color: var(--color-texto);
  }
</style>
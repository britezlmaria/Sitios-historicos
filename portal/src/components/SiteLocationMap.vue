<script setup>
import { ref } from "vue";
import "leaflet/dist/leaflet.css";
import { LMap, LTileLayer, LMarker, LPopup } from "@vue-leaflet/vue-leaflet";
import { Icon } from "leaflet";

import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

defineProps({
    lat: {
        type: Number,
        required: true
    },
    long: {
        type: Number,
        required: true
    },
    site_name: {
        type: String,
        required: true
    },
    site_short_description: {
        type: String,
        required: true
    }
});

Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const defaultIcon = new Icon({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const mapZoom = ref(14);
</script>

<template>
    <div class="map-container mb-3">
        <l-map ref="map" v-model:zoom="mapZoom" :center="[lat, long]" style="height: 400px; width: 100%;">
            <l-tile-layer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>
            <l-marker :lat-lng="[lat, long]" :icon="defaultIcon">
                <l-popup>
                    <strong>{{ site_name }}</strong><br/>
                    {{ site_short_description }}
                </l-popup>
            </l-marker>
        </l-map>
    </div>
</template>

<style scoped>
.leaflet-container img,
.leaflet-container .leaflet-marker-icon,
.leaflet-container .leaflet-tile {
  max-width: none !important;
}
.map-container {
  width: 100%;
  border-radius: 10px;
  overflow: hidden;
}
</style>
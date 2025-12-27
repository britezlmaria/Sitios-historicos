import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import MaintenanceView from './views/MaintenanceView.vue'
import api from './services/api'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { 
  faHeart as faHeartSolid, 
  faStar as faStarSolid,
  faStarHalfStroke 
} from '@fortawesome/free-solid-svg-icons'
import { 
  faHeart as faHeartRegular,
  faStar as faStarRegular
} from '@fortawesome/free-regular-svg-icons'


library.add(
  faHeartSolid, 
  faHeartRegular,
  faStarSolid,     
  faStarRegular,   
  faStarHalfStroke 
)

async function bootstrap() {
    try {
        const res = await api.get("/flags");

        const app = createApp(
            res.data.portal_maintenance ? MaintenanceView : App,
            { message: res.data.portal_maintenance_message }
        );

        app.component('font-awesome-icon', FontAwesomeIcon)
        app.use(createPinia())
        app.use(router)

        app.mount("#app");
    } catch (e) {
        console.error("Error cargando configuración:", e);

        const app = createApp(App);
        app.use(createPinia())
        app.use(router)
        app.mount("#app");
    }
}

bootstrap();

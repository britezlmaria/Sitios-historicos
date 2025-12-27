import { defineStore } from "pinia";
import api from "@/services/api";

export const useUserStore = defineStore("user", {
  state: () => ({
    user: null,
    reviews: [],
    favorites: [],
    reviewsTotal: 0,
    favoritesTotal: 0,
  }),

  actions: {
    async loadUser() {
      try {
        const r = await api.get("/me");

        if (r.data.avatar) {
          const av = r.data.avatar;
          if (typeof av === 'string' && !av.startsWith('data:')) {
            r.data.avatar = `${av}?t=${Date.now()}`;
          }
        }

        this.user = r.data;
      } catch {
        this.user = null;
      }
    },

    async loadMyReviews(page = 1, order = 'desc', perPage = 25) {
    try {
      const r = await api.get("/me/reviews", {
        params: { 
            page, 
            per_page: perPage,
            order_by: order 
        },
      });
      this.reviews = r.data.data ?? r.data.reviews ?? []; 
      this.reviewsTotal = r.data.total ?? r.data.meta?.total ?? 0;
    } catch (e) {
      console.error("loadMyReviews failed", e);
      this.reviews = [];
      this.reviewsTotal = 0;
    }
  },
  
  async loadMyFavorites(page = 1, order = 'desc', perPage = 25) { 
    try {
      const r = await api.get("/me/favorites", {
        params: { 
            page, 
            per_page: perPage,
            order_by: order 
        },
      });
      
      this.favorites = r.data.data ?? r.data.favorites ?? [];
      this.favoritesTotal = r.data.total ?? r.data.meta?.total ?? 0;
      
    } catch (e) {
      console.error("loadMyFavorites failed", e);
      this.favorites = [];
      this.favoritesTotal = 0;
    }
  },


    async updateProfile(data) {
      try {
        const payload = { name: data.name };

        if (Object.prototype.hasOwnProperty.call(data, 'last_name')) {
          payload.last_name = data.last_name || '';
        }

        if (data.avatar) payload.avatar = data.avatar;

        const r = await api.put("/me", payload);

        if (r.data.avatar) {
          const av = r.data.avatar;
          if (typeof av === 'string' && !av.startsWith('data:')) {
            r.data.avatar = `${av}?t=${Date.now()}`;
          }
        }

        this.user = r.data;
        return r;
      } catch (e) {
        console.error("updateProfile failed", e);
        throw e;
      }
    },

    async logout() {
      try {
        await api.post("/logout");
      } catch (e) {
        console.warn("logout request failed", e);
      }
      this.user = null;

      try {
        if (typeof window !== "undefined") {
          window.location.href = "/";
        }
      } catch (e) {}
    },
  },
});

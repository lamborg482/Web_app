import { createApp } from 'vue'
import App from '/Users/timurmorozov/web_test/notes-app/src/App.vue'

if (process.env.NODE_ENV === 'production') {
    // Define the feature flag for production
    process.env.__VUE_PROD_HYDRATION_MISMATCH_DETAILS__ = true;
}

createApp(App).mount('#app');
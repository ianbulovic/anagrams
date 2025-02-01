import { createApp } from "vue";

import { VueCookieNext } from "vue-cookie-next";

// Components
import App from "./App.vue";

import "./index.css";

createApp(App).use(VueCookieNext).mount("#app");

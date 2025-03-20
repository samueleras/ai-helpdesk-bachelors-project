import { defineConfig } from "cypress";
import dotenv from "dotenv";

dotenv.config();

export default defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      config.chromeWebSecurity = false;
      config.browserPermissions = {
        notifications: "allow",
        popups: "allow",
      };
    },
    baseUrl: "http://localhost:5173",
  },
});

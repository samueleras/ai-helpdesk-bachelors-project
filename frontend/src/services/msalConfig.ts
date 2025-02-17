import { PublicClientApplication } from "@azure/msal-browser";

export const msalConfig = {
  auth: {
    clientId: import.meta.env.VITE_AZURE_CLIENT_ID,
    authority: import.meta.env.VITE_AZURE_TENANT_ID,
    redirectUri: window.location.origin,
  },
};

export const msalInstance = new PublicClientApplication(msalConfig);

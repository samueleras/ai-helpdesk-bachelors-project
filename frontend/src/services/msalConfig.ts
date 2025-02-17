import { PublicClientApplication } from "@azure/msal-browser";

export const msalConfig = {
  auth: {
    clientId: "07066dcd-ac65-4ca1-b4af-dde1a08edf6a",
    authority:
      "https://login.microsoftonline.com/7ff5cf6e-223d-4492-b2ca-6b72e5fdd040",
    redirectUri: window.location.origin,
  },
};

export const msalInstance = new PublicClientApplication(msalConfig);

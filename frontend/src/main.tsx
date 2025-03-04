import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Layout from "./pages/Layout.tsx";
import LoginPage from "./pages/LoginPage.tsx";
import AIChatPage from "./pages/AIChatPage.tsx";
import TicketPage from "./pages/TicketPage.tsx";
import MyTicketsPage from "./pages/MyTicketsPage.tsx";
import TechnicianPortalPage from "./pages/TechnicianPortalPage.tsx";
import ErrorPage from "./pages/ErrorPage.tsx";
import { MsalProvider } from "@azure/msal-react";
import { msalInstance } from "./services/msalConfig.ts";
import App from "./App.tsx";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { Provider } from "@/components/ui/provider";

const queryClient = new QueryClient();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <MsalProvider instance={msalInstance}>
      <Provider>
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <Routes>
              <Route element={<App />}>
                <Route index element={<LoginPage />} />
                <Route element={<Layout />}>
                  <Route path="ai-chat" element={<AIChatPage />} />
                  <Route
                    path="technician-portal"
                    element={<TechnicianPortalPage />}
                  />
                  <Route path="my-tickets" element={<MyTicketsPage />} />
                  <Route path="ticket/:id" element={<TicketPage />} />
                  <Route path="*" element={<ErrorPage />} />
                </Route>
              </Route>
            </Routes>
          </BrowserRouter>
          <ReactQueryDevtools />
        </QueryClientProvider>
      </Provider>
    </MsalProvider>
  </StrictMode>
);

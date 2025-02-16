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

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<LoginPage />} />
          <Route path="ai-chat" element={<AIChatPage />} />
          <Route path="technician-portal" element={<TechnicianPortalPage />} />
          <Route path="my-tickets" element={<MyTicketsPage />} />
          <Route path="ticket/:id" element={<TicketPage />} />
          <Route path="*" element={<ErrorPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </StrictMode>
);

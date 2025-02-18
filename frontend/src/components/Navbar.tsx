import { NavLink } from "react-router";
import { useMsal } from "@azure/msal-react";
import useAuthStore from "../stores/AuthStore";

export function Navbar() {
  const { instance } = useMsal();
  const { logout } = useAuthStore();

  const azurelogout = () => {
    instance.clearCache();
    logout();
    console.log("Logged out.");
  };

  return (
    <nav>
      <br />
      <NavLink to="/ai-chat" end>
        AI Chat
      </NavLink>
      <br />
      <NavLink to="/technician-portal">Technician Portal</NavLink> <br />
      <NavLink to="/my-tickets">My Tickets</NavLink>
      <br />
      <NavLink to="/" onClick={azurelogout}>
        Logout
      </NavLink>
    </nav>
  );
}

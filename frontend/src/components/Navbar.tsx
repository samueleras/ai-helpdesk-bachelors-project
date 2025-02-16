import { NavLink } from "react-router";

export function Navbar() {
  return (
    <nav>
      <NavLink to="/" end>
        Login
      </NavLink>
      <br />
      <NavLink to="/ai-chat" end>
        AI Chat
      </NavLink>
      <br />
      <NavLink to="/technician-portal">Technician Portal</NavLink> <br />
      <NavLink to="/my-tickets">My Tickets</NavLink>
    </nav>
  );
}

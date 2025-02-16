import { Outlet } from "react-router-dom";
import { Navbar } from "../components/Navbar";

const Layout = () => {
  return (
    <>
      {<Navbar />}
      {/* handle route error, display error page instead of outlet */}
      <div>{<Outlet />}</div>
      <p>footer</p>
    </>
  );
};

export default Layout;

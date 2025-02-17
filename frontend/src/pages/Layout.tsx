import { Outlet } from "react-router-dom";
import { Navbar } from "../components/Navbar";
import useAuthToken from "../hooks/useAuthToken";

const Layout = () => {
  useAuthToken();
  return (
    <>
      {<Navbar />}
      <div>{<Outlet />}</div>
      <p>footer</p>
    </>
  );
};

export default Layout;

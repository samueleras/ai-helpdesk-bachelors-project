import { Outlet } from "react-router-dom";
import { Navbar } from "../components/Navbar";

const Layout = () => {
  return (
    <>
      {<Navbar />}
      <div>{<Outlet />}</div>
      <p>footer</p>
    </>
  );
};

export default Layout;

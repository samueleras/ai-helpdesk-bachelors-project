import { Outlet } from "react-router-dom";
import { Navbar } from "../components/Navbar";
import useAuthStore from "@/stores/AuthStore";

const Layout = () => {
  const { accessToken } = useAuthStore();
  if (!accessToken) {
    return;
  }
  return (
    <>
      {<Navbar />}
      <div>{<Outlet />}</div>
    </>
  );
};

export default Layout;

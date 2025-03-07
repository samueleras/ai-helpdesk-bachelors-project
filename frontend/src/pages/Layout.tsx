import { Outlet } from "react-router-dom";
import { Navbar } from "../components/Navbar";
import useAuthStore from "@/stores/AuthStore";
import { Box } from "@chakra-ui/react";

const Layout = () => {
  const { accessToken } = useAuthStore();
  if (!accessToken) {
    return;
  }
  return (
    <>
      {<Navbar />}
      <Box backgroundColor={"darkslategray"}>{<Outlet />}</Box>
    </>
  );
};

export default Layout;

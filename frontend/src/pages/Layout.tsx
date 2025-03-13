import { Outlet, useNavigate } from "react-router-dom";
import { Navbar } from "../components/Navbar";
import useAuthStore from "@/stores/AuthStore";
import { Box } from "@chakra-ui/react";

const Layout = () => {
  const { accessToken, user } = useAuthStore();
  const navigate = useNavigate();
  if (!accessToken || user.group == "") {
    navigate("/");
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

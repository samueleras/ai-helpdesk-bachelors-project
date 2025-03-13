import { Outlet, useNavigate } from "react-router-dom";
import { Navbar } from "../components/Navbar";
import useAuthStore from "@/stores/AuthStore";
import { Box } from "@chakra-ui/react";
import { useEffect } from "react";

const Layout = () => {
  const { accessToken, user } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (!accessToken || user.group == "") {
      navigate("/");
    }
  }, []);

  if (!accessToken || user.group == "") {
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

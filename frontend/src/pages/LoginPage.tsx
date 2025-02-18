import { useMsal } from "@azure/msal-react";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import useAuthStore from "../stores/AuthStore";
import useUsersMe from "../hooks/useUserMe";

const LoginPage = () => {
  const { instance } = useMsal();
  const navigate = useNavigate();
  const { user, login } = useAuthStore();

  useEffect(() => {
    if (user && Object.keys(user).length > 0) {
      console.log("Logged in successfully!");
      console.log("User ", user);
      if (user.group === "users") navigate("/my-tickets");
      if (user.group === "technicians") navigate("/technician-portal");
    }
  }, [user]);

  const handleLogin = async () => {
    try {
      instance.clearCache();
      const response = await instance.loginPopup();
      instance.setActiveAccount(response.account);
      const accessToken = response.accessToken;
      const fetchedUser = await useUsersMe(accessToken);
      login(fetchedUser);
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  return (
    <div>
      <h1>Login with Microsoft</h1>
      <button onClick={handleLogin}>Sign in with Microsoft</button>
    </div>
  );
};

export default LoginPage;

import { useMsal } from "@azure/msal-react";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import useAuthStore from "../stores/AuthStore";

const LoginPage = () => {
  const { instance } = useMsal();
  const navigate = useNavigate();
  const { user, login } = useAuthStore();

  useEffect(() => {
    if (user) {
      console.log("Logged in successfully!");
      if (user.group === "users") navigate("/my-tickets");
      if (user.group === "technicians") navigate("/technician-portal");
    }
  }, [user]);

  const handleLogin = async () => {
    try {
      instance.clearCache();
      const response = await instance.loginPopup();
      const accessToken = response.accessToken;
      await fetchUserInfo(accessToken);
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  const fetchUserInfo = async (accessToken: string) => {
    const endpoint = import.meta.env.VITE_BACKEND_URL + "/users/me";
    const response = await fetch(endpoint, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    const fetchedUser = await response.json();
    login(fetchedUser);
  };

  return (
    <div>
      <h1>Login with Microsoft</h1>
      <button onClick={handleLogin}>Sign in with Microsoft</button>
    </div>
  );
};

export default LoginPage;

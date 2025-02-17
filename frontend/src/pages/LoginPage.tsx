import { useMsal } from "@azure/msal-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const LoginPage = () => {
  const { instance } = useMsal();
  const [userGroup, setUserGroup] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (userGroup) {
      console.log("Logged in successfully!");
      if (userGroup === "users") navigate("/my-tickets");
      if (userGroup === "technicians") navigate("/technician-portal");
    }
  }, [userGroup]);

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
    const data = await response.json();
    setUserGroup(data.group);
  };

  return (
    <div>
      <h1>Login with Microsoft</h1>
      <button onClick={handleLogin}>Sign in with Microsoft</button>
    </div>
  );
};

export default LoginPage;

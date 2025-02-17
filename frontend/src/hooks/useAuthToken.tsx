import { useMsal } from "@azure/msal-react";
import { useEffect } from "react";
import {
  InteractionRequiredAuthError,
  InteractionStatus,
} from "@azure/msal-browser";
import { useNavigate } from "react-router-dom";

const useAuthToken = () => {
  const { instance, inProgress } = useMsal();
  const navigate = useNavigate();

  useEffect(() => {
    const tokenRequest = {
      scopes: ["openid"],
    };

    const getToken = async () => {
      try {
        if (!instance.getActiveAccount())
          throw new InteractionRequiredAuthError("No active account. Log in.");
        const response = await instance.acquireTokenSilent(tokenRequest);
        console.log("Access Token:", response.accessToken);
      } catch (error) {
        if (error instanceof InteractionRequiredAuthError) {
          navigate("/");
        } else {
          console.error("An unknown error occurred:", error);
        }
      }
    };

    if (inProgress === InteractionStatus.None) {
      getToken();
    }
  }, [instance, inProgress]);
};

export default useAuthToken;

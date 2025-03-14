import { useMsal } from "@azure/msal-react";
import { useEffect, useState } from "react";
import {
  InteractionRequiredAuthError,
  InteractionStatus,
} from "@azure/msal-browser";
import { useNavigate } from "react-router-dom";
import useUsersMe from "./useUserMe";
import useAuthStore from "../stores/AuthStore";

const useAuthToken = () => {
  const { instance, inProgress } = useMsal();
  const navigate = useNavigate();
  const { accessToken, setAccessToken, setUser } = useAuthStore();
  const [expiresOn, setExpiresOn] = useState(new Date());
  const { data: fetchedUser, refetch } = useUsersMe(accessToken);

  useEffect(() => {
    fetchedUser && accessToken && setUser(fetchedUser);
  }, [fetchedUser, accessToken]);

  const tokenRequest = {
    scopes: ["openid"],
  };

  const getToken = async () => {
    try {
      if (!instance.getActiveAccount())
        throw new InteractionRequiredAuthError("No active account. Log in.");
      const response = await instance.acquireTokenSilent(tokenRequest);
      instance.setActiveAccount(response.account);
      const accessToken = response.accessToken;
      response.expiresOn && setExpiresOn(response.expiresOn);
      setAccessToken(accessToken);
      refetch();
    } catch (error) {
      if (error instanceof InteractionRequiredAuthError) {
        navigate("/");
      } else {
        console.error("An unknown error occurred:", error);
      }
    }
  };

  useEffect(() => {
    if (inProgress === InteractionStatus.None) {
      getToken();
    }
  }, [instance, inProgress]);

  useEffect(() => {
    if (expiresOn) {
      const timeUntilExpiry = new Date(expiresOn).getTime() - Date.now();
      const refreshTime = timeUntilExpiry - 60000; //the time of 1 minute before the access token expires
      if (refreshTime > 0) {
        const timeout = setTimeout(getToken, refreshTime); //Call auth refresh 1 minute before expiration
        return () => clearTimeout(timeout); //Clear timeout on useeffect rerun to avoid multiple timeouts
      }
    }
  }, [expiresOn]);
};

export default useAuthToken;

import { User } from "../entities/User";
import APIClient from "../services/apiClient";

const userMeClient = new APIClient<User>("/api/users/me");

const useUsersMe = (accessToken: string) => {
  return userMeClient.get(accessToken);
};

export default useUsersMe;

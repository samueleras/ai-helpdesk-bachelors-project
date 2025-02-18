import { User } from "../entities/User";
import APIClient from "../services/apiClient";

const carClient = new APIClient<User>("/users/me");

const useUsersMe = (accessToken: string) => {
  return carClient.get(accessToken);
};

export default useUsersMe;

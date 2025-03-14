import { useQuery } from "@tanstack/react-query";
import { User } from "../entities/User";
import APIClient from "../services/apiClient";

const userMeClient = new APIClient<User>("/api/users/me");

const useUsersMe = (accessToken: string) => {
  return useQuery<User>({
    queryKey: ["user"],
    queryFn: () => userMeClient.get(accessToken),
    retry: 2,
    enabled: false,
  });
};

export default useUsersMe;

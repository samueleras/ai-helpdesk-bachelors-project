import { create } from "zustand";
import { User } from "../entities/User";
interface AuthStore {
  user: User;
  accessToken: string;
  login: (user: User, accessToken: string) => void;
  logout: () => void;
}

const useAuthStore = create<AuthStore>((set) => ({
  user: { user_name: "", group: "", user_id: "" },
  accessToken: "",
  login: (user: User, accessToken: string) =>
    set(() => ({ user, accessToken })),
  logout: () =>
    set(() => ({
      user: { user_name: "", group: "", user_id: "" },
      accessToken: "",
    })),
}));

export default useAuthStore;

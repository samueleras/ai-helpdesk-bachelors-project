import { create } from "zustand";
import { User } from "../entities/User";
interface AuthStore {
  user: User;
  accessToken: string;
  setUser: (user: User) => void;
  setAccessToken: (accessToken: string) => void;
  logout: () => void;
}

const useAuthStore = create<AuthStore>((set) => ({
  user: { user_name: "", group: "", user_id: "" },
  accessToken: "",
  setUser: (user: User) => set(() => ({ user })),
  setAccessToken: (accessToken: string) => set(() => ({ accessToken })),
  logout: () =>
    set(() => ({
      user: { user_name: "", group: "", user_id: "" },
      accessToken: "",
    })),
}));

export default useAuthStore;

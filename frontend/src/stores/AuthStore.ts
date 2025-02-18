import { create } from "zustand";
import { User } from "../entities/User";
interface AuthStore {
  user: User;
  login: (user: User) => void;
  logout: () => void;
}

const useAuthStore = create<AuthStore>((set) => ({
  user: {},
  login: (user: User) => set(() => ({ user })),
  logout: () => set(() => ({ user: {} })),
}));

export default useAuthStore;

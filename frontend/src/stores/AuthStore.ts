import { create } from "zustand";

interface User {
  user_id?: string;
  user?: string;
  group?: string;
}

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

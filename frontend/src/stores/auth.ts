import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { AuthResult, User } from "@/types";

interface AuthState {
  token: string | null;
  user: User | null;
  setAuth: (result: AuthResult) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      setAuth: (result) => set({ token: result.token.access_token, user: result.user }),
      logout: () => set({ token: null, user: null }),
      isAuthenticated: () => Boolean(get().token),
    }),
    { name: "whatsapp-saas-auth" }
  )
);

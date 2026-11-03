import type { UserInfo } from "@/app/types/user";
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface UserState {
  token: string | null;
  userInfo: UserInfo | null;
  isLogin: boolean;
  setToken: (token: string | null) => void;
  setUserInfo: (userInfo: UserInfo | null) => void;
  logout: () => void;
  triggerRefreshUser: (isLogin: boolean) => void;
}
export const useUserStore = create(
  persist<UserState>(
    (set) => ({
      token: null,
      userInfo: null,
      isLogin: false,
      setToken: (token) => set({ token }),
      setUserInfo: (userInfo) => set({ userInfo }),
      logout: () => set({ token: null, userInfo: null }),
      triggerRefreshUser: (isLogin) => set({ isLogin }),
    }),
    {
      name: "userStore",
      partialize: (state) => ({ token: state.token }) as UserState,
    },
  ),
);

export const getUserState = () => useUserStore.getState();

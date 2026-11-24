"use client";
import { useUserStore } from "@/app/store/userStore";
import { useRouter } from "next/navigation";

export function useRouterPush() {
  const router = useRouter();
  const userInfo = useUserStore((state) => state.userInfo);

  const routePush = (path: string) => {
    const redirect = encodeURIComponent(path);
    if (!userInfo?.uid) {
      router.push(`/login?redirect=${redirect}`);
      return;
    }
    router.push(path);
  };
  return routePush;
}

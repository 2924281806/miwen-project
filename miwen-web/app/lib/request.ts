import { getUserState } from "@/app/store/userStore";
import type { ApiResult } from "@/app/types/user";
import { whiteList } from "@/app/utils/whiteList";
import type { AxiosResponse } from "axios";
import axios from "axios";
import { useRouter } from "next/router";

const baseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// 401 防重复跳转控制
let isHandling401 = false;
let timer: ReturnType<typeof setTimeout> | null = null;

// 并发防抖锁：只锁读取动作，不缓存token本身
let pendingTokenPromise: Promise<string> | null = null;

/** 实时从 store 获取最新 token */
const fetchTokenFromStore = async (): Promise<string> => {
  const accessToken = getUserState().token;
  return accessToken ?? "";
};

/** 带并发防抖锁获取token */
const getToken = async (): Promise<string> => {
  if (pendingTokenPromise) {
    return pendingTokenPromise;
  }
  pendingTokenPromise = (async () => {
    try {
      return await fetchTokenFromStore();
    } catch (err) {
      console.error("读取token失败：", err);
      return "";
    } finally {
      pendingTokenPromise = null;
    }
  })();
  return pendingTokenPromise;
};

/**
 * 退出登录专用：清空并发锁 + 清空zustand里的token
 * ✅ 登录成功不要调用这个！登录只需要 setToken
 */
export const clearToken = () => {
  pendingTokenPromise = null;
  getUserState().triggerRefreshUser(false);
  getUserState().logout();
};

const request = axios.create({
  baseURL,
  timeout: 10000,
});

// 请求拦截器
request.interceptors.request.use(
  async (config) => {
    if (whiteList.some((item) => config?.url?.includes(item))) {
      return config;
    }
    const token = await getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      return config;
    }
    return Promise.reject(new Error("无token，取消请求"));
  },
  (err) => Promise.reject(err),
);

// ✅【修复类型】响应拦截器只返回 AxiosResponse，不在拦截器里 return res.data
request.interceptors.response.use(
  (res: AxiosResponse<ApiResult>) => {
    return res;
  },
  async (err) => {
    const response = err.response;
    const url = response?.config?.url ?? "";

    if (
      response?.status === 401 &&
      !whiteList.some((item) => url.includes(item))
    ) {
      if (!isHandling401) {
        isHandling401 = true;
        // 401 跳转到首页
        const router = useRouter();
        router.push("/");
        clearToken();
        clearTimeout(timer ?? undefined);
        timer = setTimeout(() => {
          isHandling401 = false;
        }, 1000);
      }
    }
    return Promise.reject(err);
  },
);

export { request };

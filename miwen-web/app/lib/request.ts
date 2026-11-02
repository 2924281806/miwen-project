import type { AxiosRequestConfig, AxiosResponse } from "axios";
import axios from "axios";
import { useState } from "react";
// 后端统一返回结构
interface ApiResult<T = unknown> {
  code: number;
  message: string;
  data: T;
}
const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
// const [token, setToken] = useState("");
// 缓存token + 锁（防止并发多次请求token）
let token: string = "";
let isFetchingToken = false;
let tokenQueue: ((t: string) => void)[] = [];

// 获取token的请求函数
const fetchToken = async (): Promise<string> => {
  const res = await axios.post(`${baseUrl}/api/auth/login`, {
    email: "tom@example.com",
    password: "123456",
  });
  return res.data?.data?.access_token || "";
};

// 获取token（带排队锁）
const getToken = async (): Promise<string> => {
  if (token) {
    return Promise.resolve(token);
  }
  return new Promise((resolve) => {
    tokenQueue.push(resolve);
    if (isFetchingToken) {
      return;
    }
    isFetchingToken = true;
    fetchToken()
      .then((newToken) => {
        token = newToken;
        tokenQueue.forEach((resolveFn) => resolveFn(newToken));
        tokenQueue = [];
      })
      .catch(() => {
        tokenQueue.forEach((resolveFn) => resolveFn(""));
        tokenQueue = [];
      })
      .finally(() => {
        isFetchingToken = false;
      });
  });
};

// axios实例
const requestInstance = axios.create({
  baseURL: baseUrl,
  timeout: 10000,
});

// 请求拦截器
requestInstance.interceptors.request.use(
  (config) => {
    return config;
  },
  (err) => Promise.reject(err),
);

// ✅ 【重点修复】响应拦截器不再return response.data，原样返回response，消除TS报错
requestInstance.interceptors.response.use(
  (response: AxiosResponse<ApiResult>) => {
    return response;
  },
  (err) => {
    // 错误处理
    const msg = err.response?.data?.message || "请求失败";
    console.error("请求错误：", msg);

    // 401 未登录跳转（仅客户端）
    if (err.response?.status === 401 && typeof window !== "undefined") {
      clearToken();
      // location.href = "/login";
    }
    return Promise.reject(err);
  },
);

// 清除token
export const clearToken = () => {
  token = "";
};

// ✅ 底层baseRequest：增加泛型，内部剥壳 res.data，对外返回 ApiResult<T>
const baseRequest = async <T>(
  config: AxiosRequestConfig,
): Promise<ApiResult<T>> => {
  const tk = await getToken();
  if (!tk) {
    throw new Error("token获取失败");
  }
  const axiosConfig: AxiosRequestConfig = {
    ...config,
    headers: {
      Authorization: `Bearer ${tk}`,
      ...config.headers,
    },
  };
  const res = await requestInstance<ApiResult<T>>(axiosConfig);
  return res.data;
};

/**
 * 导出 request 对象，支持 request.get / request.post
 * 第一个参数: 请求地址
 * 第二个参数: 请求参数
 * 第三个参数: 额外axios配置（headers等）
 */
export const request = {
  get: async <T = unknown, D = unknown>(
    url: string,
    params?: D,
    config?: AxiosRequestConfig,
  ) => {
    return baseRequest<T>({
      url,
      method: "get",
      params,
      ...config,
    });
  },
  post: async <T = unknown, D = unknown>(
    url: string,
    data?: D,
    config?: AxiosRequestConfig,
  ) => {
    return baseRequest<T>({
      url,
      method: "post",
      data,
      ...config,
    });
  },
  put: async <T = unknown, D = unknown>(
    url: string,
    data?: D,
    config?: AxiosRequestConfig,
  ) => {
    return baseRequest<T>({
      url,
      method: "put",
      data,
      ...config,
    });
  },
  delete: async <T = unknown, D = unknown>(
    url: string,
    data?: D,
    config?: AxiosRequestConfig,
  ) => {
    return baseRequest<T>({
      url,
      method: "delete",
      data,
      ...config,
    });
  },
};

import axios from "axios";

const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

// 缓存token + 锁（防止并发多次请求token）
let token: string = "";
let isFetchingToken = false;
let tokenQueue: ((t: string) => void)[] = [];

// 获取token的请求函数
const fetchToken = async (): Promise<string> => {
  console.log("fetchToken");
  const res = await axios.post(`${baseUrl}/api/auth/login`, {
    username: "string",
    email: "user@example.com",
    password: "string",
  });
  return res.data?.data?.access_token || "";
};

// axios实例
const requestInstance = axios.create({
  baseURL: baseUrl,
  timeout: 10000,
});

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
        tokenQueue.forEach((resolve) => resolve(newToken));
        tokenQueue = [];
      })
      .catch(() => {
        tokenQueue.forEach((resolve) => resolve(""));
        tokenQueue = [];
      })
      .finally(() => {
        isFetchingToken = false;
      });
  });
};

// 核心底层方法，自动带上token
const baseRequest = async (config: any) => {
  const tk = await getToken();
  if (!tk) {
    throw new Error("token获取失败");
  }
  const axiosConfig: any = {
    ...config,
    headers: {
      Authorization: `Bearer ${tk}`,
      ...config.headers,
    },
  };
  console.log("axiosConfig", axiosConfig);
  return requestInstance(axiosConfig);
};

// 请求拦截器
requestInstance.interceptors.request.use(
  (config) => {
    return config;
  },
  (err) => Promise.reject(err),
);

// 响应拦截器
requestInstance.interceptors.response.use(
  (res) => {
    // 这里根据你的后端返回结构调整
    return res.data;
  },
  (err) => {
    // 错误处理
    const msg = err.response?.data?.message || "请求失败";
    console.error("请求错误：", msg);

    // 401 未登录跳转（仅客户端）
    if (err.response?.status === 401 && typeof window !== "undefined") {
      clearToken();
      // 跳转登录
      //   location.href = "/login";
    }
    return Promise.reject(err);
  },
);
// 清除token
export const clearToken = () => {
  token = "";
};

/**
 *导出 request 对象，支持 request.get / request.post
 *第一个参数: 请求地址
 *第二个参数: 请求参数
 *第三个参数: 额外axios配置（headers等）
 */
export const request = {
  get: async (url: string, params?: any, config?: any) => {
    return baseRequest({
      url,
      method: "get",
      params,
      ...config,
    });
  },
  post: async (url: string, data?: any, config?: any) => {
    return baseRequest({
      url,
      method: "post",
      data,
      ...config,
    });
  },
  put: async (url: string, data?: any, config?: any) => {
    return baseRequest({
      url,
      method: "put",
      data,
      ...config,
    });
  },
  delete: async (url: string, data?: any, config?: any) => {
    return baseRequest({
      url,
      method: "delete",
      data,
      ...config,
    });
  },
};

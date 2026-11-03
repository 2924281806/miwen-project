import type {
  ApiResult,
  LoginDto,
  LoginInfo,
  RefreshTokenDto,
  RegisterDto,
  UpdateProfileDto,
  UserInfo,
} from "@/app/types/user";
import { request } from "./request";

/** 获取当前用户信息 */
export const getMyUser = async () => {
  const res = await request.get<ApiResult<UserInfo>>("/api/user/me");
  return res.data;
};

/** 注册 */
export const register = async (data: RegisterDto) => {
  const res = await request.post<ApiResult<UserInfo>>(
    "/api/auth/register",
    data,
  );
  return res.data;
};

/** 刷新token */
export const refreshToken = async (data: RefreshTokenDto) => {
  const res = await request.post<
    ApiResult<{ access_token: string; refresh_token: string }>
  >("/api/auth/refresh-token", data);
  return res.data;
};

/**
 * 更新个人资料
 * 仅允许修改 avatar（头像）与 bio（个性签名），username / email 不可修改
 * ⚠️ 原代码函数名 login 是错误命名，改成 updateProfile
 */
export const updateProfile = async (data: UpdateProfileDto) => {
  const res = await request.put<ApiResult<UserInfo>>("/api/user/me", data);
  return res.data;
};

/** 获取其他用户信息（你这里用post，非常规，按你原有写法保留） */
export const otherUserInfo = async (user_id: string) => {
  const res = await request.post<ApiResult<UserInfo>>(`/api/user/${user_id}`);
  return res.data;
};
// 登录
export const login = async (params: LoginInfo) => {
  const res = await request.post<ApiResult<LoginDto>>(
    "/api/auth/login",
    params,
  );
  return res.data;
};
// 退出登录
export const logout = async () => {
  const res = await request.post<ApiResult<UserInfo>>("/api/user/login");
  return res.data;
};

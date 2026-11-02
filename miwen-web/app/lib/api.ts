import type {
  LoginDto,
  LoginInfo,
  RefreshTokenDto,
  RegisterDto,
  UpdateProfileDto,
  UserInfo,
} from "@/app/types/user";
import { request } from "./request";

/** 获取当前用户信息 */
export const getMyUser = () => {
  return request.get<UserInfo>("/api/user/me");
};

/** 注册 */
export const register = (data: RegisterDto) => {
  return request.post<UserInfo>("/api/auth/register", data);
};

/** 刷新token */
export const refreshToken = (data: RefreshTokenDto) => {
  return request.post<{ access_token: string; refresh_token: string }>(
    "/api/auth/refresh-token",
    data,
  );
};

/**
 * 更新个人资料
 * 仅允许修改 avatar（头像）与 bio（个性签名），username / email 不可修改
 * ⚠️ 原代码函数名 login 是错误命名，改成 updateProfile
 */
export const updateProfile = (data: UpdateProfileDto) => {
  return request.put<UserInfo>("/api/user/me", data);
};

/** 获取其他用户信息（你这里用post，非常规，按你原有写法保留） */
export const otherUserInfo = (user_id: string) => {
  return request.post<UserInfo>(`/api/user/${user_id}`);
};
// 登录
export const login = (params: LoginInfo) => {
  return request.post<LoginDto>("/api/auth/login", params);
};
// 退出登录
export const logout = () => {
  return request.post<UserInfo>("/api/user/login");
};

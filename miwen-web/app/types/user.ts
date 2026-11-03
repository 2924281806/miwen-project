// 用户信息返回结构
export interface UserInfo {
  id: number;
  uid: string;
  username: string;
  email: string;
  avatar?: string;
  bio?: string;
}

// 注册入参
export interface RegisterDto {
  username: string;
  email: string;
  password: string;
}

// 刷新token入参
export interface RefreshTokenDto {
  refresh_token: string;
}

// 更新个人资料入参（avatar / bio）
export interface UpdateProfileDto {
  avatar?: string;
  bio?: string;
}

export interface LoginDto {
  access_token: string;
}
export interface LoginInfo {
  username: string;
  password: string;
}

export interface ApiResult<T = unknown> {
  code: number;
  message: string;
  data: T;
}

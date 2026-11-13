// 用户信息（对齐后端 UserOut / UserPublicOut 返回字段）
export interface UserInfo {
  id: number;
  uid: string;
  username: string;
  email?: string | null;
  nickname?: string | null;
  avatar?: string | null;
  /** 个性签名，对应后端 signature 字段 */
  signature?: string | null;
  status?: number;
  level?: number;
  points?: number;
  last_login_at?: string | null;
  created_at?: string;
  updated_at?: string;
  /** 是否关注该用户：0未关注，1已关注 */
  is_follow?: number;
  /** 是否是管理员：0不是，1是 */
  is_admin?: number;
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

// 登录返回的 token 信息（对齐后端 TokenOut）
export interface LoginDto {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}
// 刷新 token 返回（对齐后端 RefreshTokenOut）
export interface RefreshTokenOutDto {
  access_token: string;
  token_type: string;
  expires_in: number;
}
export interface LoginInfo {
  username: string;
  password: string;
}

export interface ApiResult<T = unknown> {
  code: number;
  /** 提示信息，所有接口（含上传）统一使用 msg 字段 */
  msg?: string;
  data: T;
}

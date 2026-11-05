import type {
  CreatePostDto,
  CreatePostDtoParams,
  ForumListDto,
  ForumListDtoParams,
} from "@/app/types/forum";
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
  const res = await request.post<ApiResult<RegisterDto>>(
    "/api/auth/register",
    data,
  );
  return res.data;
};

/** 刷新token */
export const refreshToken = async (data: RefreshTokenDto) => {
  const res = await request.post<
    ApiResult<{ access_token: string; refresh_token: string }>
  >("/api/auth/refreshToken", data);
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
export const otherUserInfo = async (uid: string) => {
  const res = await request.post<ApiResult<UserInfo>>(`/api/user/${uid}`);
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
  const res = await request.post<ApiResult<UserInfo>>("/api/auth/logout");
  return res.data;
};
// 上传图片
export const uploadImage = async (data: FormData) => {
  const res = await request.post<ApiResult<FormData>>("/api/uploadImage", data);
  return res.data;
};

export const getForumList = async (params: ForumListDtoParams) => {
  const res = await request.get<ApiResult<ForumListDto>>("/api/forum/list", {
    params,
  });
  return res.data;
};

export const getAllForumList = async () => {
  const res = await request.get<ApiResult<ForumListDto[]>>(
    "/api/forum/allForumList",
  );
  return res.data;
};

export const createPost = async (data: CreatePostDtoParams) => {
  const res = await request.post<ApiResult<CreatePostDto>>(
    "/api/forum/createForum",
    data,
  );
  return res.data;
};

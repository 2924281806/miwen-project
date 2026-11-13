import type {
  CreateForumDto,
  CreateForumDtoParams,
  ForumCategoryDto,
  ForumListDto,
  ForumListDtoParams,
  PageResult,
} from "@/app/types/forum";
import type {
  CreatePostDto,
  CreatePostParams,
  GetPostParams,
  HotTopicsImageOut,
} from "@/app/types/topic";
import type {
  ApiResult,
  LoginDto,
  LoginInfo,
  RefreshTokenDto,
  RefreshTokenOutDto,
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

/** 注册（后端返回注册后的用户信息 UserOut） */
export const register = async (data: RegisterDto) => {
  const res = await request.post<ApiResult<UserInfo>>(
    "/api/auth/register",
    data,
  );
  return res.data;
};

/** 刷新token（后端只返回 access_token / token_type / expires_in） */
export const refreshToken = async (data: RefreshTokenDto) => {
  const res = await request.post<ApiResult<RefreshTokenOutDto>>(
    "/api/auth/refreshToken",
    data,
  );
  return res.data;
};

/**
 * 更新个人资料
 * 仅允许修改 avatar（头像）与 bio（个性签名），username / email 不可修改
 * ⚠️ 原代码函数名 login 是错误命名，改成 updateProfile
 */
export const updateProfile = async (data: UpdateProfileDto) => {
  const res = await request.post<ApiResult<UserInfo>>(
    "/api/user/updateUser",
    data,
  );
  return res.data;
};

/** 获取其他用户信息（后端为 GET /api/user/{uid}） */
export const otherUserInfo = async (uid: string) => {
  const res = await request.get<ApiResult<UserInfo>>(`/api/user/${uid}`);
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
// 退出登录（后端返回 data 为 null）
export const logout = async () => {
  const res = await request.post<ApiResult<null>>("/api/auth/logout");
  return res.data;
};
// 上传图片
export const uploadImage = async (data: FormData) => {
  const res = await request.post<ApiResult<string>>("/api/uploadImage", data);
  return res.data;
};

export const getForumList = async (params: ForumListDtoParams) => {
  const res = await request.get<ApiResult<PageResult<ForumListDto>>>(
    "/api/forum/list",
    { params },
  );
  return res.data;
};

export const getAllForumList = async () => {
  const res = await request.get<ApiResult<ForumListDto[]>>(
    "/api/forum/allForumList",
  );
  return res.data;
};

/** 获取所有圈子分类（用于新建圈子时选择分类，value 必须是分类真实 id） */
export const getAllCategoryList = async () => {
  const res = await request.get<ApiResult<ForumCategoryDto[]>>(
    "/api/forumCategory/allCategoryList",
  );
  return res.data;
};

export const createForum = async (data: CreateForumDtoParams) => {
  const res = await request.post<ApiResult<CreateForumDto>>(
    "/api/forum/createForum",
    data,
  );
  return res.data;
};

export const createPost = async (data: CreatePostParams) => {
  const res = await request.post<ApiResult<CreatePostDto>>(
    "/api/topic/createPost",
    data,
  );
  return res.data;
};
export const getPostList = async (params: GetPostParams) => {
  const res = await request.get<ApiResult<PageResult<CreatePostDto>>>(
    "/api/topic/list",
    { params },
  );
  return res.data;
};

// 获取所有帖子（用于新建帖子时选择帖子分类，value 必须是帖子真实 id）
export const getAllPostList = async () => {
  const res = await request.get<ApiResult<CreatePostDto[]>>("/api/topic/list");
  return res.data;
};

// 点赞帖子（登录用户，每个帖子只能点赞一次）
export const likeTopic = async (topic_id: number) => {
  const res = await request.post<ApiResult<CreatePostDto>>(
    `/api/topic/like/${topic_id}`,
  );
  return res.data;
};

/** 取消点赞帖子（登录用户，每个帖子只能取消点赞一次） */
export const unlikeTopic = async (topic_id: number) => {
  const res = await request.post<ApiResult<CreatePostDto>>(
    `/api/topic/unlike/${topic_id}`,
  );
  return res.data;
};

/** 收藏帖子（登录用户，每个帖子只能收藏一次） */
export const favoriteTopic = async (topic_id: number) => {
  const res = await request.post<ApiResult<CreatePostDto>>(
    `/api/topic/favorite/${topic_id}`,
  );
  return res.data;
};

// 取消收藏帖子（登录用户，每个帖子只能取消收藏一次）
export const unfavoriteTopic = async (topic_id: number) => {
  const res = await request.post<ApiResult<CreatePostDto>>(
    `/api/topic/unfavorite/${topic_id}`,
  );
  return res.data;
};

/** 获取帖子详情（登录用户） */
export const getTopicListDetail = async (topic_id: number) => {
  const res = await request.get<ApiResult<CreatePostDto>>(
    `/api/topic/listDetail/${topic_id}`,
  );
  return res.data;
};

export const getForumDetail = async (forum_id: number) => {
  const res = await request.get<ApiResult<ForumListDto>>(
    `/api/forum/forumDetail/${forum_id}`,
  );
  return res.data;
};

export const getHotPostList = async () => {
  const res = await request.get<ApiResult<CreatePostDto[]>>("/api/common/hot");
  return res.data;
};

export const getHotPostImages = async () => {
  const res = await request.get<ApiResult<string[]>>("/api/common/hot/images");
  return res.data;
};

export const getHotPostImageList = async () => {
  const res = await request.get<ApiResult<HotTopicsImageOut[]>>(
    "/api/hotTopicsImage/hotImageList",
  );
  return res.data;
};

// 获取所有用户（登录用户）
export const getAllUserList = async () => {
  const res = await request.get<ApiResult<PageResult<UserInfo>>>(
    "/api/common/userList",
  );
  return res.data;
};

export const followUser = async (uid: number) => {
  const res = await request.post<ApiResult<UserInfo>>(
    `/api/user/follow/${uid}`,
  );
  return res.data;
};

export const unfollowUser = async (uid: number) => {
  const res = await request.post<ApiResult<UserInfo>>(
    `/api/user/unfollow/${uid}`,
  );
  return res.data;
};

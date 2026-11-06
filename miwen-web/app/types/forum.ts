export interface ForumListDto {
  id: number;
  forum_id: number;
  uid: number;
  category_id: number;
  category_name: string;
  name: string;
  description: string | null;
  icon: string | null;
  status: number;
  join_type: "public" | "private";
  created_at: string;
  updated_at: string;
}

export interface PageResult<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  pages: number;
}

export interface ForumListDtoParams {
  page: number;
  pageSize?: number;
  name?: string;
  uid?: number;
  keyword?: string;
  status?: number;
  include_deleted?: boolean;
  category_id?: number;
}
export interface ForumCategoryDto {
  id: number;
  name: string;
  created_at: string;
  deleted_at: string | null;
}

export interface CreateForumDtoParams {
  name: string;
  description: string;
  icon?: string;
  category_id?: number;
  join_type: "public" | "private";
}
// 创建圈子返回结构与列表一致（后端返回 ForumOut）
export type CreateForumDto = ForumListDto;

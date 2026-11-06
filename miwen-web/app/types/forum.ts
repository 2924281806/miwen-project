export interface ForumListDto {
  forum_id: number;
  name: string;
  description: string;
}

export interface ForumListDtoParams {
  page: number;
  pageSize?: number;
  name?: string;
  uid?: string;
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
export interface CreatePostDtoParams {
  name: string;
  description: string;
  icon?: string;
  category_id?: number;
  join_type: "public" | "private";
}
export interface CreatePostDto {
  detail: string[];
}

export interface CreateForumDtoParams {
  name: string;
  description: string;
  icon?: string;
  category_id?: number;
  join_type: "public" | "private";
}
export interface CreateForumDto {
  forum_id: number;
}

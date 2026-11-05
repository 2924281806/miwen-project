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
}
export interface CreatePostDtoParams {
  name: string;
  description: string;
  forum_id: number;
}
export interface CreatePostDto {
  detail: string[];
}

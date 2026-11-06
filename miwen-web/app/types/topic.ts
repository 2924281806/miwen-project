export interface CreatePostDtoParams {
  title: string;
  content: string;
  cover?: string;
  forum_id: number;
}

// 帖子返回结构（对齐后端 TopicOut，列表/发帖/改帖复用）
export interface CreatePostDto {
  id: number;
  topic_id: number;
  forum_id: number;
  uid: number;
  title: string;
  content: string;
  cover: string | null;
  is_top: number;
  is_essence: number;
  is_closed: number;
  views: number;
  reply_count: number;
  last_post_at: string;
  last_post_uid: number | null;
  status: number;
  created_at: string;
  updated_at: string;
}

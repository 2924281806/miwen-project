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
  plainText: string;
  is_votes: number; // 当前用户是否已点赞：0否1是（游客恒为0）
  votes: number; // 点赞总数
  is_favorites: number; // 当前用户是否已收藏：0否1是（游客恒为0）
  favorites: number; // 收藏总数
  comments: number;
}

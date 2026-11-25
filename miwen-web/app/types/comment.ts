// 帖子评论相关类型
export interface CommentAuthor {
  uid: string;
  username: string;
  nickname: string | null;
  avatar: string | null;
}

/** 被回复的回复摘要（toComment） */
export interface ReplyToComment {
  /** 被回复的回复编号 */
  reply_id: number;
  /** 被回复的回复内容 */
  content: string;
  /** 被回复的回复用户信息 */
  author: CommentAuthor | null;
}

/** 评论下的回复（外链到帖子编号与评论编号，回复其他回复时带 toComment） */
export interface ReplyItem {
  /** 回复唯一编号（四位数随机生成） */
  reply_id: number;
  /** 所属帖子编号 */
  topic_id: number;
  /** 所属评论唯一编号 */
  comment_id: number;
  /** 回复内容（HTML） */
  content: string;
  /** 回复用户uid */
  uid: string;
  /** 回复时间 */
  created_at: string;
  /** 回复用户信息 */
  author: CommentAuthor | null;
  /** 被回复的回复编号，直接回复评论时为空 */
  reply_to_id: number | null;
  /** 被回复的回复摘要（toComment），回复其他回复时返回 */
  to_comment: ReplyToComment | null;
  /** 该回复下的下级回复列表（reply_to_id 指向本条回复） */
  children: ReplyItem[];
  // ===== 以下为前端本地状态（接口不返回） =====
  /** 是否展开回复编辑器 */
  replyStatus?: boolean;
  /** 回复编辑器草稿 */
  reply?: string;
}

export interface CommentItem {
  /** 评论唯一编号（四位数随机生成） */
  comment_id: number;
  /** 所属帖子编号 */
  topic_id: number;
  /** 评论内容（HTML） */
  content: string;
  /** 评论用户uid */
  uid: string;
  /** 评论时间 */
  created_at: string;
  /** 点赞数量 */
  likes: number;
  /** 评论用户信息 */
  author: CommentAuthor | null;
  /** 点赞用户信息列表 */
  liked_users: CommentAuthor[];
  /** 回复信息列表 */
  replies: ReplyItem[];
  // ===== 以下为前端本地状态（接口不返回） =====
  /** 是否展开回复编辑器 */
  replyStatus?: boolean;
  /** 回复编辑器草稿 */
  reply?: string;
}

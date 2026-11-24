// 帖子评论相关类型
export interface CommentAuthor {
  uid: string;
  username: string;
  nickname: string | null;
  avatar: string | null;
}

export interface CommentItem {
  /** 评论ID */
  id: number;
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
  /** 回复信息列表（顶级评论才有） */
  replies: CommentItem[];
}

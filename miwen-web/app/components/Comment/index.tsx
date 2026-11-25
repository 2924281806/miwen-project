// 帖子评论组件：按帖子 id 拉取评论列表（含点赞数量、点赞用户信息列表、回复信息），
// 支持对评论发表回复（回复外链到帖子编号与评论编号，回复编号为四位数随机生成）。
"use client";
import { SafeHtml } from "@/app/components/Dompurify";
import TinyEditor from "@/app/components/Editor/TinyEditor";
import {
  createReply,
  getComments,
  likeComment,
  unlikeComment,
} from "@/app/lib/api";
import { getUserState } from "@/app/store/userStore";
import type {
  CommentAuthor,
  CommentItem,
  ReplyItem,
} from "@/app/types/comment";
import { useRouterPush } from "@/app/utils/routes";
import { timeAgo } from "@/app/utils/time";
import { LikeFilled, LikeOutlined, UserOutlined } from "@ant-design/icons";
import { Avatar, Button, Empty, Spin, message } from "antd";
import { useCallback, useEffect, useState } from "react";
import styles from "./index.module.scss";

interface CommentProps {
  /** 帖子编号 topic_id */
  topicId?: number | string;
  /** 变化时重新拉取评论列表（用于发表评论后刷新） */
  refreshKey?: number;
}

/** 是否已登录 */
function isLogin() {
  return Boolean(getUserState().token);
}

/** 当前登录用户是否点过赞 */
function isLikedByMe(item: CommentItem): boolean {
  const myUid = String(getUserState().userInfo?.uid ?? "");
  return Boolean(myUid) && item.liked_users.some((u) => u.uid === myUid);
}

/** 映射评论列表（点赞等更新只作用于评论本身，回复列表原样保留） */
function mapComments(
  list: CommentItem[],
  fn: (item: CommentItem) => CommentItem,
): CommentItem[] {
  return list.map((item) => ({ ...fn(item), replies: item.replies }));
}

/** 展示名：昵称优先 */
function displayName(author: CommentAuthor | null): string {
  return author?.nickname || author?.username || "未知用户";
}

/** 递归切换某条回复的编辑器展开状态（同时收起其他回复） */
function toggleReplyEditor(list: ReplyItem[], targetId: number): ReplyItem[] {
  return list.map((r) => ({
    ...r,
    replyStatus: r.reply_id === targetId ? !r.replyStatus : false,
    children: r.children ? toggleReplyEditor(r.children, targetId) : [],
  }));
}

/** 递归统计回复数量（含下级回复） */
function countReplies(list: ReplyItem[]): number {
  return list.reduce((sum, r) => sum + 1 + countReplies(r.children || []), 0);
}

export default function Comment({ topicId, refreshKey }: CommentProps) {
  const [comments, setComments] = useState<CommentItem[]>([]);
  const [loading, setLoading] = useState(false);
  const routePush = useRouterPush();

  const fetchComments = useCallback(async () => {
    if (!topicId) return;
    setLoading(true);
    try {
      const res = await getComments(Number(topicId));
      if (res.code === 200) {
        setComments(res.data || []);
      } else {
        message.warning(res.msg || "获取评论失败");
      }
    } catch {
      message.error("获取评论失败，请稍后重试");
    } finally {
      setLoading(false);
    }
  }, [topicId]);

  useEffect(() => {
    fetchComments();
  }, [fetchComments, refreshKey]);

  /** 点赞 / 取消点赞（按四位数评论编号） */
  const handleLike = async (item: CommentItem) => {
    if (!isLogin()) {
      message.warning("请先登录后再点赞");
      return;
    }
    const liked = isLikedByMe(item);
    const myUid = String(getUserState().userInfo?.uid ?? "");
    const me = getUserState().userInfo;
    try {
      const res = liked
        ? await unlikeComment(item.comment_id)
        : await likeComment(item.comment_id);
      if (res.code === 200) {
        setComments((prev) =>
          mapComments(prev, (c) =>
            c.comment_id === item.comment_id
              ? {
                  ...c,
                  likes: res.data ?? (liked ? c.likes - 1 : c.likes + 1),
                  liked_users: liked
                    ? c.liked_users.filter((u) => u.uid !== myUid)
                    : [
                        ...c.liked_users,
                        {
                          uid: myUid,
                          username: me?.username || "",
                          nickname: me?.nickname || null,
                          avatar: me?.avatar || null,
                        },
                      ],
                }
              : c,
          ),
        );
      } else {
        message.warning(res.msg || "操作失败");
      }
    } catch {
      message.error("操作失败，请稍后重试");
    }
  };

  /** 展开评论的回复编辑器 */
  const handleReply = (item: CommentItem) => {
    if (!isLogin()) {
      message.warning("请先登录后再回复!");
      return;
    }
    setComments((prev) =>
      mapComments(prev, (c) =>
        c.comment_id === item.comment_id
          ? { ...c, replyStatus: !c.replyStatus }
          : c,
      ),
    );
  };

  /** 点击回复下的“回复”：展开该回复的编辑器 */
  const handleReplyToReply = (parent: CommentItem, reply: ReplyItem) => {
    if (!isLogin()) {
      message.warning("请先登录后再回复!");
      return;
    }
    setComments((prev) =>
      prev.map((c) =>
        c.comment_id === parent.comment_id
          ? { ...c, replies: toggleReplyEditor(c.replies, reply.reply_id) }
          : c,
      ),
    );
  };

  /** 提交对回复的回复（挂在被回复的回复下一级展示，带 toComment） */
  const handleSubmitReply = async (parent: CommentItem, reply: ReplyItem) => {
    const content = (reply.reply || "").trim();
    if (!content) {
      message.warning("请输入回复内容");
      return;
    }
    try {
      const res = await createReply(parent.comment_id, content, reply.reply_id);
      if (res.code === 200) {
        message.success("回复成功");
        fetchComments();
      } else {
        message.warning(res.msg || "回复失败");
      }
    } catch {
      message.error("回复失败，请稍后重试");
    }
  };

  /** 提交回复（对评论发表，接口按 comment_id 外链帖子与评论） */
  const handleSubmit = async (item: CommentItem) => {
    const content = (item.reply || "").trim();
    if (!content) {
      message.warning("请输入回复内容");
      return;
    }
    try {
      const res = await createReply(item.comment_id, content);
      if (res.code === 200) {
        message.success("回复成功");
        fetchComments();
      } else {
        message.warning(res.msg || "回复失败");
      }
    } catch {
      message.error("回复失败，请稍后重试");
    }
  };

  /** 评论总数（含各级回复） */
  const total = comments.reduce(
    (sum, item) => sum + 1 + countReplies(item.replies || []),
    0,
  );

  /** 单条回复 */
  const renderReply = (
    reply: ReplyItem,
    parent: CommentItem,
    showReplyText: boolean,
  ) => (
    <div className={styles.replyItem} key={reply.reply_id}>
      <Avatar
        className={styles.avatar}
        icon={<UserOutlined />}
        size={28}
        src={reply.author?.avatar || undefined}
      />
      <div className={styles.body}>
        <div className={styles.meta}>
          <span className={styles.name}>
            {displayName(reply.author)}
            {reply.to_comment && (
              <span className={styles.replyTo}>
                to {displayName(reply.to_comment.author)}：
              </span>
            )}
          </span>
          <span className={styles.time}>{timeAgo(reply.created_at)}</span>
        </div>
        <div className={styles.content}>
          <SafeHtml html={reply.content} />
        </div>
        {showReplyText && (
          <div className={`${styles.footer} ${styles.replyText}`}>
            <span
              className={styles.likedText}
              onClick={() => handleReplyToReply(parent, reply)}
            >
              回复
            </span>
          </div>
        )}
        {reply.replyStatus && (
          <div className={styles.tinyInput}>
            <TinyEditor
              value={reply.reply}
              onChange={(e) => (reply.reply = e)}
              height={120}
              toolbar="bold italic underline"
              location="bottom"
              placeholder="说点什么..."
            />
            <Button
              type="primary"
              className={styles["reply-btn"]}
              onClick={() => handleSubmitReply(parent, reply)}
            >
              发送
            </Button>
          </div>
        )}
        {reply.children?.length > 0 && (
          <div className={styles.children}>
            {reply.children.map((child) => renderReply(child, parent, false))}
          </div>
        )}
      </div>
    </div>
  );

  /** 单条评论 */
  const renderComment = (item: CommentItem) => (
    <div className={styles.item} key={item.comment_id}>
      <Avatar
        className={styles.avatar}
        icon={<UserOutlined />}
        size={36}
        src={item.author?.avatar || undefined}
      />
      <div className={styles.body}>
        <div className={styles.meta}>
          <span className={styles.name}>{displayName(item.author)}</span>
          <span className={styles.time}>{timeAgo(item.created_at)}</span>
        </div>
        <div className={styles.content}>
          <SafeHtml html={item.content} />
        </div>
        <div className={styles.footer}>
          <div className={styles.likeContainer}>
            <span className={styles.likeBtn} onClick={() => handleLike(item)}>
              {isLikedByMe(item) ? (
                <LikeFilled className={styles.likedIcon} />
              ) : (
                <LikeOutlined />
              )}
              {item.likes > 0 ? ` ${item.likes}` : " 点赞"}
            </span>
            {item.liked_users.length > 0 && (
              <span className={styles.likedUsers}>
                <Avatar.Group>
                  {item.liked_users.slice(0, 3).map((user) => (
                    <a
                      key={user.uid}
                      onClick={() => routePush(`/user/${user.uid}`)}
                    >
                      <Avatar
                        className={styles.likedAvatar}
                        icon={<UserOutlined />}
                        size={18}
                        src={user.avatar || undefined}
                      />
                    </a>
                  ))}
                </Avatar.Group>
              </span>
            )}
          </div>
          <span className={styles.likedText} onClick={() => handleReply(item)}>
            回复
          </span>
        </div>
        {item.replies?.length > 0 && (
          <div className={styles.replies}>
            {item.replies.map((reply) => renderReply(reply, item, true))}
          </div>
        )}
        {item.replyStatus && (
          <div className={styles.tinyInput}>
            <TinyEditor
              value={item.reply}
              onChange={(e) => (item.reply = e.trim())}
              height={120}
              toolbar="bold italic underline"
              location="bottom"
              placeholder="说点什么..."
            />
            <Button
              type="primary"
              className={styles["reply-btn"]}
              onClick={() => handleSubmit(item)}
            >
              发送
            </Button>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className={styles.commentCard}>
      <div className={styles.header}>
        评论
        <span className={styles.count}>{total}</span>
      </div>
      {loading ? (
        <div className={styles.loading}>
          <Spin />
        </div>
      ) : comments.length === 0 ? (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="暂无评论，快来抢沙发~"
        />
      ) : (
        <div className={styles.list}>
          {comments.map((item) => renderComment(item))}
        </div>
      )}
    </div>
  );
}

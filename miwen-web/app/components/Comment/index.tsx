// 帖子评论组件：按帖子 id 拉取评论列表（含点赞数量、点赞用户信息列表、回复信息）
"use client";
import { SafeHtml } from "@/app/components/Dompurify";
import TinyEditor from "@/app/components/Editor/TinyEditor";
import { getComments, likeComment, unlikeComment } from "@/app/lib/api";
import { getUserState } from "@/app/store/userStore";
import type { CommentItem } from "@/app/types/comment";
import { useRouterPush } from "@/app/utils/routes";
import { timeAgo } from "@/app/utils/time";
import { LikeFilled, LikeOutlined, UserOutlined } from "@ant-design/icons";
import { Avatar, Empty, Spin, message } from "antd";
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

/** 递归映射评论树（用于点赞后更新对应评论） */
function mapComments(
  list: CommentItem[],
  fn: (item: CommentItem) => CommentItem,
): CommentItem[] {
  return list.map((item) => ({
    ...fn(item),
    replies: item.replies ? mapComments(item.replies, fn) : [],
  }));
}

export default function Comment({ topicId, refreshKey }: CommentProps) {
  const [comments, setComments] = useState<CommentItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [reply, setReply] = useState("");
  const [replyStatus, setReplyStatus] = useState(false);
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

  /** 点赞 / 取消点赞 */
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
        ? await unlikeComment(item.id)
        : await likeComment(item.id);
      if (res.code === 200) {
        setComments((prev) =>
          mapComments(prev, (c) =>
            c.id === item.id
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

  /** 评论总数（含回复） */
  const total = comments.reduce(
    (sum, item) => sum + 1 + (item.replies?.length ?? 0),
    0,
  );
  const handleReply = () => {
    if (!isLogin()) {
      message.warning("请先登录后再回复!");
      return;
    }
    setReplyStatus(!replyStatus);
  };

  /** 单条评论 / 回复 */
  const renderComment = (item: CommentItem, isReply: boolean) => (
    <div className={isReply ? styles.replyItem : styles.item} key={item.id}>
      <Avatar
        className={styles.avatar}
        icon={<UserOutlined />}
        size={isReply ? 28 : 36}
        src={item.author?.avatar || undefined}
      />
      <div className={styles.body}>
        <div className={styles.meta}>
          <span className={styles.name}>
            {item.author?.nickname || item.author?.username || "未知用户"}
          </span>
          <span className={styles.time}>{timeAgo(item.created_at)}</span>
        </div>
        <div className={styles.content}>
          <SafeHtml html={item.content} />
        </div>
        <div className={styles.footer}>
          <div className={styles.likeContainer}>
            <span className={styles.likeBtn} onClick={() => handleLike(item)}>
              {isLikedByMe(item) ? <LikeFilled /> : <LikeOutlined />}
              {item.likes > 0 ? ` ${item.likes}` : " 点赞"}
            </span>
            {item.liked_users.length > 0 && (
              <span className={styles.likedUsers}>
                <Avatar.Group>
                  {item.liked_users.slice(0, 3).map((user) => (
                    <a onClick={() => routePush(`/user/${user.uid}`)}>
                      <Avatar
                        className={styles.likedAvatar}
                        icon={<UserOutlined />}
                        key={user.uid}
                        size={18}
                        src={user.avatar || undefined}
                      />
                    </a>
                  ))}
                </Avatar.Group>
              </span>
            )}
          </div>
          <span className={styles.likedText} onClick={() => handleReply()}>
            回复
          </span>
        </div>
        {!isReply && item.replies?.length > 0 && (
          <div className={styles.replies}>
            {item.replies.map((reply) => renderComment(reply, true))}
          </div>
        )}
        {replyStatus && (
          <div className={styles.tinyInput}>
            <TinyEditor
              value={reply}
              onChange={setReply}
              height={120}
              toolbar="bold italic underline"
              location="bottom"
              placeholder="说点什么..."
            />
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
          {comments.map((item) => renderComment(item, false))}
        </div>
      )}
    </div>
  );
}

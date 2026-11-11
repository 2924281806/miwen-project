// 帖子详情页
"use client";
import { SafeHtml } from "@/app/components/Dompurify";
import {
  favoriteTopic,
  getAllForumList,
  getTopicListDetail,
  likeTopic,
  unfavoriteTopic,
  unlikeTopic,
} from "@/app/lib/api";
import { getUserState } from "@/app/store/userStore";
import type { CreatePostDto } from "@/app/types/topic";
import { timeAgo } from "@/app/utils/time";
import {
  CommentOutlined,
  EyeOutlined,
  LikeFilled,
  LikeOutlined,
  MailOutlined,
  PlusOutlined,
  StarFilled,
  StarOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { Avatar, Button, Input, message } from "antd";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import styles from "./detail.module.scss";

export default function TopicDetail() {
  const params = useParams();
  const tid = Number(params.id);
  const [topicDetail, setTopicDetail] = useState<CreatePostDto | null>(null);
  const [forumName, setForumName] = useState<string>("");
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      const res = await getTopicListDetail(tid);
      if (res.code === 200) {
        setLoading(false);
        setTopicDetail(res.data);
        // 面包屑：查询帖子所属圈子名称
        if (res.data?.forum_id) {
          try {
            const forumRes = await getAllForumList();
            if (forumRes?.code === 200) {
              const forum = (forumRes.data || []).find(
                (f) => f.forum_id === res.data.forum_id,
              );
              setForumName(forum?.name || "");
            }
          } catch {
            /* 圈子名获取失败不影响正文展示 */
          }
        }
      } else {
        message.error(res.msg);
        setTopicDetail(null);
        setLoading(false);
      }
    };
    init();
  }, [tid]);

  /** 点赞 / 取消点赞（未登录提示） */
  const handleVote = async () => {
    if (!topicDetail) return;
    if (!getUserState().token) {
      message.warning("请先登录后再点赞");
      return;
    }
    const liked = topicDetail.is_votes === 1;
    try {
      const res = liked
        ? await unlikeTopic(topicDetail.topic_id)
        : await likeTopic(topicDetail.topic_id);
      if (res.code === 200) {
        setTopicDetail({
          ...topicDetail,
          is_votes: liked ? 0 : 1,
          votes: topicDetail.votes + (liked ? -1 : 1),
        });
        message.success(liked ? "取消点赞成功" : "点赞成功");
      } else {
        message.warning(res.msg);
      }
    } catch {
      message.error("操作失败，请稍后重试");
    }
  };

  /** 收藏 / 取消收藏（未登录提示） */
  const handleFavorite = async () => {
    if (!topicDetail) return;
    if (!getUserState().token) {
      message.warning("请先登录后再收藏");
      return;
    }
    const faved = topicDetail.is_favorites === 1;
    try {
      const res = faved
        ? await unfavoriteTopic(topicDetail.topic_id)
        : await favoriteTopic(topicDetail.topic_id);
      if (res.code === 200) {
        setTopicDetail({
          ...topicDetail,
          is_favorites: faved ? 0 : 1,
          favorites: topicDetail.favorites + (faved ? -1 : 1),
        });
        message.success(faved ? "取消收藏成功" : "收藏成功");
      } else {
        message.warning(res.msg);
      }
    } catch {
      message.error("操作失败，请稍后重试");
    }
  };

  const author = topicDetail?.author;

  return loading ? null : (
    <div className={styles["header"]}>
      <div className={styles["content"]}>
        {/* ===== 左栏：随页面滚动 ===== */}
        <div>
          <div className={styles["breadcrumb"]}>
            <Link href="/group">圈子</Link>
            {forumName && (
              <Link href={`/group/${topicDetail?.forum_id}`}>{forumName}</Link>
            )}
            <span className={styles["current"]}>帖子详情</span>
          </div>

          <div className={styles["main"]}>
            <h1 className={styles["title"]}>{topicDetail?.title}</h1>

            <div className={styles["meta"]}>
              <span>
                发表于 {topicDetail ? timeAgo(topicDetail.created_at) : "--"}
              </span>
              <div className={styles["meta-counts"]}>
                <span>
                  <EyeOutlined /> {topicDetail?.views ?? 0}
                </span>
                <span>
                  <CommentOutlined /> {topicDetail?.comments ?? 0}
                </span>
              </div>
            </div>

            <div className={styles["author-bar"]}>
              <Avatar
                size={32}
                src={author?.avatar || undefined}
                icon={<UserOutlined />}
              />
              <span className={styles["author-bar-name"]}>
                {author?.nickname || author?.username || "未知用户"}
              </span>
            </div>

            <div className={styles["body"]}>
              <SafeHtml html={topicDetail?.content || ""} />
            </div>

            <div className={styles["actions"]}>
              <Button
                className={`${styles["action-btn"]} ${
                  topicDetail?.is_votes ? styles["actionActive"] : ""
                }`}
                icon={topicDetail?.is_votes ? <LikeFilled /> : <LikeOutlined />}
                onClick={handleVote}
              >
                点赞 {topicDetail?.votes ?? 0}
              </Button>
              <Button
                className={`${styles["action-btn"]} ${
                  topicDetail?.is_favorites ? styles["actionActive"] : ""
                }`}
                icon={
                  topicDetail?.is_favorites ? <StarFilled /> : <StarOutlined />
                }
                onClick={handleFavorite}
              >
                收藏 {topicDetail?.favorites ?? 0}
              </Button>
            </div>

            <div className={styles["comment-box"]}>
              <Input.TextArea
                className={styles["comment-input"]}
                placeholder="说点什么..."
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                autoSize={{ minRows: 2, maxRows: 4 }}
                maxLength={500}
              />
              <Button
                type="primary"
                className={styles["reply-btn"]}
                onClick={() => message.info("评论功能开发中，敬请期待")}
              >
                快速回复
              </Button>
            </div>
          </div>
        </div>

        {/* ===== 右栏：sticky 固定不随滚动 ===== */}
        <div className={styles["side"]}>
          <div className={styles["author-card"]}>
            <Avatar
              size={64}
              src={author?.avatar || undefined}
              icon={<UserOutlined />}
            />
            <div className={styles["author-name"]}>
              {author?.nickname || author?.username || "未知用户"}
              <span className={styles["op-badge"]}>楼主</span>
            </div>
            <div className={styles["author-stats"]}>
              <div className={styles["stat"]}>
                <div className={styles["stat-count"]}>{author?.posts ?? 0}</div>
                <div className={styles["stat-label"]}>帖子</div>
              </div>
              <div className={styles["stats-divider"]}></div>
              <div className={styles["stat"]}>
                <div className={styles["stat-count"]}>{author?.fans ?? 0}</div>
                <div className={styles["stat-label"]}>粉丝</div>
              </div>
            </div>
            <div className={styles["author-actions"]}>
              <Button
                type="primary"
                className={styles["follow-btn"]}
                icon={<PlusOutlined />}
                onClick={() => message.info("关注功能开发中，敬请期待")}
              >
                关注作者
              </Button>
              <Button
                className={styles["msg-btn"]}
                icon={<MailOutlined />}
                onClick={() => message.info("私信功能开发中，敬请期待")}
              >
                发私信
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

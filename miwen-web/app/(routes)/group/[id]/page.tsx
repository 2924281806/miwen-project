// 圈子详情页
"use client";
import { getAllForumList, getPostList, otherUserInfo } from "@/app/lib/api";
import type { ForumListDto } from "@/app/types/forum";
import type { CreatePostDto } from "@/app/types/topic";
import { timeAgo } from "@/app/utils/time";
import {
  CommentOutlined,
  CustomerServiceOutlined,
  EyeOutlined,
  FileTextOutlined,
  PlusOutlined,
  SignalFilled,
  StarOutlined,
  TrophyOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { Avatar, Button, Empty, message, Typography } from "antd";
import DOMPurify from "dompurify";
import { convert } from "html-to-text";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import styles from "./detail.module.scss";
const { Paragraph } = Typography;

type TabKey = "all" | "hot" | "essence";

export default function CircleDetail() {
  const router = useRouter();
  const params = useParams();
  const forumId = Number(params.id);
  const [forum, setForum] = useState<ForumListDto | null>(null);
  const [topicList, setTopicList] = useState<CreatePostDto[]>([]);
  const [ownerName, setOwnerName] = useState<string>("");
  const [activeTab, setActiveTab] = useState<TabKey>("all");
  const [keyword, setKeyword] = useState("");

  useEffect(() => {
    const init = async () => {
      // 圈子信息（从圈子列表中取当前圈子）
      const forumRes = await getAllForumList();
      if (forumRes?.code === 200) {
        const current = (forumRes.data || []).find(
          (f) => f.forum_id === forumId,
        );
        setForum(current || null);
        // 圈主昵称
        if (current?.uid) {
          try {
            const userRes = await otherUserInfo(String(current.uid));
            if (userRes?.code === 200) {
              setOwnerName(
                userRes.data?.nickname || userRes.data?.username || "",
              );
            }
          } catch {
            setOwnerName("");
          }
        }
      }
      // 帖子列表（前端按圈子过滤）
      const topicRes = await getPostList({ page: 1, pageSize: 50 });
      if (topicRes?.code === 200) {
        const items = (topicRes.data?.items || [])
          .filter((t) => t.forum_id === forumId)
          .map((t) => ({
            ...t,
            plainText: convert(DOMPurify.sanitize(t.content), {
              wordwrap: false,
              selectors: [{ selector: "img", format: "skip" }],
            }),
          }));
        setTopicList(items);
      }
    };
    init();
  }, [forumId]);

  // tab 过滤：全部 / 热门（按点赞数降序）/ 精华
  const visibleTopics = topicList
    .filter((t) => (activeTab === "essence" ? t.is_essence === 1 : true))
    .filter((t) => (keyword ? t.title.includes(keyword.trim()) : true))
    .sort((a, b) => (activeTab === "hot" ? b.votes - a.votes : 0));

  // 今日统计
  const today = new Date().toDateString();
  const todayPosts = topicList.filter(
    (t) => new Date(t.created_at).toDateString() === today,
  ).length;
  const todayReplies = topicList.reduce(
    (sum, t) => sum + (t.reply_count || 0),
    0,
  );
  const handleNewPostClick = () => {
    router.push(`/topics/waite?fid=${forumId}`);
  };
  return (
    <div className={styles["circle-detail"]}>
      {/* ===== 顶部横幅 + 信息卡 ===== */}
      <div className={styles["banner"]}>
        <div className={styles["info-card"]}>
          <div className={styles["info-main"]}>
            <div className={styles["info-header"]}>
              <h2 className={styles["info-name"]}>{forum?.name}</h2>
              <span
                className={`${styles["join-tag"]} ${
                  forum?.join_type === "private" ? styles["joinTagPrivate"] : ""
                }`}
              >
                {forum?.join_type === "private" ? "私密" : "公开"}
              </span>
              <span className={styles["info-stat"]}>
                <FileTextOutlined /> {topicList.length} 帖子
              </span>
              <span className={styles["info-stat"]}>
                <StarOutlined /> {forum?.favorites ?? 0} 收藏
              </span>
              <span className={styles["forum-code"]}>
                RS {forum?.forum_id ?? "-"}
              </span>
            </div>
            <div className={styles["info-desc"]}>
              <Avatar
                size={56}
                className={styles["info-avatar"]}
                src={forum?.icon || undefined}
                icon={<SignalFilled />}
              />
              <div className={styles["desc-text"]}>
                <p className={styles["desc-content"]}>
                  {forum?.description || "暂无圈子简介"}
                </p>
                <p className={styles["desc-owner"]}>
                  圈主：
                  <UserOutlined /> {ownerName || "未知"}
                </p>
              </div>
            </div>
          </div>
          <div className={styles["info-actions"]}>
            <Button
              type="primary"
              className={styles["join-btn"]}
              onClick={() => message.info("申请加入功能开发中，敬请期待")}
            >
              申请加入圈子
            </Button>
            <Button
              className={styles["invite-btn"]}
              onClick={() => message.info("邀请用户功能开发中，敬请期待")}
            >
              邀请用户
            </Button>
          </div>
        </div>
      </div>

      {/* ===== 主体两栏 ===== */}
      <div className={styles["content"]}>
        {/* 左栏：筛选 + 帖子列表 */}
        <div className={styles["main-col"]}>
          <div className={styles["filter-bar"]}>
            <div className={styles["filter-left"]}>
              <span className={styles["filter-item"]}>全部时间</span>
              <span className={styles["filter-divider"]}>|</span>
              <span className={styles["filter-item"]}>默认排序</span>
            </div>
            <div className={styles["tabs"]}>
              {(
                [
                  ["all", "全部"],
                  ["hot", "热门"],
                  ["essence", "精华"],
                ] as [TabKey, string][]
              ).map(([key, label]) => (
                <span
                  key={key}
                  className={`${styles["tab"]} ${
                    activeTab === key ? styles["tabActive"] : ""
                  }`}
                  onClick={() => setActiveTab(key)}
                >
                  {label}
                </span>
              ))}
            </div>
          </div>

          {visibleTopics.length === 0 ? (
            <div className={styles["empty-wrap"]}>
              <Empty description="暂无帖子" />
            </div>
          ) : (
            visibleTopics.map((item) => (
              <Link
                key={item.topic_id}
                href={`/topics/${item.topic_id}`}
                className={styles["topic-item"]}
              >
                <div className={styles["topic-body"]}>
                  <h3 className={styles["topic-title"]}>{item.title}</h3>
                  <Paragraph ellipsis={{ rows: 2 }}>{item.plainText}</Paragraph>
                  <div className={styles["topic-meta"]}>
                    <span>{timeAgo(item.created_at)}</span>
                    <span>
                      <EyeOutlined /> {item.views}
                    </span>
                    <span>
                      <CommentOutlined /> {item.comments}
                    </span>
                  </div>
                </div>
                {item.cover && (
                  <img
                    className={styles["topic-cover"]}
                    src={item.cover}
                    alt={item.title}
                  />
                )}
              </Link>
            ))
          )}
        </div>

        {/* 右栏：统计 + 发布新帖 + 排行/版主 */}
        <div className={styles["side-col"]}>
          <div className={styles["stats-panel"]}>
            <div className={styles["stat"]}>
              <div className={styles["stat-count"]}>{todayPosts}</div>
              <div className={styles["stat-label"]}>今日新帖</div>
            </div>
            <div className={styles["stats-divider"]}></div>
            <div className={styles["stat"]}>
              <div className={styles["stat-count"]}>{todayReplies}</div>
              <div className={styles["stat-label"]}>今日回复</div>
            </div>
          </div>

          <Button
            className={styles["publish-btn"]}
            icon={<PlusOutlined />}
            onClick={handleNewPostClick}
          >
            发布新帖
          </Button>

          <div className={styles["side-panel"]}>
            <div className={styles["panel-title"]}>
              <TrophyOutlined /> 专家排行
            </div>
            <div className={styles["panel-body"]}>
              <p className={styles["panel-empty"]}>暂无上榜专家</p>
            </div>
          </div>

          <div className={styles["side-panel"]}>
            <div className={styles["panel-title"]}>
              <CustomerServiceOutlined /> 值班版主
            </div>
            <div className={styles["panel-body"]}>
              <p className={styles["panel-empty"]}>
                暂无值班版主，请联系管理员
                {ownerName ? `（${ownerName}）` : ""}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

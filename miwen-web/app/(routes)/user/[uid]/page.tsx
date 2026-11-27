// 用户主页（他人主页）：样式对齐设计稿
"use client";
import { PlainText, SafeHtml } from "@/app/components/Dompurify";
import {
  followUser,
  getForumList,
  getPostList,
  listCommentsByUid,
  listFavoriteTopicsByUid,
  otherUserInfo,
  unfollowUser,
} from "@/app/lib/api";
import { useUserStore } from "@/app/store/userStore";
import type { ForumListDto } from "@/app/types/forum";
import type { CreatePostDto } from "@/app/types/topic";
import type { UserInfo } from "@/app/types/user";
import { useRouterPush } from "@/app/utils/routes";
import {
  HighlightOutlined,
  PlusOutlined,
  SearchOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { Avatar, Button, message, Pagination, Typography } from "antd";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import styles from "./user.module.scss";
/** 右侧关注列表 */
const FOLLOW_ITEMS = [
  { label: "关注的话题", count: 0 },
  { label: "关注的专栏", count: 0 },
  { label: "关注的问题", count: 0 },
];

export type TabKey = "topics" | "answer" | "group" | "favorite";
export type TabItem = CreatePostDto | ForumListDto;

interface TabMeta {
  key: TabKey;
  label: string;
  type: "topic" | "group";
}

/** tab 元信息：静态定义在模块层，不随渲染重建，也不放进 state */
const TAB_META: TabMeta[] = [
  { key: "topics", label: "帖子", type: "topic" },
  { key: "answer", label: "回答", type: "topic" },
  { key: "group", label: "圈子", type: "group" },
  { key: "favorite", label: "收藏", type: "topic" },
];

interface TabState {
  count: number;
  page: number;
  list: TabItem[];
}

/** 每个 tab 独立的状态，请求结果按 key 合并，互不覆盖 */
const createInitialTabs = (): Record<TabKey, TabState> => ({
  topics: { count: 0, page: 1, list: [] },
  answer: { count: 0, page: 1, list: [] },
  group: { count: 0, page: 1, list: [] },
  favorite: { count: 0, page: 1, list: [] },
});

/** 各 tab 加载失败时的提示语 */
const TAB_ERROR_MSG: Record<TabKey, string> = {
  topics: "获取用户帖子失败",
  answer: "获取用户评论失败",
  group: "获取用户圈子失败",
  favorite: "获取用户收藏帖子失败",
};

export default function UserProfile() {
  const { uid } = useParams();
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [following, setFollowing] = useState(false);
  const [activeTab, setActiveTab] = useState<TabKey>("topics");
  const [tabsData, setTabsData] =
    useState<Record<TabKey, TabState>>(createInitialTabs);
  // 展开全文状态
  const [expandMap, setExpandMap] = useState<Record<number, boolean>>({});

  const currentUserInfo = useUserStore((state) => state.userInfo);
  const routePush = useRouterPush();

  /** 加载指定 tab 的数据：按 key 合并进 state，避免并发请求整份覆盖 */
  const loadTab = useCallback(
    async (key: TabKey, page: number) => {
      if (!uid) return;
      try {
        let total = 0;
        let list: TabItem[] = [];
        if (key === "topics") {
          const res = await getPostList({
            uid: Number(uid),
            page,
            pageSize: 10,
          });
          if (res?.code !== 200 || !res.data) return;
          total = res.data.total || 0;
          list = res.data.lists || [];
        } else if (key === "answer") {
          const res = await listCommentsByUid({
            uid: Number(uid),
            page,
            pageSize: 10,
          });
          if (res?.code !== 200 || !res.data) return;
          total = res.data.total || 0;
          list = res.data.lists || [];
        } else if (key === "group") {
          const res = await getForumList({
            uid: Number(uid),
            page,
            pageSize: 10,
          });
          if (res?.code !== 200 || !res.data) return;
          total = res.data.total || 0;
          list = res.data.lists || [];
        } else {
          const res = await listFavoriteTopicsByUid({
            uid: Number(uid),
            page,
            pageSize: 10,
          });
          if (res?.code !== 200 || !res.data) return;
          total = res.data.total || 0;
          list = res.data.lists || [];
        }
        setTabsData((prev) => ({
          ...prev,
          [key]: { count: total, page, list },
        }));
      } catch {
        message.error(TAB_ERROR_MSG[key]);
      }
    },
    [uid],
  );

  useEffect(() => {
    if (!uid) return;
    otherUserInfo(String(uid))
      .then((res) => {
        if (res?.code === 200 && res.data) {
          setUserInfo(res.data);
          setFollowing(Number(res.data.is_follow) === 1);
        }
      })
      .catch(() => {
        message.error("获取用户信息失败");
      });
    // 切换用户时重置全部 tab，再并行加载，各自按 key 合并互不影响
    setTabsData(createInitialTabs());
    TAB_META.forEach((tab) => loadTab(tab.key, 1));
  }, [uid, loadTab]);
  // 切换关注状态
  const toggleFollow = async () => {
    if (!userInfo) return;
    try {
      if (following) {
        const res = await unfollowUser(Number(userInfo.uid));
        if (res?.code === 200) {
          setFollowing(false);
          message.success("已取消关注");
        } else {
          message.error(res?.msg || "取消关注失败");
        }
      } else {
        const res = await followUser(Number(userInfo.uid));
        if (res?.code === 200) {
          setFollowing(true);
          message.success("关注成功");
        } else {
          message.error(res?.msg || "关注失败");
        }
      }
    } catch {
      message.error("操作失败，请稍后重试");
    }
  };
  // 跳转修改资料页面
  const updateUserInfo = () => {
    routePush(`/user/update/${currentUserInfo?.uid}`);
  };
  // 切换展开全文状态
  const toggleExpand = (id: number) => {
    setExpandMap((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const renderContent = (id: number, title: string, content: string) => (
    <div className={styles.card} key={id}>
      <h2 className={styles.cardTitle}>
        <Link href={activeTab === "group" ? `/group/${id}` : `/topics/${id}`}>
          {title}
        </Link>
      </h2>
      <div className={styles.cardBody}>
        <Typography.Paragraph
          ellipsis={{
            rows: 4,
            expandable: true,
            expanded: expandMap[id],
            symbol: "阅读全文",
            onExpand: () => toggleExpand(id),
          }}
        >
          {expandMap[id] ? <SafeHtml html={content} /> : PlainText(content)}
        </Typography.Paragraph>
      </div>
    </div>
  );
  // 分页改变时触发：只重新加载当前 tab 的指定页
  const onChangePage = (page: number) => {
    loadTab(activeTab, page);
  };

  const currentTab =
    TAB_META.find((tab) => tab.key === activeTab) ?? TAB_META[0];
  const currentData = tabsData[activeTab];

  return (
    <div className={styles.profilePage}>
      <div className={styles.topCard}>
        {/* 封面横幅 */}
        <div className={styles.cover}>
          <img src="/images/user-bg.png" alt={userInfo?.nickname || ""} />
        </div>

        {/* 资料区：头像 + 昵称 + 关注按钮 */}
        <div className={styles.profileRow}>
          <Avatar
            className={styles.avatar}
            icon={<UserOutlined />}
            size={110}
            src={userInfo?.avatar || undefined}
          />
          <div className={styles.identity}>
            <h1 className={styles.nickname}>{userInfo?.nickname || ""}</h1>
            {userInfo?.created_at && (
              <div className={styles.detailItem}>
                <span className={styles.detailLabel}>注册时间:</span>
                {userInfo.created_at.slice(0, 10)}
              </div>
            )}
          </div>
          {userInfo?.uid === currentUserInfo?.uid ? (
            <Button className={styles.followBtn} onClick={updateUserInfo}>
              修改资料
            </Button>
          ) : (
            <Button
              className={`${styles.followBtn} ${following ? styles.followed : ""}`}
              onClick={toggleFollow}
            >
              {following ? "已关注" : "+关注"}
            </Button>
          )}
        </div>

        {/* tab 导航 */}
        <div className={styles.tabsRow}>
          {TAB_META.map((tab) => (
            <span
              className={`${styles.tabItem} ${activeTab === tab.key ? styles.active : ""}`}
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label}
              {tabsData[tab.key].count}
            </span>
          ))}
          <SearchOutlined className={styles.searchIcon} />
        </div>
      </div>
      {/* 内容区：左主右辅 */}
      <div className={styles.contentRow}>
        <div className={styles.mainCol}>
          {currentData.list.length > 0 ? (
            <div className={styles.pagination}>
              {currentData.list.map((item) =>
                renderContent(
                  currentTab.type === "group" ? item.forum_id : item.topic_id,
                  currentTab.type === "group"
                    ? item.name || ""
                    : item.topicTitle || item.title || "",
                  currentTab.type === "group"
                    ? item.description || ""
                    : item.content || "",
                ),
              )}
              {currentData.count > 10 && (
                <Pagination
                  current={currentData.page}
                  pageSize={10}
                  total={currentData.count}
                  onChange={onChangePage}
                />
              )}
            </div>
          ) : (
            <div className={styles.emptyState}>
              <img src="/images/user-data.svg" alt="" />
              <p className={styles.emptyText}>暂无数据</p>
            </div>
          )}
        </div>
        <div className={styles.sideCol}>
          {/* 创作中心 */}
          <div className={styles.creatorCard}>
            <div className={styles.creatorHead}>
              <span className={styles.creatorIcon}>
                <HighlightOutlined />
              </span>
              <span className={styles.creatorTitle}>创作中心</span>
            </div>
            <div className={styles.creatorBanner}>
              <div>
                <p className={styles.bannerTitle}>开启你的创作之旅</p>
                <p className={styles.bannerSub}>快来成为创作者吧～</p>
              </div>
              <img src="/images/write.svg" alt="" />
            </div>
            <Button
              block
              className={styles.startBtn}
              onClick={() => {
                routePush("topics/write");
              }}
            >
              <PlusOutlined />
              开始创作
            </Button>
          </div>

          {/* 关注了 / 关注者 */}
          <div className={styles.statsCard}>
            <div className={styles.statsItem}>
              <span className={styles.statsLabel}>关注了</span>
              <strong className={styles.statsValue}>0</strong>
            </div>
            <div className={styles.statsItem}>
              <span className={styles.statsLabel}>关注者</span>
              <strong className={styles.statsValue}>0</strong>
            </div>
          </div>

          {/* 关注列表 */}
          <div className={styles.followListCard}>
            {FOLLOW_ITEMS.map((item) => (
              <div className={styles.followItem} key={item.label}>
                <span>{item.label}</span>
                <span className={styles.followCount}>{item.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

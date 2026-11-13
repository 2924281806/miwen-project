// 用户主页（他人主页）：样式对齐设计稿
"use client";
import { followUser, otherUserInfo, unfollowUser } from "@/app/lib/api";
import { useUserStore } from "@/app/store/userStore";
import type { UserInfo } from "@/app/types/user";
import {
  HighlightOutlined,
  PlusOutlined,
  SearchOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { Avatar, Button, message } from "antd";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import styles from "./user.module.scss";

/** 顶部导航 tab */
const TABS = [
  { key: "activity", label: "动态", count: 0 },
  { key: "answer", label: "回答", count: 0 },
  { key: "article", label: "文章", count: 0 },
  { key: "column", label: "圈子", count: 0 },
  { key: "favorite", label: "收藏", count: 0 },
];

/** 右侧关注列表 */
const FOLLOW_ITEMS = [
  { label: "关注的话题", count: 0 },
  { label: "关注的专栏", count: 0 },
  { label: "关注的问题", count: 0 },
];

export default function UserProfile() {
  const router = useRouter();
  const { uid } = useParams();
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [following, setFollowing] = useState(false);
  const [activeTab, setActiveTab] = useState("activity");
  const currentUserInfo = useUserStore((state) => state.userInfo);

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
  }, [uid]);

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
    router.push(`/user/update/${currentUserInfo?.uid}`);
  };

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
          {TABS.map((tab) => (
            <span
              className={`${styles.tabItem} ${activeTab === tab.key ? styles.active : ""}`}
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label}
              {tab.count}
            </span>
          ))}
          <SearchOutlined className={styles.searchIcon} />
        </div>
      </div>

      {/* 内容区：左主右辅 */}
      <div className={styles.contentRow}>
        <div className={styles.mainCol}>
          <div className={styles.mainHead}>
            {userInfo?.uid === currentUserInfo?.uid ? "我" : "TA"}
            的动态
          </div>
          <div className={styles.emptyState}>
            <img src="/images/user-data.svg" alt="" />
            <p className={styles.emptyText}>
              刚来这里？去<Link href="/group">看看感兴趣的圈子</Link>
            </p>
          </div>
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
              onClick={() => router.push("/topics/write")}
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

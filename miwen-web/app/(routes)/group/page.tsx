"use client";
import { getAllCategoryList, getAllForumList } from "@/app/lib/api";
import { useUserStore } from "@/app/store/userStore";
import { ForumCategoryDto, ForumListDto } from "@/app/types/forum";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import styles from "./group.module.scss";

/** 圈子无封面图时的默认 banner */
const DEFAULT_BANNER =
  "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=minimal%20abstract%20wide%20banner%2C%20soft%20teal%20and%20mint%20gradient%2C%20subtle%20geometric%20shapes%2C%20clean%20modern%20community%20cover%2C%20no%20text&image_size=landscape_16_9";

export default function Group() {
  const [forumList, setForumList] = useState<ForumListDto[]>([]);
  const [categories, setCategories] = useState<ForumCategoryDto[]>([]);
  // null 表示「精选」：展示全部圈子
  const [activeCategory, setActiveCategory] = useState<number | null>(null);
  const [joinedIds, setJoinedIds] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(true);
  const userInfo = useUserStore((state) => state.userInfo);

  useEffect(() => {
    const init = async () => {
      const [forumRes, cateRes] = await Promise.all([
        getAllForumList(),
        getAllCategoryList(),
      ]);
      if (forumRes?.code === 200) {
        setForumList(forumRes?.data || []);
      }
      if (cateRes?.code === 200) {
        setCategories(cateRes?.data || []);
      }
      setLoading(false);
    };
    init();
  }, []);

  const filteredList = useMemo(
    () =>
      activeCategory === null
        ? forumList
        : forumList.filter((item) => item.category_id === activeCategory),
    [forumList, activeCategory],
  );

  /** 加入 / 取消加入（本地状态反馈） */
  const toggleJoin = (forumId: number) => {
    setJoinedIds((prev) => {
      const next = new Set(prev);
      if (next.has(forumId)) {
        next.delete(forumId);
      } else {
        next.add(forumId);
      }
      return next;
    });
  };

  return (
    <div className="container">
      {/* 页头：圈子广场 + 分隔线 */}
      <header className={styles.header}>
        <span className={styles.headerIcon}>
          <svg
            viewBox="0 0 24 24"
            width="16"
            height="16"
            fill="none"
            stroke="#fff"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="12" cy="12" r="9" />
            <path d="M15.5 8.5l-2 5-5 2 2-5z" fill="#fff" stroke="none" />
          </svg>
        </span>
        <h1 className={styles.headerTitle}>圈子广场</h1>
        <span className={styles.headerLine} />
        {userInfo?.uid && (
          <Link href="/group/new" className={styles.newLink}>
            + 新建圈子
          </Link>
        )}
      </header>

      {/* 导航：为你推荐 + 分类标签 */}
      <nav className={styles.nav}>
        <span className={styles.navTitle}>为你推荐</span>
        <div className={styles.tags}>
          <button
            type="button"
            className={`${styles.tag} ${activeCategory === null ? styles.tagActive : ""}`}
            onClick={() => setActiveCategory(null)}
          >
            精选
          </button>
          {categories.map((cate) => (
            <button
              type="button"
              key={cate.id}
              className={`${styles.tag} ${activeCategory === cate.id ? styles.tagActive : ""}`}
              onClick={() => setActiveCategory(cate.id)}
            >
              {cate.name}
            </button>
          ))}
        </div>
      </nav>

      {/* 卡片网格 */}
      {loading ? (
        <div className={styles.loading}>加载中...</div>
      ) : filteredList.length === 0 ? (
        <div className={styles.empty}>
          暂无圈子，点击右上角「新建圈子」创建一个吧
        </div>
      ) : (
        <div className={styles.grid}>
          {filteredList.map((item) => {
            const isJoined = joinedIds.has(item.forum_id);
            return (
              <div key={item.forum_id} className={styles.card}>
                {item.icon ? (
                  <img
                    className={styles.avatar}
                    src={item.icon}
                    alt={item.name}
                  />
                ) : (
                  <span className={`${styles.avatar} ${styles.avatarFallback}`}>
                    {item.name.slice(0, 1)}
                  </span>
                )}
                <div className={styles.cardBody}>
                  <div className={styles.cardHead}>
                    <div className={styles.cardInfo}>
                      <Link
                        href={`/group/${item.forum_id}`}
                        className={styles.cardTitle}
                      >
                        {item.name}
                      </Link>
                      <p className={styles.cardSub}>
                        {item.category_name} ·{" "}
                        {item.join_type === "public" ? "公开" : "私有"}
                      </p>
                    </div>
                    <button
                      type="button"
                      className={`${styles.joinBtn} ${isJoined ? styles.joined : ""}`}
                      onClick={() => toggleJoin(item.forum_id)}
                    >
                      {isJoined ? "已加入" : "+ 加入"}
                    </button>
                  </div>
                  <p className={styles.cardDesc}>
                    {item.description || "暂无简介"}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

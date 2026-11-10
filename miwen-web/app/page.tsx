"use client";
import { Dompurify } from "@/app/components/Dompurify";
import {
  favoriteTopic,
  getPostList,
  likeTopic,
  unfavoriteTopic,
  unlikeTopic,
} from "@/app/lib/api";
import { getUserState } from "@/app/store/userStore";
import { CreatePostDto } from "@/app/types/topic";
import { CaretDownFilled, CaretUpFilled } from "@ant-design/icons";
import { message, Typography } from "antd";
import DOMPurify from "dompurify";
import { convert } from "html-to-text";
import { useEffect, useState } from "react";
import styles from "./page.module.scss";

/** 根据标签返回样式类名 */
const tagClass = (tag: string) => {
  if (tag === "热") return styles.tagHot;
  if (tag === "新") return styles.tagNew;
  if (tag === "活") return styles.tagLive;
  return "";
};

// 首页
export default function Home() {
  useEffect(() => {
    const init = async () => {
      const postRes = await getPostList({
        page: searchPage,
        pageSize: 10,
      });
      if (postRes?.code === 200) {
        postRes?.data?.items.forEach((item) => {
          const safeHtml = DOMPurify.sanitize(item.content);
          // 提取纯文本，交给 antd ellipsis 计算打点
          const plainText = convert(safeHtml, { wordwrap: false });
          item.plainText = plainText;
        });
        setPostList(postRes?.data?.items || []);
      }
    };
    init();
  }, []);
  // 展开全文状态
  const [expandMap, setExpandMap] = useState<Record<number, boolean>>({});
  // 热搜轮换页码
  const [searchPage, setSearchPage] = useState(1);
  const [postList, setPostList] = useState<CreatePostDto[]>([]);
  const [allPostList, setAllPostList] = useState<CreatePostDto[]>([]);

  /** 点赞：游客提示登录；已点赞不重复请求；成功后用服务端数据更新总数与状态 */
  const toggleVote = async (item: CreatePostDto) => {
    if (!getUserState().token) {
      message.warning("请先登录后再点赞");
      return;
    }
    if (item.is_votes === 1) {
      // 已点赞，调用取消点赞 API
      try {
        const res = await unlikeTopic(item.topic_id);
        if (res?.code === 200) {
          message.success("取消点赞成功");
          setPostList((prev) =>
            prev.map((p) =>
              p.topic_id === res?.data?.topic_id
                ? { ...p, is_votes: res?.data.is_votes, votes: res?.data.votes }
                : p,
            ),
          );
        } else {
          message.warning(res?.msg || "取消点赞失败");
        }
      } catch (err: unknown) {
        const msg =
          (err as { response?: { data?: { msg?: string } } })?.response?.data
            ?.msg || "取消点赞失败";
        message.warning(msg);
      }
      return;
    }
    try {
      const res = await likeTopic(item.topic_id);
      if (res?.code === 200) {
        message.success("点赞成功");
        setPostList((prev) =>
          prev.map((p) =>
            p.topic_id === res?.data?.topic_id
              ? { ...p, is_votes: res?.data.is_votes, votes: res?.data.votes }
              : p,
          ),
        );
      } else {
        message.warning(res?.msg || "点赞失败");
      }
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { msg?: string } } })?.response?.data
          ?.msg || "点赞失败";
      message.warning(msg);
    }
  };
  /** 收藏：游客提示登录；已收藏不重复请求；成功后用服务端数据更新总数与状态 */
  const toggleFav = async (item: CreatePostDto) => {
    if (!getUserState().token) {
      message.warning("请先登录后再收藏");
      return;
    }
    if (item.is_favorites === 1) {
      try {
        const res = await unfavoriteTopic(item.topic_id);
        if (res?.code === 200) {
          message.success("取消收藏成功");
          setPostList((prev) =>
            prev.map((p) =>
              p.topic_id === res?.data?.topic_id
                ? {
                    ...p,
                    is_favorites: res?.data.is_favorites,
                    favorites: res?.data.favorites,
                  }
                : p,
            ),
          );
        }
      } catch (err: unknown) {
        const msg =
          (err as { response?: { data?: { msg?: string } } })?.response?.data
            ?.msg || "取消收藏失败";
        message.warning(msg);
      }
      return;
    }
    try {
      const res = await favoriteTopic(item.topic_id);
      if (res?.code === 200) {
        message.success("收藏成功");
        setPostList((prev) =>
          prev.map((p) =>
            p.topic_id === res?.data?.topic_id
              ? {
                  ...p,
                  is_favorites: res?.data.is_favorites,
                  favorites: res?.data.favorites,
                }
              : p,
          ),
        );
      } else {
        message.warning(res?.msg || "收藏失败");
      }
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { msg?: string } } })?.response?.data
          ?.msg || "收藏失败";
      message.warning(msg);
    }
  };
  const toggleExpand = (id: number) => {
    setExpandMap((prev) => ({ ...prev, [id]: !prev[id] }));
  };
  const handleRefresh = () => {};

  return (
    <div className="container">
      <div className={styles["content-home"]}>
        {/* 主列：创作入口 + 信息流 */}
        <div className={styles["main-column"]}>
          {/* 信息流卡片 */}
          {postList.map((item) => {
            const voted = item.is_votes === 1;
            const fav = item.is_favorites === 1;
            return (
              <div key={item.id} className={styles.feedCard}>
                <h2 className={styles.cardTitle}>{item.title}</h2>
                <div className={styles.cardBody}>
                  <Typography.Paragraph
                    ellipsis={{
                      rows: 4,
                      expandable: true,
                      expanded: expandMap[item.topic_id],
                      symbol: "阅读全文",
                      onExpand: () => toggleExpand(item.topic_id),
                    }}
                  >
                    {expandMap[item.topic_id] ? (
                      <Dompurify html={item.content} />
                    ) : (
                      item.plainText
                    )}
                  </Typography.Paragraph>
                </div>

                {/* 底部操作栏 */}
                <div className={styles.cardFooter}>
                  <div className={styles.voteGroup}>
                    <button
                      type="button"
                      className={`${styles.voteBtn} ${item.is_votes === 1 ? styles.voteBtnActive : ""}`}
                      onClick={() => toggleVote(item)}
                    >
                      <CaretUpFilled />
                      {item.is_votes ? "已赞同" : "赞同"} {item.votes}
                    </button>
                    <button
                      type="button"
                      className={styles.downBtn}
                      aria-label="反对"
                    >
                      <CaretDownFilled />
                    </button>
                  </div>
                  <button type="button" className={styles.actionItem}>
                    <svg
                      viewBox="0 0 24 24"
                      width="15"
                      height="15"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M21 11.5a8.38 8.38 0 01-.9 3.8 8.5 8.5 0 01-7.6 4.7 8.38 8.38 0 01-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 01-.9-3.8 8.5 8.5 0 014.7-7.6 8.38 8.38 0 013.8-.9h.5a8.48 8.48 0 018 8v.5z" />
                    </svg>
                    {item.comments > 0 ? `${item.comments} 条评论` : "添加评论"}
                  </button>
                  <button
                    type="button"
                    className={`${styles.actionItem} ${fav ? styles.liked : ""}`}
                    onClick={() => toggleFav(item)}
                  >
                    <svg
                      viewBox="0 0 24 24"
                      width="15"
                      height="15"
                      fill={fav ? "currentColor" : "none"}
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                    </svg>
                    {item.favorites}
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* 右侧栏 */}
        <div className={styles["sider-right"]}>
          {/* 大家都在搜 */}
          <div className={styles.sideCard}>
            <div className={styles.sideHead}>
              <span className={styles.sideTitle}>大家都在搜</span>
              <button
                type="button"
                className={styles.refreshBtn}
                onClick={handleRefresh}
              >
                <svg
                  viewBox="0 0 24 24"
                  width="13"
                  height="13"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <polyline points="23 4 23 10 17 10" />
                  <polyline points="1 20 1 14 7 14" />
                  <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15" />
                </svg>
                换一换
              </button>
            </div>
            {allPostList.map((item) => (
              <div key={item.id} className={styles.searchItem}>
                <span className={styles.dot} />
                <span className={styles.keyword}>{item.title}</span>
                <span className={styles.hotness}>{item.favorites}热度</span>
                {item.favorites > 0 && (
                  <span
                    className={`${styles.tag} ${tagClass(String(item.favorites))}`}
                  >
                    {item.favorites}
                  </span>
                )}
              </div>
            ))}
          </div>

          {/* 作者平台推广卡片 */}
          <div className={styles.promoCard}>
            <div className={styles.promoHead}>
              <span className={styles.badge}>¥</span>
              <span className={styles.promoTitle}>觅文作者平台</span>
            </div>
            <p className={styles.promoDesc}>
              写好故事，赚高收益！签约作者保底分成，新手扶持流量包，即刻开启你的创作之旅。
            </p>
            <button type="button" className={styles.promoBtn}>
              加入我们
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* 右侧栏 */
"use client";
import { getHotPostList } from "@/app/lib/api";
import { CreatePostDto } from "@/app/types/topic";
import {
  FireFilled,
  HighlightTwoTone,
  PlusOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import styles from "./index.module.scss";

/** 根据标签返回样式类名 */
const tagClass = (tag: string) => {
  if (tag === "热") return styles.tagHot;
  if (tag === "新") return styles.tagNew;
  if (tag === "活") return styles.tagLive;
  return "";
};

export default function SiderRight() {
  useEffect(() => {
    const init = async () => {
      const hotPostRes = await getHotPostList();
      if (hotPostRes?.code === 200) {
        hotPostRes.data.length > 0 && (hotPostRes.data[0].tag = "热");
        hotPostRes.data.length > 1 && (hotPostRes.data[1].tag = "新");
        hotPostRes.data.length > 2 && (hotPostRes.data[2].tag = "活");
        setHotPostList(hotPostRes?.data || []);
      }
    };
    init();
  }, []);
  const router = useRouter();
  const [hotPostList, setHotPostList] = useState<CreatePostDto[]>([]);

  const handleWriteClick = () => {
    router.push("topics/write");
  };

  return (
    <div className={styles["sider-right"]}>
      {/* 创作中心卡片 */}
      <div className={styles.creationCard}>
        <div className={styles.creationHead}>
          <UserOutlined className={styles.creationIcon} />
          <span className={styles.creationTitle}>创作中心</span>
        </div>
        <div className={styles.creationBanner}>
          <div className={styles.creationText}>
            <div className={styles.creationBannerTitle}>
              开启你的觅问创作之旅
            </div>
            <div className={styles.creationBannerDesc}>
              快来成为觅问创作者吧~
            </div>
          </div>
          <HighlightTwoTone className={styles.creationMascot} />
        </div>
        <button
          type="button"
          className={styles.creationBtn}
          onClick={() => handleWriteClick()}
        >
          <PlusOutlined />
          开始创作
        </button>
      </div>
      {/* 大家都在搜 */}
      <div className={styles.sideCard}>
        <div className={styles.sideHead}>
          <FireFilled className={styles.icon} />
          <span className={styles.sideTitle}>大家都在搜</span>
        </div>
        <div>
          {hotPostList.map((item) => (
            <div key={item.id} className={styles.searchItem}>
              <span className={styles.dot} />
              <span
                className={styles.keyword}
                onClick={() => router.push(`/topics/${item.topic_id}`)}
              >
                {item.title}
              </span>
              <span className={styles.hotness}>{item.votes}热度</span>
              <span className={`${tagClass(item.tag || "")} ${styles.tag}`}>
                {item.tag || ""}
              </span>
            </div>
          ))}
        </div>
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
  );
}

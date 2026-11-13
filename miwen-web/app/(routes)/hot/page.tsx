"use client";
import { PlainText } from "@/app/components/Dompurify";
import SiderRight from "@/app/components/SiderRight";
import { getHotPostList } from "@/app/lib/api";
import { CreatePostDto } from "@/app/types/topic";
import { FireFilled, ShareAltOutlined } from "@ant-design/icons";
import { Typography } from "antd";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import styles from "./hot.module.scss";

const { Paragraph } = Typography;
const defaultCover = "/logo.svg";

export default function Hot() {
  const router = useRouter();
  const [hotList, setHotList] = useState<CreatePostDto[]>([]);
  useEffect(() => {
    const init = async () => {
      const res = await getHotPostList();
      setHotList(res.data);
    };
    init();
  }, []);

  return (
    <div className="container">
      <div className={styles["content-home"]}>
        {/* 主列：热榜列表 */}
        <div className={styles["main-column"]}>
          <div className={styles.hotList}>
            {hotList.map((item, index) => (
              <div key={index} className={styles.hotItem}>
                <div className={styles.rankCol}>
                  <span className={styles.rankNum}>{index + 1}</span>
                </div>
                <div className={styles.itemBody}>
                  <div
                    className={styles.itemTitle}
                    onClick={() => router.push(`/topics/${item.topic_id}`)}
                  >
                    {item.title}
                  </div>
                  <div className={styles.itemSummary}>
                    <Paragraph ellipsis={{ rows: 4 }}>
                      {PlainText(item.content)}
                    </Paragraph>
                  </div>

                  <div className={styles.itemMeta}>
                    <span className={styles.metaHeat}>
                      <FireFilled />
                      {item.votes}
                    </span>
                    <span className={styles.metaShare}>
                      <ShareAltOutlined />
                      分享
                    </span>
                  </div>
                </div>
                <img
                  className={styles.itemThumb}
                  src={item.cover || defaultCover}
                  alt={item.title}
                />
              </div>
            ))}
          </div>
        </div>
        {/* 右侧栏 */}
        <SiderRight />
      </div>
    </div>
  );
}

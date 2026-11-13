"use client";
import { PlainText } from "@/app/components/Dompurify";
import SiderRight from "@/app/components/SiderRight";
import { getAllUserList } from "@/app/lib/api";
import type { UserInfo } from "@/app/types/user";
import { Typography } from "antd";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import styles from "./follow.module.scss";

const { Paragraph } = Typography;
const defaultCover = "/logo.svg";

export default function Follow() {
  const router = useRouter();
  const [userList, setUserList] = useState<UserInfo[]>([]);
  useEffect(() => {
    const init = async () => {
      const res = await getAllUserList();
      setUserList(res.data?.lists || []);
    };
    init();
  }, []);
  return (
    <div className="container">
      <div className={styles["content-home"]}>
        {/* 主列：热榜列表 */}
        <div className={styles["main-column"]}>
          <div className={styles.hotList}>
            {userList.map((item, index) => (
              <div key={index} className={styles.hotItem}>
                <div className={styles.rankCol}>
                  <span className={styles.rankNum}>{index + 1}</span>
                </div>
                <img
                  className={styles.itemThumb}
                  src={item.avatar || defaultCover}
                  alt={item.username}
                />
                <div className={styles.itemBody}>
                  <div
                    className={styles.itemTitle}
                    onClick={() => router.push(`/users/${item.uid}`)}
                  >
                    {item.username}
                  </div>
                  <div className={styles.itemSummary}>
                    <Paragraph ellipsis={{ rows: 4 }}>
                      {PlainText(item.signature || "")}
                    </Paragraph>
                  </div>
                </div>
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

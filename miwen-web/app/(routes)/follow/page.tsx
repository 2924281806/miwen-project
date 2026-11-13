"use client";
import { PlainText } from "@/app/components/Dompurify";
import SiderRight from "@/app/components/SiderRight";
import { followUser, getAllUserList, unfollowUser } from "@/app/lib/api";
import { useUserStore } from "@/app/store/userStore";
import type { UserInfo } from "@/app/types/user";
import { PlusOutlined } from "@ant-design/icons";
import { Button, Empty, message, Typography } from "antd";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import styles from "./follow.module.scss";

const { Paragraph } = Typography;
const defaultCover = "/logo.svg";

export default function Follow() {
  const router = useRouter();
  const [userList, setUserList] = useState<UserInfo[]>([]);
  const userInfo = useUserStore((state) => state.userInfo);

  useEffect(() => {
    const init = async () => {
      const res = await getAllUserList();
      if (res.code === 200) {
        setUserList(res.data?.lists || []);
      } else {
        setUserList([]);
      }
    };
    init();
  }, []);

  // 关注用户
  const handleFollowUser = async (uid: number) => {
    const res = await followUser(uid);
    if (res.code === 200) {
      message.success(res.msg || "关注成功");
      setUserList((prev) =>
        prev.map((item) =>
          parseInt(item.uid) === uid ? { ...item, is_follow: true } : item,
        ),
      );
    } else {
      message.error(res.msg || "关注失败");
    }
  };

  // 取消关注用户
  const handleUnfollowUser = async (uid: number) => {
    const res = await unfollowUser(uid);
    if (res.code === 200) {
      message.success(res.msg || "取消关注成功");
      setUserList((prev) =>
        prev.map((item) =>
          parseInt(item.uid) === uid ? { ...item, is_follow: false } : item,
        ),
      );
    } else {
      message.error(res.msg || "取消关注失败");
    }
  };

  return (
    <div className="container">
      <div className={styles["content-home"]}>
        {/* 主列：热榜列表 */}
        <div className={styles["main-column"]}>
          <div className={styles.hotList}>
            {userList.length === 0 ? (
              <Empty
                style={{ height: "100vh", marginTop: "80px" }}
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description="暂无数据"
              />
            ) : (
              userList.map((item, index) => (
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
                      onClick={() => router.push(`/user/${item.uid}`)}
                    >
                      {item.username}
                    </div>
                    <div className={styles.itemSummary}>
                      <Paragraph ellipsis={{ rows: 2 }}>
                        {PlainText(item.signature || "")}
                      </Paragraph>
                    </div>
                  </div>
                  {String(item.uid) === userInfo?.uid ? null : (
                    <div>
                      <Button
                        color="primary"
                        variant="outlined"
                        icon={item?.is_follow ? "" : <PlusOutlined />}
                        className={item?.is_follow ? styles.followBtn : ""}
                        onClick={() => {
                          if (item?.is_follow) {
                            handleUnfollowUser(parseInt(item.uid));
                          } else {
                            handleFollowUser(parseInt(item.uid));
                          }
                        }}
                      >
                        {item?.is_follow ? "已关注" : "关注"}
                      </Button>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
        {/* 右侧栏 */}
        <SiderRight />
      </div>
    </div>
  );
}

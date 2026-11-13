"use client";
import SearchBar from "@/app/components/header/SearchBar";
import { getMyUser, logout } from "@/app/lib/api";
import { useUserStore } from "@/app/store/userStore";
import type { UserInfo } from "@/app/types/user";
import logo from "@/public/logo.svg";
import {
  PlusOutlined,
  PoweroffOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { Avatar, Layout, Popover, PopoverProps } from "antd";
import { createStaticStyles } from "antd-style";
import clsx from "clsx";
import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import styles from "./Header.module.scss";

const { Header } = Layout;

const App = () => {
  // ========== 【全部Hook放在最顶部，顺序固定，永远优先执行】 ==========
  const router = useRouter();
  const defaultAvatar =
    "https://zos.alipayobjects.com/rmsportal/jkjgkEfvpUPVyRjUImniVslZfWPnJuuZ.png";

  const pathname = usePathname();
  const setUserInfo = useUserStore((state) => state.setUserInfo);
  const userLogout = useUserStore((state) => state.logout);
  const isLogin = useUserStore((state) => state.isLogin);
  const userInfo = useUserStore((state) => state.userInfo);

  const classNames = createStaticStyles(({ css }) => ({
    container: css`
      background: "red";
    `,
  }));
  const style: PopoverProps["styles"] = {
    container: {
      padding: "16px 0",
    },
    content: {
      color: "#333",
    },
  };
  // ========== 普通函数定义 ==========
  // ========== 获取当前用户信息 ==========
  async function getCurrentUser() {
    try {
      const res = await getMyUser();
      if (res?.code === 200) {
        setUserInfo(res.data as UserInfo);
      }
    } catch (error) {
      console.error("获取用户信息失败", error);
    }
  }

  // ========== 处理退出登录 ==========
  const handleLogout = async () => {
    try {
      const res = await logout();
      if (res?.code === 200) {
        router.push("/");
        useUserStore.getState().triggerRefreshUser(false);
        userLogout();
      }
    } catch (error) {
      console.error("退出失败", error);
    }
  };

  // ========== Effect ==========
  useEffect(() => {
    getCurrentUser();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLogin]);

  // ========== 条件return：必须放在所有Hook、Effect之后 ==========
  const hideHeader = ["/login", "/register"].includes(pathname);
  if (hideHeader) return null;

  // ========== JSX ==========
  return (
    <div>
      <div className={styles["header-container"]}>
        <Header>
          <div className={styles["css-lgijre"]}>
            <div className={styles["link-items"]}>
              <Link href="/" className={styles["logo-link"]}>
                <Image src={logo} alt="logo" />
              </Link>
              <nav className={styles["nav"]}>
                <Link href="/follow">
                  <div
                    className={clsx(
                      styles["nav-link"],
                      pathname === "/follow" && styles["nav-link-active"],
                    )}
                  >
                    关注
                  </div>
                </Link>
                <Link href="/">
                  <div
                    className={clsx(
                      styles["nav-link"],
                      pathname === "/" && styles["nav-link-active"],
                    )}
                  >
                    首页
                  </div>
                </Link>
                <Link href="/hot">
                  <div
                    className={clsx(
                      styles["nav-link"],
                      pathname === "/hot" && styles["nav-link-active"],
                    )}
                  >
                    热榜
                  </div>
                </Link>
                <Link href="/group">
                  <div
                    className={clsx(
                      styles["nav-link"],
                      pathname.startsWith("/group") &&
                        styles["nav-link-active"],
                    )}
                  >
                    圈子
                  </div>
                </Link>
              </nav>
            </div>

            <div className={styles["right-area"]}>
              <SearchBar />
              <Link href="/topics/write" className={styles["btn-primary"]}>
                <PlusOutlined />
                写作
              </Link>

              {userInfo ? (
                <div className={styles["user-area"]}>
                  <Popover
                    placement="bottomLeft"
                    trigger="click"
                    classNames={classNames}
                    styles={style}
                    content={
                      <div>
                        <Link
                          href={`/user/${userInfo.uid}`}
                          className={styles["menu-items"]}
                        >
                          <span className={styles["user-icon"]}>
                            <UserOutlined />
                          </span>
                          {userInfo.username}
                        </Link>
                        <div className={styles["menu-items"]}>
                          <span className={styles["user-icon"]}>
                            <PoweroffOutlined />
                          </span>
                          <div onClick={handleLogout}>退出登录</div>
                        </div>
                      </div>
                    }
                  >
                    <div className={styles["items-center"]}>
                      <Avatar
                        src={userInfo.avatar ?? defaultAvatar}
                        size="medium"
                        className={styles["rounded-full"]}
                      />
                    </div>
                  </Popover>
                </div>
              ) : (
                <Link href="/login" className={styles["btn-secondary"]}>
                  登录
                </Link>
              )}
            </div>
          </div>
        </Header>
      </div>
      <div className={styles["css-1g41cri"]}></div>
    </div>
  );
};

export default App;

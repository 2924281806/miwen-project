"use client";
import SearchBar from "@/app/components/header/SearchBar";
import { getMyUser, logout } from "@/app/lib/api";
import { useUserStore } from "@/app/store/userStore";
import type { UserInfo } from "@/app/types/user";
import logo from "@/public/logo.svg";
import { PlusOutlined } from "@ant-design/icons";
import { Avatar, Layout, Popover } from "antd";
import clsx from "clsx";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect } from "react";
import styles from "./Header.module.scss";

const { Header } = Layout;

const App = () => {
  // ========== 【全部Hook放在最顶部，顺序固定，永远优先执行】 ==========
  const defaultAvatar =
    "https://zos.alipayobjects.com/rmsportal/jkjgkEfvpUPVyRjUImniVslZfWPnJuuZ.png";

  const pathname = usePathname();
  const setUserInfo = useUserStore((state) => state.setUserInfo);
  const userLogout = useUserStore((state) => state.logout);
  const isLogin = useUserStore((state) => state.isLogin);
  const userInfo = useUserStore((state) => state.userInfo);

  // ========== 普通函数定义 ==========
  // ========== 获取当前用户信息 ==========
  async function getCurrentUser() {
    try {
      const res = await getMyUser();
      if (res?.code === 200) {
        const result = res.data as UserInfo;
        setUserInfo(result);
      } else {
      }
    } catch (error) {}
  }

  // ========== 处理退出登录 ==========
  const handleLogout = async () => {
    try {
      const res = await logout();
      if (res?.code === 200) {
        useUserStore.getState().triggerRefreshUser(false);
        userLogout();
      }
    } catch (error) {
      console.error("退出失败", error);
    }
  };

  // ========== Effect ==========
  useEffect(() => {
    console.log("isLogin", isLogin);
    getCurrentUser();
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
            <div
              className={clsx(
                "flex items-center gap-8 link-items",
                styles["link-items"],
              )}
            >
              <Link href="/" className="flex items-center gap-2">
                <Image src={logo} alt="logo" />
              </Link>
              <nav className="hidden md:flex items-center gap-6">
                <Link href="/follow">
                  <div
                    className={clsx(
                      "transition-colors",
                      pathname === "/follow" && "text-lg font-bold",
                    )}
                  >
                    关注
                  </div>
                </Link>
                <Link href="/">
                  <div
                    className={clsx(
                      "transition-colors",
                      pathname === "/" && "text-lg font-bold",
                    )}
                  >
                    首页
                  </div>
                </Link>
                <Link href="/recommend">
                  <div
                    className={clsx(
                      "transition-colors",
                      pathname === "/recommend" && "text-lg font-bold",
                    )}
                  >
                    推荐
                  </div>
                </Link>
                <Link href="/hot">
                  <div
                    className={clsx(
                      "transition-colors",
                      pathname === "/hot" && "text-lg font-bold",
                    )}
                  >
                    热榜
                  </div>
                </Link>
                <Link href="/group">
                  <div
                    className={clsx(
                      "transition-colors",
                      pathname === "/group" && "text-lg font-bold",
                    )}
                  >
                    圈子
                  </div>
                </Link>
              </nav>
            </div>

            <div className="flex items-center gap-4">
              <SearchBar />
              <Link href="/waite" className={styles["btn-primary"]}>
                <PlusOutlined />
                写作
              </Link>

              {userInfo ? (
                <div className="flex items-center gap-3">
                  <Popover
                    placement="bottomLeft"
                    content={<a onClick={handleLogout}>退出登录</a>}
                  >
                    <Link
                      href={`/user/${userInfo.uid}`}
                      className="flex items-center gap-2"
                    >
                      <Avatar
                        src={userInfo.avatar ?? defaultAvatar}
                        size="medium"
                        className={styles["rounded-full"]}
                      />
                    </Link>
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

"use client";
import SearchBar from "@/app/components/header/SearchBar";
import { getMyUser } from "@/app/lib/api";
import type { UserInfo } from "@/app/types/user";
import logo from "@/public/logo.svg";
import { PlusOutlined } from "@ant-design/icons";
import { Avatar, Layout } from "antd";
import clsx from "clsx";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import styles from "./Header.module.scss";

const { Header } = Layout;

const App = () => {
  const defaultAvatar =
    "https://zos.alipayobjects.com/rmsportal/jkjgkEfvpUPVyRjUImniVslZfWPnJuuZ.png";

  const [currentUser, setCurrentUser] = useState<UserInfo | null>(null);
  const pathname = usePathname();

  // 登录注册页不显示菜单
  const pathnameList = ["/login", "/register"];
  if (pathnameList.includes(pathname)) {
    return null;
  }

  const getCurrentUser = async () => {
    try {
      const res = await getMyUser();
      if (res?.code === 200) {
        const result = res.data as UserInfo;
        setCurrentUser(result);
      } else {
        setCurrentUser(null);
      }
    } catch (error) {
      setCurrentUser(null);
    }
  };
  useEffect(() => {
    getCurrentUser();
  }, []);

  useEffect(() => {
    console.log(styles);
    console.log("currentUser", currentUser);
  }, [currentUser]);

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
              <Link href="/questions/ask" className={styles["btn-primary"]}>
                <PlusOutlined />
                提问
              </Link>

              {currentUser ? (
                <div className="flex items-center gap-3">
                  <Link
                    href={`/user/${currentUser.uid}`}
                    className="flex items-center gap-2"
                  >
                    <Avatar
                      src={currentUser.avatar ?? defaultAvatar}
                      size="medium"
                      className={styles["rounded-full"]}
                    />
                  </Link>
                </div>
              ) : (
                <Link href="/auth/login" className={styles["btn-secondary"]}>
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

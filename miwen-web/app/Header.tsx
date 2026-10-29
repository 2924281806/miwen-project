"use client";
import type { MenuProps } from "antd";
import { Menu } from "antd";
import { createStaticStyles } from "antd-style";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";

import menuItems from "@/app/utils/routes";

const classNames = createStaticStyles(({ css }) => ({
  root: css`
    width: 1200px;
    margin: 0 auto;
    padding: 8px;
  `,
  item: css`
    color: red;
  `,
}));

const styles: MenuProps["styles"] = {
  root: { border: "none", padding: 8, width: 1200, margin: "0 auto" },
  item: { color: "#333", fontSize: 18, padding: 8 },
  subMenu: { list: { color: "#fa541c" } },
};
const App = () => {
  const [current, setCurrent] = useState("");
  const router = useRouter();
  const pathname = usePathname();

  const shareProps: MenuProps = {
    classNames,
    items: menuItems,
  };
  // 点击菜单切换当前选中项
  const onClick: MenuProps["onClick"] = (e) => {
    setCurrent(e.key);
    router.push(e.key);
  };
  // 登录注册页不显示菜单
  const pathnameList = ["/login", "/register"];
  if (pathnameList.includes(pathname)) {
    return null;
  }

  return (
    <Menu
      onClick={onClick}
      selectedKeys={[current]}
      mode="horizontal"
      items={menuItems}
      {...shareProps}
      styles={styles}
    />
  );
};

export default App;

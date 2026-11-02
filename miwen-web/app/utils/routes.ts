import type { MenuProps } from "antd";
type MenuItem = Required<MenuProps>["items"][number];

const menuItems: MenuItem[] = [
  {
    key: "/",
    label: "首页",
  },
  {
    key: "/login",
    label: "登录",
  },
  {
    key: "/register",
    label: "注册",
  },
  {
    key: "/home",
    label: "home页",
  },
  {
    key: "/hot",
    label: "热榜",
  },
  {
    key: "/recommend",
    label: "推荐",
  },
  {
    key: "/group",
    label: "圈子",
  },
];
export default menuItems;

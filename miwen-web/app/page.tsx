import styles from "./page.module.scss";

// 首页
export default function Home() {
  return (
    <div className="container">
      <div className={styles["content-home"]}>
        <div className={styles["main-column"]}>11</div>
        <div className={styles["sider-right"]}>22</div>
      </div>
    </div>
  );
}

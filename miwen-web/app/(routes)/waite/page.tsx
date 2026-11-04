"use client";
import dynamic from "next/dynamic";
import { useState } from "react";
import styles from "./write.module.scss";

// 引入TinyEditor组件，设置为客户端组件
const TinyEditor = dynamic(
  () => import("@/app/components/markdown/TinyEditor"),
  {
    ssr: false,
  },
);

export default function Waite() {
  const [content, setContent] = useState("");

  return (
    <div>
      <div className={styles["write-center"]}>
        <TinyEditor value={content} onChange={setContent} height={400} />
        <div>{content}</div>
      </div>
    </div>
  );
}

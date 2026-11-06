"use client";
import { getAllForumList } from "@/app/lib/api";
import { ForumListDto } from "@/app/types/forum";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function Group() {
  const [forumList, setForumList] = useState<ForumListDto[]>([]);

  useEffect(() => {
    const getForum = async () => {
      const res = await getAllForumList();
      if (res?.code === 200) {
        setForumList(res?.data || []);
      }
    };
    getForum();
  }, []);

  return (
    <div className="container">
      <Link href="/group/new">新建圈子</Link>
      {forumList.map((item) => (
        <div key={item.forum_id}>
          <Link href={`/group/${item.forum_id}`}>{item.name}</Link>
        </div>
      ))}
    </div>
  );
}

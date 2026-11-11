"use client";
import ImageUpload from "@/app/components/ImageUpload";
import TinyEditor from "@/app/components/markdown/TinyEditor";
import { createPost, getAllForumList, uploadImage } from "@/app/lib/api";
import type { ApiResult } from "@/app/types/user";
import { PlusOutlined, QuestionCircleOutlined } from "@ant-design/icons";
import { Button, Input, message, Popover, Select } from "antd";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import styles from "./write.module.scss";

const { TextArea } = Input;

export default function Waite() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const fid = searchParams.get("fid");
  const [content, setContent] = useState("");
  const [title, setTitle] = useState("");
  const [imgList, setImgList] = useState<string[]>([]);
  const [forumId, setForumId] = useState<number>();
  const [forumList, setForumList] = useState<
    { value: number; label: string }[]
  >([]);

  // 自定义上传图标
  const uploadApi = async (file: File, onSuccess: (url: string) => void) => {
    const fd = new FormData();
    fd.append("file", file);
    const res: ApiResult<string> = await uploadImage(fd);
    if (res.code === 200) {
      onSuccess(res.data);
      return;
    }
    throw new Error(res.msg || "上传图片失败");
  };

  // ========== Get Forum ==========
  const getForum = async () => {
    const res = await getAllForumList();
    if (res?.code === 200) {
      const result = res?.data || [];
      const list = result.map((item) => ({
        value: item?.forum_id,
        label: item?.name,
      }));
      setForumList(list);
    }
  };
  // ========== Post ==========
  const handlePost = async () => {
    if (!title) {
      message.error("请输入帖子标题！");
      return;
    }
    if (!content) {
      message.error("请输入帖子内容！");
      return;
    }
    if (!forumId) {
      message.error("请选择帖子圈子！");
      return;
    }
    const res = await createPost({
      title: title,
      content: content,
      cover: imgList[0],
      forum_id: forumId,
    });
    if (res?.code === 200) {
      message.success("帖子发布成功！");
      let timer: ReturnType<typeof setTimeout> | null = null;
      timer = setTimeout(() => {
        // 跳转到帖子详情页
        router.push(`/topics/${res?.data?.topic_id}`);
        clearTimeout(timer ?? undefined);
        timer = null;
        setTitle("");
        setContent("");
        setImgList([]);
        setForumId(undefined);
      }, 1000);
    } else {
      message.error(res?.msg || "帖子发布失败！");
    }
  };

  // ========== Effect ==========
  useEffect(() => {
    const load = async () => {
      if (fid) {
        setForumId(Number(fid));
      }
      await getForum();
    };
    load();
  }, []);

  return (
    <div className={styles["write-container"]}>
      <div className={styles["write-center"]}>
        <div className={styles["write-input"]}>
          <TextArea
            className={styles["write-textarea"]}
            placeholder="请输入标题（最大长度200个字符）"
            autoSize
            variant="underlined"
            value={title}
            maxLength={200}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>
        <TinyEditor value={content} onChange={setContent} height={400} />
        <div className={styles["write-setting"]}>
          <div className={styles["write-setting-title"]}>发布设置</div>
          <div className={styles["write-setting-img"]}>
            <span className={styles["write-setting-img-title"]}>
              添加封面
              <Popover
                content="图片上传格式支持 JPEG、JPG、PNG,并且不能超过2MB！"
                placement="bottomRight"
                trigger="hover"
              >
                <QuestionCircleOutlined
                  className={styles["write-setting-img-icon"]}
                />
              </Popover>
            </span>
            <div className={styles["write-setting-img-btn"]}>
              <div>
                <ImageUpload
                  value={imgList}
                  onChange={setImgList}
                  multiple={false}
                  maxCount={1}
                  maxSize={2}
                  customUpload={uploadApi}
                  slotTrigger={
                    <div>
                      <PlusOutlined />
                      添加帖子封面
                    </div>
                  }
                ></ImageUpload>
              </div>
              <div className={styles["write-setting-img-tip"]}>
                图片上传格式支持 JPEG、JPG、PNG
              </div>
            </div>
          </div>
          <div className={styles["write-setting-img"]}>
            <span className={styles["write-setting-img-title"]}>
              选择圈子
              <Popover
                content="该帖子发布在哪个圈子下面！"
                placement="bottomRight"
                trigger="hover"
              >
                <QuestionCircleOutlined
                  className={styles["write-setting-img-icon"]}
                />
              </Popover>
            </span>
            <div className={styles["write-setting-img-btn"]}>
              <Select
                className={styles["write-setting-select"]}
                onChange={(value) => setForumId(Number(value))}
                options={forumList}
                value={forumId}
              />
            </div>
          </div>
          <div className={styles["write-setting-btn"]}>
            <Button type="primary" onClick={handlePost}>
              发布帖子
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

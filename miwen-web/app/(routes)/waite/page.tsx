"use client";
import TinyEditor from "@/app/components/markdown/TinyEditor";
import { createPost, getAllForumList } from "@/app/lib/api";
import { PlusOutlined, QuestionCircleOutlined } from "@ant-design/icons";
import type { GetProp, UploadProps } from "antd";
import { Button, Input, message, Popover, Select, Upload } from "antd";
import { useEffect, useState } from "react";
import styles from "./write.module.scss";

type FileType = Parameters<GetProp<UploadProps, "beforeUpload">>[0];

const { TextArea } = Input;

const getBase64 = (img: FileType, callback: (url: string) => void) => {
  const reader = new FileReader();
  reader.addEventListener("load", () => callback(reader.result as string));
  reader.readAsDataURL(img);
};

export default function Waite() {
  const [content, setContent] = useState("");
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [imageUrl, setImageUrl] = useState<string>();
  const [forumId, setForumId] = useState<number>();
  const [forumList, setForumList] = useState<
    { value: number; label: string }[]
  >([]);

  const props: UploadProps = {
    name: "avatar",
    accept: "image/jpeg,image/png,image/jpg,image/gif",
    listType: "picture-card",
    showUploadList: false,
    maxCount: 1,
    className: styles["write-upload"],
    beforeUpload(file: FileType) {
      return beforeUpload(file);
    },
    onChange(info) {
      if (info.file.status === "uploading") {
        console.log(info.file, info.fileList);
        setLoading(true);
        return;
      }
      if (info.file.status === "done") {
        // 上传成功后，获取图片的base64编码
        getBase64(info.file.originFileObj as FileType, (url) => {
          message.success(`${info.file.name} file uploaded successfully`);
          setLoading(false);
          setImageUrl(url);
        });
      }
    },
  };
  const beforeUpload = (file: FileType) => {
    const isJpgOrPng =
      file.type === "image/jpeg" ||
      file.type === "image/png" ||
      file.type === "image/jpg" ||
      file.type === "image/gif";
    if (!isJpgOrPng) {
      message.error(
        "You can only upload <JPEG>/<JPG>/<PNG>/<GIF> format file!",
      );
    }
    const isLt2M = file.size / 1024 / 1024 < 2;
    if (!isLt2M) {
      message.error("Image must smaller than 2MB!");
    }
    return isJpgOrPng && isLt2M;
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
    console.log(title, content, forumId);
    if (!title) {
      message.error("请输入帖子标题！");
      return;
    }
    if (!content) {
      message.error("请输入帖子内容！");
      return;
    }
    if (!forumId) {
      message.error("请选择帖子板块！");
      return;
    }
    const res = await createPost({
      title: title,
      content: content,
      cover: imageUrl,
      forum_id: forumId,
    });
    if (res?.code === 200) {
      message.success("帖子发布成功！");
      // 跳转到帖子详情页
    }
  };

  // ========== Effect ==========
  useEffect(() => {
    getForum();
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
                <Upload {...props}>
                  <PlusOutlined />
                  添加帖子封面
                </Upload>
              </div>
              <div className={styles["write-setting-img-tip"]}>
                图片上传格式支持 JPEG、JPG、PNG
              </div>
            </div>
          </div>
          <div className={styles["write-setting-img"]}>
            <span className={styles["write-setting-img-title"]}>
              选择板块
              <Popover
                content="该帖子发布在哪个板块下面！"
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
              发布
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

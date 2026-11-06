"use client";
import { PlusOutlined } from "@ant-design/icons";
import type { UploadProps } from "antd";
import { Upload, message } from "antd";
import styles from "./index.module.scss";
import type { ImageUploadProps } from "./types";

export default function ImageUpload(props: ImageUploadProps) {
  const {
    value = [],
    onChange,
    multiple = false,
    maxCount = 1,
    maxSize = 5,
    accept = "image/png,image/jpeg,image/jpg,image/webp",
    disabled = false,
    customUpload,
    slotTrigger,
  } = props;

  // 上传前校验
  const beforeUpload: UploadProps["beforeUpload"] = (file) => {
    const isImage = file.type.startsWith("image/");
    if (!isImage) {
      message.error("只能上传图片文件！");
      return Upload.LIST_IGNORE;
    }
    const isLtSize = file.size / 1024 / 1024 < maxSize;
    if (!isLtSize) {
      message.error(`图片不能超过 ${maxSize}MB！`);
      return Upload.LIST_IGNORE;
    }
    return false; // 阻止 antd 自带上传，走自定义上传
  };

  // 自定义上传
  const handleChange: UploadProps["onChange"] = async (info) => {
    const rawFile = info.file.originFileObj ?? (info.file as unknown as File);
    // 只处理刚加入的文件
    if (!rawFile) {
      return;
    }
    if (!customUpload) {
      message.warning("请传入 customUpload 方法");
      return;
    }
    try {
      await customUpload(rawFile, (url) => {
        const newList = multiple ? [...value, url] : [url];
        onChange?.(newList);
      });
    } catch (err) {
      message.error(err instanceof Error ? err.message : "上传失败");
    }
  };

  // 删除图片
  const handleRemove = (url: string) => {
    const newList = value.filter((item) => item !== url);
    onChange?.(newList);
  };

  const uploadList = value?.map((url) => ({
    uid: url,
    name: url,
    status: "done" as const,
    url,
  }));
  // 默认上传按钮
  const defaultTrigger = (
    <div className={styles["upload-btn"]}>
      <PlusOutlined />
      <div>上传图片</div>
    </div>
  );

  return (
    <Upload
      className={styles["upload-container"]}
      listType="picture-card"
      fileList={uploadList}
      beforeUpload={beforeUpload}
      onChange={handleChange}
      onRemove={(file) => handleRemove(file.url!)}
      multiple={multiple}
      maxCount={maxCount}
      accept={accept}
      disabled={disabled}
    >
      {uploadList.length >= maxCount ? null : (slotTrigger ?? defaultTrigger)}
    </Upload>
  );
}

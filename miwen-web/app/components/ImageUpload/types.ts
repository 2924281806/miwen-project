import React from "react";

export interface ImageUploadProps {
  // 绑定值，图片地址数组
  value?: string[];
  onChange?: (urls: string[]) => void;
  // 是否多图
  multiple?: boolean;
  // 最大上传数量
  maxCount?: number;
  // 单文件大小 MB
  maxSize?: number;
  // 允许后缀
  accept?: string;
  // 是否禁用
  disabled?: boolean;
  // 上传按钮名称
  buttonText?: string;
  // 自定义上传请求
  customUpload?: (file: File, onSuccess: (url: string) => void) => void;
  // 自定义触发按钮
  slotTrigger?: React.ReactNode;
}

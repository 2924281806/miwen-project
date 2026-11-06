"use client";
import { uploadImage } from "@/app/lib/api";
import type { Editor as TinyMCEEditor } from "@tinymce/tinymce-react";
import dynamic from "next/dynamic";
import { useCallback, useRef } from "react";
const apiKey = process.env.NEXT_PUBLIC_API_KEY;

// TinyMCE 编辑器实例在 setup 中可用的最小 API 结构
interface TinyMCEInstance {
  ui: {
    registry: {
      addButton: (
        name: string,
        config: {
          text: string;
          tooltip: string;
          icon: string;
          onAction: () => void;
        },
      ) => void;
    };
  };
  selection: {
    getBookmark: (type: number, normalize: boolean) => unknown;
    getContent: (args: { format: string }) => string;
    moveToBookmark: (bookmark: unknown) => void;
  };
  dom: { encode: (text: string) => string };
  setContent: (html: string) => void;
}

// 动态导入，关闭SSR，核心！
const Editor = dynamic(
  () => import("@tinymce/tinymce-react").then((mod) => mod.Editor),
  {
    ssr: false,
  },
);

export interface TinyEditorProps {
  value?: string;
  initialValue?: string;
  onChange?: (html: string) => void;
  height?: number;
  readonly?: boolean;
  disabled?: boolean;
  /** 额外tinymce init配置，会合并默认配置 */
  initExtra?: Record<string, unknown>;
  /** 编辑器实例回调，拿到editor调用原生api */
  onReady?: (editor: TinyMCEEditor) => void;
}

export default function TinyEditor(props: TinyEditorProps) {
  const {
    value,
    initialValue,
    onChange,
    height = 400,
    readonly = false,
    disabled = false,
    initExtra = {},
    onReady,
  } = props;

  const editorRef = useRef<TinyMCEEditor | null>(null);

  const handleInit = useCallback(
    (_evt: unknown, editor: TinyMCEEditor) => {
      editorRef.current = editor;
      onReady?.(editor);
    },
    [onReady],
  );

  const handleChange = useCallback(
    (content: string) => {
      onChange?.(content);
    },
    [onChange],
  );

  // 默认配置
  const initConfig = {
    height,
    menubar: false,
    language: "zh-CN",
    placeholder: "请输入帖子内容",
    plugins: "advlist autolink link image table lists code preview",
    toolbar:
      "undo redo | blocks | bold italic underline strikethrough | bullist numlist | link image table | code preview clearallformat",
    content_style:
      "body { font-family:system-ui; font-size:14px; } img { max-width:100%; height:auto; }",

    // 图片上传钩子
    images_upload_handler: async (blobInfo: {
      blob: () => Blob;
      filename: () => string;
    }) => {
      //  处理图片上传逻辑
      const formData = new FormData();
      formData.append("file", blobInfo.blob(), blobInfo.filename());
      // 上传图片到服务器
      const res = await uploadImage(formData);
      if (res.code !== 200) throw new Error(res.msg || "上传图片失败");
      return res.data;
    },
    setup(editor: unknown) {
      const ed = editor as TinyMCEInstance;
      // 自定义方法：调用tinymce原生API
      ed.ui.registry.addButton("clearallformat", {
        text: "",
        tooltip: "清除全部格式",
        icon: "removeformat",
        onAction: () => {
          // 保存选区书签
          const bookmark = ed.selection.getBookmark(2, true);
          // 获取选中内容的纯文本
          const text = ed.selection.getContent({ format: "text" });
          if (!text) return;

          // 把换行分隔的文本转成p段落，你也可以改成<br/>
          const html = text
            .split(/\r?\n/)
            .filter(Boolean)
            .map((line: string) => `<p>${ed.dom.encode(line)}</p>`)
            .join("");

          // 替换选中区域
          ed.setContent(html);
          // 恢复选区
          ed.selection.moveToBookmark(bookmark);
        },
      });
    },
    ...initExtra,
  };

  return (
    <Editor
      apiKey={apiKey}
      value={value}
      initialValue={initialValue}
      disabled={disabled}
      readonly={readonly}
      init={initConfig}
      onInit={handleInit}
      onEditorChange={handleChange}
    />
  );
}

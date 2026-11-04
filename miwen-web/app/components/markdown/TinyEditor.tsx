"use client";
import { uploadImage } from "@/app/lib/api";
import { Editor } from "@tinymce/tinymce-react";
import { useRef } from "react";

type TinyEditorProps = {
  value: string;
  onChange: (value: string) => void;
  height: number;
};

const apiKey = process.env.NEXT_PUBLIC_API_KEY;

export default function TinyEditor({
  value,
  onChange,
  height,
}: TinyEditorProps) {
  const editorRef = useRef<Editor>(null);

  const onInit = (editor: Editor) => {
    editorRef.current = editor;
  };
  const onEditorChange = (content: string) => {
    // onChange?.(content);
    console.log(content);
  };
  const init = {
    initialValue: "Welcome to TinyMCE!",
    language: "zh-CN",
    plugins: [
      "advlist",
      "autolink",
      "lists",
      "link",
      "image",
      "charmap",
      "anchor",
      "searchreplace",
      "visualblocks",
      "code",
      "fullscreen",
      "insertdatetime",
      "media",
      "table",
      "preview",
      "help",
      "wordcount",
    ],
    toolbar:
      "undo redo | blocks | bold italic forecolor | alignleft aligncenter alignright | bullist numlist outdent indent | link image table code | removeformat help",
    menubar: false, // 关闭顶部菜单栏
    branding: false, // 去掉tiny水印
    tinycomments_mode: "embedded",
    tinycomments_author: "Author name",
    mergetags_list: [
      { value: "First.Name", title: "First Name" },
      { value: "Email", title: "Email" },
    ],
    images_upload_handler: async (blobInfo: any) => {
      //  处理图片上传逻辑
      const formData = new FormData();
      formData.append("file", blobInfo.blob(), blobInfo.filename());
      // 上传图片到服务器
      const res = await uploadImage(formData);
      if (!res.code) throw new Error(res.message);
      return res.data;
    },
  };
  return (
    <Editor
      apiKey={apiKey}
      ref={editorRef}
      initialValue={value ?? ""}
      onInit={onInit}
      onEditorChange={onEditorChange}
      init={init}
    />
  );
}

"use client";
import ImageUpload from "@/app/components/ImageUpload";
import { createForum, getAllCategoryList, uploadImage } from "@/app/lib/api";
import type { CreateForumDtoParams } from "@/app/types/forum";
import type { ApiResult } from "@/app/types/user";
import { PlusOutlined } from "@ant-design/icons";
import type { FormProps, RadioChangeEvent } from "antd";
import { Button, Form, Input, message, Radio, Space, Typography } from "antd";
import axios from "axios";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import styles from "./newCircle.module.scss";

const { TextArea } = Input;
const { Text } = Typography;

export default function NewCircle() {
  const router = useRouter();
  const [form] = Form.useForm();
  const [value, setValue] = useState("");
  const [imgList, setImgList] = useState<string[]>([]);
  const [categoryValue, setCategoryValue] = useState<number | undefined>(
    undefined,
  );

  // 分类列表：value 必须是后端返回的分类真实 id，否则创建圈子会参数校验失败
  const [categoryList, setCategoryList] = useState<
    { label: string; value: number }[]
  >([]);

  useEffect(() => {
    const loadCategories = async () => {
      try {
        const res = await getAllCategoryList();
        if (res.code === 200) {
          setCategoryList(
            res.data.map((item) => ({ label: item.name, value: item.id })),
          );
          return;
        }
        message.error(res.msg || "获取分类列表失败");
      } catch (err) {
        console.error("获取分类列表失败：", err);
      }
    };
    loadCategories();
  }, []);

  const joinOptions = [
    { label: "公开加入", value: "public", className: "label-1" },
    { label: "需要申请", value: "private", className: "label-2" },
  ];

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
  // 分类选择器
  const onChange = ({ target: { value } }: RadioChangeEvent) => {
    setCategoryValue(value as number);
  };
  const onFinish: FormProps<CreateForumDtoParams>["onFinish"] = async (
    values,
  ) => {
    values.icon = imgList[0];
    try {
      const res = await createForum(values);
      if (res.code === 200) {
        message.success("新建圈子成功");
        form.resetFields();
        setImgList([]);
        setValue("");
        setCategoryValue(undefined);
        setTimeout(() => {
          router.push(`/group/${res?.data?.forum_id}`);
        }, 1000);
        return;
      }
      message.error(res.msg || "新建圈子失败");
    } catch (err) {
      const msg = axios.isAxiosError(err)
        ? err.response?.data?.msg || err.message
        : (err as Error).message;
      message.error(msg || "新建圈子失败");
    }
  };

  return (
    <div className={styles["circle-container"]}>
      <div className={styles["circle-center"]}>
        <div className={styles["circle-title"]}>新建圈子</div>
        <Form
          initialValues={{
            join_type: "public",
          }}
          form={form}
          name="control-hooks"
          onFinish={onFinish}
          style={{ maxWidth: "100%" }}
          labelCol={{ flex: "80px" }}
          labelAlign="end"
        >
          <Form.Item name="name" label="圈子名称" rules={[{ required: true }]}>
            <Input placeholder="请输入圈子名称" />
          </Form.Item>
          <Form.Item
            name="description"
            label="简介"
            rules={[{ required: true }]}
          >
            <TextArea
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder="请输入圈子描述"
              autoSize={{ minRows: 3, maxRows: 5 }}
            />
          </Form.Item>
          <Form.Item name="icon" label="圈子图标">
            <ImageUpload
              value={imgList}
              onChange={setImgList}
              multiple={false}
              maxCount={1}
              maxSize={2}
              buttonText="添加圈子图标"
              customUpload={uploadApi}
              slotTrigger={
                <div>
                  <PlusOutlined />
                  添加圈子图标
                </div>
              }
            ></ImageUpload>
          </Form.Item>
          <Form.Item name="category_id" label="圈子分类">
            <Radio.Group
              onChange={onChange}
              className={styles["category-group"]}
              buttonStyle="solid"
            >
              {categoryList.map((item) => (
                <Radio.Button
                  className={styles["category-group-item"]}
                  value={item.value}
                  key={item.value}
                >
                  <Text
                    ellipsis={{
                      tooltip: {
                        title: item.label,
                        color: "#f8f8fa",
                        placement: "bottom",
                      },
                    }}
                    style={{
                      display: "inline-block",
                      maxWidth: "100%",
                      lineHeight: "30px",
                    }}
                  >
                    <span
                      style={{
                        color:
                          categoryValue === item.value ? "#fff" : undefined,
                      }}
                    >
                      {item.label}
                    </span>
                  </Text>
                </Radio.Button>
              ))}
            </Radio.Group>
          </Form.Item>
          <Form.Item name="join_type" label="加入方式">
            <Radio.Group options={joinOptions} />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                发布圈子
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </div>
    </div>
  );
}

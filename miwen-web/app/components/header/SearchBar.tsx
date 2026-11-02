import { SearchOutlined } from "@ant-design/icons";
import type { FormProps } from "antd";
import { Form, Input } from "antd";
import clsx from "clsx";
import styles from "./SearchBar.module.scss";
type FieldType = {
  query?: string;
};

export default function SearchBar() {
  const onFinish: FormProps<FieldType>["onFinish"] = (values) => {
    if (values.query) {
      console.log("Success:", values.query);
    }
  };
  const [form] = Form.useForm<FieldType>();

  return (
    <Form form={form} onFinish={onFinish} className="relative">
      <Form.Item name="query" style={{ marginBottom: 0 }}>
        <Input
          type="text"
          placeholder="搜索问题..."
          className={styles["input-search"]}
        />
      </Form.Item>
      <SearchOutlined
        onClick={() => form.submit()}
        className={clsx(
          "absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2",
          styles["search-icon"],
        )}
      />
    </Form>
  );
}

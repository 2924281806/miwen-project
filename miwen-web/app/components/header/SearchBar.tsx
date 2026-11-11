import { SearchOutlined } from "@ant-design/icons";
import type { FormProps } from "antd";
import { Form, Input } from "antd";
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
    <Form form={form} onFinish={onFinish} className={styles["search-form"]}>
      <Form.Item name="query" style={{ marginBottom: 0 }}>
        <Input
          type="text"
          placeholder="搜索问题..."
          className={styles["input-search"]}
        />
      </Form.Item>
      <SearchOutlined
        onClick={() => form.submit()}
        className={styles["search-icon"]}
      />
    </Form>
  );
}

"use client";
import ImageUpload from "@/app/components/ImageUpload";
import { register, uploadImage } from "@/app/lib/api";
import type { ApiResult } from "@/app/types/user";
import { Button, Form, Input } from "antd";
import axios from "axios";
import Link from "next/link";
import { useRouter } from "next/navigation";
import type { FormEvent } from "react";
import { useState } from "react";
import styles from "../auth.module.scss";

// 与后端 schema 保持一致：用户名 2-50，密码 6-32，邮箱合法
const USERNAME_MIN = 2;
const USERNAME_MAX = 50;
const PASSWORD_MIN = 6;
const PASSWORD_MAX = 32;

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function Register() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [avatar, setAvatar] = useState<string[]>([]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    const name = username.trim();
    const mail = email.trim();

    if (!name || !mail || !password) {
      setError("请填写用户名、邮箱和密码");
      return;
    }
    if (name.length < USERNAME_MIN || name.length > USERNAME_MAX) {
      setError(`用户名长度需在 ${USERNAME_MIN}-${USERNAME_MAX} 个字符之间`);
      return;
    }
    if (!EMAIL_PATTERN.test(mail)) {
      setError("请输入正确的邮箱地址");
      return;
    }
    if (password.length < PASSWORD_MIN || password.length > PASSWORD_MAX) {
      setError(`密码长度需在 ${PASSWORD_MIN}-${PASSWORD_MAX} 位之间`);
      return;
    }

    setLoading(true);
    setError("");
    setSuccess(false);
    try {
      const params = {
        username: name,
        email: mail,
        password,
        avatar: avatar[0],
      };
      const result = await register(params);
      if (result.code !== 200 || !result.data) {
        setError(result.msg || "注册失败");
        return;
      }
      setSuccess(true);
      let timer: ReturnType<typeof setTimeout> | null = null;
      timer = setTimeout(() => {
        // 跳转到帖子详情页
        router.push("/login");
        setUsername("");
        setEmail("");
        setPassword("");
        clearTimeout(timer ?? undefined);
        timer = null;
      }, 1000);
    } catch (err) {
      const msg = axios.isAxiosError(err) ? err.response?.data?.msg : "";
      setError(msg || "网络异常，请稍后重试");
      setSuccess(false);
    } finally {
      setLoading(false);
    }
  };
  const uploadApi = async (file: File, onSuccess: (url: string) => void) => {
    const formData = new FormData();
    formData.append("file", file);
    const res: ApiResult<string> = await uploadImage(formData);
    if (res?.code !== 200 || !res?.data) {
      throw new Error(res?.msg || "上传失败");
    }
    onSuccess(res.data);
  };

  return (
    <main className={styles.main}>
      <div className={styles.card}>
        <h1 className={styles.title}>注册</h1>
        <Form
          name="basic"
          labelCol={{ span: 4 }}
          wrapperCol={{ span: 20 }}
          style={{ maxWidth: 600 }}
          initialValues={{ remember: true }}
          onFinish={handleSubmit}
          autoComplete="off"
        >
          <Form.Item label="头像" name="avatar" className={styles.avatar}>
            <ImageUpload
              value={avatar}
              listType="picture-circle"
              onChange={setAvatar}
              multiple={false}
              maxCount={1}
              maxSize={2}
              customUpload={uploadApi}
              slotTrigger={<div>选择头像</div>}
            />
          </Form.Item>
          <Form.Item
            label="用户名"
            name="username"
            rules={[{ required: true, message: "请输入用户名!" }]}
          >
            <Input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="请输入用户名"
              autoComplete="username"
              maxLength={USERNAME_MAX}
              className={styles.input}
            />
          </Form.Item>
          <Form.Item
            label="邮箱"
            name="email"
            rules={[{ required: true, message: "请输入邮箱!" }]}
          >
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="请输入邮箱"
              autoComplete="email"
              className={styles.input}
            />
          </Form.Item>

          <Form.Item
            label="密码"
            name="password"
            rules={[
              {
                required: true,
                message: `请输入密码（${PASSWORD_MIN}-${PASSWORD_MAX} 位）!`,
              },
            ]}
          >
            <Input.Password
              name="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={`请输入密码（${PASSWORD_MIN}-${PASSWORD_MAX} 位）`}
              autoComplete="new-password"
              maxLength={PASSWORD_MAX}
              className={styles.input}
            />
          </Form.Item>

          <Form.Item className={styles.submitForm}>
            {error && (
              <p role="alert" className={styles.error}>
                {error}
              </p>
            )}

            {success && (
              <p role="status" className={styles.success}>
                注册成功，请前往登录页登录
              </p>
            )}
            <Button
              type="primary"
              htmlType="submit"
              disabled={loading}
              className={styles.submit}
            >
              {loading ? "注册中..." : "注册"}
            </Button>
          </Form.Item>
        </Form>
        <Link href="/login" className={styles.link}>
          已有账号，去登录
        </Link>
      </div>
    </main>
  );
}

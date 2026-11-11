"use client";

import { login } from "@/app/lib/api";
import { useUserStore } from "@/app/store/userStore";
import type { LoginInfo } from "@/app/types/user";
import { Button, Form, Input } from "antd";
import axios from "axios";
import Link from "next/link";
import { useRouter } from "next/navigation";
import type { FormEvent } from "react";
import { useState } from "react";
import styles from "../auth.module.scss";

export default function Login() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const setToken = useUserStore((s) => s.setToken);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    if (!username.trim() || !password) {
      setError("请输入用户名和密码");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const param: LoginInfo = {
        username,
        password,
      };
      const res = await login(param);

      if (res.code !== 200 || !res.data) {
        setError("登录失败");
        return;
      }
      const accessToken = res.data.access_token;
      setToken(accessToken);
      useUserStore.getState().triggerRefreshUser(true);
      router.push("/");
    } catch (err) {
      const msg = axios.isAxiosError(err) ? err.response?.data?.msg : "";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className={styles.main}>
      <div className={styles.card}>
        <h1 className={styles.title}>登录</h1>
        <Form
          name="basic"
          labelCol={{ span: 4 }}
          wrapperCol={{ span: 20 }}
          style={{ maxWidth: 600 }}
          initialValues={{ remember: true }}
          onFinish={handleSubmit}
          autoComplete="off"
        >
          <Form.Item
            label="用户名"
            name="username"
            rules={[{ required: true, message: "请输入邮箱或用户名!" }]}
          >
            <Input
              id="username"
              name="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="请输入邮箱或用户名"
              autoComplete="username"
              className={styles.input}
            />
          </Form.Item>

          <Form.Item
            label="密码"
            name="password"
            rules={[{ required: true, message: "请输入用户密码!" }]}
          >
            <Input.Password
              id="password"
              name="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="请输入用户密码"
              autoComplete="current-password"
              className={styles.input}
            />
          </Form.Item>

          <Form.Item className={styles.submitForm}>
            {error && (
              <p role="alert" className={styles.error}>
                {error}
              </p>
            )}

            <Button type="primary" htmlType="submit" className={styles.submit}>
              {loading ? "登录中..." : "登录"}
            </Button>
          </Form.Item>
        </Form>

        <Link href="/register" className={styles.link}>
          注册新用户
        </Link>
      </div>
    </main>
  );
}

"use client";

import { register } from "@/app/lib/api";
import axios from "axios";
import Link from "next/link";
import { useRouter } from "next/navigation";
import type { FormEvent } from "react";
import { useState } from "react";

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

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

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
      };
      const result = await register(params);
      if (result.code !== 200 || !result.data) {
        setError(result.msg || "注册失败");
        return;
      }
      setSuccess(true);
      setTimeout(() => {
        router.push("/login");
        setUsername("");
        setEmail("");
        setPassword("");
      }, 1000);
    } catch (err) {
      const msg = axios.isAxiosError(err) ? err.response?.data?.msg : "";
      setError(msg || "网络异常，请稍后重试");
      setSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-neutral-100 px-4 dark:bg-neutral-950">
      <div className="w-full max-w-sm rounded-xl bg-white p-8 shadow-md dark:bg-neutral-900">
        <h1 className="mb-6 text-center text-2xl font-semibold text-neutral-900 dark:text-neutral-100">
          注册
        </h1>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1">
            <label
              htmlFor="username"
              className="text-sm text-neutral-600 dark:text-neutral-400"
            >
              用户名
            </label>
            <input
              id="username"
              name="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="请输入用户名"
              autoComplete="username"
              maxLength={USERNAME_MAX}
              className="rounded-lg border border-neutral-300 px-3 py-2 text-sm outline-none focus:border-blue-500 dark:border-neutral-700 dark:bg-neutral-800 dark:text-neutral-100"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label
              htmlFor="email"
              className="text-sm text-neutral-600 dark:text-neutral-400"
            >
              邮箱
            </label>
            <input
              id="email"
              name="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="请输入邮箱"
              autoComplete="email"
              className="rounded-lg border border-neutral-300 px-3 py-2 text-sm outline-none focus:border-blue-500 dark:border-neutral-700 dark:bg-neutral-800 dark:text-neutral-100"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label
              htmlFor="password"
              className="text-sm text-neutral-600 dark:text-neutral-400"
            >
              密码
            </label>
            <input
              id="password"
              name="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={`请输入密码（${PASSWORD_MIN}-${PASSWORD_MAX} 位）`}
              autoComplete="new-password"
              maxLength={PASSWORD_MAX}
              className="rounded-lg border border-neutral-300 px-3 py-2 text-sm outline-none focus:border-blue-500 dark:border-neutral-700 dark:bg-neutral-800 dark:text-neutral-100"
            />
          </div>

          {error && (
            <p role="alert" className="text-sm text-red-500">
              {error}
            </p>
          )}

          {success && (
            <p
              role="status"
              className="text-sm text-green-600 dark:text-green-400"
            >
              注册成功，请前往登录页登录
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="mt-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "注册中..." : "注册"}
          </button>
        </form>

        <Link
          href="/login"
          className="mt-4 block rounded-lg border border-neutral-300 px-4 py-2 text-center text-sm text-neutral-700 transition hover:bg-neutral-100 dark:border-neutral-700 dark:text-neutral-300 dark:hover:bg-neutral-800"
        >
          已有账号，去登录
        </Link>
      </div>
    </main>
  );
}

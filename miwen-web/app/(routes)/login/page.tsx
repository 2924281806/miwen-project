"use client";

import { login } from "@/app/lib/api";
import type { LoginInfo } from "@/app/types/user";
import axios from "axios";
import Link from "next/link";
import { useRouter } from "next/navigation";
import type { FormEvent } from "react";
import { useState } from "react";

export default function Login() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

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
      const body = res.data.access_token;
      setToken(body || "");
      // 后端业务错误也以 HTTP 200 返回，需要判断 code
      // if (body.code !== 200 || !body.data) {
      //   setError(body.msg || "登录失败");
      //   return;
      // }

      // localStorage.setItem("access_token", body.data.access_token);
      // localStorage.setItem("refresh_token", body.data.refresh_token);
      // router.push("/home");
    } catch (err) {
      const msg = axios.isAxiosError(err) ? err.response?.data?.msg : "";
      setError(msg || "网络异常，请稍后重试");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-neutral-100 px-4 dark:bg-neutral-950">
      <div className="w-full max-w-sm rounded-xl bg-white p-8 shadow-md dark:bg-neutral-900">
        <h1 className="mb-6 text-center text-2xl font-semibold text-neutral-900 dark:text-neutral-100">
          登录
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
              placeholder="请输入邮箱或用户名"
              autoComplete="username"
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
              placeholder="请输入用户密码"
              autoComplete="current-password"
              className="rounded-lg border border-neutral-300 px-3 py-2 text-sm outline-none focus:border-blue-500 dark:border-neutral-700 dark:bg-neutral-800 dark:text-neutral-100"
            />
          </div>

          {error && (
            <p role="alert" className="text-sm text-red-500">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="mt-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "登录中..." : "登录"}
          </button>
        </form>

        <Link
          href="/register"
          className="mt-4 block rounded-lg border border-neutral-300 px-4 py-2 text-center text-sm text-neutral-700 transition hover:bg-neutral-100 dark:border-neutral-700 dark:text-neutral-300 dark:hover:bg-neutral-800"
        >
          注册新用户
        </Link>
      </div>
    </main>
  );
}

"use client";
import DOMPurify from "isomorphic-dompurify";

// 自定义安全配置：禁止iframe、禁止所有on事件
const DEFAULT_CONFIG = {
  // USE_PROFILES: { html: true }, // 只允许html标签，关闭svg/mathml
  // FORBID_TAGS: ["iframe", "embed", "object"],
  // FORBID_ATTR: [/^on/, "formaction"], // 干掉 onclick / onload / onerror 等所有事件
  // ALLOWED_TAGS: ["p", "b", "i", "u", "br", "a", "img"], // 白名单，只保留这些标签
  // ALLOWED_ATTR: ["href", "src", "alt", "title"],
};

export function SafeHtml({ html }: { html: string }) {
  const clean = DOMPurify.sanitize(html, DEFAULT_CONFIG);
  return <div dangerouslySetInnerHTML={{ __html: clean }} />;
}

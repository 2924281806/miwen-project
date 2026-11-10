"use client";
import DOMPurify from "dompurify";

export function Dompurify({ html }: { html: string }) {
  const safe = DOMPurify.sanitize(html);
  return <div dangerouslySetInnerHTML={{ __html: safe }} />;
}

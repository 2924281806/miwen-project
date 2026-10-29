import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  // 匹配根路径 / 到首页
  // if (request.nextUrl.pathname === "/") {
  //   return NextResponse.redirect(new URL("/home", request.url));
  // }
}

// 匹配器：只拦截根路径
export const config = {
  matcher: ["/"],
};

import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

const protectedRoutes = ["/dashboard", "/analyze", "/history", "/account", "/admin"]

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  const isProtected = protectedRoutes.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`)
  )

  if (!isProtected) {
    return NextResponse.next()
  }

  const hasToken =
    request.cookies.has("sb-access-token") ||
    request.headers.get("authorization")?.startsWith("Bearer ")

  if (!hasToken) {
    const loginUrl = new URL("/auth/login", request.url)
    loginUrl.searchParams.set("redirect", pathname)
    return NextResponse.redirect(loginUrl)
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/analyze/:path*",
    "/history/:path*",
    "/account/:path*",
    "/admin/:path*",
  ],
}

import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"
import { createClient } from "@/lib/supabase-server"

const protectedRoutes = ["/dashboard", "/analyze", "/history", "/account", "/admin"]

export async function middleware(request: NextRequest) {
  const authDisabled = process.env.NEXT_PUBLIC_DISABLE_AUTH === "true"
  const supabaseConfigured = !!(
    process.env.NEXT_PUBLIC_SUPABASE_URL &&
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
  )

  if (authDisabled || !supabaseConfigured) {
    return NextResponse.next()
  }

  const { pathname } = request.nextUrl

  const isProtected = protectedRoutes.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`)
  )

  if (!isProtected) {
    return NextResponse.next()
  }

  const response = NextResponse.next()
  const supabase = createClient(request, response)
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    const loginUrl = new URL("/auth/login", request.url)
    loginUrl.searchParams.set("redirect", pathname)
    return NextResponse.redirect(loginUrl)
  }

  return response
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

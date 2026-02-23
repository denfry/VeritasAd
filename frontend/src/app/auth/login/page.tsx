"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { ArrowRight, ShieldCheck, Github, Globe } from "lucide-react"

export default function LoginPage() {
  return (
    <div className="min-h-screen grid lg:grid-cols-2 relative overflow-hidden bg-background">
      {/* Left Panel: Content & Visualization */}
      <div className="relative hidden lg:flex flex-col justify-between p-12 border-r bg-muted/5">
        <div className="z-10">
          <Link href="/" className="flex items-center gap-2 font-semibold">
            <ShieldCheck className="h-6 w-6" />
            <span>VeritasAd</span>
          </Link>
        </div>
        
        <div className="z-10 max-w-lg">
          <blockquote className="space-y-2">
            <p className="text-lg font-medium text-foreground">
              "VeritasAd has transformed how we monitor brand safety across thousands of user-generated videos. 
              The accuracy of their multi-modal detection is unmatched."
            </p>
            <footer className="text-sm text-muted-foreground">
              Sofia Davis, Compliance Lead at Acme Corp
            </footer>
          </blockquote>
        </div>

        <div className="absolute inset-0 z-0">
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:24px_24px]"></div>
          <motion.div 
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-primary/5 rounded-full blur-3xl"
            animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.5, 0.3] }}
            transition={{ duration: 10, repeat: Infinity }}
          />
        </div>
      </div>

      {/* Right Panel: Form */}
      <div className="flex items-center justify-center p-8">
        <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
          <div className="flex flex-col space-y-2 text-center">
            <h1 className="text-2xl font-semibold tracking-tight">Welcome back</h1>
            <p className="text-sm text-muted-foreground">
              Enter your email to sign in to your account
            </p>
          </div>

          <div className="grid gap-6">
            <form onSubmit={(e) => e.preventDefault()}>
              <div className="grid gap-4">
                <div className="grid gap-2">
                  <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70" htmlFor="email">
                    Email
                  </label>
                  <input
                    id="email"
                    placeholder="name@example.com"
                    type="email"
                    autoCapitalize="none"
                    autoComplete="email"
                    autoCorrect="off"
                    className="input-field"
                  />
                </div>
                <div className="grid gap-2">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70" htmlFor="password">
                      Password
                    </label>
                    <Link
                      href="/auth/forgot-password"
                      className="text-xs text-muted-foreground underline-offset-4 hover:underline"
                    >
                      Forgot password?
                    </Link>
                  </div>
                  <input
                    id="password"
                    type="password"
                    className="input-field"
                  />
                </div>
                <button className="btn btn-primary w-full group">
                  Sign In with Email
                  <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                </button>
              </div>
            </form>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">
                  Or continue with
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <button className="btn btn-outline w-full" type="button">
                <Github className="mr-2 h-4 w-4" />
                GitHub
              </button>
              <button className="btn btn-outline w-full" type="button">
                <Globe className="mr-2 h-4 w-4" />
                Google
              </button>
            </div>
          </div>

          <p className="px-8 text-center text-sm text-muted-foreground">
            <Link href="/auth/register" className="hover:text-foreground underline underline-offset-4">
              Don't have an account? Sign Up
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

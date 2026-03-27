"use client"
/* eslint-disable @next/next/no-img-element */

import * as React from "react"
import { cn } from "@/lib/utils"

interface AvatarProps {
  src?: string
  alt?: string
  fallback?: string
  size?: "sm" | "md" | "lg" | "xl"
  className?: string
}

const sizeClasses = {
  sm: "h-8 w-8 text-xs",
  md: "h-10 w-10 text-sm",
  lg: "h-12 w-12 text-base",
  xl: "h-16 w-16 text-lg",
}

export function Avatar({ src, alt, fallback, size = "md", className }: AvatarProps) {
  const [error, setError] = React.useState(false)

  const initials = fallback
    ? fallback.split(" ").map(n => n[0]).join("").toUpperCase().slice(0, 2)
    : "?"

  if (src && !error) {
    // eslint-disable-next-line @next/next/no-img-element
    return (
      <div
        className={cn(
          "relative flex shrink-0 overflow-hidden rounded-full bg-muted",
          sizeClasses[size],
          className
        )}
      >
        <img
          src={src}
          alt={alt || "Avatar"}
          className="aspect-square h-full w-full object-cover"
          onError={() => setError(true)}
        />
      </div>
    )
  }

  return (
    <div
      className={cn(
        "relative flex shrink-0 overflow-hidden rounded-full bg-muted",
        sizeClasses[size],
        className
      )}
    >
      <div className="flex h-full w-full items-center justify-center bg-primary/10 text-primary font-medium">
        {initials}
      </div>
    </div>
  )
}

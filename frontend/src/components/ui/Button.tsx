import { ButtonHTMLAttributes, forwardRef } from "react"
import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"

function cn(...inputs: Array<string | undefined | null | false | Record<string, boolean>>) {
  return twMerge(clsx(inputs))
}

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "primary" | "outline" | "ghost" | "link"
  size?: "default" | "sm" | "lg" | "icon"
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    const variantStyles: Record<string, boolean> = {
      "bg-primary text-primary-foreground hover:opacity-90 shadow-md hover:shadow-lg hover:shadow-primary/30":
        variant === "default" || variant === "primary",
      "border border-border text-foreground hover:border-primary/50 hover:bg-primary/5":
        variant === "outline",
      "text-muted-foreground hover:text-foreground hover:bg-muted/50":
        variant === "ghost",
      "text-primary underline-offset-4 hover:underline":
        variant === "link",
    }

    const sizeStyles: Record<string, boolean> = {
      "h-9 px-3": size === "sm",
      "h-11 px-8": size === "lg",
      "h-10 w-10": size === "icon",
    }

    return (
      <button
        className={cn(
          "inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50",
          variantStyles,
          sizeStyles,
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)

Button.displayName = "Button"

export { Button }

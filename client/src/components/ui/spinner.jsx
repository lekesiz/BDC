import * as React from "react"
import { cn } from "@/lib/utils"

const Spinner = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "inline-block animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]",
      "h-6 w-6",
      className
    )}
    role="status"
    {...props}
  >
    <span className="sr-only">Loading...</span>
  </div>
))
Spinner.displayName = "Spinner"

export { Spinner }
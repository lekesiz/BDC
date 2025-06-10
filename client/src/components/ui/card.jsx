// TODO: i18n - processed
import React from 'react';
import { cn } from '@/lib/utils';
/**
 * Card component for displaying content in a card layout
 */import { useTranslation } from "react-i18next";
const Card = React.forwardRef(({ className, ...props }, ref) =>
<div
  ref={ref}
  className={cn(
    "rounded-lg border bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-card-foreground shadow-sm",
    "transition-shadow hover:shadow-md",
    className
  )}
  {...props} />

);
Card.displayName = "Card";
/**
 * Card header component
 */
const CardHeader = React.forwardRef(({ className, ...props }, ref) =>
<div
  ref={ref}
  className={cn("flex flex-col space-y-1.5 p-4 sm:p-6", className)}
  {...props} />

);
CardHeader.displayName = "CardHeader";
/**
 * Card title component
 */
const CardTitle = React.forwardRef(({ className, ...props }, ref) =>
<h3
  ref={ref}
  className={cn(
    "text-lg sm:text-xl lg:text-2xl font-semibold leading-none tracking-tight text-gray-900 dark:text-gray-100",
    className
  )}
  {...props} />

);
CardTitle.displayName = "CardTitle";
/**
 * Card description component
 */
const CardDescription = React.forwardRef(({ className, ...props }, ref) =>
<p
  ref={ref}
  className={cn("text-sm text-gray-600 dark:text-gray-400", className)}
  {...props} />

);
CardDescription.displayName = "CardDescription";
/**
 * Card content component
 */
const CardContent = React.forwardRef(({ className, ...props }, ref) =>
<div ref={ref} className={cn("p-4 sm:p-6 pt-0", className)} {...props} />
);
CardContent.displayName = "CardContent";
/**
 * Card footer component
 */
const CardFooter = React.forwardRef(({ className, ...props }, ref) =>
<div
  ref={ref}
  className={cn("flex flex-col sm:flex-row sm:items-center gap-2 p-4 sm:p-6 pt-0", className)}
  {...props} />

);
CardFooter.displayName = "CardFooter";
export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent };
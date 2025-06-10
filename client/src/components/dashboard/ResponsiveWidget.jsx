// TODO: i18n - processed
import React from 'react';
import { Link } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { ArrowUpRight, TrendingUp, TrendingDown } from 'lucide-react';
/**
 * Responsive dashboard widget component
 * Adapts layout and content based on screen size
 */import { useTranslation } from "react-i18next";
export const ResponsiveWidget = ({
  title,
  value,
  icon: Icon,
  trend,
  trendValue,
  link,
  linkText = 'View all',
  className,
  loading = false,
  error = null,
  size = 'default', // 'compact', 'default', 'large'
  priority = 'normal' // 'high', 'normal', 'low' - affects mobile visibility
}) => {const { t } = useTranslation();
  // Size classes for different widget sizes
  const sizeClasses = {
    compact: 'p-3 sm:p-4',
    default: 'p-4 sm:p-6',
    large: 'p-6 sm:p-8'
  };
  const iconSizes = {
    compact: 'h-8 w-8 sm:h-10 sm:w-10',
    default: 'h-10 w-10 sm:h-12 sm:w-12',
    large: 'h-12 w-12 sm:h-14 sm:w-14'
  };
  const valueSizes = {
    compact: 'text-xl sm:text-2xl',
    default: 'text-2xl sm:text-3xl',
    large: 'text-3xl sm:text-4xl'
  };
  // Hide low priority widgets on very small screens
  const priorityClasses = {
    high: '',
    normal: '',
    low: 'hidden xs:block'
  };
  if (loading) {
    return (
      <Card className={cn('animate-pulse', className)}>
        <div className={sizeClasses[size]}>
          <div className="flex items-center justify-between">
            <div className="space-y-2 flex-1">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24"></div>
              <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-32"></div>
            </div>
            <div className={cn('bg-gray-200 dark:bg-gray-700 rounded-full', iconSizes[size])}></div>
          </div>
        </div>
      </Card>);

  }
  if (error) {
    return (
      <Card className={cn('border-red-200 dark:border-red-800', className)}>
        <div className={sizeClasses[size]}>
          <p className="text-sm text-red-600 dark:text-red-400">{t("components.failed_to_load")}{title}</p>
        </div>
      </Card>);

  }
  return (
    <Card className={cn(
      'hover:shadow-md transition-shadow',
      priorityClasses[priority],
      className
    )}>
      <div className={sizeClasses[size]}>
        <div className="flex items-start justify-between">
          <div className="space-y-1 sm:space-y-2 flex-1 min-w-0">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 truncate">
              {title}
            </h3>
            <div className="flex items-baseline space-x-2">
              <p className={cn(
                'font-semibold text-gray-900 dark:text-gray-100',
                valueSizes[size]
              )}>
                {value}
              </p>
              {trend &&
              <div className={cn(
                'flex items-center text-xs sm:text-sm font-medium',
                trend === 'up' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
              )}>
                  {trend === 'up' ?
                <TrendingUp className="h-3 w-3 sm:h-4 sm:w-4 mr-0.5" /> :

                <TrendingDown className="h-3 w-3 sm:h-4 sm:w-4 mr-0.5" />
                }
                  <span>{trendValue}</span>
                </div>
              }
            </div>
            {link &&
            <Link
              to={link}
              className="inline-flex items-center text-xs sm:text-sm text-primary hover:text-primary-dark dark:text-primary-light dark:hover:text-primary transition-colors mt-2">

                {linkText}
                <ArrowUpRight className="h-3 w-3 sm:h-4 sm:w-4 ml-1" />
              </Link>
            }
          </div>
          {Icon &&
          <div className={cn(
            'flex-shrink-0 ml-3 sm:ml-4',
            'bg-primary/10 dark:bg-primary/20 text-primary dark:text-primary-light rounded-full p-2 sm:p-3'
          )}>
              <Icon className={iconSizes[size]} />
            </div>
          }
        </div>
      </div>
    </Card>);

};
/**
 * Responsive widget grid component
 * Automatically adjusts grid layout based on screen size
 */
export const ResponsiveWidgetGrid = ({
  children,
  columns = 'auto',
  className
}) => {const { t } = useTranslation();
  const columnClasses = {
    auto: 'grid-cols-1 xs:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
    1: 'grid-cols-1',
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 xs:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
    6: 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6'
  };
  return (
    <div className={cn(
      'grid gap-3 sm:gap-4 lg:gap-6',
      columnClasses[columns] || columnClasses.auto,
      className
    )}>
      {children}
    </div>);

};
/**
 * Mobile-optimized activity feed widget
 */
export const ActivityWidget = ({
  activities = [],
  title = 'Recent Activity',
  loading = false,
  className
}) => {const { t } = useTranslation();
  if (loading) {
    return (
      <Card className={cn('animate-pulse', className)}>
        <CardHeader className="pb-3">
          <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-32"></div>
        </CardHeader>
        <CardContent className="space-y-3">
          {[1, 2, 3].map((i) =>
          <div key={i} className="flex items-start space-x-3">
              <div className="h-8 w-8 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
              <div className="flex-1 space-y-2">
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>);

  }
  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <CardTitle className="text-base sm:text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3 sm:space-y-4">
          {activities.length === 0 ?
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">{t("components.no_recent_activity")}

          </p> :

          activities.slice(0, 5).map((activity, index) =>
          <div key={index} className="flex items-start space-x-3">
                <div className={cn(
              'flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center',
              activity.type === 'success' ? 'bg-green-100 dark:bg-green-900 text-green-600 dark:text-green-400' :
              activity.type === 'warning' ? 'bg-yellow-100 dark:bg-yellow-900 text-yellow-600 dark:text-yellow-400' :
              activity.type === 'error' ? 'bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-400' :
              'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
            )}>
                  {activity.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-900 dark:text-gray-100 line-clamp-2">
                    {activity.message}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {activity.time}
                  </p>
                </div>
              </div>
          )
          }
        </div>
      </CardContent>
    </Card>);

};
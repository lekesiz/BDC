// TODO: i18n - processed
import React, { useState } from 'react';
import { RefreshCw, X, Download, AlertCircle, CheckCircle } from 'lucide-react';
import { useAppUpdate } from '../../hooks/usePWA';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';
/**
 * App Update Notification Component
 * Displays when a new version of the app is available
 */import { useTranslation } from "react-i18next";
export function UpdateNotification({ onDismiss, className = '' }) {const { t } = useTranslation();
  const { hasUpdate, isUpdating, applyUpdate } = useAppUpdate();
  const [dismissed, setDismissed] = useState(false);
  const [updateStatus, setUpdateStatus] = useState(null);
  if (!hasUpdate || dismissed) {
    return null;
  }
  const handleUpdate = async () => {
    try {
      setUpdateStatus('updating');
      await applyUpdate();
      setUpdateStatus('success');
    } catch (error) {
      console.error('Update failed:', error);
      setUpdateStatus('error');
    }
  };
  const handleDismiss = () => {
    setDismissed(true);
    onDismiss?.();
  };
  const handleLater = () => {
    setDismissed(true);
    // Could schedule a reminder for later
    onDismiss?.();
  };
  if (updateStatus === 'success') {
    return (
      <Alert className={`border-green-200 bg-green-50 dark:bg-green-950 dark:border-green-800 ${className}`}>
        <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
        <AlertDescription className="text-green-800 dark:text-green-200">{t("components.update_applied_successfully_the_app_will_reload_sh")}

        </AlertDescription>
      </Alert>);

  }
  if (updateStatus === 'error') {
    return (
      <Alert className={`border-red-200 bg-red-50 dark:bg-red-950 dark:border-red-800 ${className}`}>
        <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400" />
        <AlertDescription className="text-red-800 dark:text-red-200">
          Update failed. Please refresh the page manually or try again later.
        </AlertDescription>
      </Alert>);

  }
  return (
    <Card className={`border-orange-200 bg-orange-50 dark:bg-orange-950 dark:border-orange-800 ${className}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <RefreshCw className="h-5 w-5 text-orange-600 dark:text-orange-400" />
            <CardTitle className="text-lg text-orange-900 dark:text-orange-100">{t("components.new_version_available")}

            </CardTitle>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleDismiss}
            className="h-6 w-6 p-0 text-orange-600 hover:text-orange-800 dark:text-orange-400">

            <X className="h-4 w-4" />
          </Button>
        </div>
        <CardDescription className="text-orange-700 dark:text-orange-300">{t("components.a_new_version_of_bdc_is_available_with_improvement")}

        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Update benefits */}
          <div className="text-sm text-orange-700 dark:text-orange-300">
            <ul className="list-disc list-inside space-y-1">
              <li>{t("components.performance_improvements")}</li>
              <li>{t("components.security_updates")}</li>
              <li>{t("components.bug_fixes_and_stability")}</li>
              <li>{t("components.new_features_and_enhancements")}</li>
            </ul>
          </div>
          {/* Action buttons */}
          <div className="flex gap-2">
            <Button
              onClick={handleUpdate}
              disabled={isUpdating || updateStatus === 'updating'}
              className="bg-orange-600 hover:bg-orange-700 text-white">

              {isUpdating || updateStatus === 'updating' ?
              <>
                  <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />{t("components.updating")}

              </> :

              <>
                  <Download className="mr-2 h-4 w-4" />{t("components.update_now")}

              </>
              }
            </Button>
            <Button variant="outline" onClick={handleLater}>{t("components.later")}

            </Button>
          </div>
        </div>
      </CardContent>
    </Card>);

}
/**
 * Update Banner
 * Minimal banner notification for updates
 */
export function UpdateBanner({ onDismiss, className = '' }) {const { t } = useTranslation();
  const { hasUpdate, isUpdating, applyUpdate } = useAppUpdate();
  const [dismissed, setDismissed] = useState(false);
  if (!hasUpdate || dismissed) {
    return null;
  }
  const handleUpdate = async () => {
    try {
      await applyUpdate();
    } catch (error) {
      console.error('Update failed:', error);
    }
  };
  const handleDismiss = () => {
    setDismissed(true);
    onDismiss?.();
  };
  return (
    <div className={`bg-gradient-to-r from-orange-500 to-orange-600 text-white ${className}`}>
      <div className="max-w-7xl mx-auto px-4 py-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm">
            <RefreshCw className="h-4 w-4" />
            <span>{t("components.new_version_available")}</span>
          </div>
          <div className="flex items-center gap-2">
            <Button
              onClick={handleUpdate}
              disabled={isUpdating}
              variant="secondary"
              size="sm"
              className="bg-white text-orange-600 hover:bg-orange-50 text-xs px-2 py-1">

              {isUpdating ? 'Updating...' : 'Update'}
            </Button>
            <Button
              onClick={handleDismiss}
              variant="ghost"
              size="sm"
              className="text-white hover:bg-orange-700 h-6 w-6 p-0">

              <X className="h-3 w-3" />
            </Button>
          </div>
        </div>
      </div>
    </div>);

}
/**
 * Update Status Component
 * Shows update progress and status
 */
export function UpdateStatus({ className = '' }) {const { t } = useTranslation();
  const { hasUpdate, isUpdating } = useAppUpdate();
  if (!hasUpdate && !isUpdating) {
    return null;
  }
  return (
    <div className={`flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 ${className}`}>
      {isUpdating &&
      <>
          <div className="h-3 w-3 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
          <span>{t("components.updating_app")}</span>
        </>
      }
      {hasUpdate && !isUpdating &&
      <>
          <AlertCircle className="h-3 w-3 text-orange-500" />
          <span>{t("components.update_available")}</span>
        </>
      }
    </div>);

}
export default UpdateNotification;
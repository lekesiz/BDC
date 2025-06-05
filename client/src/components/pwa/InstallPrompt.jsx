import React, { useState } from 'react';
import { Download, X, Smartphone, Monitor, Zap } from 'lucide-react';
import { useInstallPrompt } from '../../hooks/usePWA';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
/**
 * PWA Installation Prompt Component
 * Shows when the app can be installed as a PWA
 */
export function InstallPrompt({ onDismiss, className = '' }) {
  const { canInstall, isInstalled, isLoading, promptInstall } = useInstallPrompt();
  const [dismissed, setDismissed] = useState(false);
  if (!canInstall || isInstalled || dismissed) {
    return null;
  }
  const handleInstall = async () => {
    try {
      await promptInstall();
    } catch (error) {
      console.error('Installation failed:', error);
    }
  };
  const handleDismiss = () => {
    setDismissed(true);
    onDismiss?.();
  };
  return (
    <Card className={`border-blue-200 bg-blue-50 dark:bg-blue-950 dark:border-blue-800 ${className}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Download className="h-5 w-5 text-blue-600 dark:text-blue-400" />
            <CardTitle className="text-lg text-blue-900 dark:text-blue-100">
              Install BDC App
            </CardTitle>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleDismiss}
            className="h-6 w-6 p-0 text-blue-600 hover:text-blue-800 dark:text-blue-400"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
        <CardDescription className="text-blue-700 dark:text-blue-300">
          Install BDC as an app for a better experience with offline access and faster loading.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Benefits */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="flex items-center gap-2 text-sm text-blue-700 dark:text-blue-300">
              <Zap className="h-4 w-4" />
              <span>Faster loading</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-blue-700 dark:text-blue-300">
              <Smartphone className="h-4 w-4" />
              <span>Works offline</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-blue-700 dark:text-blue-300">
              <Monitor className="h-4 w-4" />
              <span>Native experience</span>
            </div>
          </div>
          {/* Action buttons */}
          <div className="flex gap-2">
            <Button
              onClick={handleInstall}
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              {isLoading ? (
                <>
                  <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  Installing...
                </>
              ) : (
                <>
                  <Download className="mr-2 h-4 w-4" />
                  Install App
                </>
              )}
            </Button>
            <Button variant="outline" onClick={handleDismiss}>
              Not now
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
/**
 * Floating Install Button
 * Minimalist install button that can be placed anywhere
 */
export function FloatingInstallButton({ className = '' }) {
  const { canInstall, isInstalled, isLoading, promptInstall } = useInstallPrompt();
  if (!canInstall || isInstalled) {
    return null;
  }
  const handleInstall = async () => {
    try {
      await promptInstall();
    } catch (error) {
      console.error('Installation failed:', error);
    }
  };
  return (
    <Button
      onClick={handleInstall}
      disabled={isLoading}
      className={`fixed bottom-4 right-4 z-50 h-14 w-14 rounded-full bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl transition-all duration-200 ${className}`}
      aria-label="Install app"
    >
      {isLoading ? (
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-white border-t-transparent" />
      ) : (
        <Download className="h-6 w-6" />
      )}
    </Button>
  );
}
/**
 * Install Banner
 * Full-width banner for prominent display
 */
export function InstallBanner({ onDismiss, className = '' }) {
  const { canInstall, isInstalled, isLoading, promptInstall } = useInstallPrompt();
  const [dismissed, setDismissed] = useState(false);
  if (!canInstall || isInstalled || dismissed) {
    return null;
  }
  const handleInstall = async () => {
    try {
      await promptInstall();
    } catch (error) {
      console.error('Installation failed:', error);
    }
  };
  const handleDismiss = () => {
    setDismissed(true);
    onDismiss?.();
  };
  return (
    <div className={`bg-gradient-to-r from-blue-600 to-blue-700 text-white ${className}`}>
      <div className="max-w-7xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Download className="h-5 w-5" />
              <span className="font-medium">Install BDC App</span>
            </div>
            <span className="hidden sm:inline text-blue-100">
              Get faster access and work offline
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Button
              onClick={handleInstall}
              disabled={isLoading}
              variant="secondary"
              size="sm"
              className="bg-white text-blue-600 hover:bg-blue-50"
            >
              {isLoading ? 'Installing...' : 'Install'}
            </Button>
            <Button
              onClick={handleDismiss}
              variant="ghost"
              size="sm"
              className="text-white hover:bg-blue-800"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
export default InstallPrompt;
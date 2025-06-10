// Advanced Analytics Dashboard Page
// Main analytics hub integrating all advanced analytics components

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BarChart3,
  Activity,
  Users,
  Settings,
  Layout,
  TrendingUp,
  Server,
  Eye,
  Download,
  Filter,
  Calendar,
  Target,
  Zap,
  Globe,
  Bell,
  RefreshCw
} from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AnalyticsProvider } from '@/contexts/AnalyticsContext';
import CustomizableDashboard from '@/components/analytics/CustomizableDashboard';
import RealTimeDashboard from '@/components/analytics/RealTimeDashboard';
import TrainerPerformanceDashboard from '@/components/analytics/TrainerPerformanceDashboard';
import SystemHealthMonitoring from '@/components/analytics/SystemHealthMonitoring';
import { useAuth } from '@/hooks/useAuth';
import { useTranslation } from 'react-i18next';

const AdvancedAnalyticsDashboardPage = () => {
  const { user } = useAuth();
  const { t } = useTranslation();
  
  // State management
  const [activeTab, setActiveTab] = useState('overview');
  const [notificationCount, setNotificationCount] = useState(0);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  // Check user permissions for different analytics views
  const hasAdminAccess = user?.role === 'admin' || user?.role === 'super_admin';
  const hasTrainerAccess = user?.role === 'trainer' || hasAdminAccess;

  // Tab configuration with permissions
  const analyticsTabsConfig = [
    {
      id: 'overview',
      label: 'Overview',
      icon: Layout,
      component: CustomizableDashboard,
      description: 'Customizable dashboard with key metrics',
      permission: true // Available to all authenticated users
    },
    {
      id: 'realtime',
      label: 'Real-time',
      icon: Activity,
      component: RealTimeDashboard,
      description: 'Live monitoring and real-time analytics',
      permission: true
    },
    {
      id: 'trainers',
      label: 'Trainer Performance',
      icon: Users,
      component: TrainerPerformanceDashboard,
      description: 'Trainer effectiveness and performance metrics',
      permission: hasTrainerAccess
    },
    {
      id: 'system',
      label: 'System Health',
      icon: Server,
      component: SystemHealthMonitoring,
      description: 'System monitoring and performance tracking',
      permission: hasAdminAccess
    }
  ];

  // Filter tabs based on permissions
  const availableTabs = analyticsTabsConfig.filter(tab => tab.permission);

  // Update notification count from analytics context
  useEffect(() => {
    // This would be connected to the analytics context
    // setNotificationCount(alertCount);
  }, []);

  // Auto-refresh indicator
  useEffect(() => {
    const interval = setInterval(() => {
      setLastRefresh(new Date());
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  // Tab content renderer
  const renderTabContent = (TabComponent, tabId) => (
    <motion.div
      key={tabId}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      <TabComponent />
    </motion.div>
  );

  return (
    <AnalyticsProvider>
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto py-6">
          {/* Page Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-bold text-gray-900 mb-2">
                  {t('pages.advanced_analytics')}
                </h1>
                <p className="text-gray-600 text-lg">
                  Comprehensive analytics and insights for the BDC platform
                </p>
              </div>
              
              {/* Header Actions */}
              <div className="flex items-center space-x-4">
                <div className="text-sm text-gray-500 flex items-center">
                  <RefreshCw className="w-4 h-4 mr-1" />
                  Last updated: {lastRefresh.toLocaleTimeString()}
                </div>
                
                {notificationCount > 0 && (
                  <div className="relative">
                    <Bell className="w-6 h-6 text-gray-600" />
                    <Badge 
                      variant="destructive" 
                      className="absolute -top-2 -right-2 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
                    >
                      {notificationCount}
                    </Badge>
                  </div>
                )}
                
                <Button variant="outline" size="sm">
                  <Settings className="w-4 h-4 mr-2" />
                  Settings
                </Button>
              </div>
            </div>

            {/* Quick Stats Banner */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="p-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <BarChart3 className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Active Dashboards</p>
                    <p className="text-2xl font-bold">{availableTabs.length}</p>
                  </div>
                </div>
              </Card>
              
              <Card className="p-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <Activity className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Real-time Monitoring</p>
                    <p className="text-2xl font-bold">Live</p>
                  </div>
                </div>
              </Card>
              
              <Card className="p-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <Target className="w-6 h-6 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Data Sources</p>
                    <p className="text-2xl font-bold">8</p>
                  </div>
                </div>
              </Card>
              
              <Card className="p-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-yellow-100 rounded-lg">
                    <Zap className="w-6 h-6 text-yellow-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">System Status</p>
                    <p className="text-lg font-bold text-green-600">Healthy</p>
                  </div>
                </div>
              </Card>
            </div>
          </div>

          {/* Main Analytics Tabs */}
          <Card className="overflow-hidden">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              {/* Tab Navigation */}
              <div className="border-b border-gray-200 bg-white px-6 py-4">
                <TabsList className="grid w-full grid-cols-2 lg:grid-cols-4 gap-4">
                  {availableTabs.map((tab) => (
                    <TabsTrigger
                      key={tab.id}
                      value={tab.id}
                      className="flex items-center space-x-2 p-4 data-[state=active]:bg-primary data-[state=active]:text-white"
                    >
                      <tab.icon className="w-5 h-5" />
                      <div className="text-left">
                        <div className="font-medium">{tab.label}</div>
                        <div className="text-xs opacity-75">{tab.description}</div>
                      </div>
                    </TabsTrigger>
                  ))}
                </TabsList>
              </div>

              {/* Tab Content */}
              <div className="p-6">
                <AnimatePresence mode="wait">
                  {availableTabs.map((tab) => (
                    <TabsContent key={tab.id} value={tab.id} className="mt-0">
                      {renderTabContent(tab.component, tab.id)}
                    </TabsContent>
                  ))}
                </AnimatePresence>
              </div>
            </Tabs>
          </Card>

          {/* Footer Information */}
          <div className="mt-8 text-center text-sm text-gray-500">
            <p>
              Advanced Analytics Dashboard • Version 2.0 • 
              Powered by BDC Analytics Engine
            </p>
            <p className="mt-1">
              {user?.name} • {user?.role} • Last login: {new Date().toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>
    </AnalyticsProvider>
  );
};

export default AdvancedAnalyticsDashboardPage;
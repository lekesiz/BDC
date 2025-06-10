// Trainer Performance Metrics Dashboard
// Comprehensive trainer effectiveness tracking and analytics

import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  User,
  Users,
  Calendar,
  Star,
  TrendingUp,
  TrendingDown,
  Clock,
  Target,
  Award,
  BookOpen,
  MessageSquare,
  BarChart3,
  PieChart,
  Activity,
  CheckCircle,
  AlertTriangle,
  Download,
  Filter,
  Search,
  ChevronDown,
  Eye,
  MoreHorizontal
} from 'lucide-react';
import { useAnalytics } from '@/contexts/AnalyticsContext';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import { 
  BaseChart, 
  TimeSeriesChart, 
  ComparisonChart,
  DistributionChart,
  PerformanceRadar,
  MetricCard 
} from './charts/ChartLibrary';
import exportService from '@/services/export.service';
import { format, subMonths } from 'date-fns';

const TrainerPerformanceDashboard = () => {
  const { requestAnalyticsData, exportAnalytics, isLoading } = useAnalytics();
  
  // State management
  const [trainerData, setTrainerData] = useState(null);
  const [selectedTrainer, setSelectedTrainer] = useState(null);
  const [dateRange, setDateRange] = useState('last3months');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('rating');
  const [sortOrder, setSortOrder] = useState('desc');
  const [filterSpecialization, setFilterSpecialization] = useState('all');
  const [showFilters, setShowFilters] = useState(false);

  // Fetch trainer analytics data
  useEffect(() => {
    const fetchTrainerData = async () => {
      try {
        const data = await requestAnalyticsData('trainers', {
          dateRange,
          includeDetails: true,
          includeMetrics: true
        });
        setTrainerData(data);
      } catch (error) {
        console.error('Error fetching trainer data:', error);
      }
    };

    fetchTrainerData();
  }, [dateRange, requestAnalyticsData]);

  // Filter and sort trainers
  const filteredTrainers = useMemo(() => {
    if (!trainerData?.trainers) return [];

    let filtered = trainerData.trainers.filter(trainer => {
      const matchesSearch = trainer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           trainer.specialization.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesSpecialization = filterSpecialization === 'all' || 
                                   trainer.specialization === filterSpecialization;
      return matchesSearch && matchesSpecialization;
    });

    // Sort trainers
    filtered.sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];
      
      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return filtered;
  }, [trainerData, searchTerm, sortBy, sortOrder, filterSpecialization]);

  // Get specializations for filter
  const specializations = useMemo(() => {
    if (!trainerData?.trainers) return [];
    return [...new Set(trainerData.trainers.map(t => t.specialization))];
  }, [trainerData]);

  // Performance metrics
  const performanceMetrics = useMemo(() => {
    if (!trainerData?.overview) return [];

    return [
      {
        title: 'Total Trainers',
        value: trainerData.overview.totalTrainers,
        change: trainerData.overview.trainerGrowth,
        changeType: trainerData.overview.trainerGrowth >= 0 ? 'positive' : 'negative',
        icon: Users,
        color: 'blue'
      },
      {
        title: 'Average Rating',
        value: `${trainerData.overview.averageRating}/5`,
        change: trainerData.overview.ratingChange,
        changeType: trainerData.overview.ratingChange >= 0 ? 'positive' : 'negative',
        icon: Star,
        color: 'yellow'
      },
      {
        title: 'Sessions Conducted',
        value: trainerData.overview.totalSessions,
        change: trainerData.overview.sessionGrowth,
        changeType: trainerData.overview.sessionGrowth >= 0 ? 'positive' : 'negative',
        icon: Calendar,
        color: 'green'
      },
      {
        title: 'Success Rate',
        value: `${trainerData.overview.successRate}%`,
        change: trainerData.overview.successRateChange,
        changeType: trainerData.overview.successRateChange >= 0 ? 'positive' : 'negative',
        icon: Target,
        color: 'purple'
      }
    ];
  }, [trainerData]);

  // Performance distribution data
  const performanceDistribution = useMemo(() => {
    if (!trainerData?.performanceDistribution) return null;

    return {
      labels: ['Excellent (4.5+)', 'Good (4.0-4.4)', 'Average (3.5-3.9)', 'Below Average (<3.5)'],
      datasets: [{
        data: [
          trainerData.performanceDistribution.excellent,
          trainerData.performanceDistribution.good,
          trainerData.performanceDistribution.average,
          trainerData.performanceDistribution.belowAverage
        ],
        backgroundColor: ['#10B981', '#3B82F6', '#F59E0B', '#EF4444']
      }]
    };
  }, [trainerData]);

  // Workload distribution data
  const workloadData = useMemo(() => {
    if (!trainerData?.workloadData) return null;

    return {
      labels: trainerData.workloadData.labels,
      datasets: [{
        label: 'Assigned Beneficiaries',
        data: trainerData.workloadData.assignedBeneficiaries,
        backgroundColor: 'rgba(59, 130, 246, 0.8)'
      }, {
        label: 'Active Sessions',
        data: trainerData.workloadData.activeSessions,
        backgroundColor: 'rgba(16, 185, 129, 0.8)'
      }]
    };
  }, [trainerData]);

  // Handle trainer selection
  const handleTrainerSelect = (trainer) => {
    setSelectedTrainer(trainer);
  };

  // Handle export
  const handleExport = async (format) => {
    try {
      const exportData = {
        summary: {
          totalTrainers: trainerData?.overview?.totalTrainers || 0,
          averageRating: trainerData?.overview?.averageRating || 0,
          totalSessions: trainerData?.overview?.totalSessions || 0,
          successRate: trainerData?.overview?.successRate || 0
        },
        trainerPerformance: filteredTrainers.map(trainer => ({
          name: trainer.name,
          specialization: trainer.specialization,
          assignedBeneficiaries: trainer.assignedBeneficiaries,
          sessionsConducted: trainer.sessionsConducted,
          avgRating: trainer.avgRating,
          successRate: trainer.successRate,
          workload: trainer.workload,
          status: trainer.status
        })),
        dateRange: {
          start: format(subMonths(new Date(), 3), 'yyyy-MM-dd'),
          end: format(new Date(), 'yyyy-MM-dd')
        }
      };

      if (format === 'pdf') {
        await exportService.exportToPDF(exportData, { filename: 'trainer_performance_report' });
      } else if (format === 'excel') {
        await exportService.exportToExcel(exportData, { filename: 'trainer_performance_data' });
      } else if (format === 'csv') {
        await exportService.exportToCSV(exportData, { 
          filename: 'trainer_performance', 
          dataType: 'trainers' 
        });
      }
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  // Trainer card component
  const TrainerCard = ({ trainer, onClick }) => (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <Card 
        className="p-6 cursor-pointer transition-all hover:shadow-lg hover:border-primary"
        onClick={() => onClick(trainer)}
      >
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
              <User className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">{trainer.name}</h3>
              <p className="text-sm text-gray-500">{trainer.specialization}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-1">
            <Star className="w-4 h-4 text-yellow-400 fill-current" />
            <span className="font-medium">{trainer.avgRating}</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600">{trainer.assignedBeneficiaries}</p>
            <p className="text-xs text-gray-500">Beneficiaries</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">{trainer.sessionsConducted}</p>
            <p className="text-xs text-gray-500">Sessions</p>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Success Rate</span>
            <span className="text-sm font-medium">{trainer.successRate}%</span>
          </div>
          <Progress value={trainer.successRate} className="h-2" />
        </div>

        <div className="mt-4 flex items-center justify-between">
          <Badge variant={
            trainer.workload > 80 ? 'destructive' : 
            trainer.workload > 60 ? 'secondary' : 'default'
          }>
            Workload: {trainer.workload}%
          </Badge>
          
          <Badge variant={trainer.status === 'active' ? 'default' : 'secondary'}>
            {trainer.status}
          </Badge>
        </div>
      </Card>
    </motion.div>
  );

  // Trainer detail modal/panel
  const TrainerDetailPanel = ({ trainer, onClose }) => (
    <motion.div
      initial={{ opacity: 0, x: 300 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 300 }}
      className="fixed right-0 top-0 h-full w-96 bg-white shadow-xl z-50 overflow-y-auto"
    >
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold">Trainer Details</h2>
          <Button variant="ghost" size="sm" onClick={onClose}>✕</Button>
        </div>

        <div className="space-y-6">
          {/* Trainer Info */}
          <div className="text-center">
            <div className="w-20 h-20 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
              <User className="w-10 h-10 text-white" />
            </div>
            <h3 className="text-lg font-semibold">{trainer.name}</h3>
            <p className="text-gray-500">{trainer.specialization}</p>
            <div className="flex items-center justify-center mt-2">
              <Star className="w-4 h-4 text-yellow-400 fill-current mr-1" />
              <span className="font-medium">{trainer.avgRating}/5</span>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-3 bg-blue-50 rounded-lg">
              <p className="text-2xl font-bold text-blue-600">{trainer.assignedBeneficiaries}</p>
              <p className="text-sm text-gray-600">Beneficiaries</p>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <p className="text-2xl font-bold text-green-600">{trainer.sessionsConducted}</p>
              <p className="text-sm text-gray-600">Sessions</p>
            </div>
          </div>

          {/* Success Rate */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium">Success Rate</span>
              <span className="text-sm">{trainer.successRate}%</span>
            </div>
            <Progress value={trainer.successRate} className="h-3" />
          </div>

          {/* Workload */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium">Workload</span>
              <span className="text-sm">{trainer.workload}%</span>
            </div>
            <Progress 
              value={trainer.workload} 
              className={`h-3 ${
                trainer.workload > 80 ? 'bg-red-100' : 
                trainer.workload > 60 ? 'bg-yellow-100' : 'bg-green-100'
              }`}
            />
          </div>

          {/* Recent Feedback */}
          {trainer.recentFeedback && (
            <div>
              <h4 className="font-medium mb-3">Recent Feedback</h4>
              <div className="space-y-2">
                {trainer.recentFeedback.slice(0, 3).map((feedback, index) => (
                  <div key={index} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center">
                        <Star className="w-3 h-3 text-yellow-400 fill-current mr-1" />
                        <span className="text-xs font-medium">{feedback.rating}/5</span>
                      </div>
                      <span className="text-xs text-gray-500">
                        {format(new Date(feedback.date), 'MMM dd')}
                      </span>
                    </div>
                    <p className="text-xs text-gray-600">{feedback.comment}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Performance Radar Chart */}
          {trainer.skillsAssessment && (
            <div>
              <h4 className="font-medium mb-3">Skills Assessment</h4>
              <PerformanceRadar
                data={{
                  labels: ['Communication', 'Technical Skills', 'Leadership', 'Adaptability', 'Problem Solving'],
                  datasets: [{
                    label: trainer.name,
                    data: [
                      trainer.skillsAssessment.communication,
                      trainer.skillsAssessment.technical,
                      trainer.skillsAssessment.leadership,
                      trainer.skillsAssessment.adaptability,
                      trainer.skillsAssessment.problemSolving
                    ]
                  }]
                }}
                height={250}
              />
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );

  if (isLoading && !trainerData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Activity className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p>Loading trainer analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Trainer Performance Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Track and analyze trainer effectiveness and performance metrics
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter className="w-4 h-4 mr-2" />
            Filters
          </Button>
          
          <div className="relative">
            <Button variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Export
              <ChevronDown className="w-4 h-4 ml-2" />
            </Button>
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border p-2 hidden group-hover:block">
              <Button
                variant="ghost"
                size="sm"
                className="w-full justify-start"
                onClick={() => handleExport('pdf')}
              >
                Export as PDF
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="w-full justify-start"
                onClick={() => handleExport('excel')}
              >
                Export as Excel
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="w-full justify-start"
                onClick={() => handleExport('csv')}
              >
                Export as CSV
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Filters Panel */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <Card className="p-4">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Search</label>
                  <Input
                    placeholder="Search trainers..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                
                <div>
                  <label className="text-sm font-medium mb-2 block">Specialization</label>
                  <select
                    className="w-full p-2 border border-gray-300 rounded-md"
                    value={filterSpecialization}
                    onChange={(e) => setFilterSpecialization(e.target.value)}
                  >
                    <option value="all">All Specializations</option>
                    {specializations.map(spec => (
                      <option key={spec} value={spec}>{spec}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="text-sm font-medium mb-2 block">Sort By</label>
                  <select
                    className="w-full p-2 border border-gray-300 rounded-md"
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                  >
                    <option value="rating">Rating</option>
                    <option value="name">Name</option>
                    <option value="assignedBeneficiaries">Beneficiaries</option>
                    <option value="sessionsConducted">Sessions</option>
                    <option value="successRate">Success Rate</option>
                  </select>
                </div>
                
                <div>
                  <label className="text-sm font-medium mb-2 block">Order</label>
                  <select
                    className="w-full p-2 border border-gray-300 rounded-md"
                    value={sortOrder}
                    onChange={(e) => setSortOrder(e.target.value)}
                  >
                    <option value="desc">Descending</option>
                    <option value="asc">Ascending</option>
                  </select>
                </div>
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {performanceMetrics.map((metric, index) => (
          <MetricCard
            key={index}
            title={metric.title}
            value={metric.value}
            change={metric.change}
            changeType={metric.changeType}
            icon={metric.icon}
            color={metric.color}
            loading={isLoading}
          />
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <DistributionChart
          data={performanceDistribution}
          title="Performance Distribution"
          description="Distribution of trainers by performance rating"
        />
        
        <ComparisonChart
          data={workloadData}
          title="Workload Distribution"
          description="Comparison of trainer workloads across specializations"
        />
      </div>

      {/* Trainers Grid */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Trainer Performance ({filteredTrainers.length})</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTrainers.map((trainer) => (
            <TrainerCard
              key={trainer.id}
              trainer={trainer}
              onClick={handleTrainerSelect}
            />
          ))}
        </div>
        
        {filteredTrainers.length === 0 && (
          <div className="text-center py-12">
            <Users className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p className="text-gray-500">No trainers found matching your criteria</p>
          </div>
        )}
      </div>

      {/* Trainer Detail Panel */}
      <AnimatePresence>
        {selectedTrainer && (
          <TrainerDetailPanel
            trainer={selectedTrainer}
            onClose={() => setSelectedTrainer(null)}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default TrainerPerformanceDashboard;
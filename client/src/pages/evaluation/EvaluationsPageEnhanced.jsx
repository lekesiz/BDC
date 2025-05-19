import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Search,
  Filter,
  Plus,
  ChevronDown,
  ChevronUp,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
  ClipboardList,
  Clock,
  CheckCircle,
  AlertCircle,
  FileText
} from 'lucide-react';

import api from '@/lib/api';
import { useToast } from '@/components/ui/toast';
import { AnimatedButton, AnimatedCard, AnimatedPage, AnimatedTable, AnimatedTableRow } from '@/components/animations';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { useAsync } from '@/hooks/useAsync';
import AsyncBoundary from '@/components/common/AsyncBoundary';
import { SkeletonTable, SkeletonCard, CardLoader } from '@/components/common/LoadingStates';
import { ErrorDisplay } from '@/components/common/ErrorBoundary';
import { motion } from 'framer-motion';
import { fadeInUp, staggerContainer, staggerItem } from '@/lib/animations';

/**
 * Enhanced EvaluationsPage with improved loading states and error handling
 */
const EvaluationsPageEnhanced = () => {
  const navigate = useNavigate();
  const { addToast } = useToast();
  
  // State variables
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [sortField, setSortField] = useState('created_at');
  const [sortDirection, setSortDirection] = useState('desc');
  const [showFilters, setShowFilters] = useState(false);
  
  // Pagination
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  
  // Use async hooks for fetching data
  const evaluationsAsync = useAsync(
    async () => {
      const params = {
        page,
        per_page: pageSize,
        sort_by: sortField,
        sort_dir: sortDirection,
        status: statusFilter !== 'all' ? statusFilter : undefined,
        type: typeFilter !== 'all' ? typeFilter : undefined,
        query: searchTerm || undefined
      };
      
      const response = await api.get('/api/evaluations', { params });
      return response.data;
    },
    [page, pageSize, sortField, sortDirection, statusFilter, typeFilter, searchTerm],
    true
  );
  
  const statsAsync = useAsync(
    async () => {
      const response = await api.get('/api/evaluations/stats');
      return response.data;
    },
    [],
    true
  );
  
  // Extract data from async responses
  const evaluations = evaluationsAsync.data?.evaluations || [];
  const totalPages = evaluationsAsync.data?.pages || 1;
  const totalCount = evaluationsAsync.data?.total || 0;
  const stats = statsAsync.data || {};
  
  // Handle search
  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
  };
  
  // Handle sort
  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };
  
  // Create a new evaluation
  const handleCreateEvaluation = () => {
    navigate('/tests/create');
  };
  
  // View evaluation details
  const handleViewEvaluation = (id) => {
    navigate(`/tests/results/${id}`);
  };
  
  // Refresh data
  const handleRefresh = async () => {
    try {
      await Promise.all([evaluationsAsync.execute(), statsAsync.execute()]);
      addToast({
        type: 'success',
        title: 'Data refreshed',
        message: 'Evaluations list has been updated'
      });
    } catch (error) {
      addToast({
        type: 'error',
        title: 'Refresh failed',
        message: 'Failed to refresh evaluations list'
      });
    }
  };
  
  // Status badge component
  const StatusBadge = ({ status }) => {
    const config = {
      completed: { bg: 'bg-green-100', text: 'text-green-800', icon: CheckCircle },
      in_progress: { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: Clock },
      scheduled: { bg: 'bg-blue-100', text: 'text-blue-800', icon: Clock },
      draft: { bg: 'bg-gray-100', text: 'text-gray-800', icon: FileText },
      cancelled: { bg: 'bg-red-100', text: 'text-red-800', icon: AlertCircle }
    };
    
    const { bg, text, icon: Icon } = config[status] || config.draft;
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${bg} ${text}`}>
        <Icon className="w-3 h-3 mr-1" />
        {status.replace('_', ' ')}
      </span>
    );
  };
  
  // Stats card component
  const StatsCard = ({ title, value, icon: Icon, color = 'primary' }) => {
    const colors = {
      primary: 'text-primary',
      green: 'text-green-600',
      yellow: 'text-yellow-600',
      red: 'text-red-600'
    };
    
    return (
      <motion.div variants={staggerItem}>
        <AnimatedCard className="p-4">
          <div className="flex items-center">
            <div className={`p-2 rounded-lg bg-gray-50`}>
              <Icon className={`h-6 w-6 ${colors[color]}`} />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">{title}</p>
              <p className="text-2xl font-semibold text-gray-900">{value}</p>
            </div>
          </div>
        </AnimatedCard>
      </motion.div>
    );
  };
  
  return (
    <AnimatedPage className="space-y-6">
      {/* Page header */}
      <motion.div 
        className="sm:flex sm:items-center sm:justify-between"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Evaluations</h1>
          <p className="mt-1 text-sm text-gray-700">
            Manage and track all evaluations in the system
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <AnimatedButton
            onClick={handleCreateEvaluation}
            className="inline-flex items-center"
          >
            <Plus className="h-4 w-4 mr-2" />
            Create Evaluation
          </AnimatedButton>
        </div>
      </motion.div>
      
      {/* Stats cards */}
      <AsyncBoundary
        loading={statsAsync.loading}
        error={statsAsync.error}
        loadingComponent={
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {[...Array(4)].map((_, i) => <SkeletonCard key={i} height="h-24" />)}
          </div>
        }
      >
        <motion.div 
          className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4"
          variants={staggerContainer}
          initial="initial"
          animate="animate"
        >
          <StatsCard
            title="Total Evaluations"
            value={stats.total || 0}
            icon={ClipboardList}
          />
          <StatsCard
            title="Completed"
            value={stats.completed || 0}
            icon={CheckCircle}
            color="green"
          />
          <StatsCard
            title="In Progress"
            value={stats.in_progress || 0}
            icon={Clock}
            color="yellow"
          />
          <StatsCard
            title="Average Score"
            value={`${stats.average_score || 0}%`}
            icon={FileText}
            color="primary"
          />
        </motion.div>
      </AsyncBoundary>
      
      {/* Filters and Search */}
      <AnimatedCard>
        <div className="p-4 sm:p-6">
          {/* Search bar */}
          <div className="flex flex-col sm:flex-row gap-4">
            <form onSubmit={handleSearch} className="flex-1">
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="h-4 w-4 text-gray-400" />
                </div>
                <Input
                  type="text"
                  placeholder="Search evaluations..."
                  className="pl-10"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  disabled={evaluationsAsync.loading}
                />
              </div>
            </form>
            
            <div className="flex gap-2">
              <AnimatedButton
                variant="outline"
                onClick={() => setShowFilters(!showFilters)}
                className="inline-flex items-center"
              >
                <Filter className="h-4 w-4 mr-2" />
                Filters
                {showFilters ? (
                  <ChevronUp className="h-4 w-4 ml-2" />
                ) : (
                  <ChevronDown className="h-4 w-4 ml-2" />
                )}
              </AnimatedButton>
              
              <AnimatedButton
                variant="outline"
                onClick={handleRefresh}
                disabled={evaluationsAsync.loading || statsAsync.loading}
                className="inline-flex items-center"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${(evaluationsAsync.loading || statsAsync.loading) ? 'animate-spin' : ''}`} />
                Refresh
              </AnimatedButton>
            </div>
          </div>
          
          {/* Advanced filters */}
          {showFilters && (
            <div className="mt-4 border-t pt-4">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Status
                  </label>
                  <select
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    disabled={evaluationsAsync.loading}
                  >
                    <option value="all">All Statuses</option>
                    <option value="completed">Completed</option>
                    <option value="in_progress">In Progress</option>
                    <option value="scheduled">Scheduled</option>
                    <option value="draft">Draft</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Type
                  </label>
                  <select
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                    value={typeFilter}
                    onChange={(e) => setTypeFilter(e.target.value)}
                    disabled={evaluationsAsync.loading}
                  >
                    <option value="all">All Types</option>
                    <option value="quiz">Quiz</option>
                    <option value="test">Test</option>
                    <option value="assessment">Assessment</option>
                    <option value="survey">Survey</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Items per page
                  </label>
                  <select
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                    value={pageSize}
                    onChange={(e) => {
                      setPageSize(Number(e.target.value));
                      setPage(1);
                    }}
                    disabled={evaluationsAsync.loading}
                  >
                    <option value={10}>10</option>
                    <option value={25}>25</option>
                    <option value={50}>50</option>
                    <option value={100}>100</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>
      </AnimatedCard>
      
      {/* Evaluations table */}
      <AsyncBoundary
        loading={evaluationsAsync.loading}
        error={evaluationsAsync.error}
        data={evaluations}
        loadingComponent={<SkeletonTable rows={5} columns={7} />}
        errorComponent={
          <ErrorDisplay 
            error={evaluationsAsync.error} 
            onRetry={evaluationsAsync.execute}
            title="Failed to load evaluations"
          />
        }
        emptyComponent={
          <AnimatedCard>
            <div className="p-8 text-center">
              <ClipboardList className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No evaluations found</h3>
              <p className="mt-1 text-sm text-gray-500">
                {searchTerm ? 'Try adjusting your search filters.' : 'Get started by creating a new evaluation.'}
              </p>
              {!searchTerm && (
                <div className="mt-6">
                  <AnimatedButton onClick={handleCreateEvaluation}>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Evaluation
                  </AnimatedButton>
                </div>
              )}
            </div>
          </AnimatedCard>
        }
      >
        <AnimatedCard>
          <div className="overflow-hidden">
            <AnimatedTable className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                    onClick={() => handleSort('title')}
                  >
                    <div className="flex items-center">
                      Title
                      {sortField === 'title' && (
                        sortDirection === 'asc' ? <ChevronUp className="ml-1 h-4 w-4" /> : <ChevronDown className="ml-1 h-4 w-4" />
                      )}
                    </div>
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Participants
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Average Score
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                    onClick={() => handleSort('created_at')}
                  >
                    <div className="flex items-center">
                      Created
                      {sortField === 'created_at' && (
                        sortDirection === 'asc' ? <ChevronUp className="ml-1 h-4 w-4" /> : <ChevronDown className="ml-1 h-4 w-4" />
                      )}
                    </div>
                  </th>
                  <th scope="col" className="relative px-6 py-3">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {evaluations.map((evaluation) => (
                  <AnimatedTableRow
                    key={evaluation.id}
                    onClick={() => handleViewEvaluation(evaluation.id)}
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {evaluation.title}
                        </div>
                        <div className="text-sm text-gray-500">
                          {evaluation.description}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        {evaluation.type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <StatusBadge status={evaluation.status} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {evaluation.participants_count || 0}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-1 bg-gray-200 rounded-full h-2 mr-3 max-w-[100px]">
                          <div
                            className="bg-primary h-2 rounded-full transition-all duration-300"
                            style={{ width: `${evaluation.average_score || 0}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-700">
                          {evaluation.average_score || 0}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(evaluation.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleViewEvaluation(evaluation.id);
                        }}
                      >
                        View Results
                      </Button>
                    </td>
                  </AnimatedTableRow>
                ))}
              </tbody>
            </AnimatedTable>
          </div>
          
          {/* Pagination */}
          {totalPages > 1 && (
            <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
              <div className="flex-1 flex justify-between sm:hidden">
                <Button
                  variant="outline"
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1 || evaluationsAsync.loading}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setPage(page + 1)}
                  disabled={page === totalPages || evaluationsAsync.loading}
                >
                  Next
                </Button>
              </div>
              <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-gray-700">
                    Showing{' '}
                    <span className="font-medium">{((page - 1) * pageSize) + 1}</span>
                    {' '}to{' '}
                    <span className="font-medium">
                      {Math.min(page * pageSize, totalCount)}
                    </span>
                    {' '}of{' '}
                    <span className="font-medium">{totalCount}</span>
                    {' '}results
                  </p>
                </div>
                <div>
                  <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                    <Button
                      variant="outline"
                      className="relative inline-flex items-center px-2 py-2 rounded-l-md"
                      onClick={() => setPage(page - 1)}
                      disabled={page === 1 || evaluationsAsync.loading}
                    >
                      <span className="sr-only">Previous</span>
                      <ChevronLeft className="h-5 w-5" />
                    </Button>
                    
                    {/* Page numbers */}
                    {[...Array(Math.min(5, totalPages))].map((_, i) => {
                      const pageNumber = i + 1;
                      const isCurrentPage = pageNumber === page;
                      return (
                        <Button
                          key={pageNumber}
                          variant={isCurrentPage ? "primary" : "outline"}
                          className={`relative inline-flex items-center px-4 py-2 ${isCurrentPage ? '' : 'hover:bg-gray-50'}`}
                          onClick={() => setPage(pageNumber)}
                          disabled={evaluationsAsync.loading}
                        >
                          {pageNumber}
                        </Button>
                      );
                    })}
                    
                    {totalPages > 5 && (
                      <span className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                        ...
                      </span>
                    )}
                    
                    <Button
                      variant="outline"
                      className="relative inline-flex items-center px-2 py-2 rounded-r-md"
                      onClick={() => setPage(page + 1)}
                      disabled={page === totalPages || evaluationsAsync.loading}
                    >
                      <span className="sr-only">Next</span>
                      <ChevronRight className="h-5 w-5" />
                    </Button>
                  </nav>
                </div>
              </div>
            </div>
          )}
        </AnimatedCard>
      </AsyncBoundary>
    </AnimatedPage>
  );
};

export default EvaluationsPageEnhanced;
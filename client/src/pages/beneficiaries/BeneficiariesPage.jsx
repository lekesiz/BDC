import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Search,
  Filter,
  Plus,
  UserPlus,
  ChevronDown,
  ChevronUp,
  ChevronLeft,
  ChevronRight,
  Users,
  UserCheck,
  AlertCircle
} from 'lucide-react';
import { useAsync } from '@/hooks/useAsync';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import AsyncData from '@/components/ui/async-data';
import { ErrorBoundary } from '@/components/ui/error-boundary';
import TableSkeleton from '@/components/ui/skeleton/table-skeleton';
import Retry from '@/components/ui/retry';
import Badge from '@/components/ui/badge';
import Select from '@/components/ui/select';
import { formatDate } from '@/lib/utils';
/**
 * Enhanced BeneficiariesPage showcasing best practices for loading states,
 * error handling, and async operations
 */
const BeneficiariesPageV2 = () => {
  const navigate = useNavigate();
  // State variables
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    status: 'all',
    sortField: 'created_at',
    sortDirection: 'desc',
  });
  const [showFilters, setShowFilters] = useState(false);
  // Pagination
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 10,
  });
  // Build query parameters
  const queryParams = {
    page: pagination.page,
    per_page: pagination.pageSize,
    sort_by: filters.sortField,
    sort_dir: filters.sortDirection,
    status: filters.status !== 'all' ? filters.status : undefined,
    query: searchTerm || undefined
  };
  // Fetch beneficiaries with enhanced error handling
  const {
    data: beneficiariesData,
    loading,
    error,
    retry: refetchBeneficiaries
  } = useApiCall(
    '/api/beneficiaries',
    {
      params: queryParams,
      debounce: 300 // Debounce search requests
    },
    [pagination.page, pagination.pageSize, filters, searchTerm]
  );
  // Secondary loading state for UI interactions
  const {
    loading: isUpdating,
    startLoading: startUpdating,
    stopLoading: stopUpdating
  } = useLoadingState();
  // Calculate total pages
  const totalPages = beneficiariesData?.total_pages || beneficiariesData?.pages || 1;
  const beneficiaries = beneficiariesData?.items || [];
  const totalCount = beneficiariesData?.total || 0;
  // Handle search with debouncing
  const handleSearch = useCallback((value) => {
    setSearchTerm(value);
    setPagination(prev => ({ ...prev, page: 1 })); // Reset to first page
  }, []);
  // Handle filter changes
  const handleFilterChange = useCallback((key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPagination(prev => ({ ...prev, page: 1 })); // Reset to first page
  }, []);
  // Handle sort
  const handleSort = useCallback((field) => {
    setFilters(prev => ({
      ...prev,
      sortField: field,
      sortDirection: prev.sortField === field && prev.sortDirection === 'asc' ? 'desc' : 'asc'
    }));
  }, []);
  // Handle pagination
  const handlePageChange = useCallback((newPage) => {
    startUpdating();
    setPagination(prev => ({ ...prev, page: newPage }));
    setTimeout(stopUpdating, 300); // Simulate transition
  }, [startUpdating, stopUpdating]);
  // Handle page size change
  const handlePageSizeChange = useCallback((newSize) => {
    setPagination({
      page: 1,
      pageSize: Number(newSize)
    });
  }, []);
  // Navigation handlers
  const handleCreateBeneficiary = () => {
    navigate('/beneficiaries/new');
  };
  const handleViewBeneficiary = (id) => {
    navigate(`/beneficiaries/${id}`);
  };
  // Render status badge with improved styling
  const renderStatusBadge = (status) => {
    const variants = {
      active: 'success',
      inactive: 'default',
      pending: 'warning',
      completed: 'info'
    };
    return (
      <Badge variant={variants[status] || 'default'}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };
  // Render sort icon
  const renderSortIcon = (field) => {
    if (filters.sortField !== field) return null;
    return filters.sortDirection === 'asc' ? (
      <ChevronUp className="w-4 h-4 ml-1" />
    ) : (
      <ChevronDown className="w-4 h-4 ml-1" />
    );
  };
  // Enhanced error state with retry
  const ErrorState = () => (
    <div className="min-h-[400px] flex items-center justify-center">
      <Retry 
        error={error}
        onRetry={refetchBeneficiaries}
        title="Failed to load beneficiaries"
        message={error.message || "We couldn't load the beneficiaries list. Please try again."}
      />
    </div>
  );
  // Empty state
  const EmptyState = () => (
    <Card className="p-16 text-center">
      <div className="flex flex-col items-center space-y-4">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
          <Users className="w-8 h-8 text-gray-400" />
        </div>
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No beneficiaries found</h3>
          <p className="text-sm text-gray-500 mb-4">
            {searchTerm 
              ? `No beneficiaries match "${searchTerm}"`
              : "Get started by adding your first beneficiary"}
          </p>
          {!searchTerm && (
            <Button onClick={handleCreateBeneficiary} leftIcon={<UserPlus className="w-4 h-4" />}>
              Add First Beneficiary
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
  // Beneficiaries table component
  const BeneficiariesTable = () => (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th 
              scope="col" 
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
              onClick={() => handleSort('last_name')}
            >
              <div className="flex items-center">
                Name
                {renderSortIcon('last_name')}
              </div>
            </th>
            <th 
              scope="col" 
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
              onClick={() => handleSort('email')}
            >
              <div className="flex items-center">
                Email
                {renderSortIcon('email')}
              </div>
            </th>
            <th 
              scope="col" 
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
              onClick={() => handleSort('created_at')}
            >
              <div className="flex items-center">
                Created
                {renderSortIcon('created_at')}
              </div>
            </th>
            <th 
              scope="col" 
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
              onClick={() => handleSort('status')}
            >
              <div className="flex items-center">
                Status
                {renderSortIcon('status')}
              </div>
            </th>
            <th 
              scope="col" 
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Progress
            </th>
            <th scope="col" className="relative px-6 py-3">
              <span className="sr-only">Actions</span>
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {beneficiaries.map((beneficiary) => (
            <tr 
              key={beneficiary.id} 
              className="hover:bg-gray-50 cursor-pointer transition-colors"
              onClick={() => handleViewBeneficiary(beneficiary.id)}
            >
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <div className="flex-shrink-0 h-10 w-10 rounded-full bg-gradient-to-br from-primary/20 to-primary/10 flex items-center justify-center">
                    <span className="text-primary font-medium">
                      {beneficiary.first_name?.charAt(0)}{beneficiary.last_name?.charAt(0)}
                    </span>
                  </div>
                  <div className="ml-4">
                    <div className="text-sm font-medium text-gray-900">
                      {beneficiary.first_name} {beneficiary.last_name}
                    </div>
                    <div className="text-sm text-gray-500">
                      {beneficiary.phone || 'No phone'}
                    </div>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-900">{beneficiary.email}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-900">
                  {formatDate(beneficiary.created_at)}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {renderStatusBadge(beneficiary.status)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <div className="flex-1">
                    <div className="text-sm text-gray-900">
                      {beneficiary.evaluation_count || 0} evaluations
                    </div>
                    <div className="text-xs text-gray-500 flex items-center mt-1">
                      <UserCheck className="w-3 h-3 mr-1" />
                      {beneficiary.completed_evaluation_count || 0} completed
                    </div>
                  </div>
                  {beneficiary.evaluation_count > 0 && (
                    <div className="ml-4">
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-primary h-2 rounded-full transition-all"
                          style={{ 
                            width: `${(beneficiary.completed_evaluation_count / beneficiary.evaluation_count) * 100}%` 
                          }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleViewBeneficiary(beneficiary.id);
                  }}
                >
                  View
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
  // Enhanced pagination component
  const Pagination = () => (
    <div className="px-4 py-3 bg-white border-t border-gray-200 sm:px-6">
      <div className="flex items-center justify-between">
        <div className="flex-1 flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-700">
              Showing{' '}
              <span className="font-medium">
                {totalCount > 0 ? ((pagination.page - 1) * pagination.pageSize) + 1 : 0}
              </span>{' '}
              to{' '}
              <span className="font-medium">
                {Math.min(pagination.page * pagination.pageSize, totalCount)}
              </span>{' '}
              of{' '}
              <span className="font-medium">{totalCount}</span> results
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <Select
              value={pagination.pageSize}
              onChange={handlePageSizeChange}
              options={[
                { value: 5, label: '5 per page' },
                { value: 10, label: '10 per page' },
                { value: 25, label: '25 per page' },
                { value: 50, label: '50 per page' }
              ]}
              className="w-32"
            />
            <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(Math.max(1, pagination.page - 1))}
                disabled={pagination.page === 1 || isUpdating}
                leftIcon={<ChevronLeft className="h-4 w-4" />}
              >
                Previous
              </Button>
              <div className="hidden md:flex -space-x-px">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum;
                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (pagination.page <= 3) {
                    pageNum = i + 1;
                  } else if (pagination.page >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = pagination.page - 2 + i;
                  }
                  return (
                    <Button
                      key={pageNum}
                      variant={pagination.page === pageNum ? 'primary' : 'outline'}
                      size="sm"
                      onClick={() => handlePageChange(pageNum)}
                      disabled={isUpdating}
                      className="min-w-[40px]"
                    >
                      {pageNum}
                    </Button>
                  );
                })}
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(Math.min(totalPages, pagination.page + 1))}
                disabled={pagination.page === totalPages || isUpdating}
                rightIcon={<ChevronRight className="h-4 w-4" />}
              >
                Next
              </Button>
            </nav>
          </div>
        </div>
      </div>
    </div>
  );
  return (
    <ErrorBoundary fallback={<ErrorState />}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Beneficiaries</h1>
            <p className="text-sm text-gray-500">Manage your beneficiaries and track their progress</p>
          </div>
          <Button 
            onClick={handleCreateBeneficiary} 
            leftIcon={<UserPlus className="w-4 h-4" />}
            loading={loading}
          >
            Add Beneficiary
          </Button>
        </div>
        {/* Filters Card */}
        <Card>
          <div className="p-4 border-b border-gray-200">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  type="text"
                  placeholder="Search by name, email or phone..."
                  value={searchTerm}
                  onChange={(e) => handleSearch(e.target.value)}
                  leftIcon={<Search className="h-4 w-4 text-gray-400" />}
                  className="w-full"
                />
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  onClick={() => setShowFilters(!showFilters)}
                  leftIcon={<Filter className="h-4 w-4" />}
                  rightIcon={
                    showFilters ? 
                    <ChevronUp className="h-4 w-4" /> : 
                    <ChevronDown className="h-4 w-4" />
                  }
                >
                  Filters
                </Button>
                <Button
                  variant="outline"
                  onClick={refetchBeneficiaries}
                  loading={loading}
                  disabled={loading}
                >
                  Refresh
                </Button>
              </div>
            </div>
            {/* Expandable Filters */}
            {showFilters && (
              <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700 mb-1">
                    Status
                  </label>
                  <Select
                    id="status-filter"
                    value={filters.status}
                    onChange={(value) => handleFilterChange('status', value)}
                    options={[
                      { value: 'all', label: 'All Statuses' },
                      { value: 'active', label: 'Active' },
                      { value: 'inactive', label: 'Inactive' },
                      { value: 'pending', label: 'Pending' },
                      { value: 'completed', label: 'Completed' }
                    ]}
                    className="w-full"
                  />
                </div>
                <div>
                  <label htmlFor="sort-field" className="block text-sm font-medium text-gray-700 mb-1">
                    Sort By
                  </label>
                  <Select
                    id="sort-field"
                    value={filters.sortField}
                    onChange={(value) => handleFilterChange('sortField', value)}
                    options={[
                      { value: 'created_at', label: 'Date Created' },
                      { value: 'last_name', label: 'Last Name' },
                      { value: 'email', label: 'Email' },
                      { value: 'status', label: 'Status' }
                    ]}
                    className="w-full"
                  />
                </div>
                <div>
                  <label htmlFor="sort-direction" className="block text-sm font-medium text-gray-700 mb-1">
                    Sort Order
                  </label>
                  <Select
                    id="sort-direction"
                    value={filters.sortDirection}
                    onChange={(value) => handleFilterChange('sortDirection', value)}
                    options={[
                      { value: 'asc', label: 'Ascending' },
                      { value: 'desc', label: 'Descending' }
                    ]}
                    className="w-full"
                  />
                </div>
              </div>
            )}
          </div>
          {/* Main Content with AsyncData */}
          <AsyncData
            loading={loading}
            error={error}
            data={beneficiaries}
            skeleton={<TableSkeleton columns={6} rows={5} />}
            errorComponent={<ErrorState />}
            emptyComponent={<EmptyState />}
            showEmptyOnError={false}
          >
            {() => (
              <>
                <BeneficiariesTable />
                <Pagination />
              </>
            )}
          </AsyncData>
        </Card>
      </div>
    </ErrorBoundary>
  );
};
export default BeneficiariesPageV2;
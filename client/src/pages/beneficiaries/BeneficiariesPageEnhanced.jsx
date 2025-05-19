import { useState, useEffect } from 'react';
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
  RefreshCw,
  AlertCircle
} from 'lucide-react';

import api from '@/lib/api';
import { useToast } from '@/components/ui/toast';
import { AnimatedButton, AnimatedCard, AnimatedPage, AnimatedTable, AnimatedTableRow } from '@/components/animations';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { useAsync } from '@/hooks/useAsync';
import AsyncBoundary from '@/components/common/AsyncBoundary';
import { SkeletonTable, DataState } from '@/components/common/LoadingStates';
import { ErrorDisplay } from '@/components/common/ErrorBoundary';
import { motion } from 'framer-motion';
import { fadeInUp, staggerContainer, staggerItem } from '@/lib/animations';

/**
 * Enhanced BeneficiariesPage with improved loading states and error handling
 */
const BeneficiariesPageEnhanced = () => {
  const navigate = useNavigate();
  const { addToast } = useToast();
  
  // State variables
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortField, setSortField] = useState('created_at');
  const [sortDirection, setSortDirection] = useState('desc');
  const [showFilters, setShowFilters] = useState(false);
  
  // Pagination
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  
  // Use async hook for fetching beneficiaries
  const beneficiariesAsync = useAsync(
    async () => {
      const params = {
        page,
        per_page: pageSize,
        sort_by: sortField,
        sort_dir: sortDirection,
        status: statusFilter !== 'all' ? statusFilter : undefined,
        query: searchTerm || undefined
      };
      
      const response = await api.get('/api/beneficiaries', { params });
      return response.data;
    },
    [page, pageSize, sortField, sortDirection, statusFilter, searchTerm],
    true // Immediate execution
  );
  
  // Extract data from async response
  const beneficiaries = beneficiariesAsync.data?.items || [];
  const totalPages = beneficiariesAsync.data?.pages || beneficiariesAsync.data?.total_pages || 1;
  const totalCount = beneficiariesAsync.data?.total || 0;
  
  // Handle search
  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1); // Reset to first page when searching
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
  
  // Create a new beneficiary
  const handleCreateBeneficiary = () => {
    navigate('/beneficiaries/new');
  };
  
  // View beneficiary details
  const handleViewBeneficiary = (id) => {
    navigate(`/beneficiaries/${id}`);
  };
  
  // Refresh data
  const handleRefresh = async () => {
    try {
      await beneficiariesAsync.execute();
      addToast({
        type: 'success',
        title: 'Data refreshed',
        message: 'Beneficiaries list has been updated'
      });
    } catch (error) {
      addToast({
        type: 'error',
        title: 'Refresh failed',
        message: 'Failed to refresh beneficiaries list'
      });
    }
  };
  
  // Status badge component
  const StatusBadge = ({ status }) => {
    const statusClasses = {
      active: 'bg-green-100 text-green-800',
      inactive: 'bg-red-100 text-red-800',
      pending: 'bg-yellow-100 text-yellow-800'
    };
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusClasses[status] || 'bg-gray-100 text-gray-800'}`}>
        {status}
      </span>
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
          <h1 className="text-2xl font-bold text-gray-900">Beneficiaries</h1>
          <p className="mt-1 text-sm text-gray-700">
            Manage and view all beneficiaries in the system
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <AnimatedButton
            onClick={handleCreateBeneficiary}
            className="inline-flex items-center"
          >
            <UserPlus className="h-4 w-4 mr-2" />
            Add Beneficiary
          </AnimatedButton>
        </div>
      </motion.div>
      
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
                  placeholder="Search beneficiaries..."
                  className="pl-10"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  disabled={beneficiariesAsync.loading}
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
                disabled={beneficiariesAsync.loading}
                className="inline-flex items-center"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${beneficiariesAsync.loading ? 'animate-spin' : ''}`} />
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
                    disabled={beneficiariesAsync.loading}
                  >
                    <option value="all">All Statuses</option>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="pending">Pending</option>
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
                    disabled={beneficiariesAsync.loading}
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
      </Card>
      
      {/* Beneficiaries table */}
      <AsyncBoundary
        loading={beneficiariesAsync.loading}
        error={beneficiariesAsync.error}
        data={beneficiaries}
        loadingComponent={<SkeletonTable rows={5} columns={6} />}
        errorComponent={
          <ErrorDisplay 
            error={beneficiariesAsync.error} 
            onRetry={beneficiariesAsync.execute}
            title="Failed to load beneficiaries"
          />
        }
        emptyComponent={
          <Card>
            <div className="p-8 text-center">
              <UserPlus className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No beneficiaries found</h3>
              <p className="mt-1 text-sm text-gray-500">
                {searchTerm ? 'Try adjusting your search filters.' : 'Get started by creating a new beneficiary.'}
              </p>
              {!searchTerm && (
                <div className="mt-6">
                  <Button onClick={handleCreateBeneficiary}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Beneficiary
                  </Button>
                </div>
              )}
            </div>
          </Card>
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
                    onClick={() => handleSort('full_name')}
                  >
                    <div className="flex items-center">
                      Name
                      {sortField === 'full_name' && (
                        sortDirection === 'asc' ? <ChevronUp className="ml-1 h-4 w-4" /> : <ChevronDown className="ml-1 h-4 w-4" />
                      )}
                    </div>
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Trainer
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Progress
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
                {beneficiaries.map((beneficiary) => (
                  <AnimatedTableRow
                    key={beneficiary.id}
                    onClick={() => handleViewBeneficiary(beneficiary.id)}
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                            <span className="text-sm font-medium text-primary">
                              {beneficiary.full_name?.charAt(0)?.toUpperCase() || '?'}
                            </span>
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {beneficiary.full_name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {beneficiary.email}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <StatusBadge status={beneficiary.status} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {beneficiary.assigned_trainer || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-1 bg-gray-200 rounded-full h-2 mr-3">
                          <div
                            className="bg-primary h-2 rounded-full transition-all duration-300"
                            style={{ width: `${beneficiary.progress || 0}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-700">
                          {beneficiary.progress || 0}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(beneficiary.created_at).toLocaleDateString()}
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
                  disabled={page === 1 || beneficiariesAsync.loading}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setPage(page + 1)}
                  disabled={page === totalPages || beneficiariesAsync.loading}
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
                    <AnimatedButton
                      variant="outline"
                      className="relative inline-flex items-center px-2 py-2 rounded-l-md"
                      onClick={() => setPage(page - 1)}
                      disabled={page === 1 || beneficiariesAsync.loading}
                    >
                      <span className="sr-only">Previous</span>
                      <ChevronLeft className="h-5 w-5" />
                    </AnimatedButton>
                    
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
                          disabled={beneficiariesAsync.loading}
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
                      disabled={page === totalPages || beneficiariesAsync.loading}
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

export default BeneficiariesPageEnhanced;
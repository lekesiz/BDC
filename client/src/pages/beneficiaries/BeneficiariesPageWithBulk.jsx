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
  AlertCircle,
  MoreVertical,
  Trash2,
  Edit3,
  Download,
  Upload,
  CheckSquare,
  Square
} from 'lucide-react';
import { useAsync } from '@/hooks/useAsync';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import Badge from '@/components/ui/badge';
import Select from '@/components/ui/select';
import { formatDate } from '@/lib/utils';
import { useToast } from '@/components/ui/toast';
import BulkOperationsModal from '@/components/bulk/BulkOperationsModal';
import { Checkbox } from '@/components/ui/checkbox';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

/**
 * Enhanced BeneficiariesPage with bulk operations support
 */
const BeneficiariesPageWithBulk = () => {
  const navigate = useNavigate();
  const { addToast } = useToast();
  
  // State variables
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    status: 'all',
    sortField: 'created_at',
    sortDirection: 'desc',
  });
  const [showFilters, setShowFilters] = useState(false);
  const [selectedIds, setSelectedIds] = useState([]);
  const [showBulkModal, setShowBulkModal] = useState(false);
  
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
    q: searchTerm || undefined
  };
  
  // Fetch beneficiaries
  const {
    data: beneficiariesData,
    loading,
    error,
    execute: refetchBeneficiaries
  } = useAsync(
    async () => {
      const response = await api.get('/api/v2/beneficiaries', { params: queryParams });
      return response.data;
    },
    [pagination.page, pagination.pageSize, filters, searchTerm]
  );
  
  // Calculate data
  const totalPages = beneficiariesData?.pagination?.pages || 1;
  const beneficiaries = beneficiariesData?.beneficiaries || [];
  const totalCount = beneficiariesData?.pagination?.total || 0;
  
  // Selection handlers
  const handleSelectAll = useCallback((checked) => {
    if (checked) {
      setSelectedIds(beneficiaries.map(b => b.id));
    } else {
      setSelectedIds([]);
    }
  }, [beneficiaries]);
  
  const handleSelectOne = useCallback((id, checked) => {
    if (checked) {
      setSelectedIds(prev => [...prev, id]);
    } else {
      setSelectedIds(prev => prev.filter(selectedId => selectedId !== id));
    }
  }, []);
  
  const isAllSelected = beneficiaries.length > 0 && selectedIds.length === beneficiaries.length;
  const isIndeterminate = selectedIds.length > 0 && selectedIds.length < beneficiaries.length;
  
  // Handle search with debouncing
  const handleSearch = useCallback((value) => {
    setSearchTerm(value);
    setPagination(prev => ({ ...prev, page: 1 }));
  }, []);
  
  // Handle filter changes
  const handleFilterChange = useCallback((key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPagination(prev => ({ ...prev, page: 1 }));
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
    setPagination(prev => ({ ...prev, page: newPage }));
  }, []);
  
  // Handle bulk operations
  const handleBulkSuccess = () => {
    setShowBulkModal(false);
    setSelectedIds([]);
    refetchBeneficiaries();
  };
  
  // Navigation handlers
  const handleCreateBeneficiary = () => {
    navigate('/beneficiaries/new');
  };
  
  const handleViewBeneficiary = (id) => {
    navigate(`/beneficiaries/${id}`);
  };
  
  // Render status badge
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
  
  // Error state
  if (error) {
    return (
      <div className="min-h-[400px] flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Failed to load beneficiaries</h3>
          <p className="text-sm text-gray-500 mb-4">{error.message}</p>
          <Button onClick={refetchBeneficiaries}>Try Again</Button>
        </div>
      </div>
    );
  }
  
  // Empty state
  if (!loading && beneficiaries.length === 0) {
    return (
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
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Beneficiaries</h1>
          <p className="text-sm text-gray-500 mt-1">
            Manage and track beneficiary information
          </p>
        </div>
        <div className="flex gap-2">
          {selectedIds.length > 0 && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline">
                  <MoreVertical className="h-4 w-4 mr-2" />
                  Bulk Actions ({selectedIds.length})
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem onClick={() => setShowBulkModal(true)}>
                  <Edit3 className="h-4 w-4 mr-2" />
                  Update Selected
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setShowBulkModal(true)}>
                  <UserPlus className="h-4 w-4 mr-2" />
                  Assign Trainer
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setShowBulkModal(true)}>
                  <Download className="h-4 w-4 mr-2" />
                  Export Selected
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem 
                  onClick={() => setShowBulkModal(true)}
                  className="text-red-600"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete Selected
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
          <Button 
            onClick={handleCreateBeneficiary} 
            leftIcon={<UserPlus className="w-4 h-4" />}
          >
            Add Beneficiary
          </Button>
        </div>
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
            </div>
          )}
        </div>
        
        {/* Table */}
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left">
                  <Checkbox
                    checked={isAllSelected}
                    indeterminate={isIndeterminate}
                    onCheckedChange={handleSelectAll}
                  />
                </th>
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
                <th scope="col" className="relative px-6 py-3">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan="6" className="px-6 py-4 text-center text-gray-500">
                    Loading beneficiaries...
                  </td>
                </tr>
              ) : (
                beneficiaries.map((beneficiary) => (
                  <tr 
                    key={beneficiary.id} 
                    className="hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Checkbox
                        checked={selectedIds.includes(beneficiary.id)}
                        onCheckedChange={(checked) => handleSelectOne(beneficiary.id, checked)}
                        onClick={(e) => e.stopPropagation()}
                      />
                    </td>
                    <td 
                      className="px-6 py-4 whitespace-nowrap cursor-pointer"
                      onClick={() => handleViewBeneficiary(beneficiary.id)}
                    >
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
                            ID: {beneficiary.id}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td 
                      className="px-6 py-4 whitespace-nowrap cursor-pointer"
                      onClick={() => handleViewBeneficiary(beneficiary.id)}
                    >
                      <div className="text-sm text-gray-900">{beneficiary.email}</div>
                      {beneficiary.phone && (
                        <div className="text-sm text-gray-500">{beneficiary.phone}</div>
                      )}
                    </td>
                    <td 
                      className="px-6 py-4 whitespace-nowrap cursor-pointer"
                      onClick={() => handleViewBeneficiary(beneficiary.id)}
                    >
                      <div className="text-sm text-gray-900">
                        {formatDate(beneficiary.created_at)}
                      </div>
                    </td>
                    <td 
                      className="px-6 py-4 whitespace-nowrap cursor-pointer"
                      onClick={() => handleViewBeneficiary(beneficiary.id)}
                    >
                      {renderStatusBadge(beneficiary.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleViewBeneficiary(beneficiary.id)}
                      >
                        View
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        
        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing {((pagination.page - 1) * pagination.pageSize) + 1} to{' '}
              {Math.min(pagination.page * pagination.pageSize, totalCount)} of{' '}
              {totalCount} results
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(pagination.page - 1)}
                disabled={pagination.page === 1}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <span className="text-sm text-gray-700">
                Page {pagination.page} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(pagination.page + 1)}
                disabled={pagination.page === totalPages}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </Card>
      
      {/* Bulk Operations Modal */}
      {showBulkModal && (
        <BulkOperationsModal
          isOpen={showBulkModal}
          onClose={() => setShowBulkModal(false)}
          entityType="beneficiaries"
          selectedIds={selectedIds}
          onSuccess={handleBulkSuccess}
        />
      )}
    </div>
  );
};

export default BeneficiariesPageWithBulk;
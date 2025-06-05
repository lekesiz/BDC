import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, UserPlus, Edit, Trash2, MoreHorizontal, Download, RefreshCw } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ui/toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableHeader, TableBody, TableRow, TableCell, TablePagination } from '@/components/ui/table';
import { Dropdown, DropdownItem, DropdownDivider } from '@/components/ui/dropdown';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '@/components/ui/modal';
import { Alert } from '@/components/ui/alert';
import { Avatar } from '@/components/ui/avatar';
import { formatDate } from '@/lib/utils';
import api from '@/lib/api';
/**
 * Users listing and management page
 */
const UsersPage = () => {
  const { hasRole } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();
  // State
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalItems, setTotalItems] = useState(0);
  const [sortField, setSortField] = useState('created_at');
  const [sortDirection, setSortDirection] = useState('desc');
  const [roleFilter, setRoleFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedUser, setSelectedUser] = useState(null);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  // Determine if user can manage users
  const canManageUsers = hasRole(['super_admin', 'tenant_admin']);
  // Fetch users
  const fetchUsers = async (page = 1, limit = pageSize) => {
    try {
      setIsLoading(true);
      const response = await api.get('/api/users', {
        params: {
          page,
          limit,
          sort_by: sortField,
          sort_direction: sortDirection,
          role: roleFilter !== 'all' ? roleFilter : undefined,
          status: statusFilter !== 'all' ? statusFilter : undefined,
          search: searchTerm || undefined,
        }
      });
      setUsers(response.data.items);
      setFilteredUsers(response.data.items);
      setTotalPages(response.data.total_pages);
      setTotalItems(response.data.total_items);
    } catch (error) {
      console.error('Error fetching users:', error);
      addToast({
        type: 'error',
        title: 'Failed to load users',
        message: error.response?.data?.message || 'An error occurred while loading users.',
      });
    } finally {
      setIsLoading(false);
    }
  };
  // Load users on component mount and when filters change
  useEffect(() => {
    fetchUsers(currentPage, pageSize);
  }, [currentPage, pageSize, sortField, sortDirection, roleFilter, statusFilter, searchTerm]);
  // Handle search input change
  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1); // Reset to first page on new search
  };
  // Handle role filter change
  const handleRoleFilterChange = (value) => {
    setRoleFilter(value);
    setCurrentPage(1); // Reset to first page on filter change
  };
  // Handle status filter change
  const handleStatusFilterChange = (value) => {
    setStatusFilter(value);
    setCurrentPage(1); // Reset to first page on filter change
  };
  // Handle sorting
  const handleSort = (field) => {
    if (sortField === field) {
      // Toggle direction if clicking the same field
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // Default to ascending for new sort field
      setSortField(field);
      setSortDirection('asc');
    }
    setCurrentPage(1); // Reset to first page on sort change
  };
  // Handle page change
  const handlePageChange = (page) => {
    setCurrentPage(page);
  };
  // Handle page size change
  const handlePageSizeChange = (size) => {
    setPageSize(size);
    setCurrentPage(1); // Reset to first page on page size change
  };
  // Handle create new user
  const handleCreateUser = () => {
    navigate('/users/create');
  };
  // Handle edit user
  const handleEditUser = (userId) => {
    navigate(`/users/${userId}/edit`);
  };
  // Handle view user
  const handleViewUser = (userId) => {
    navigate(`/users/${userId}`);
  };
  // Handle delete user
  const handleDeleteUser = (user) => {
    setSelectedUser(user);
    setIsDeleteModalOpen(true);
  };
  // Confirm delete user
  const confirmDeleteUser = async () => {
    if (!selectedUser) return;
    try {
      setIsLoading(true);
      await api.delete(`/api/users/${selectedUser.id}`);
      addToast({
        type: 'success',
        title: 'User deleted',
        message: `User ${selectedUser.first_name} ${selectedUser.last_name} has been deleted.`,
      });
      // Close modal and refresh user list
      setIsDeleteModalOpen(false);
      setSelectedUser(null);
      fetchUsers(currentPage, pageSize);
    } catch (error) {
      console.error('Error deleting user:', error);
      addToast({
        type: 'error',
        title: 'Failed to delete user',
        message: error.response?.data?.message || 'An error occurred while deleting the user.',
      });
    } finally {
      setIsLoading(false);
    }
  };
  // Handle export users
  const handleExportUsers = async () => {
    try {
      setIsExporting(true);
      const response = await api.get('/api/users/export', {
        params: {
          role: roleFilter !== 'all' ? roleFilter : undefined,
          status: statusFilter !== 'all' ? statusFilter : undefined,
          search: searchTerm || undefined,
        },
        responseType: 'blob',
      });
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `users-export-${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      // Clean up
      link.remove();
      window.URL.revokeObjectURL(url);
      addToast({
        type: 'success',
        title: 'Export successful',
        message: 'Users have been exported to CSV.',
      });
    } catch (error) {
      console.error('Error exporting users:', error);
      addToast({
        type: 'error',
        title: 'Export failed',
        message: error.response?.data?.message || 'An error occurred while exporting users.',
      });
    } finally {
      setIsExporting(false);
    }
  };
  // Render role badge
  const renderRoleBadge = (role) => {
    let color;
    let label;
    switch (role) {
      case 'super_admin':
        color = 'red';
        label = 'Super Admin';
        break;
      case 'tenant_admin':
        color = 'purple';
        label = 'Admin';
        break;
      case 'trainer':
        color = 'blue';
        label = 'Trainer';
        break;
      case 'trainee':
        color = 'green';
        label = 'Trainee';
        break;
      default:
        color = 'gray';
        label = role;
    }
    return <Badge color={color}>{label}</Badge>;
  };
  // Render status badge
  const renderStatusBadge = (status) => {
    let color;
    switch (status) {
      case 'active':
        color = 'green';
        break;
      case 'inactive':
        color = 'gray';
        break;
      case 'suspended':
        color = 'yellow';
        break;
      default:
        color = 'gray';
    }
    return <Badge color={color}>{status}</Badge>;
  };
  return (
    <div className="container mx-auto py-8 px-4">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">User Management</h1>
          <p className="text-gray-600">Manage users and their access</p>
        </div>
        {canManageUsers && (
          <Button
            onClick={handleCreateUser}
            className="mt-4 md:mt-0"
          >
            <UserPlus className="h-4 w-4 mr-2" />
            Add User
          </Button>
        )}
      </div>
      <Card>
        {/* Filters and search */}
        <div className="p-4 border-b">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <Input
                type="text"
                placeholder="Search users..."
                value={searchTerm}
                onChange={handleSearchChange}
                leftIcon={<Search className="h-4 w-4 text-gray-400" />}
                className="w-full"
              />
            </div>
            <div className="flex flex-row gap-2">
              <div className="w-40">
                <select
                  value={roleFilter}
                  onChange={(e) => handleRoleFilterChange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="all">All Roles</option>
                  <option value="super_admin">Super Admin</option>
                  <option value="tenant_admin">Admin</option>
                  <option value="trainer">Trainer</option>
                  <option value="trainee">Trainee</option>
                </select>
              </div>
              <div className="w-40">
                <select
                  value={statusFilter}
                  onChange={(e) => handleStatusFilterChange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="all">All Statuses</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="suspended">Suspended</option>
                </select>
              </div>
              <Button
                variant="outline"
                onClick={() => fetchUsers(currentPage, pageSize)}
                title="Refresh"
              >
                <RefreshCw className="h-4 w-4" />
              </Button>
              {canManageUsers && (
                <Button
                  variant="outline"
                  onClick={handleExportUsers}
                  isLoading={isExporting}
                  disabled={isExporting}
                  title="Export to CSV"
                >
                  <Download className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
        </div>
        {/* Users table */}
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableCell onClick={() => handleSort('first_name')} className="cursor-pointer">
                  <div className="flex items-center">
                    Name
                    {sortField === 'first_name' && (
                      <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </TableCell>
                <TableCell onClick={() => handleSort('email')} className="cursor-pointer">
                  <div className="flex items-center">
                    Email
                    {sortField === 'email' && (
                      <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </TableCell>
                <TableCell onClick={() => handleSort('role')} className="cursor-pointer">
                  <div className="flex items-center">
                    Role
                    {sortField === 'role' && (
                      <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </TableCell>
                <TableCell onClick={() => handleSort('status')} className="cursor-pointer">
                  <div className="flex items-center">
                    Status
                    {sortField === 'status' && (
                      <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </TableCell>
                <TableCell onClick={() => handleSort('created_at')} className="cursor-pointer">
                  <div className="flex items-center">
                    Created
                    {sortField === 'created_at' && (
                      <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  <span className="sr-only">Actions</span>
                </TableCell>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8">
                    <div className="flex flex-col items-center justify-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mb-2"></div>
                      <span className="text-gray-500">Loading users...</span>
                    </div>
                  </TableCell>
                </TableRow>
              ) : filteredUsers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8">
                    <div className="flex flex-col items-center justify-center">
                      <span className="text-gray-500">No users found</span>
                      <p className="text-gray-400 text-sm mt-1">Try changing your search or filters</p>
                    </div>
                  </TableCell>
                </TableRow>
              ) : (
                filteredUsers.map((user) => (
                  <TableRow key={user.id} onClick={() => handleViewUser(user.id)} className="cursor-pointer hover:bg-gray-50">
                    <TableCell>
                      <div className="flex items-center">
                        <Avatar
                          src={user.profile_picture}
                          alt={`${user.first_name} ${user.last_name}`}
                          initials={`${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`}
                          size="sm"
                          className="mr-3"
                        />
                        <div>
                          <div className="font-medium">{user.first_name} {user.last_name}</div>
                          {user.organization && (
                            <div className="text-xs text-gray-500">{user.organization}</div>
                          )}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>{renderRoleBadge(user.role)}</TableCell>
                    <TableCell>{renderStatusBadge(user.status)}</TableCell>
                    <TableCell>{formatDate(user.created_at)}</TableCell>
                    <TableCell>
                      <div className="flex justify-end" onClick={(e) => e.stopPropagation()}>
                        <Dropdown
                          align="right"
                          trigger={
                            <button className="p-1 rounded-full hover:bg-gray-100">
                              <MoreHorizontal className="h-5 w-5 text-gray-500" />
                            </button>
                          }
                        >
                          <DropdownItem onClick={() => handleViewUser(user.id)}>
                            View Profile
                          </DropdownItem>
                          {canManageUsers && (
                            <>
                              <DropdownItem onClick={() => handleEditUser(user.id)}>
                                <Edit className="h-4 w-4 mr-2" />
                                Edit
                              </DropdownItem>
                              <DropdownDivider />
                              <DropdownItem
                                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                onClick={() => handleDeleteUser(user)}
                              >
                                <Trash2 className="h-4 w-4 mr-2" />
                                Delete
                              </DropdownItem>
                            </>
                          )}
                        </Dropdown>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
        {/* Pagination */}
        <div className="p-4 border-t">
          <TablePagination
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={totalItems}
            pageSize={pageSize}
            pageSizeOptions={[10, 25, 50, 100]}
            onPageChange={handlePageChange}
            onPageSizeChange={handlePageSizeChange}
          />
        </div>
      </Card>
      {/* Delete confirmation modal */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
      >
        <ModalHeader>
          <h3 className="text-lg font-medium text-red-600">Delete User</h3>
        </ModalHeader>
        <ModalBody>
          {selectedUser && (
            <div className="space-y-4">
              <Alert type="error" title="Warning: This action cannot be undone">
                Are you sure you want to delete the user <strong>{selectedUser.first_name} {selectedUser.last_name}</strong>?
                This will permanently remove their account and all associated data.
              </Alert>
              <div className="p-4 bg-gray-50 rounded-md">
                <div className="flex items-center">
                  <Avatar
                    src={selectedUser.profile_picture}
                    alt={`${selectedUser.first_name} ${selectedUser.last_name}`}
                    initials={`${selectedUser.first_name?.[0] || ''}${selectedUser.last_name?.[0] || ''}`}
                    size="md"
                    className="mr-4"
                  />
                  <div>
                    <div className="font-medium">{selectedUser.first_name} {selectedUser.last_name}</div>
                    <div className="text-sm text-gray-500">{selectedUser.email}</div>
                    <div className="mt-1">{renderRoleBadge(selectedUser.role)}</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </ModalBody>
        <ModalFooter>
          <Button
            variant="outline"
            onClick={() => setIsDeleteModalOpen(false)}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={confirmDeleteUser}
            isLoading={isLoading}
            disabled={isLoading}
          >
            Delete User
          </Button>
        </ModalFooter>
      </Modal>
    </div>
  );
};
export default UsersPage;
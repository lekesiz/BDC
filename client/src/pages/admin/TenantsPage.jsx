import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Building, 
  Plus, 
  Edit, 
  Trash2, 
  Search, 
  Filter,
  MoreHorizontal,
  Check,
  X
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';
/**
 * Tenants management page
 */
const TenantsPage = () => {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [tenants, setTenants] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [showNewTenantModal, setShowNewTenantModal] = useState(false);
  const [editingTenant, setEditingTenant] = useState(null);
  // Fetch tenants
  useEffect(() => {
    const fetchTenants = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/api/tenants');
        setTenants(response.data);
      } catch (error) {
        console.error('Error fetching tenants:', error);
        addToast({
          title: 'Error',
          message: 'Failed to load tenants',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchTenants();
  }, [addToast]);
  // Filter tenants based on search
  const filteredTenants = tenants.filter(tenant => 
    tenant.name.toLowerCase().includes(searchTerm.toLowerCase())
  );
  // Handle create/update tenant
  const handleSaveTenant = async (tenantData) => {
    try {
      if (editingTenant) {
        // Update existing tenant
        const response = await api.put(`/api/tenants/${editingTenant.id}`, tenantData);
        setTenants(prev => prev.map(t => t.id === editingTenant.id ? response.data : t));
        addToast({
          title: 'Success',
          message: 'Tenant updated successfully',
          type: 'success',
        });
        setShowNewTenantModal(false);
        setEditingTenant(null);
      } else {
        // Create new tenant
        const response = await api.post('/api/tenants', tenantData);
        setTenants(prev => [...prev, response.data]);
        addToast({
          title: 'Success',
          message: 'Tenant created successfully',
          type: 'success',
        });
        setShowNewTenantModal(false);
        setEditingTenant(null);
      }
    } catch (error) {
      console.error('Error saving tenant:', error);
      addToast({
        title: 'Error',
        message: 'Failed to save tenant',
        type: 'error',
      });
    }
  };
  // Handle delete tenant
  const handleDeleteTenant = async (tenantId) => {
    if (!window.confirm('Are you sure you want to delete this tenant?')) {
      return;
    }
    try {
      await api.delete(`/api/tenants/${tenantId}`);
      setTenants(prev => prev.filter(t => t.id !== tenantId));
      addToast({
        title: 'Success',
        message: 'Tenant deleted successfully',
        type: 'success',
      });
    } catch (error) {
      console.error('Error deleting tenant:', error);
      addToast({
        title: 'Error',
        message: 'Failed to delete tenant',
        type: 'error',
      });
    }
  };
  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Tenants Management</h1>
        <Button
          onClick={() => {
            setEditingTenant(null);
            setShowNewTenantModal(true);
          }}
          className="flex items-center"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Tenant
        </Button>
      </div>
      {/* Search bar */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
          <Input
            type="text"
            placeholder="Search tenants..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>
      {/* Tenants list */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          <div className="col-span-full flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : filteredTenants.length === 0 ? (
          <div className="col-span-full text-center py-8 text-gray-500">
            <Building className="w-12 h-12 mx-auto text-gray-300 mb-3" />
            <p>No tenants found</p>
            {searchTerm && <p className="text-sm mt-1">Try adjusting your search</p>}
          </div>
        ) : (
          filteredTenants.map(tenant => (
            <Card key={tenant.id} className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center">
                  <div className="p-3 bg-primary-100 rounded-lg mr-4">
                    <Building className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-medium text-lg">{tenant.name}</h3>
                    <p className="text-sm text-gray-500">ID: {tenant.id}</p>
                  </div>
                </div>
                <div className="relative group">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => e.stopPropagation()}
                    className="relative"
                  >
                    <MoreHorizontal className="w-4 h-4" />
                  </Button>
                  <div className="absolute right-0 top-8 w-48 bg-white border border-gray-200 rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                    <button
                      onClick={() => {
                        setEditingTenant(tenant);
                        setShowNewTenantModal(true);
                      }}
                      className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center"
                    >
                      <Edit className="w-4 h-4 mr-2" />
                      Edit Tenant
                    </button>
                    <button
                      onClick={() => navigate(`/admin/tenants/${tenant.id}`)}
                      className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center"
                    >
                      <Building className="w-4 h-4 mr-2" />
                      View Details
                    </button>
                    <button
                      onClick={() => handleDeleteTenant(tenant.id)}
                      className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center text-red-600"
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Delete Tenant
                    </button>
                  </div>
                </div>
              </div>
              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Status:</span>
                  <span className={`flex items-center ${tenant.is_active ? 'text-green-600' : 'text-red-600'}`}>
                    {tenant.is_active ? (
                      <>
                        <Check className="w-4 h-4 mr-1" />
                        Active
                      </>
                    ) : (
                      <>
                        <X className="w-4 h-4 mr-1" />
                        Inactive
                      </>
                    )}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Users:</span>
                  <span>{tenant.user_count || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Created:</span>
                  <span>{new Date(tenant.created_at).toLocaleDateString()}</span>
                </div>
              </div>
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setEditingTenant(tenant);
                    setShowNewTenantModal(true);
                  }}
                  className="flex-1"
                >
                  <Edit className="w-4 h-4 mr-1" />
                  Edit
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDeleteTenant(tenant.id)}
                  className="flex-1 text-red-600 hover:text-red-700"
                >
                  <Trash2 className="w-4 h-4 mr-1" />
                  Delete
                </Button>
              </div>
            </Card>
          ))
        )}
      </div>
      {/* Create/Edit Tenant Modal */}
      {showNewTenantModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" onClick={() => setShowNewTenantModal(false)}>
              <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
            </div>
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  {editingTenant ? 'Edit Tenant' : 'Create New Tenant'}
                </h3>
                <div className="space-y-4">
                  <div>
                    <label htmlFor="tenantName" className="block text-sm font-medium text-gray-700">
                      Tenant Name
                    </label>
                    <Input
                      type="text"
                      id="tenantName"
                      defaultValue={editingTenant?.name}
                      placeholder="Enter tenant name"
                      className="mt-1 w-full"
                    />
                  </div>
                  <div>
                    <label htmlFor="tenantEmail" className="block text-sm font-medium text-gray-700">
                      Email
                    </label>
                    <Input
                      type="email"
                      id="tenantEmail"
                      defaultValue={editingTenant?.email}
                      placeholder="tenant@example.com"
                      className="mt-1 w-full"
                    />
                  </div>
                  <div>
                    <label htmlFor="tenantPlan" className="block text-sm font-medium text-gray-700">
                      Plan
                    </label>
                    <select
                      id="tenantPlan"
                      defaultValue={editingTenant?.plan || 'basic'}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
                    >
                      <option value="basic">Basic</option>
                      <option value="standard">Standard</option>
                      <option value="premium">Premium</option>
                      <option value="enterprise">Enterprise</option>
                    </select>
                  </div>
                  <div>
                    <label htmlFor="tenantStatus" className="block text-sm font-medium text-gray-700">
                      Status
                    </label>
                    <select
                      id="tenantStatus"
                      defaultValue={editingTenant?.is_active ?? true}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
                    >
                      <option value={true}>Active</option>
                      <option value={false}>Inactive</option>
                    </select>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <Button
                  variant="primary"
                  onClick={() => {
                    const name = document.getElementById('tenantName').value;
                    const email = document.getElementById('tenantEmail').value;
                    const plan = document.getElementById('tenantPlan').value;
                    const is_active = document.getElementById('tenantStatus').value === 'true';
                    if (name.trim()) {
                      const tenantData = { 
                        name, 
                        is_active,
                        ...(email && { email }),
                        ...(plan && { plan })
                      };
                      handleSaveTenant(tenantData);
                    }
                  }}
                  className="w-full sm:w-auto"
                >
                  {editingTenant ? 'Update' : 'Create'} Tenant
                </Button>
                <Button
                  variant="ghost"
                  onClick={() => {
                    setShowNewTenantModal(false);
                    setEditingTenant(null);
                  }}
                  className="mt-3 w-full sm:mt-0 sm:mr-3 sm:w-auto"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default TenantsPage;
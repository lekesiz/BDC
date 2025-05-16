import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Building, 
  ArrowLeft,
  Edit,
  Shield,
  Users,
  Package,
  Calendar,
  Settings,
  Check,
  X
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/toast';

/**
 * Tenant Detail Page
 */
const TenantDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [tenant, setTenant] = useState(null);
  
  // Fetch tenant details
  useEffect(() => {
    const fetchTenant = async () => {
      try {
        setIsLoading(true);
        const response = await api.get(`/api/tenants/${id}`);
        setTenant(response.data);
      } catch (error) {
        console.error('Error fetching tenant:', error);
        addToast({
          title: 'Error',
          message: 'Failed to load tenant details',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchTenant();
  }, [id, addToast]);
  
  if (isLoading) {
    return (
      <div className="flex-1 space-y-4 p-8 pt-6">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }
  
  if (!tenant) {
    return (
      <div className="flex-1 space-y-4 p-8 pt-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900">Tenant not found</h2>
          <Button
            onClick={() => navigate('/admin/tenants')}
            className="mt-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Tenants
          </Button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            onClick={() => navigate('/admin/tenants')}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <h2 className="text-3xl font-bold tracking-tight flex items-center">
            <Building className="w-8 h-8 mr-3 text-primary" />
            {tenant.name}
          </h2>
        </div>
        <Button
          onClick={() => navigate(`/admin/tenants/${id}/edit`)}
        >
          <Edit className="w-4 h-4 mr-2" />
          Edit Tenant
        </Button>
      </div>
      
      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="p-6">
          <div className="flex items-center space-x-2">
            <div className={`p-2 rounded-lg ${tenant.is_active ? 'bg-green-100' : 'bg-red-100'}`}>
              {tenant.is_active ? (
                <Check className={`w-5 h-5 text-green-600`} />
              ) : (
                <X className={`w-5 h-5 text-red-600`} />
              )}
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Status</p>
              <p className="text-lg font-semibold">
                {tenant.is_active ? 'Active' : 'Inactive'}
              </p>
            </div>
          </div>
        </Card>
        
        <Card className="p-6">
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Users className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Users</p>
              <p className="text-lg font-semibold">{tenant.user_count || 0}</p>
            </div>
          </div>
        </Card>
        
        <Card className="p-6">
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Package className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Plan</p>
              <p className="text-lg font-semibold">{tenant.plan || 'Basic'}</p>
            </div>
          </div>
        </Card>
        
        <Card className="p-6">
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Calendar className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Created</p>
              <p className="text-lg font-semibold">
                {new Date(tenant.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </Card>
      </div>
      
      {/* Details Card */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-medium mb-4 flex items-center">
            <Shield className="w-5 h-5 mr-2 text-primary" />
            Tenant Details
          </h3>
          
          <div className="grid gap-6 md:grid-cols-2">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Contact Information</h4>
              <div className="space-y-2">
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">Email</span>
                  <span className="text-gray-900">{tenant.email || 'Not provided'}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">Phone</span>
                  <span className="text-gray-900">{tenant.phone || 'Not provided'}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">Address</span>
                  <span className="text-gray-900">{tenant.address || 'Not provided'}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">Slug</span>
                  <span className="text-gray-900">{tenant.slug}</span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Subscription Details</h4>
              <div className="space-y-2">
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">Plan</span>
                  <span className="text-gray-900">{tenant.plan || 'Basic'}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">Max Users</span>
                  <span className="text-gray-900">{tenant.max_users || 10}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">Max Beneficiaries</span>
                  <span className="text-gray-900">{tenant.max_beneficiaries || 50}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">Expiration Date</span>
                  <span className="text-gray-900">
                    {tenant.expiration_date ? new Date(tenant.expiration_date).toLocaleDateString() : 'Not set'}
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-6">
            <h4 className="font-medium text-gray-900 mb-3">Activity</h4>
            <div className="space-y-2">
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Created At</span>
                <span className="text-gray-900">
                  {new Date(tenant.created_at).toLocaleDateString()} at {new Date(tenant.created_at).toLocaleTimeString()}
                </span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Last Updated</span>
                <span className="text-gray-900">
                  {new Date(tenant.updated_at).toLocaleDateString()} at {new Date(tenant.updated_at).toLocaleTimeString()}
                </span>
              </div>
              {tenant.activation_date && (
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">Activation Date</span>
                  <span className="text-gray-900">
                    {new Date(tenant.activation_date).toLocaleDateString()}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </Card>
      
      {/* Actions */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-medium mb-4 flex items-center">
            <Settings className="w-5 h-5 mr-2 text-primary" />
            Quick Actions
          </h3>
          
          <div className="grid gap-4 md:grid-cols-3">
            <Button
              variant="outline"
              disabled
              className="relative"
            >
              <Users className="w-4 h-4 mr-2" />
              Manage Users
              <span className="absolute -top-2 -right-2 px-2 py-1 text-xs bg-gray-500 text-white rounded-full">Soon</span>
            </Button>
            
            <Button
              variant="outline"
              disabled
              className="relative"
            >
              <Settings className="w-4 h-4 mr-2" />
              Tenant Settings
              <span className="absolute -top-2 -right-2 px-2 py-1 text-xs bg-gray-500 text-white rounded-full">Soon</span>
            </Button>
            
            <Button
              variant="outline"
              disabled
              className="relative"
            >
              <Package className="w-4 h-4 mr-2" />
              Billing & Subscription
              <span className="absolute -top-2 -right-2 px-2 py-1 text-xs bg-gray-500 text-white rounded-full">Soon</span>
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default TenantDetailPage;
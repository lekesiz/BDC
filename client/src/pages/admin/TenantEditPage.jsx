// TODO: i18n - processed
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Building,
  ArrowLeft,
  Save,
  Loader2 } from
'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/toast';
/**
 * Tenant Edit Page
 */import { useTranslation } from "react-i18next";
const TenantEditPage = () => {const { t } = useTranslation();
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [tenant, setTenant] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    plan: 'basic',
    max_users: 10,
    max_beneficiaries: 50,
    is_active: true
  });
  // Fetch tenant details
  useEffect(() => {
    const fetchTenant = async () => {
      try {
        setIsLoading(true);
        const response = await api.get(`/api/tenants/${id}`);
        setTenant(response.data);
        setFormData({
          name: response.data.name || '',
          email: response.data.email || '',
          phone: response.data.phone || '',
          address: response.data.address || '',
          plan: response.data.plan || 'basic',
          max_users: response.data.max_users || 10,
          max_beneficiaries: response.data.max_beneficiaries || 50,
          is_active: response.data.is_active || true
        });
      } catch (error) {
        console.error('Error fetching tenant:', error);
        addToast({
          title: 'Error',
          message: 'Failed to load tenant details',
          type: 'error'
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchTenant();
  }, [id, addToast]);
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setIsSaving(true);
      const response = await api.put(`/api/tenants/${id}`, formData);
      addToast({
        title: 'Success',
        message: 'Tenant updated successfully',
        type: 'success'
      });
      navigate(`/admin/tenants/${id}`);
    } catch (error) {
      console.error('Error updating tenant:', error);
      addToast({
        title: 'Error',
        message: 'Failed to update tenant',
        type: 'error'
      });
    } finally {
      setIsSaving(false);
    }
  };
  // Handle input change
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };
  if (isLoading) {
    return (
      <div className="flex-1 space-y-4 p-8 pt-6">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>);

  }
  if (!tenant) {
    return (
      <div className="flex-1 space-y-4 p-8 pt-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900">{t("pages.tenant_not_found")}</h2>
          <Button
            onClick={() => navigate('/admin/tenants')}
            className="mt-4">

            <ArrowLeft className="w-4 h-4 mr-2" />{t("pages.back_to_tenants")}

          </Button>
        </div>
      </div>);

  }
  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            onClick={() => navigate(`/admin/tenants/${id}`)}>

            <ArrowLeft className="w-4 h-4 mr-2" />{t("components.back")}

          </Button>
          <h2 className="text-3xl font-bold tracking-tight flex items-center">
            <Building className="w-8 h-8 mr-3 text-primary" />{t("components.edit")}
            {tenant.name}
          </h2>
        </div>
      </div>
      {/* Edit Form */}
      <form onSubmit={handleSubmit}>
        <div className="grid gap-6">
          {/* Basic Information */}
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-medium mb-4">{t("pages.basic_information")}</h3>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">{t("pages.tenant_name_")}

                  </label>
                  <Input
                    id="name"
                    name="name"
                    type="text"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    className="w-full" />

                </div>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">{t("components.email")}

                  </label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="w-full" />

                </div>
                <div>
                  <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">{t("components.phone")}

                  </label>
                  <Input
                    id="phone"
                    name="phone"
                    type="tel"
                    value={formData.phone}
                    onChange={handleInputChange}
                    className="w-full" />

                </div>
                <div>
                  <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-1">{t("pages.address")}

                  </label>
                  <Input
                    id="address"
                    name="address"
                    type="text"
                    value={formData.address}
                    onChange={handleInputChange}
                    className="w-full" />

                </div>
              </div>
            </div>
          </Card>
          {/* Subscription Settings */}
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-medium mb-4">{t("pages.subscription_settings")}</h3>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label htmlFor="plan" className="block text-sm font-medium text-gray-700 mb-1">{t("pages.plan")}

                  </label>
                  <select
                    id="plan"
                    name="plan"
                    value={formData.plan}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary focus:border-primary">

                    <option value="basic">{t("components.basic")}</option>
                    <option value="standard">{t("components.standard")}</option>
                    <option value="premium">{t("pages.premium")}</option>
                    <option value="enterprise">{t("components.enterprise")}</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="is_active" className="block text-sm font-medium text-gray-700 mb-1">{t("components.status")}

                  </label>
                  <select
                    id="is_active"
                    name="is_active"
                    value={formData.is_active}
                    onChange={(e) => setFormData((prev) => ({ ...prev, is_active: e.target.value === 'true' }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary focus:border-primary">

                    <option value="true">{t("components.active")}</option>
                    <option value="false">{t("components.inactive")}</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="max_users" className="block text-sm font-medium text-gray-700 mb-1">{t("pages.max_users")}

                  </label>
                  <Input
                    id="max_users"
                    name="max_users"
                    type="number"
                    value={formData.max_users}
                    onChange={handleInputChange}
                    min="1"
                    className="w-full" />

                </div>
                <div>
                  <label htmlFor="max_beneficiaries" className="block text-sm font-medium text-gray-700 mb-1">{t("pages.max_beneficiaries")}

                  </label>
                  <Input
                    id="max_beneficiaries"
                    name="max_beneficiaries"
                    type="number"
                    value={formData.max_beneficiaries}
                    onChange={handleInputChange}
                    min="1"
                    className="w-full" />

                </div>
              </div>
            </div>
          </Card>
          {/* Action Buttons */}
          <div className="flex justify-end space-x-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate(`/admin/tenants/${id}`)}>{t("components.cancel")}


            </Button>
            <Button
              type="submit"
              disabled={isSaving}>

              {isSaving ?
              <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Saving...
                </> :

              <>
                  <Save className="w-4 h-4 mr-2" />{t("components.save_changes")}

              </>
              }
            </Button>
          </div>
        </div>
      </form>
    </div>);

};
export default TenantEditPage;
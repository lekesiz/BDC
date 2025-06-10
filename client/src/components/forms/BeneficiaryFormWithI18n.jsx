import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from '@/i18n/hooks/useTranslation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { toast } from '@/components/ui/toast';
import { AlertCircle, Save, X } from 'lucide-react';
import api from '@/lib/api';

const BeneficiaryFormWithI18n = ({ beneficiary = null, onSubmit, onCancel }) => {
  const { t, validation, ui, format } = useTranslation();
  const navigate = useNavigate();
  const isEditing = !!beneficiary;

  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    dateOfBirth: '',
    gender: '',
    address: {
      street: '',
      city: '',
      state: '',
      zipCode: '',
      country: ''
    },
    emergencyContact: {
      name: '',
      phone: '',
      relationship: ''
    },
    status: 'active',
    notes: ''
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Initialize form with beneficiary data if editing
  useEffect(() => {
    if (beneficiary) {
      setFormData({
        firstName: beneficiary.first_name || '',
        lastName: beneficiary.last_name || '',
        email: beneficiary.email || '',
        phone: beneficiary.phone || '',
        dateOfBirth: beneficiary.date_of_birth || '',
        gender: beneficiary.gender || '',
        address: {
          street: beneficiary.address?.street || '',
          city: beneficiary.address?.city || '',
          state: beneficiary.address?.state || '',
          zipCode: beneficiary.address?.zip_code || '',
          country: beneficiary.address?.country || ''
        },
        emergencyContact: {
          name: beneficiary.emergency_contact?.name || '',
          phone: beneficiary.emergency_contact?.phone || '',
          relationship: beneficiary.emergency_contact?.relationship || ''
        },
        status: beneficiary.status || 'active',
        notes: beneficiary.notes || ''
      });
    }
  }, [beneficiary]);

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    
    if (name.includes('.')) {
      const [parent, child] = name.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
    
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};

    // Required fields
    if (!formData.firstName.trim()) {
      newErrors.firstName = t('beneficiaries.validation.firstNameRequired');
    }
    if (!formData.lastName.trim()) {
      newErrors.lastName = t('beneficiaries.validation.lastNameRequired');
    }
    if (!formData.email.trim()) {
      newErrors.email = t('beneficiaries.validation.emailRequired');
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = t('beneficiaries.validation.invalidEmail');
    }
    if (!formData.phone.trim()) {
      newErrors.phone = t('beneficiaries.validation.phoneRequired');
    }
    if (!formData.dateOfBirth) {
      newErrors.dateOfBirth = t('beneficiaries.validation.dateOfBirthRequired');
    } else {
      const birthDate = new Date(formData.dateOfBirth);
      if (birthDate > new Date()) {
        newErrors.dateOfBirth = t('beneficiaries.validation.futureDate');
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      toast.error(t('messages.error.validation'));
      return;
    }

    setIsSubmitting(true);

    try {
      const payload = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        phone: formData.phone,
        date_of_birth: formData.dateOfBirth,
        gender: formData.gender,
        address: formData.address,
        emergency_contact: formData.emergencyContact,
        status: formData.status,
        notes: formData.notes
      };

      if (onSubmit) {
        await onSubmit(payload);
      } else {
        if (isEditing) {
          await api.put(`/api/beneficiaries/${beneficiary.id}`, payload);
          toast.success(t('beneficiaries.messages.updateSuccess'));
        } else {
          await api.post('/api/beneficiaries', payload);
          toast.success(t('beneficiaries.messages.createSuccess'));
        }
        navigate('/beneficiaries');
      }
    } catch (error) {
      console.error('Error saving beneficiary:', error);
      toast.error(
        error.response?.data?.message || 
        t(isEditing ? 'messages.error.general' : 'messages.error.general')
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const genderOptions = [
    { value: 'male', label: t('common.male', { defaultValue: 'Male' }) },
    { value: 'female', label: t('common.female', { defaultValue: 'Female' }) },
    { value: 'other', label: t('common.other') }
  ];

  const statusOptions = [
    { value: 'active', label: t('beneficiaries.status.active') },
    { value: 'inactive', label: t('beneficiaries.status.inactive') },
    { value: 'pending', label: t('beneficiaries.status.pending') }
  ];

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">
          {t('beneficiaries.fields.personalInfo', { defaultValue: 'Personal Information' })}
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="firstName">
              {t('beneficiaries.fields.firstName')} *
            </Label>
            <Input
              id="firstName"
              name="firstName"
              value={formData.firstName}
              onChange={handleChange}
              placeholder={t('placeholders.firstName')}
              className={errors.firstName ? 'border-red-500' : ''}
            />
            {errors.firstName && (
              <p className="mt-1 text-sm text-red-600 flex items-center">
                <AlertCircle className="w-4 h-4 mr-1" />
                {errors.firstName}
              </p>
            )}
          </div>

          <div>
            <Label htmlFor="lastName">
              {t('beneficiaries.fields.lastName')} *
            </Label>
            <Input
              id="lastName"
              name="lastName"
              value={formData.lastName}
              onChange={handleChange}
              placeholder={t('placeholders.lastName')}
              className={errors.lastName ? 'border-red-500' : ''}
            />
            {errors.lastName && (
              <p className="mt-1 text-sm text-red-600 flex items-center">
                <AlertCircle className="w-4 h-4 mr-1" />
                {errors.lastName}
              </p>
            )}
          </div>

          <div>
            <Label htmlFor="email">
              {t('beneficiaries.fields.email')} *
            </Label>
            <Input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder={t('placeholders.email')}
              className={errors.email ? 'border-red-500' : ''}
            />
            {errors.email && (
              <p className="mt-1 text-sm text-red-600 flex items-center">
                <AlertCircle className="w-4 h-4 mr-1" />
                {errors.email}
              </p>
            )}
          </div>

          <div>
            <Label htmlFor="phone">
              {t('beneficiaries.fields.phone')} *
            </Label>
            <Input
              id="phone"
              name="phone"
              type="tel"
              value={formData.phone}
              onChange={handleChange}
              placeholder={t('placeholders.phone')}
              className={errors.phone ? 'border-red-500' : ''}
            />
            {errors.phone && (
              <p className="mt-1 text-sm text-red-600 flex items-center">
                <AlertCircle className="w-4 h-4 mr-1" />
                {errors.phone}
              </p>
            )}
          </div>

          <div>
            <Label htmlFor="dateOfBirth">
              {t('beneficiaries.fields.dateOfBirth')} *
            </Label>
            <Input
              id="dateOfBirth"
              name="dateOfBirth"
              type="date"
              value={formData.dateOfBirth}
              onChange={handleChange}
              className={errors.dateOfBirth ? 'border-red-500' : ''}
              max={new Date().toISOString().split('T')[0]}
            />
            {errors.dateOfBirth && (
              <p className="mt-1 text-sm text-red-600 flex items-center">
                <AlertCircle className="w-4 h-4 mr-1" />
                {errors.dateOfBirth}
              </p>
            )}
          </div>

          <div>
            <Label htmlFor="gender">
              {t('beneficiaries.fields.gender')}
            </Label>
            <Select
              id="gender"
              name="gender"
              value={formData.gender}
              onChange={handleChange}
            >
              <option value="">{t('placeholders.select')}</option>
              {genderOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </Select>
          </div>

          <div>
            <Label htmlFor="status">
              {t('beneficiaries.fields.status')}
            </Label>
            <Select
              id="status"
              name="status"
              value={formData.status}
              onChange={handleChange}
            >
              {statusOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </Select>
          </div>
        </div>
      </Card>

      {/* Address Information */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">
          {t('beneficiaries.fields.address')}
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="md:col-span-2">
            <Label htmlFor="street">
              {t('beneficiaries.fields.street')}
            </Label>
            <Input
              id="street"
              name="address.street"
              value={formData.address.street}
              onChange={handleChange}
              placeholder={t('placeholders.street', { defaultValue: 'Street address' })}
            />
          </div>

          <div>
            <Label htmlFor="city">
              {t('beneficiaries.fields.city')}
            </Label>
            <Input
              id="city"
              name="address.city"
              value={formData.address.city}
              onChange={handleChange}
              placeholder={t('placeholders.city', { defaultValue: 'City' })}
            />
          </div>

          <div>
            <Label htmlFor="state">
              {t('beneficiaries.fields.state')}
            </Label>
            <Input
              id="state"
              name="address.state"
              value={formData.address.state}
              onChange={handleChange}
              placeholder={t('placeholders.state', { defaultValue: 'State/Province' })}
            />
          </div>

          <div>
            <Label htmlFor="zipCode">
              {t('beneficiaries.fields.zipCode')}
            </Label>
            <Input
              id="zipCode"
              name="address.zipCode"
              value={formData.address.zipCode}
              onChange={handleChange}
              placeholder={t('placeholders.zipCode', { defaultValue: 'ZIP/Postal code' })}
            />
          </div>

          <div>
            <Label htmlFor="country">
              {t('beneficiaries.fields.country')}
            </Label>
            <Input
              id="country"
              name="address.country"
              value={formData.address.country}
              onChange={handleChange}
              placeholder={t('placeholders.country', { defaultValue: 'Country' })}
            />
          </div>
        </div>
      </Card>

      {/* Emergency Contact */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">
          {t('beneficiaries.fields.emergencyContact')}
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Label htmlFor="emergencyName">
              {t('beneficiaries.fields.emergencyContactName')}
            </Label>
            <Input
              id="emergencyName"
              name="emergencyContact.name"
              value={formData.emergencyContact.name}
              onChange={handleChange}
              placeholder={t('placeholders.contactName', { defaultValue: 'Contact name' })}
            />
          </div>

          <div>
            <Label htmlFor="emergencyPhone">
              {t('beneficiaries.fields.emergencyContactPhone')}
            </Label>
            <Input
              id="emergencyPhone"
              name="emergencyContact.phone"
              type="tel"
              value={formData.emergencyContact.phone}
              onChange={handleChange}
              placeholder={t('placeholders.phone')}
            />
          </div>

          <div>
            <Label htmlFor="emergencyRelationship">
              {t('beneficiaries.fields.emergencyContactRelation')}
            </Label>
            <Input
              id="emergencyRelationship"
              name="emergencyContact.relationship"
              value={formData.emergencyContact.relationship}
              onChange={handleChange}
              placeholder={t('placeholders.relationship', { defaultValue: 'Relationship' })}
            />
          </div>
        </div>
      </Card>

      {/* Additional Notes */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">
          {t('beneficiaries.fields.notes')}
        </h3>
        
        <Textarea
          id="notes"
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          placeholder={t('placeholders.notes')}
          rows={4}
        />
      </Card>

      {/* Form Actions */}
      <div className="flex justify-end gap-4">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel || (() => navigate('/beneficiaries'))}
          disabled={isSubmitting}
        >
          <X className="w-4 h-4 mr-2" />
          {ui.cancel()}
        </Button>
        <Button
          type="submit"
          disabled={isSubmitting}
        >
          <Save className="w-4 h-4 mr-2" />
          {isSubmitting ? ui.saving() : (isEditing ? ui.update() : ui.save())}
        </Button>
      </div>
    </form>
  );
};

export default BeneficiaryFormWithI18n;
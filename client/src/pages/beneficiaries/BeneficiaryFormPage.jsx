import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { 
  ArrowLeft, 
  Save, 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Calendar, 
  Users, 
  Globe,
  Building,
  AlertCircle,
  Info
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ui/toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsList, TabTrigger, TabContent } from '@/components/ui/tabs';
import { Form, FormGroup, FormLabel, FormHelper } from '@/components/ui/form';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Alert } from '@/components/ui/alert';
import { Avatar } from '@/components/ui/avatar';
import api from '@/lib/api';
// Beneficiary form validation schema
const beneficiarySchema = z.object({
  // Personal Information
  first_name: z.string().min(2, 'First name must be at least 2 characters'),
  last_name: z.string().min(2, 'Last name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
  phone: z.string().optional(),
  birth_date: z.string().optional(),
  gender: z.enum(['male', 'female', 'other', '']).optional(),
  nationality: z.string().optional(),
  native_language: z.string().optional(),
  // Address
  address: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  zip_code: z.string().optional(),
  country: z.string().optional(),
  // Additional Information
  organization: z.string().optional(),
  occupation: z.string().optional(),
  education_level: z.string().optional(),
  bio: z.string().optional(),
  goals: z.string().optional(),
  // Status and Classification
  status: z.enum(['active', 'inactive', 'pending', 'completed']),
  category: z.string().optional(),
  referral_source: z.string().optional(),
  notes: z.string().optional(),
  // Custom fields (can be extended as needed)
  custom_fields: z.record(z.string(), z.any()).optional()
});
/**
 * BeneficiaryFormPage component for creating and editing beneficiary records
 */
const BeneficiaryFormPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { hasRole } = useAuth();
  const { addToast } = useToast();
  const isEditMode = Boolean(id);
  // State
  const [activeTab, setActiveTab] = useState('personal');
  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(isEditMode);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [trainers, setTrainers] = useState([]);
  const [selectedTrainers, setSelectedTrainers] = useState([]);
  const [customFields, setCustomFields] = useState({});
  const [showCustomFieldForm, setShowCustomFieldForm] = useState(false);
  const [newFieldName, setNewFieldName] = useState('');
  const [newFieldValue, setNewFieldValue] = useState('');
  // Check if user can manage beneficiaries
  const canManage = hasRole(['super_admin', 'tenant_admin', 'trainer']);
  // Form setup
  const { 
    register, 
    handleSubmit, 
    formState: { errors, isDirty },
    reset,
    setValue,
    watch,
    getValues,
    control,
  } = useForm({
    resolver: zodResolver(beneficiarySchema),
    defaultValues: {
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      birth_date: '',
      gender: '',
      nationality: '',
      native_language: '',
      address: '',
      city: '',
      state: '',
      zip_code: '',
      country: '',
      organization: '',
      occupation: '',
      education_level: '',
      bio: '',
      goals: '',
      status: 'active',
      category: '',
      referral_source: '',
      notes: '',
      custom_fields: {}
    }
  });
  // Fetch trainers for assignment
  useEffect(() => {
    const fetchTrainers = async () => {
      try {
        const response = await api.get('/api/users', {
          params: { role: 'trainer', status: 'active' }
        });
        setTrainers(response.data.items || []);
      } catch (error) {
        console.error('Error fetching trainers:', error);
        addToast({
          type: 'error',
          title: 'Failed to load trainers',
          message: 'Could not fetch the list of available trainers.'
        });
      }
    };
    fetchTrainers();
  }, [addToast]);
  // Fetch beneficiary data in edit mode
  useEffect(() => {
    if (isEditMode) {
      const fetchBeneficiary = async () => {
        try {
          setIsFetching(true);
          const response = await api.get(`/api/beneficiaries/${id}`);
          const beneficiaryData = response.data;
          // Populate form with beneficiary data
          Object.entries(beneficiaryData).forEach(([key, value]) => {
            if (key !== 'custom_fields' && value !== null && value !== undefined) {
              setValue(key, value);
            }
          });
          // Handle custom fields separately
          if (beneficiaryData.custom_fields) {
            setCustomFields(beneficiaryData.custom_fields);
            setValue('custom_fields', beneficiaryData.custom_fields);
          }
          // Fetch assigned trainers
          if (beneficiaryData.id) {
            const trainersResponse = await api.get(`/api/beneficiaries/${id}/trainers`);
            setSelectedTrainers(trainersResponse.data.map(trainer => trainer.id));
          }
        } catch (error) {
          console.error('Error fetching beneficiary:', error);
          addToast({
            type: 'error',
            title: 'Failed to load beneficiary',
            message: error.response?.data?.message || 'An unexpected error occurred.'
          });
          // Navigate back on error
          navigate('/beneficiaries');
        } finally {
          setIsFetching(false);
        }
      };
      fetchBeneficiary();
    }
  }, [id, isEditMode, setValue, navigate, addToast]);
  // Handle form submission
  const onSubmit = async (data) => {
    try {
      setIsLoading(true);
      // Add custom fields to the data
      data.custom_fields = customFields;
      let response;
      if (isEditMode) {
        // Update existing beneficiary
        response = await api.put(`/api/beneficiaries/${id}`, data);
      } else {
        // Create new beneficiary
        response = await api.post('/api/beneficiaries', data);
      }
      const beneficiaryId = response.data.id;
      // Handle profile picture upload if provided
      if (uploadedImage) {
        const formData = new FormData();
        formData.append('profile_picture', uploadedImage);
        await api.post(`/api/beneficiaries/${beneficiaryId}/profile-picture`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
      }
      // Update trainer assignments
      if (selectedTrainers.length > 0) {
        // Assign first trainer (current backend only supports single trainer)
        await api.post(`/api/beneficiaries/${beneficiaryId}/assign-trainer`, {
          trainer_id: selectedTrainers[0]
        });
      }
      // Show success message
      addToast({
        type: 'success',
        title: isEditMode ? 'Beneficiary updated' : 'Beneficiary created',
        message: isEditMode
          ? `${data.first_name} ${data.last_name}'s information has been updated.`
          : `${data.first_name} ${data.last_name} has been created successfully.`
      });
      // Navigate to beneficiary details page
      navigate(`/beneficiaries/${beneficiaryId}`);
    } catch (error) {
      console.error(isEditMode ? 'Error updating beneficiary:' : 'Error creating beneficiary:', error);
      addToast({
        type: 'error',
        title: isEditMode ? 'Update failed' : 'Creation failed',
        message: error.response?.data?.message || `An error occurred while ${isEditMode ? 'updating' : 'creating'} the beneficiary.`
      });
    } finally {
      setIsLoading(false);
    }
  };
  // Handle image upload
  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type and size
      const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
      const maxSize = 5 * 1024 * 1024; // 5MB
      if (!validTypes.includes(file.type)) {
        addToast({
          type: 'error',
          title: 'Invalid file type',
          message: 'Please upload a JPEG, PNG, or GIF image.'
        });
        return;
      }
      if (file.size > maxSize) {
        addToast({
          type: 'error',
          title: 'File too large',
          message: 'Please upload an image smaller than 5MB.'
        });
        return;
      }
      // Set uploaded image
      setUploadedImage(file);
    }
  };
  // Toggle trainer selection
  const toggleTrainerSelection = (trainerId) => {
    setSelectedTrainers(prev => {
      if (prev.includes(trainerId)) {
        return prev.filter(id => id !== trainerId);
      } else {
        return [...prev, trainerId];
      }
    });
  };
  // Add custom field
  const addCustomField = () => {
    if (!newFieldName.trim()) {
      addToast({
        type: 'error',
        title: 'Invalid field name',
        message: 'Please enter a name for the custom field.'
      });
      return;
    }
    const fieldKey = newFieldName.trim().toLowerCase().replace(/\s+/g, '_');
    setCustomFields(prev => ({
      ...prev,
      [fieldKey]: newFieldValue
    }));
    // Reset form
    setNewFieldName('');
    setNewFieldValue('');
    setShowCustomFieldForm(false);
  };
  // Remove custom field
  const removeCustomField = (fieldKey) => {
    setCustomFields(prev => {
      const newFields = { ...prev };
      delete newFields[fieldKey];
      return newFields;
    });
  };
  // Loading state
  if (isFetching) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }
  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header with navigation */}
      <div className="mb-6">
        <Button
          variant="outline"
          onClick={() => navigate('/beneficiaries')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Beneficiaries
        </Button>
        <h1 className="text-2xl font-bold">{isEditMode ? 'Edit Beneficiary' : 'Add New Beneficiary'}</h1>
        <p className="text-gray-600">
          {isEditMode 
            ? 'Update beneficiary information and status' 
            : 'Enter details to create a new beneficiary record'
          }
        </p>
      </div>
      {/* Form layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <CardContent className="pt-6">
              {/* Profile picture upload */}
              <div className="flex flex-col items-center text-center">
                <div className="relative mb-4 group">
                  <Avatar 
                    src={uploadedImage ? URL.createObjectURL(uploadedImage) : undefined}
                    size="xl"
                    className="cursor-pointer"
                  />
                  <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 rounded-full opacity-0 group-hover:opacity-100 transition-opacity">
                    <label htmlFor="profile-picture" className="cursor-pointer p-2 text-white">
                      <User className="h-6 w-6" />
                    </label>
                    <input
                      id="profile-picture"
                      type="file"
                      className="hidden"
                      accept="image/*"
                      onChange={handleImageUpload}
                    />
                  </div>
                </div>
                {uploadedImage && (
                  <p className="text-sm text-gray-500 mb-2">
                    {uploadedImage.name}
                  </p>
                )}
                <p className="text-sm text-gray-500">
                  Click on the avatar to upload a profile picture
                </p>
              </div>
              {/* Trainer assignment section */}
              <div className="mt-6 border-t pt-6">
                <h3 className="text-sm font-medium mb-3">Assign Trainers</h3>
                {trainers.length === 0 ? (
                  <p className="text-sm text-gray-500 italic">No trainers available.</p>
                ) : (
                  <div className="space-y-2 max-h-64 overflow-y-auto p-1">
                    {trainers.map(trainer => (
                      <div 
                        key={trainer.id} 
                        className={`flex items-center p-2 rounded-md cursor-pointer ${
                          selectedTrainers.includes(trainer.id) ? 'bg-primary bg-opacity-10' : 'hover:bg-gray-100'
                        }`}
                        onClick={() => toggleTrainerSelection(trainer.id)}
                      >
                        <input
                          type="checkbox"
                          className="h-4 w-4 text-primary rounded border-gray-300 focus:ring-primary"
                          checked={selectedTrainers.includes(trainer.id)}
                          onChange={() => {}}
                        />
                        <div className="ml-3">
                          <p className="text-sm font-medium">{trainer.first_name} {trainer.last_name}</p>
                          <p className="text-xs text-gray-500">{trainer.email}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              {/* Status section */}
              <div className="mt-6 border-t pt-6">
                <h3 className="text-sm font-medium mb-3">Status</h3>
                <select
                  id="status"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  {...register('status')}
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="pending">Pending</option>
                  <option value="completed">Completed</option>
                </select>
                {errors.status && (
                  <p className="text-sm text-red-500 mt-1">{errors.status.message}</p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
        {/* Main form content */}
        <div className="lg:col-span-3">
          <Card>
            <form onSubmit={handleSubmit(onSubmit)}>
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <CardHeader className="pb-0">
                  <TabsList>
                    <TabTrigger value="personal">
                      <User className="h-4 w-4 mr-2" />
                      Personal Info
                    </TabTrigger>
                    <TabTrigger value="address">
                      <MapPin className="h-4 w-4 mr-2" />
                      Address
                    </TabTrigger>
                    <TabTrigger value="additional">
                      <Info className="h-4 w-4 mr-2" />
                      Additional Info
                    </TabTrigger>
                    <TabTrigger value="custom">
                      <AlertCircle className="h-4 w-4 mr-2" />
                      Custom Fields
                    </TabTrigger>
                  </TabsList>
                </CardHeader>
                {/* Personal Information Tab */}
                <TabContent value="personal">
                  <CardContent className="pt-6 space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <FormGroup>
                        <FormLabel htmlFor="first_name">First Name *</FormLabel>
                        <Input
                          id="first_name"
                          placeholder="First name"
                          leftIcon={<User className="h-4 w-4 text-gray-400" />}
                          error={errors.first_name?.message}
                          disabled={isLoading}
                          {...register('first_name')}
                        />
                      </FormGroup>
                      <FormGroup>
                        <FormLabel htmlFor="last_name">Last Name *</FormLabel>
                        <Input
                          id="last_name"
                          placeholder="Last name"
                          leftIcon={<User className="h-4 w-4 text-gray-400" />}
                          error={errors.last_name?.message}
                          disabled={isLoading}
                          {...register('last_name')}
                        />
                      </FormGroup>
                    </div>
                    <FormGroup>
                      <FormLabel htmlFor="email">Email Address *</FormLabel>
                      <Input
                        id="email"
                        type="email"
                        placeholder="email@example.com"
                        leftIcon={<Mail className="h-4 w-4 text-gray-400" />}
                        error={errors.email?.message}
                        disabled={isLoading}
                        {...register('email')}
                      />
                    </FormGroup>
                    <FormGroup>
                      <FormLabel htmlFor="phone">Phone Number</FormLabel>
                      <Input
                        id="phone"
                        placeholder="+1 (555) 123-4567"
                        leftIcon={<Phone className="h-4 w-4 text-gray-400" />}
                        error={errors.phone?.message}
                        disabled={isLoading}
                        {...register('phone')}
                      />
                    </FormGroup>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <FormGroup>
                        <FormLabel htmlFor="birth_date">Birth Date</FormLabel>
                        <Input
                          id="birth_date"
                          type="date"
                          leftIcon={<Calendar className="h-4 w-4 text-gray-400" />}
                          error={errors.birth_date?.message}
                          disabled={isLoading}
                          {...register('birth_date')}
                        />
                      </FormGroup>
                      <FormGroup>
                        <FormLabel htmlFor="gender">Gender</FormLabel>
                        <select
                          id="gender"
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          disabled={isLoading}
                          {...register('gender')}
                        >
                          <option value="">Select gender</option>
                          <option value="male">Male</option>
                          <option value="female">Female</option>
                          <option value="other">Other</option>
                        </select>
                        {errors.gender && (
                          <p className="text-sm text-red-500 mt-1">{errors.gender.message}</p>
                        )}
                      </FormGroup>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <FormGroup>
                        <FormLabel htmlFor="nationality">Nationality</FormLabel>
                        <Input
                          id="nationality"
                          placeholder="Nationality"
                          leftIcon={<Globe className="h-4 w-4 text-gray-400" />}
                          error={errors.nationality?.message}
                          disabled={isLoading}
                          {...register('nationality')}
                        />
                      </FormGroup>
                      <FormGroup>
                        <FormLabel htmlFor="native_language">Native Language</FormLabel>
                        <Input
                          id="native_language"
                          placeholder="Native language"
                          error={errors.native_language?.message}
                          disabled={isLoading}
                          {...register('native_language')}
                        />
                      </FormGroup>
                    </div>
                    <Alert type="info" title="Required Fields">
                      Fields marked with * are required.
                    </Alert>
                  </CardContent>
                </TabContent>
                {/* Address Tab */}
                <TabContent value="address">
                  <CardContent className="pt-6 space-y-4">
                    <FormGroup>
                      <FormLabel htmlFor="address">Street Address</FormLabel>
                      <Input
                        id="address"
                        placeholder="123 Main St"
                        leftIcon={<MapPin className="h-4 w-4 text-gray-400" />}
                        error={errors.address?.message}
                        disabled={isLoading}
                        {...register('address')}
                      />
                    </FormGroup>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <FormGroup>
                        <FormLabel htmlFor="city">City</FormLabel>
                        <Input
                          id="city"
                          placeholder="City"
                          error={errors.city?.message}
                          disabled={isLoading}
                          {...register('city')}
                        />
                      </FormGroup>
                      <FormGroup>
                        <FormLabel htmlFor="state">State / Province</FormLabel>
                        <Input
                          id="state"
                          placeholder="State or province"
                          error={errors.state?.message}
                          disabled={isLoading}
                          {...register('state')}
                        />
                      </FormGroup>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <FormGroup>
                        <FormLabel htmlFor="zip_code">ZIP / Postal Code</FormLabel>
                        <Input
                          id="zip_code"
                          placeholder="Postal code"
                          error={errors.zip_code?.message}
                          disabled={isLoading}
                          {...register('zip_code')}
                        />
                      </FormGroup>
                      <FormGroup>
                        <FormLabel htmlFor="country">Country</FormLabel>
                        <Input
                          id="country"
                          placeholder="Country"
                          error={errors.country?.message}
                          disabled={isLoading}
                          {...register('country')}
                        />
                      </FormGroup>
                    </div>
                    <Alert type="info" title="Address Information">
                      Address information is optional but helpful for contacting the beneficiary.
                    </Alert>
                  </CardContent>
                </TabContent>
                {/* Additional Information Tab */}
                <TabContent value="additional">
                  <CardContent className="pt-6 space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <FormGroup>
                        <FormLabel htmlFor="organization">Organization</FormLabel>
                        <Input
                          id="organization"
                          placeholder="Company or organization"
                          leftIcon={<Building className="h-4 w-4 text-gray-400" />}
                          error={errors.organization?.message}
                          disabled={isLoading}
                          {...register('organization')}
                        />
                      </FormGroup>
                      <FormGroup>
                        <FormLabel htmlFor="occupation">Occupation</FormLabel>
                        <Input
                          id="occupation"
                          placeholder="Current occupation"
                          error={errors.occupation?.message}
                          disabled={isLoading}
                          {...register('occupation')}
                        />
                      </FormGroup>
                    </div>
                    <FormGroup>
                      <FormLabel htmlFor="education_level">Education Level</FormLabel>
                      <select
                        id="education_level"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        disabled={isLoading}
                        {...register('education_level')}
                      >
                        <option value="">Select education level</option>
                        <option value="primary">Primary Education</option>
                        <option value="secondary">Secondary Education</option>
                        <option value="bachelor">Bachelor's Degree</option>
                        <option value="master">Master's Degree</option>
                        <option value="doctorate">Doctorate</option>
                        <option value="other">Other</option>
                      </select>
                      {errors.education_level && (
                        <p className="text-sm text-red-500 mt-1">{errors.education_level.message}</p>
                      )}
                    </FormGroup>
                    <FormGroup>
                      <FormLabel htmlFor="category">Category</FormLabel>
                      <Input
                        id="category"
                        placeholder="Beneficiary category"
                        error={errors.category?.message}
                        disabled={isLoading}
                        {...register('category')}
                      />
                      <FormHelper>
                        Category helps in grouping beneficiaries for reporting and analytics.
                      </FormHelper>
                    </FormGroup>
                    <FormGroup>
                      <FormLabel htmlFor="referral_source">Referral Source</FormLabel>
                      <Input
                        id="referral_source"
                        placeholder="How did they hear about the program?"
                        error={errors.referral_source?.message}
                        disabled={isLoading}
                        {...register('referral_source')}
                      />
                    </FormGroup>
                    <FormGroup>
                      <FormLabel htmlFor="bio">Biography</FormLabel>
                      <textarea
                        id="bio"
                        placeholder="Brief background information"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        rows={3}
                        disabled={isLoading}
                        {...register('bio')}
                      ></textarea>
                      {errors.bio && (
                        <p className="text-sm text-red-500 mt-1">{errors.bio.message}</p>
                      )}
                    </FormGroup>
                    <FormGroup>
                      <FormLabel htmlFor="goals">Goals</FormLabel>
                      <textarea
                        id="goals"
                        placeholder="What are the beneficiary's main goals?"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        rows={3}
                        disabled={isLoading}
                        {...register('goals')}
                      ></textarea>
                      {errors.goals && (
                        <p className="text-sm text-red-500 mt-1">{errors.goals.message}</p>
                      )}
                    </FormGroup>
                    <FormGroup>
                      <FormLabel htmlFor="notes">Notes</FormLabel>
                      <textarea
                        id="notes"
                        placeholder="Additional notes"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        rows={3}
                        disabled={isLoading}
                        {...register('notes')}
                      ></textarea>
                      {errors.notes && (
                        <p className="text-sm text-red-500 mt-1">{errors.notes.message}</p>
                      )}
                    </FormGroup>
                  </CardContent>
                </TabContent>
                {/* Custom Fields Tab */}
                <TabContent value="custom">
                  <CardContent className="pt-6 space-y-4">
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="text-lg font-medium">Custom Fields</h3>
                      <Button 
                        type="button" 
                        variant="outline" 
                        onClick={() => setShowCustomFieldForm(true)}
                        disabled={showCustomFieldForm}
                      >
                        Add Field
                      </Button>
                    </div>
                    {showCustomFieldForm && (
                      <div className="bg-gray-50 p-4 rounded-md mb-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                          <FormGroup>
                            <FormLabel htmlFor="new-field-name">Field Name</FormLabel>
                            <Input
                              id="new-field-name"
                              placeholder="Field name"
                              value={newFieldName}
                              onChange={e => setNewFieldName(e.target.value)}
                            />
                          </FormGroup>
                          <FormGroup>
                            <FormLabel htmlFor="new-field-value">Field Value</FormLabel>
                            <Input
                              id="new-field-value"
                              placeholder="Field value"
                              value={newFieldValue}
                              onChange={e => setNewFieldValue(e.target.value)}
                            />
                          </FormGroup>
                        </div>
                        <div className="flex justify-end space-x-2">
                          <Button 
                            type="button" 
                            variant="outline" 
                            onClick={() => setShowCustomFieldForm(false)}
                          >
                            Cancel
                          </Button>
                          <Button 
                            type="button" 
                            onClick={addCustomField}
                          >
                            Add
                          </Button>
                        </div>
                      </div>
                    )}
                    {Object.keys(customFields).length === 0 ? (
                      <div className="text-center py-8 border rounded-md">
                        <AlertCircle className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                        <h4 className="font-medium text-gray-500">No custom fields</h4>
                        <p className="text-gray-400 text-sm mt-1">
                          Add custom fields to store additional information about this beneficiary.
                        </p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {Object.entries(customFields).map(([key, value]) => (
                          <div key={key} className="flex items-center justify-between bg-gray-50 p-4 rounded-md">
                            <div>
                              <h4 className="font-medium">
                                {key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                              </h4>
                              <p className="text-sm text-gray-600 mt-1">{value}</p>
                            </div>
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => removeCustomField(key)}
                              className="text-red-500 hover:text-red-700 hover:bg-red-50"
                            >
                              Remove
                            </Button>
                          </div>
                        ))}
                      </div>
                    )}
                    <Alert type="info" title="Custom Fields">
                      Custom fields allow you to store additional information that doesn't fit into the standard fields.
                    </Alert>
                  </CardContent>
                </TabContent>
                <CardFooter className="border-t pt-6 flex justify-between">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => navigate('/beneficiaries')}
                    disabled={isLoading}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    isLoading={isLoading}
                    disabled={isLoading}
                  >
                    {!isLoading && (
                      <Save className="h-4 w-4 mr-2" />
                    )}
                    {isEditMode ? 'Update Beneficiary' : 'Create Beneficiary'}
                  </Button>
                </CardFooter>
              </Tabs>
            </form>
          </Card>
        </div>
      </div>
    </div>
  );
};
export default BeneficiaryFormPage;
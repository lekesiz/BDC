import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { User, Mail, Lock, Phone, Building, Key, ArrowLeft, Save, Loader } from 'lucide-react';

import { useToast } from '@/components/ui/toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, FormGroup, FormLabel, FormControl, FormHelper } from '@/components/ui/form';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Avatar } from '@/components/ui/avatar';
import { Alert } from '@/components/ui/alert';
import api from '@/lib/api';

// Create user form validation schema
const createUserSchema = z.object({
  first_name: z.string().min(2, 'First name must be at least 2 characters'),
  last_name: z.string().min(2, 'Last name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirm_password: z.string(),
  phone: z.string().optional(),
  organization: z.string().optional(),
  role: z.enum(['super_admin', 'tenant_admin', 'trainer', 'trainee']),
  status: z.enum(['active', 'inactive', 'suspended']),
})
.refine(data => data.password === data.confirm_password, {
  message: "Passwords don't match",
  path: ['confirm_password'],
});

// Edit user form validation schema (password is optional)
const editUserSchema = z.object({
  first_name: z.string().min(2, 'First name must be at least 2 characters'),
  last_name: z.string().min(2, 'Last name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters').optional().or(z.literal('')),
  confirm_password: z.string().optional().or(z.literal('')),
  phone: z.string().optional(),
  organization: z.string().optional(),
  role: z.enum(['super_admin', 'tenant_admin', 'trainer', 'trainee']),
  status: z.enum(['active', 'inactive', 'suspended']),
})
.refine(data => !data.password || data.password === data.confirm_password, {
  message: "Passwords don't match",
  path: ['confirm_password'],
});

/**
 * User form page for creating and editing users
 */
const UserFormPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToast } = useToast();
  const isEditMode = Boolean(id);
  
  // State
  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(isEditMode);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  // Form setup with conditional schema based on mode
  const { 
    register, 
    handleSubmit, 
    formState: { errors }, 
    reset,
    setValue,
    watch,
  } = useForm({
    resolver: zodResolver(isEditMode ? editUserSchema : createUserSchema),
    defaultValues: {
      first_name: '',
      last_name: '',
      email: '',
      password: '',
      confirm_password: '',
      phone: '',
      organization: '',
      role: 'trainee',
      status: 'active',
    }
  });
  
  // Watch role for conditional fields
  const currentRole = watch('role');
  
  // Fetch user data for edit mode
  useEffect(() => {
    if (isEditMode) {
      const fetchUser = async () => {
        try {
          setIsFetching(true);
          
          const response = await api.get(`/api/users/${id}`);
          const userData = response.data;
          
          // Populate form with user data
          setValue('first_name', userData.first_name);
          setValue('last_name', userData.last_name);
          setValue('email', userData.email);
          setValue('phone', userData.phone || '');
          setValue('organization', userData.organization || '');
          setValue('role', userData.role);
          setValue('status', userData.status);
          
          // Clear password fields in edit mode
          setValue('password', '');
          setValue('confirm_password', '');
          
        } catch (error) {
          console.error('Error fetching user:', error);
          addToast({
            type: 'error',
            title: 'Failed to load user',
            message: error.response?.data?.message || 'An error occurred while loading user data.',
          });
          
          // Navigate back to users list on error
          navigate('/users');
        } finally {
          setIsFetching(false);
        }
      };
      
      fetchUser();
    }
  }, [id, isEditMode, setValue, navigate, addToast]);
  
  // Handle form submission
  const onSubmit = async (data) => {
    try {
      setIsLoading(true);
      
      // For edit mode, only include password if provided
      if (isEditMode && !data.password) {
        delete data.password;
        delete data.confirm_password;
      }
      
      // Remove confirm_password field
      const { confirm_password, ...userData } = data;
      
      let response;
      if (isEditMode) {
        // Update existing user
        response = await api.put(`/api/users/${id}`, userData);
      } else {
        // Create new user
        response = await api.post('/api/users', userData);
      }
      
      // Handle profile picture upload if provided
      if (uploadedImage && response.data.id) {
        const formData = new FormData();
        formData.append('profile_picture', uploadedImage);
        
        await api.post(`/api/users/${response.data.id}/profile-picture`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
      }
      
      // Show success message
      addToast({
        type: 'success',
        title: isEditMode ? 'User updated' : 'User created',
        message: isEditMode
          ? `${data.first_name} ${data.last_name}'s information has been updated.`
          : `${data.first_name} ${data.last_name} has been created successfully.`,
      });
      
      // Navigate back to users list
      navigate('/users');
      
    } catch (error) {
      console.error(isEditMode ? 'Error updating user:' : 'Error creating user:', error);
      
      addToast({
        type: 'error',
        title: isEditMode ? 'Update failed' : 'Creation failed',
        message: error.response?.data?.message || `An error occurred while ${isEditMode ? 'updating' : 'creating'} the user.`,
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
          message: 'Please upload a JPEG, PNG, or GIF image.',
        });
        return;
      }
      
      if (file.size > maxSize) {
        addToast({
          type: 'error',
          title: 'File too large',
          message: 'Please upload an image smaller than 5MB.',
        });
        return;
      }
      
      // Set uploaded image
      setUploadedImage(file);
    }
  };
  
  // Loading state while fetching user data
  if (isFetching) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto py-8 px-4">
      <div className="mb-6">
        <Button
          variant="outline"
          onClick={() => navigate('/users')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Users
        </Button>
        
        <h1 className="text-2xl font-bold">{isEditMode ? 'Edit User' : 'Create User'}</h1>
        <p className="text-gray-600">
          {isEditMode 
            ? 'Update user information and permissions' 
            : 'Add a new user to the system'
          }
        </p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <CardContent className="pt-6">
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
              
              {isEditMode && (
                <div className="mt-6 pt-6 border-t">
                  <Alert type="info" title="Updating Password">
                    <p>Leave the password fields empty to keep the current password.</p>
                  </Alert>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
        
        {/* Main form */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>{isEditMode ? 'Edit User Information' : 'New User Information'}</CardTitle>
              <CardDescription>
                {isEditMode
                  ? 'Update the user details and role'
                  : 'Fill in the details to create a new user'
                }
              </CardDescription>
            </CardHeader>
            
            <form onSubmit={handleSubmit(onSubmit)}>
              <CardContent className="space-y-6">
                {/* Personal Information Section */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium">Personal Information</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormGroup>
                      <FormLabel htmlFor="first_name">First Name</FormLabel>
                      <Input
                        id="first_name"
                        placeholder="John"
                        leftIcon={<User className="h-4 w-4 text-gray-400" />}
                        error={errors.first_name?.message}
                        disabled={isLoading}
                        {...register('first_name')}
                      />
                    </FormGroup>
                    
                    <FormGroup>
                      <FormLabel htmlFor="last_name">Last Name</FormLabel>
                      <Input
                        id="last_name"
                        placeholder="Doe"
                        leftIcon={<User className="h-4 w-4 text-gray-400" />}
                        error={errors.last_name?.message}
                        disabled={isLoading}
                        {...register('last_name')}
                      />
                    </FormGroup>
                  </div>
                  
                  <FormGroup>
                    <FormLabel htmlFor="email">Email Address</FormLabel>
                    <Input
                      id="email"
                      type="email"
                      placeholder="johndoe@example.com"
                      leftIcon={<Mail className="h-4 w-4 text-gray-400" />}
                      error={errors.email?.message}
                      disabled={isLoading}
                      {...register('email')}
                    />
                  </FormGroup>
                  
                  <FormGroup>
                    <FormLabel htmlFor="phone">Phone Number (Optional)</FormLabel>
                    <Input
                      id="phone"
                      placeholder="+1 (555) 123-4567"
                      leftIcon={<Phone className="h-4 w-4 text-gray-400" />}
                      error={errors.phone?.message}
                      disabled={isLoading}
                      {...register('phone')}
                    />
                  </FormGroup>
                  
                  <FormGroup>
                    <FormLabel htmlFor="organization">Organization (Optional)</FormLabel>
                    <Input
                      id="organization"
                      placeholder="Company or Institution"
                      leftIcon={<Building className="h-4 w-4 text-gray-400" />}
                      error={errors.organization?.message}
                      disabled={isLoading}
                      {...register('organization')}
                    />
                  </FormGroup>
                </div>
                
                {/* Access and Permissions Section */}
                <div className="space-y-4 pt-4 border-t">
                  <h3 className="text-lg font-medium">Access & Permissions</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormGroup>
                      <FormLabel htmlFor="role">User Role</FormLabel>
                      <select
                        id="role"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        disabled={isLoading}
                        {...register('role')}
                      >
                        <option value="trainee">Trainee</option>
                        <option value="trainer">Trainer</option>
                        <option value="tenant_admin">Admin</option>
                        <option value="super_admin">Super Admin</option>
                      </select>
                      {errors.role?.message && (
                        <p className="text-sm text-red-500 mt-1">{errors.role.message}</p>
                      )}
                    </FormGroup>
                    
                    <FormGroup>
                      <FormLabel htmlFor="status">Account Status</FormLabel>
                      <select
                        id="status"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        disabled={isLoading}
                        {...register('status')}
                      >
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                        <option value="suspended">Suspended</option>
                      </select>
                      {errors.status?.message && (
                        <p className="text-sm text-red-500 mt-1">{errors.status.message}</p>
                      )}
                    </FormGroup>
                  </div>
                </div>
                
                {/* Password Section */}
                <div className="space-y-4 pt-4 border-t">
                  <h3 className="text-lg font-medium">
                    {isEditMode ? 'Change Password' : 'Set Password'}
                  </h3>
                  
                  <FormGroup>
                    <FormLabel htmlFor="password">
                      {isEditMode ? 'New Password' : 'Password'}
                    </FormLabel>
                    <Input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder={isEditMode ? '••••••••' : 'Create a strong password'}
                      leftIcon={<Lock className="h-4 w-4 text-gray-400" />}
                      rightIcon={
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="text-gray-400 hover:text-gray-500"
                        >
                          {showPassword ? 'Hide' : 'Show'}
                        </button>
                      }
                      error={errors.password?.message}
                      disabled={isLoading}
                      {...register('password')}
                    />
                    <FormHelper>
                      {isEditMode 
                        ? 'Leave empty to keep current password'
                        : 'Password must be at least 8 characters'
                      }
                    </FormHelper>
                  </FormGroup>
                  
                  <FormGroup>
                    <FormLabel htmlFor="confirm_password">Confirm Password</FormLabel>
                    <Input
                      id="confirm_password"
                      type={showConfirmPassword ? 'text' : 'password'}
                      placeholder="••••••••"
                      leftIcon={<Key className="h-4 w-4 text-gray-400" />}
                      rightIcon={
                        <button
                          type="button"
                          onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                          className="text-gray-400 hover:text-gray-500"
                        >
                          {showConfirmPassword ? 'Hide' : 'Show'}
                        </button>
                      }
                      error={errors.confirm_password?.message}
                      disabled={isLoading}
                      {...register('confirm_password')}
                    />
                  </FormGroup>
                </div>
              </CardContent>
              
              <CardFooter className="border-t pt-6 flex justify-between">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/users')}
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
                  {isEditMode ? 'Update User' : 'Create User'}
                </Button>
              </CardFooter>
            </form>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default UserFormPage;
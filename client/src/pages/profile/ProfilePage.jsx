import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { User, Mail, Phone, MapPin, Building, Save, X, Camera, Upload, Trash2, Lock } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ui/toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, FormGroup, FormLabel, FormControl, FormHelper } from '@/components/ui/form';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Tabs, TabsList, TabTrigger, TabContent } from '@/components/ui/tabs';
import { Avatar } from '@/components/ui/avatar';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '@/components/ui/modal';
import { Alert } from '@/components/ui/alert';
import api from '@/lib/api';
// Profile form validation schema
const profileSchema = z.object({
  first_name: z.string().min(2, 'First name must be at least 2 characters'),
  last_name: z.string().min(2, 'Last name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
  phone: z.string().optional(),
  address: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  zip_code: z.string().optional(),
  country: z.string().optional(),
  organization: z.string().optional(),
  bio: z.string().optional(),
  // Preferences
  email_notifications: z.boolean().optional(),
  push_notifications: z.boolean().optional(),
  sms_notifications: z.boolean().optional(),
  language: z.string().optional(),
  timezone: z.string().optional(),
  theme: z.string().optional(),
});
// Password change validation schema
const passwordSchema = z.object({
  current_password: z.string().min(1, 'Current password is required'),
  new_password: z.string().min(8, 'New password must be at least 8 characters'),
  confirm_password: z.string(),
})
.refine(data => data.new_password === data.confirm_password, {
  message: "Passwords don't match",
  path: ['confirm_password'],
});
/**
 * Profile page component
 */
const ProfilePage = () => {
  const { user, refreshToken } = useAuth();
  const { addToast } = useToast();
  // State management
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('personal');
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const [isDeleteAccountModalOpen, setIsDeleteAccountModalOpen] = useState(false);
  const [uploadedImage, setUploadedImage] = useState(null);
  // Form for profile data
  const { 
    register, 
    handleSubmit, 
    formState: { errors, isDirty },
    reset
  } = useForm({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      email: user?.email || '',
      phone: user?.phone || '',
      address: user?.address || '',
      city: user?.city || '',
      state: user?.state || '',
      zip_code: user?.zip_code || '',
      country: user?.country || '',
      organization: user?.organization || '',
      bio: user?.bio || '',
      // Preferences
      email_notifications: user?.email_notifications ?? true,
      push_notifications: user?.push_notifications ?? false,
      sms_notifications: user?.sms_notifications ?? false,
      language: user?.language || 'en',
      timezone: user?.timezone || 'UTC',
      theme: user?.theme || 'light',
    }
  });
  // Form for password change
  const { 
    register: registerPassword, 
    handleSubmit: handleSubmitPassword, 
    formState: { errors: passwordErrors },
    reset: resetPassword
  } = useForm({
    resolver: zodResolver(passwordSchema),
    defaultValues: {
      current_password: '',
      new_password: '',
      confirm_password: '',
    }
  });
  // Handle profile form submission
  const onSubmit = async (data) => {
    try {
      setIsLoading(true);
      // Upload profile picture if changed
      let profilePictureUrl = user?.profile_picture;
      if (uploadedImage) {
        const formData = new FormData();
        formData.append('profile_picture', uploadedImage);
        const uploadResponse = await api.post('/api/users/profile-picture', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        profilePictureUrl = uploadResponse.data.url;
      }
      // Update profile data
      const response = await api.patch('/api/users/me/profile', {
        ...data,
        profile_picture: profilePictureUrl,
      });
      // Show success message
      addToast({
        type: 'success',
        title: 'Profile updated',
        message: 'Your profile has been updated successfully.',
      });
      // Update form with new data
      // Merge the returned data with form data to keep all fields
      const updatedData = {
        ...data,  // Keep all submitted data
        ...(response.data.profile || response.data)  // Override with returned data
      };
      reset(updatedData);
      setUploadedImage(null);
      // Fetch updated user data
      const userResponse = await api.get('/api/users/me');
      if (userResponse.data) {
        // Update auth context with fresh data
        // Don't reset form here as it might lose data
      }
    } catch (err) {
      console.error('Profile update error:', err);
      addToast({
        type: 'error',
        title: 'Update failed',
        message: err.response?.data?.message || 'Failed to update profile. Please try again.',
      });
    } finally {
      setIsLoading(false);
    }
  };
  // Handle password change
  const handlePasswordChange = async (data) => {
    try {
      setIsLoading(true);
      // Call the change password API
      await api.post('/api/auth/change-password', {
        current_password: data.current_password,
        new_password: data.new_password,
      });
      // Show success message
      addToast({
        type: 'success',
        title: 'Password changed',
        message: 'Your password has been changed successfully.',
      });
      // Reset form and close modal
      resetPassword();
      setIsPasswordModalOpen(false);
    } catch (err) {
      console.error('Password change error:', err);
      addToast({
        type: 'error',
        title: 'Password change failed',
        message: err.response?.data?.message || 'Failed to change password. Please try again.',
      });
    } finally {
      setIsLoading(false);
    }
  };
  // Handle profile picture upload
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
  // Handle image removal
  const handleRemoveImage = () => {
    setUploadedImage(null);
  };
  return (
    <div className="container mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold mb-6">My Profile</h1>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col items-center text-center">
                <div className="relative mb-4 group">
                  <Avatar 
                    src={uploadedImage ? URL.createObjectURL(uploadedImage) : user?.profile_picture}
                    alt={user?.first_name}
                    initials={`${user?.first_name?.[0] || ''}${user?.last_name?.[0] || ''}`}
                    size="xl"
                    className="cursor-pointer"
                  />
                  <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 rounded-full opacity-0 group-hover:opacity-100 transition-opacity">
                    <label htmlFor="profile-picture" className="cursor-pointer p-2 text-white">
                      <Camera className="h-6 w-6" />
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
                  <div className="flex items-center space-x-2 mb-4">
                    <span className="text-sm text-muted-foreground">{uploadedImage.name}</span>
                    <button
                      type="button"
                      className="text-red-500 hover:text-red-700"
                      onClick={handleRemoveImage}
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                )}
                <h2 className="text-xl font-semibold">{user?.first_name} {user?.last_name}</h2>
                <p className="text-muted-foreground">{user?.email}</p>
                {user?.role && (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary bg-opacity-10 text-primary mt-2">
                    {user.role === 'trainee' ? 'Trainee' : 
                     user.role === 'trainer' ? 'Trainer' : 
                     user.role === 'tenant_admin' ? 'Admin' : 
                     user.role === 'super_admin' ? 'Super Admin' : user.role}
                  </span>
                )}
                {user?.organization && (
                  <p className="text-sm text-muted-foreground mt-2 flex items-center justify-center">
                    <Building className="h-4 w-4 mr-1" />
                    {user.organization}
                  </p>
                )}
              </div>
              <div className="mt-6 border-t pt-6">
                <Button
                  variant="outline"
                  className="w-full mb-3"
                  onClick={() => setIsPasswordModalOpen(true)}
                >
                  <Lock className="h-4 w-4 mr-2" />
                  Change Password
                </Button>
                <Button
                  variant="destructive"
                  className="w-full"
                  onClick={() => setIsDeleteAccountModalOpen(true)}
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete Account
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
        {/* Main content */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
              <CardDescription>
                Update your personal information and settings
              </CardDescription>
            </CardHeader>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <CardContent className="pb-0">
                <TabsList className="mb-6">
                  <TabTrigger value="personal">Personal Info</TabTrigger>
                  <TabTrigger value="address">Address</TabTrigger>
                  <TabTrigger value="preferences">Preferences</TabTrigger>
                </TabsList>
              </CardContent>
              <form onSubmit={handleSubmit(onSubmit)}>
                <TabContent value="personal">
                  <CardContent className="space-y-4">
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
                        placeholder="you@example.com"
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
                    <FormGroup>
                      <FormLabel htmlFor="organization">Organization</FormLabel>
                      <Input
                        id="organization"
                        placeholder="Your organization or institution"
                        leftIcon={<Building className="h-4 w-4 text-gray-400" />}
                        error={errors.organization?.message}
                        disabled={isLoading}
                        {...register('organization')}
                      />
                    </FormGroup>
                    <FormGroup>
                      <FormLabel htmlFor="bio">Bio</FormLabel>
                      <textarea
                        id="bio"
                        rows={4}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="Tell us about yourself"
                        disabled={isLoading}
                        {...register('bio')}
                      />
                      {errors.bio?.message && (
                        <p className="text-sm text-red-500 mt-1">{errors.bio.message}</p>
                      )}
                    </FormGroup>
                  </CardContent>
                </TabContent>
                <TabContent value="address">
                  <CardContent className="space-y-4">
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
                          placeholder="New York"
                          error={errors.city?.message}
                          disabled={isLoading}
                          {...register('city')}
                        />
                      </FormGroup>
                      <FormGroup>
                        <FormLabel htmlFor="state">State / Province</FormLabel>
                        <Input
                          id="state"
                          placeholder="NY"
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
                          placeholder="10001"
                          error={errors.zip_code?.message}
                          disabled={isLoading}
                          {...register('zip_code')}
                        />
                      </FormGroup>
                      <FormGroup>
                        <FormLabel htmlFor="country">Country</FormLabel>
                        <Input
                          id="country"
                          placeholder="United States"
                          error={errors.country?.message}
                          disabled={isLoading}
                          {...register('country')}
                        />
                      </FormGroup>
                    </div>
                  </CardContent>
                </TabContent>
                <TabContent value="preferences">
                  <CardContent className="space-y-6">
                    <div>
                      <h3 className="text-lg font-medium mb-4">Notification Preferences</h3>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between py-2">
                          <div>
                            <label className="font-medium">Email Notifications</label>
                            <p className="text-sm text-gray-500">Receive notifications via email</p>
                          </div>
                          <input
                            type="checkbox"
                            className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                            {...register('email_notifications')}
                          />
                        </div>
                        <div className="flex items-center justify-between py-2">
                          <div>
                            <label className="font-medium">Push Notifications</label>
                            <p className="text-sm text-gray-500">Receive push notifications in browser</p>
                          </div>
                          <input
                            type="checkbox"
                            className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                            {...register('push_notifications')}
                          />
                        </div>
                        <div className="flex items-center justify-between py-2">
                          <div>
                            <label className="font-medium">SMS Notifications</label>
                            <p className="text-sm text-gray-500">Receive notifications via SMS</p>
                          </div>
                          <input
                            type="checkbox"
                            className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                            {...register('sms_notifications')}
                          />
                        </div>
                      </div>
                    </div>
                    <div>
                      <h3 className="text-lg font-medium mb-4">Language & Region</h3>
                      <div className="space-y-4">
                        <FormGroup>
                          <FormLabel htmlFor="language">Language</FormLabel>
                          <select
                            id="language"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                            {...register('language')}
                          >
                            <option value="en">English</option>
                            <option value="fr">Français</option>
                            <option value="es">Español</option>
                            <option value="de">Deutsch</option>
                          </select>
                        </FormGroup>
                        <FormGroup>
                          <FormLabel htmlFor="timezone">Timezone</FormLabel>
                          <select
                            id="timezone"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                            {...register('timezone')}
                          >
                            <option value="UTC">UTC</option>
                            <option value="America/New_York">Eastern Time</option>
                            <option value="America/Chicago">Central Time</option>
                            <option value="America/Denver">Mountain Time</option>
                            <option value="America/Los_Angeles">Pacific Time</option>
                            <option value="Europe/London">London</option>
                            <option value="Europe/Paris">Paris</option>
                            <option value="Asia/Tokyo">Tokyo</option>
                          </select>
                        </FormGroup>
                      </div>
                    </div>
                    <div>
                      <h3 className="text-lg font-medium mb-4">Display Preferences</h3>
                      <div className="space-y-4">
                        <FormGroup>
                          <FormLabel htmlFor="theme">Theme</FormLabel>
                          <select
                            id="theme"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                            {...register('theme')}
                          >
                            <option value="light">Light</option>
                            <option value="dark">Dark</option>
                            <option value="system">System</option>
                          </select>
                        </FormGroup>
                      </div>
                    </div>
                  </CardContent>
                </TabContent>
                <CardFooter className="border-t pt-6">
                  <Button
                    type="submit"
                    className="ml-auto"
                    isLoading={isLoading}
                    disabled={isLoading || !isDirty && !uploadedImage}
                  >
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </Button>
                </CardFooter>
              </form>
            </Tabs>
          </Card>
        </div>
      </div>
      {/* Password Change Modal */}
      <Modal
        isOpen={isPasswordModalOpen}
        onClose={() => setIsPasswordModalOpen(false)}
        title="Change Password"
      >
        <form onSubmit={handleSubmitPassword(handlePasswordChange)}>
          <ModalHeader>
            <h3 className="text-lg font-medium">Change Password</h3>
          </ModalHeader>
          <ModalBody className="space-y-4">
            <FormGroup>
              <FormLabel htmlFor="current_password">Current Password</FormLabel>
              <Input
                id="current_password"
                type="password"
                placeholder="••••••••"
                error={passwordErrors.current_password?.message}
                disabled={isLoading}
                {...registerPassword('current_password')}
              />
            </FormGroup>
            <FormGroup>
              <FormLabel htmlFor="new_password">New Password</FormLabel>
              <Input
                id="new_password"
                type="password"
                placeholder="••••••••"
                error={passwordErrors.new_password?.message}
                disabled={isLoading}
                {...registerPassword('new_password')}
              />
              <FormHelper>
                Password must be at least 8 characters
              </FormHelper>
            </FormGroup>
            <FormGroup>
              <FormLabel htmlFor="confirm_password">Confirm New Password</FormLabel>
              <Input
                id="confirm_password"
                type="password"
                placeholder="••••••••"
                error={passwordErrors.confirm_password?.message}
                disabled={isLoading}
                {...registerPassword('confirm_password')}
              />
            </FormGroup>
          </ModalBody>
          <ModalFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsPasswordModalOpen(false)}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              isLoading={isLoading}
              disabled={isLoading}
            >
              Change Password
            </Button>
          </ModalFooter>
        </form>
      </Modal>
      {/* Delete Account Modal */}
      <Modal
        isOpen={isDeleteAccountModalOpen}
        onClose={() => setIsDeleteAccountModalOpen(false)}
        title="Delete Account"
      >
        <ModalHeader>
          <h3 className="text-lg font-medium text-red-600">Delete Account</h3>
        </ModalHeader>
        <ModalBody>
          <div className="space-y-4">
            <Alert type="error" title="Warning: This action cannot be undone">
              <p>You're about to delete your account. This will:</p>
              <ul className="list-disc list-inside mt-2">
                <li>Remove all your personal information</li>
                <li>Delete your profile data</li>
                <li>Cancel any active subscriptions</li>
                <li>Remove access to all services</li>
              </ul>
            </Alert>
            <div className="pt-2">
              <p className="text-sm text-gray-600">Please type <strong>delete my account</strong> to confirm:</p>
              <input
                type="text"
                className="w-full mt-2 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                placeholder="delete my account"
              />
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() => setIsDeleteAccountModalOpen(false)}
          >
            Cancel
          </Button>
          <Button
            type="button"
            variant="destructive"
          >
            Delete Account
          </Button>
        </ModalFooter>
      </Modal>
    </div>
  );
};
export default ProfilePage;
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Eye, EyeOff, Mail, Lock, User, UserPlus, Building } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ui/toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, FormGroup, FormLabel, FormControl, FormHelper, Select } from '@/components/ui/form';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
// Registration form validation schema
const createRegisterSchema = (t) => z.object({
  first_name: z.string().min(2, t('validation.firstName.min', { min: 2 })),
  last_name: z.string().min(2, t('validation.lastName.min', { min: 2 })),
  email: z.string().email(t('validation.email.invalid')),
  password: z.string().min(8, t('validation.password.min', { min: 8 })),
  confirm_password: z.string(),
  role: z.enum(['trainee', 'trainer']),
  organization: z.string().min(2, t('validation.organization.min', { min: 2 })).optional(),
})
.refine(data => data.password === data.confirm_password, {
  message: t('validation.password.mismatch'),
  path: ['confirm_password'],
});
/**
 * Register page component
 */
const RegisterPage = () => {
  const { t } = useTranslation();
  const { register: registerUser, error: authError } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  // Create schema with translations
  const registerSchema = createRegisterSchema(t);
  
  // React Hook Form with Zod validation
  const { 
    register, 
    handleSubmit, 
    watch,
    formState: { errors },
    reset
  } = useForm({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      first_name: '',
      last_name: '',
      email: '',
      password: '',
      confirm_password: '',
      role: 'trainee',
      organization: '',
    }
  });
  // Get current role from form
  const currentRole = watch('role');
  // Handle form submission
  const onSubmit = async (data) => {
    try {
      setIsLoading(true);
      // Prepare user data - omit confirm_password
      const { confirm_password, ...userData } = data;
      // Register user
      const user = await registerUser(userData);
      addToast({
        type: 'success',
        title: 'Registration successful',
        message: `Welcome, ${user.first_name}!`,
      });
      // Reset form
      reset();
      // Redirect to dashboard
      navigate('/', { replace: true });
    } catch (err) {
      console.error('Registration error:', err);
      addToast({
        type: 'error',
        title: 'Registration failed',
        message: err.response?.data?.message || 'Failed to register. Please try again.',
      });
    } finally {
      setIsLoading(false);
    }
  };
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-lg">
        <div className="text-center mb-10">
          <div className="inline-block">
            <div className="w-12 h-12 mx-auto bg-primary rounded-md flex items-center justify-center">
              <span className="text-white font-bold text-2xl">B</span>
            </div>
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">Create your account</h2>
          <p className="mt-2 text-sm text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-primary hover:text-primary-dark">
              Sign in
            </Link>
          </p>
        </div>
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">Join BDC</CardTitle>
            <CardDescription>
              Enter your information to create an account
            </CardDescription>
          </CardHeader>
          <form onSubmit={handleSubmit(onSubmit)}>
            <CardContent className="space-y-4">
              {/* Name fields */}
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
              {/* Email */}
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
              {/* Password */}
              <FormGroup>
                <FormLabel htmlFor="password">Password</FormLabel>
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  leftIcon={<Lock className="h-4 w-4 text-gray-400" />}
                  rightIcon={
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="text-gray-400 hover:text-gray-500"
                    >
                      {showPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  }
                  error={errors.password?.message}
                  disabled={isLoading}
                  {...register('password')}
                />
                <FormHelper>
                  Password must be at least 8 characters
                </FormHelper>
              </FormGroup>
              {/* Confirm Password */}
              <FormGroup>
                <FormLabel htmlFor="confirm_password">Confirm Password</FormLabel>
                <Input
                  id="confirm_password"
                  type={showConfirmPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  leftIcon={<Lock className="h-4 w-4 text-gray-400" />}
                  rightIcon={
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="text-gray-400 hover:text-gray-500"
                    >
                      {showConfirmPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  }
                  error={errors.confirm_password?.message}
                  disabled={isLoading}
                  {...register('confirm_password')}
                />
              </FormGroup>
              {/* Role Selection */}
              <FormGroup>
                <FormLabel htmlFor="role">I am a</FormLabel>
                <Select
                  id="role"
                  error={errors.role?.message}
                  disabled={isLoading}
                  {...register('role')}
                >
                  <option value="trainee">Trainee / Student</option>
                  <option value="trainer">Trainer / Instructor</option>
                </Select>
              </FormGroup>
              {/* Organization field (only for trainers) */}
              {currentRole === 'trainer' && (
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
              )}
              <div className="flex items-center pt-2">
                <input
                  id="terms"
                  name="terms"
                  type="checkbox"
                  className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                  required
                />
                <label htmlFor="terms" className="ml-2 block text-sm text-gray-900">
                  I agree to the{' '}
                  <Link to="/terms" className="font-medium text-primary hover:text-primary-dark">
                    Terms of Service
                  </Link>
                  {' '}and{' '}
                  <Link to="/privacy" className="font-medium text-primary hover:text-primary-dark">
                    Privacy Policy
                  </Link>
                </label>
              </div>
            </CardContent>
            <CardFooter>
              <Button
                type="submit"
                className="w-full"
                isLoading={isLoading}
                disabled={isLoading}
              >
                <UserPlus className="h-4 w-4 mr-2" />
                Create Account
              </Button>
            </CardFooter>
          </form>
        </Card>
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-primary hover:text-primary-dark">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};
export default RegisterPage;
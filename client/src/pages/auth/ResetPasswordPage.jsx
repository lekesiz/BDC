import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Lock, Eye, EyeOff, Check, ArrowLeft } from 'lucide-react';

import { useToast } from '@/components/ui/toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import api from '@/lib/api';

// Validation schema
const resetPasswordSchema = z.object({
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirm_password: z.string(),
})
.refine(data => data.password === data.confirm_password, {
  message: "Passwords don't match",
  path: ['confirm_password'],
});

/**
 * Reset Password page component
 */
const ResetPasswordPage = () => {
  const { addToast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Get token from URL params
  const searchParams = new URLSearchParams(location.search);
  const token = searchParams.get('token');
  
  const [isLoading, setIsLoading] = useState(false);
  const [isTokenValid, setIsTokenValid] = useState(false);
  const [isTokenChecking, setIsTokenChecking] = useState(true);
  const [isResetComplete, setIsResetComplete] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  // React Hook Form with Zod validation
  const { 
    register, 
    handleSubmit, 
    formState: { errors },
    reset
  } = useForm({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      password: '',
      confirm_password: '',
    }
  });
  
  // Verify token on mount
  useEffect(() => {
    const verifyToken = async () => {
      try {
        setIsTokenChecking(true);
        
        if (!token) {
          setIsTokenValid(false);
          addToast({
            type: 'error',
            title: 'Invalid token',
            message: 'The password reset link is invalid or has expired.',
          });
          return;
        }
        
        // Call API to verify token
        await api.get(`/api/auth/verify-reset-token?token=${token}`);
        
        // If no error, token is valid
        setIsTokenValid(true);
      } catch (err) {
        console.error('Token verification error:', err);
        
        setIsTokenValid(false);
        addToast({
          type: 'error',
          title: 'Invalid token',
          message: 'The password reset link is invalid or has expired.',
        });
      } finally {
        setIsTokenChecking(false);
      }
    };
    
    verifyToken();
  }, [token, addToast]);
  
  // Handle form submission
  const onSubmit = async (data) => {
    try {
      setIsLoading(true);
      
      // Call the reset password API
      await api.post('/api/auth/reset-password', {
        token,
        password: data.password,
      });
      
      // Show success message
      addToast({
        type: 'success',
        title: 'Password reset successful',
        message: 'Your password has been reset successfully.',
      });
      
      // Update UI state
      setIsResetComplete(true);
      
      // Reset form
      reset();
    } catch (err) {
      console.error('Password reset error:', err);
      
      addToast({
        type: 'error',
        title: 'Password reset failed',
        message: err.response?.data?.message || 'Failed to reset password. Please try again.',
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Redirect to login if completed
  const handleLoginClick = () => {
    navigate('/login');
  };
  
  // Show loading state
  if (isTokenChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-md text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600">Verifying your reset link...</p>
        </div>
      </div>
    );
  }
  
  // Show error for invalid token
  if (!isTokenValid) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-md">
          <div className="text-center mb-10">
            <div className="inline-block">
              <div className="w-12 h-12 mx-auto bg-primary rounded-md flex items-center justify-center">
                <span className="text-white font-bold text-2xl">B</span>
              </div>
            </div>
            <h2 className="mt-6 text-3xl font-extrabold text-gray-900">Invalid Reset Link</h2>
          </div>
          
          <Card>
            <CardContent className="pt-6 pb-4 space-y-4">
              <div className="bg-red-50 p-4 rounded-md border border-red-100">
                <h3 className="text-sm font-medium text-red-800">Invalid or expired link</h3>
                <p className="mt-1 text-sm text-red-700">
                  The password reset link is invalid or has expired. Please request a new link.
                </p>
              </div>
            </CardContent>
            
            <CardFooter>
              <Link to="/forgot-password" className="w-full">
                <Button className="w-full">
                  Request new reset link
                </Button>
              </Link>
            </CardFooter>
          </Card>
          
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              <Link to="/login" className="font-medium text-primary hover:text-primary-dark inline-flex items-center">
                <ArrowLeft className="h-4 w-4 mr-1" />
                Return to login
              </Link>
            </p>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md">
        <div className="text-center mb-10">
          <div className="inline-block">
            <div className="w-12 h-12 mx-auto bg-primary rounded-md flex items-center justify-center">
              <span className="text-white font-bold text-2xl">B</span>
            </div>
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">Reset your password</h2>
          <p className="mt-2 text-sm text-gray-600">
            <Link to="/login" className="font-medium text-primary hover:text-primary-dark inline-flex items-center">
              <ArrowLeft className="h-4 w-4 mr-1" />
              Back to login
            </Link>
          </p>
        </div>
        
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">Create new password</CardTitle>
            <CardDescription>
              Enter your new password below to reset your account.
            </CardDescription>
          </CardHeader>
          
          {isResetComplete ? (
            <CardContent className="space-y-4">
              <div className="bg-green-50 p-4 rounded-md border border-green-100 flex items-start">
                <div className="flex-shrink-0">
                  <Check className="h-5 w-5 text-green-500" />
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-green-800">Success!</h3>
                  <p className="mt-1 text-sm text-green-700">
                    Your password has been reset successfully. You can now log in with your new password.
                  </p>
                </div>
              </div>
              
              <Button
                className="w-full mt-4"
                onClick={handleLoginClick}
              >
                Go to login
              </Button>
            </CardContent>
          ) : (
            <form onSubmit={handleSubmit(onSubmit)}>
              <CardContent className="space-y-4">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  label="New Password"
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
                
                <Input
                  id="confirm_password"
                  type={showConfirmPassword ? 'text' : 'password'}
                  label="Confirm Password"
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
              </CardContent>
              
              <CardFooter>
                <Button
                  type="submit"
                  className="w-full"
                  isLoading={isLoading}
                  disabled={isLoading}
                >
                  Reset password
                </Button>
              </CardFooter>
            </form>
          )}
        </Card>
      </div>
    </div>
  );
};

export default ResetPasswordPage;
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Mail, ArrowLeft } from 'lucide-react';

import { useToast } from '@/components/ui/toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import api from '@/lib/api';

// Validation schema
const forgotPasswordSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
});

/**
 * Forgot Password page component
 */
const ForgotPasswordPage = () => {
  const { addToast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [isEmailSent, setIsEmailSent] = useState(false);
  
  // React Hook Form with Zod validation
  const { 
    register, 
    handleSubmit, 
    formState: { errors },
    reset
  } = useForm({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: {
      email: '',
    }
  });
  
  // Handle form submission
  const onSubmit = async (data) => {
    try {
      setIsLoading(true);
      
      // Call the forgot password API
      await api.post('/api/auth/forgot-password', {
        email: data.email,
      });
      
      // Show success message
      addToast({
        type: 'success',
        title: 'Email sent',
        message: 'If an account exists with this email, a password reset link has been sent.',
      });
      
      // Update UI state
      setIsEmailSent(true);
      
      // Reset form
      reset();
    } catch (err) {
      console.error('Forgot password error:', err);
      
      // We don't want to reveal if the email exists or not for security reasons
      // So we show a success message even if the API call fails
      addToast({
        type: 'success',
        title: 'Email sent',
        message: 'If an account exists with this email, a password reset link has been sent.',
      });
      
      // Update UI state
      setIsEmailSent(true);
    } finally {
      setIsLoading(false);
    }
  };
  
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
            <CardTitle className="text-xl">Forgot your password?</CardTitle>
            <CardDescription>
              Enter your email address and we'll send you a link to reset your password.
            </CardDescription>
          </CardHeader>
          
          {isEmailSent ? (
            <CardContent className="space-y-4">
              <div className="bg-green-50 p-4 rounded-md border border-green-100">
                <h3 className="text-sm font-medium text-green-800">Check your email</h3>
                <p className="mt-1 text-sm text-green-700">
                  We've sent a password reset link to your email address. Please check your inbox and spam folder.
                </p>
              </div>
              
              <div className="text-center mt-4">
                <p className="text-sm text-gray-600">
                  Didn't receive the email?{' '}
                  <button
                    type="button"
                    className="font-medium text-primary hover:text-primary-dark"
                    onClick={() => setIsEmailSent(false)}
                  >
                    Try again
                  </button>
                </p>
              </div>
            </CardContent>
          ) : (
            <form onSubmit={handleSubmit(onSubmit)}>
              <CardContent className="space-y-4">
                <Input
                  id="email"
                  type="email"
                  label="Email address"
                  placeholder="you@example.com"
                  leftIcon={<Mail className="h-4 w-4 text-gray-400" />}
                  error={errors.email?.message}
                  disabled={isLoading}
                  {...register('email')}
                />
              </CardContent>
              
              <CardFooter>
                <Button
                  type="submit"
                  className="w-full"
                  isLoading={isLoading}
                  disabled={isLoading}
                >
                  Send reset link
                </Button>
              </CardFooter>
            </form>
          )}
        </Card>
        
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Remember your password?{' '}
            <Link to="/login" className="font-medium text-primary hover:text-primary-dark">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;
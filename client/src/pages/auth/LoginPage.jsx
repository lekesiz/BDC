import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Eye, EyeOff, Mail, Lock, LogIn } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ui/toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, FormGroup, FormLabel, FormControl, FormHelper } from '@/components/ui/form';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';

// Login form validation schema
const createLoginSchema = (t) => z.object({
  email: z.string().email(t('validation.email.invalid')),
  password: z.string().min(1, t('validation.password.required')),
});

/**
 * Login page component
 */
const LoginPage = () => {
  const { t } = useTranslation();
  const { login } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  const from = location.state?.from?.pathname || '/';

  // React Hook Form with Zod validation
  const { 
    register, 
    handleSubmit, 
    formState: { errors },
    reset
  } = useForm({
    resolver: zodResolver(createLoginSchema(t)),
    defaultValues: {
      email: '',
      password: '',
    }
  });

  // Handle form submission
  const onSubmit = async (data) => {
    try {
      setIsLoading(true);
      
      const user = await login(data.email, data.password, rememberMe);
      
      addToast({
        type: 'success',
        title: t('components.auth.login_success'),
        message: t('components.auth.welcome_back', { name: user.first_name }),
      });

      // Reset form
      reset();

      // Redirect based on role
      const redirectPath = getRedirectPath(user, from);
      navigate(redirectPath, { replace: true });
    } catch (err) {
      console.error('Login error:', err);
      
      addToast({
        type: 'error',
        title: t('components.auth.login_failed'),
        message: err.response?.data?.message || t('components.auth.check_credentials'),
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Helper function to determine redirect path based on role
  const getRedirectPath = (user, from) => {
    // If there's a specific 'from' location, use it (unless it's the login page)
    if (from && from !== '/login') {
      return from;
    }
    
    // Otherwise, redirect based on role
    switch (user.role) {
      case 'student':
        return '/portal';
      case 'super_admin':
      case 'tenant_admin':
      case 'trainer':
        return '/';
      default:
        return '/';
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
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">{t('components.auth.login_title')}</h2>
          <p className="mt-2 text-sm text-gray-600">
            {t('components.auth.dont_have_account')}{' '}
            <Link to="/register" className="font-medium text-primary hover:text-primary-dark">
              {t('components.auth.sign_up')}
            </Link>
          </p>
        </div>

        <Card>
          <CardContent className="pt-6">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <FormGroup>
                <FormLabel htmlFor="email">{t('components.auth.email')}</FormLabel>
                <FormControl>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <Input
                      {...register('email')}
                      id="email"
                      type="email"
                      autoComplete="email"
                      className="pl-10"
                      placeholder={t('components.auth.email')}
                      error={errors.email}
                    />
                  </div>
                </FormControl>
                {errors.email && (
                  <FormHelper variant="error">{errors.email.message}</FormHelper>
                )}
              </FormGroup>

              <FormGroup>
                <FormLabel htmlFor="password">{t('components.auth.password')}</FormLabel>
                <FormControl>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <Input
                      {...register('password')}
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      autoComplete="current-password"
                      className="pl-10 pr-10"
                      placeholder={t('components.auth.password')}
                      error={errors.password}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      tabIndex={-1}
                    >
                      {showPassword ? (
                        <EyeOff className="h-5 w-5" />
                      ) : (
                        <Eye className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                </FormControl>
                {errors.password && (
                  <FormHelper variant="error">{errors.password.message}</FormHelper>
                )}
              </FormGroup>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    id="remember-me"
                    name="remember-me"
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                  />
                  <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700">
                    {t('components.auth.remember_me')}
                  </label>
                </div>

                <div className="text-sm">
                  <Link to="/forgot-password" className="font-medium text-primary hover:text-primary-dark">
                    {t('components.auth.forgot_password')}
                  </Link>
                </div>
              </div>

              <Button
                type="submit"
                className="w-full"
                size="lg"
                disabled={isLoading}
              >
                {isLoading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Loading...
                  </span>
                ) : (
                  <>
                    <LogIn className="h-5 w-5 mr-2" />
                    {t('components.auth.sign_in')}
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        <p className="mt-6 text-center text-sm text-gray-500">
          {t('components.auth.back_to_login')}{' '}
          <Link to="/" className="font-medium text-primary hover:text-primary-dark">
            {t('components.navigation.home')}
          </Link>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
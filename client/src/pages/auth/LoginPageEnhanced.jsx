import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock } from 'lucide-react';

import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ui/toast';
import { AnimatedButton, AnimatedForm, AnimatedInput, AnimatedCheckbox } from '@/components/animations';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { motion } from 'framer-motion';
import { fadeInUp } from '@/lib/animations';

/**
 * Enhanced login page component with proper role-based redirects
 */
const LoginPageEnhanced = () => {
  const { login, error: authError } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  
  // Destination after login (redirect or default based on role)
  const from = location.state?.from;
  
  // Validate form
  const validateForm = () => {
    const newErrors = {};
    
    if (!email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!password.trim()) {
      newErrors.password = 'Password is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  // Get redirect path based on user role
  const getRoleBasedRedirect = (user) => {
    // If there's a specific redirect path, use it
    if (from) {
      return from;
    }
    
    // Otherwise, redirect based on role
    switch (user.role) {
      case 'student':
        return '/portal';
      case 'super_admin':
      case 'tenant_admin':
      case 'trainer':
        return '/dashboard';
      default:
        return '/';
    }
  };
  
  // Handle login
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsLoading(true);
    
    try {
      const response = await login(email, password, remember);
      
      if (response.user) {
        // Success!
        addToast('Login successful!', { type: 'success' });
        
        // Redirect based on role
        const redirectPath = getRoleBasedRedirect(response.user);
        navigate(redirectPath, { replace: true });
      }
    } catch (err) {
      addToast(
        authError || err.message || 'Failed to login',
        { type: 'error' }
      );
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-4">
      <motion.div
        className="w-full max-w-md"
        initial="hidden"
        animate="visible"
        variants={fadeInUp}
      >
        <Card>
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-bold text-center">
              Welcome back
            </CardTitle>
            <CardDescription className="text-center">
              Sign in to your account to continue
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            <AnimatedForm onSubmit={handleSubmit} className="space-y-4">
              {/* Email field */}
              <div>
                <AnimatedInput
                  type="email"
                  placeholder="Email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  onFocus={() => {
                    const newErrors = { ...errors };
                    delete newErrors.email;
                    setErrors(newErrors);
                  }}
                  className={errors.email ? 'border-red-500' : ''}
                  icon={<Mail className="h-4 w-4" />}
                  disabled={isLoading}
                  autoComplete="email"
                />
                {errors.email && (
                  <p className="text-red-500 text-xs mt-1">{errors.email}</p>
                )}
              </div>
              
              {/* Password field */}
              <div>
                <AnimatedInput
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onFocus={() => {
                    const newErrors = { ...errors };
                    delete newErrors.password;
                    setErrors(newErrors);
                  }}
                  className={errors.password ? 'border-red-500' : ''}
                  icon={<Lock className="h-4 w-4" />}
                  disabled={isLoading}
                  autoComplete="current-password"
                  rightIcon={
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="focus:outline-none hover:text-gray-700"
                      tabIndex={-1}
                    >
                      {showPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  }
                />
                {errors.password && (
                  <p className="text-red-500 text-xs mt-1">{errors.password}</p>
                )}
              </div>
              
              {/* Remember me & Forgot password */}
              <div className="flex items-center justify-between">
                <AnimatedCheckbox
                  label="Remember me"
                  checked={remember}
                  onChange={setRemember}
                  disabled={isLoading}
                />
                
                <Link
                  to="/forgot-password"
                  className="text-sm text-primary hover:underline transition-colors"
                >
                  Forgot password?
                </Link>
              </div>
              
              {/* Submit button */}
              <AnimatedButton
                type="submit"
                className="w-full"
                isLoading={isLoading}
                loadingText="Signing in..."
              >
                Sign in
              </AnimatedButton>
            </AnimatedForm>
            
            {/* OAuth options */}
            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">
                    Or continue with
                  </span>
                </div>
              </div>
              
              <div className="mt-6 grid grid-cols-2 gap-3">
                <AnimatedButton
                  type="button"
                  variant="outline"
                  className="w-full"
                  disabled={isLoading}
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path
                      fill="currentColor"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="currentColor"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="currentColor"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    />
                    <path
                      fill="currentColor"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    />
                  </svg>
                  <span className="ml-2">Google</span>
                </AnimatedButton>
                
                <AnimatedButton
                  type="button"
                  variant="outline"
                  className="w-full"
                  disabled={isLoading}
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                  </svg>
                  <span className="ml-2">GitHub</span>
                </AnimatedButton>
              </div>
            </div>
          </CardContent>
          
          <CardFooter className="flex justify-center">
            <p className="text-center text-sm text-gray-600">
              Don't have an account?{' '}
              <Link
                to="/register"
                className="font-medium text-primary hover:underline transition-colors"
              >
                Sign up
              </Link>
            </p>
          </CardFooter>
        </Card>
        
        {/* Debug info in development */}
        {process.env.NODE_ENV === 'development' && (
          <div className="mt-4 text-xs text-gray-500 text-center">
            <p>Test accounts:</p>
            <p>admin@bdc.com / Admin123!</p>
            <p>tenant@bdc.com / Tenant123!</p>
            <p>trainer@bdc.com / Trainer123!</p>
            <p>student@bdc.com / Student123!</p>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default LoginPageEnhanced;
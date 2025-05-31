import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock } from 'lucide-react';
import { useBreakpoint } from '@/hooks/useMediaQuery';

import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ui/toast';
import { AnimatedButton, AnimatedForm, AnimatedInput, AnimatedCheckbox } from '@/components/animations';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { motion } from 'framer-motion';
import { fadeInUp } from '@/lib/animations';

/**
 * Login page component
 */
const LoginPage = () => {
  const { login, error: authError } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const { isMobile } = useBreakpoint();
  
  // Form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  
  // Destination after login (redirect or default to dashboard)
  const from = location.state?.from || '/';
  
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
  const getRedirectPath = (user, from) => {
    // If there's a specific 'from' location, use it (unless it's the login page)
    if (from && from !== '/login' && from !== '/') {
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
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    try {
      setIsLoading(true);
      
      const result = await login(email, password, remember);
      
      if (result.success) {
        addToast({
          type: 'success',
          title: 'Login successful',
          message: `Welcome back, ${result.user.first_name}!`,
        });
        
        // Use role-based redirect
        const redirectPath = getRedirectPath(result.user, from);
        navigate(redirectPath, { replace: true });
      } else {
        throw new Error(result.error);
      }
    } catch (err) {
      console.error('Login error:', err);
      
      addToast({
        type: 'error',
        title: 'Login failed',
        message: err.response?.data?.message || 'Failed to login. Please check your credentials.',
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-6 sm:py-12 px-4 sm:px-6 lg:px-8">
      <motion.div 
        className="w-full max-w-md"
        initial={{ opacity: 0, y: isMobile ? 10 : 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: isMobile ? 0.3 : 0.5 }}
      >
        <motion.div 
          className="text-center mb-6 sm:mb-10"
          initial={{ opacity: 0, y: isMobile ? -10 : -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: isMobile ? 0.3 : 0.5 }}
        >
          <div className="inline-block">
            <motion.div 
              className="w-12 h-12 sm:w-14 sm:h-14 mx-auto bg-primary dark:bg-primary-dark rounded-md flex items-center justify-center"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            >
              <span className="text-white font-bold text-2xl sm:text-3xl">B</span>
            </motion.div>
          </div>
          <h2 className="mt-4 sm:mt-6 text-2xl sm:text-3xl font-extrabold text-gray-900 dark:text-gray-100">Sign in to your account</h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Or{' '}
            <Link to="/register" className="font-medium text-primary dark:text-primary-light hover:text-primary-dark dark:hover:text-primary">
              create a new account
            </Link>
          </p>
        </motion.div>
        
        <motion.div
          variants={fadeInUp}
          initial="initial"
          animate="animate"
          transition={{ delay: 0.3 }}
        >
          <Card className="border-0 sm:border shadow-xl sm:shadow-sm">
          <CardHeader className="space-y-1 px-4 sm:px-6">
            <CardTitle className="text-lg sm:text-xl">Welcome back</CardTitle>
            <CardDescription className="text-sm">
              Enter your credentials to access your account
            </CardDescription>
          </CardHeader>
          
          <AnimatedForm onSubmit={handleSubmit}>
            <CardContent className="space-y-4 px-4 sm:px-6 pb-4 sm:pb-6">
              <AnimatedInput
                id="email"
                type="email"
                label="Email address"
                placeholder="you@example.com"
                autoComplete="username"
                leftIcon={<Mail className="h-4 w-4 text-gray-400" />}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                error={errors.email}
                disabled={isLoading}
                required
                className="min-h-[44px]"
                inputMode="email"
              />
              
              <AnimatedInput
                id="password"
                type={showPassword ? 'text' : 'password'}
                label="Password"
                placeholder="••••••••"
                autoComplete="current-password"
                leftIcon={<Lock className="h-4 w-4 text-gray-400" />}
                rightIcon={
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="p-2 -m-2 text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary rounded"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                }
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                error={errors.password}
                disabled={isLoading}
                required
                className="min-h-[44px]"
              />
              
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <AnimatedCheckbox
                  id="remember-me"
                  name="remember-me"
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                  label="Remember me"
                  className="min-h-[44px]"
                />
                
                <div className="text-sm text-center sm:text-right">
                  <Link to="/forgot-password" className="font-medium text-primary dark:text-primary-light hover:text-primary-dark dark:hover:text-primary">
                    Forgot your password?
                  </Link>
                </div>
              </div>
            </CardContent>
            
            <CardFooter className="px-4 sm:px-6 pb-6">
              <AnimatedButton
                type="submit"
                className="w-full min-h-[44px] text-base sm:text-sm"
                isLoading={isLoading}
                disabled={isLoading}
              >
                Sign in
              </AnimatedButton>
            </CardFooter>
          </AnimatedForm>
        </Card>
        
        <motion.div 
          className="mt-4 sm:mt-6 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: isMobile ? 0.3 : 0.5 }}
        >
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Don't have an account?{' '}
            <Link to="/register" className="font-medium text-primary dark:text-primary-light hover:text-primary-dark dark:hover:text-primary">
              Sign up
            </Link>
          </p>
        </motion.div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default LoginPage;
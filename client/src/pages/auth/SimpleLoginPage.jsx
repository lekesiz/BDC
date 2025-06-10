import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ui/toast';
import { Button } from '@/components/ui/button';

/**
 * Simple login page for testing purposes
 */
const SimpleLoginPage = () => {
  const { login } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const handleQuickLogin = async (email, role) => {
    try {
      const user = await login(email, 'password123', false);
      
      addToast({
        type: 'success',
        title: 'Login successful',
        message: `Logged in as ${role}`,
      });

      // Redirect based on role
      if (role === 'student') {
        navigate('/portal', { replace: true });
      } else {
        navigate('/', { replace: true });
      }
    } catch (err) {
      console.error('Login error:', err);
      
      addToast({
        type: 'error',
        title: 'Login failed',
        message: err.response?.data?.message || 'Failed to login',
      });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-extrabold text-gray-900">Quick Login (Test Only)</h2>
          <p className="mt-2 text-sm text-gray-600">
            Select a test account to login
          </p>
        </div>

        <div className="space-y-4">
          <Button
            onClick={() => handleQuickLogin('admin@example.com', 'admin')}
            className="w-full"
            size="lg"
          >
            Login as Admin
          </Button>
          
          <Button
            onClick={() => handleQuickLogin('trainer@example.com', 'trainer')}
            className="w-full"
            size="lg"
            variant="secondary"
          >
            Login as Trainer
          </Button>
          
          <Button
            onClick={() => handleQuickLogin('student@example.com', 'student')}
            className="w-full"
            size="lg"
            variant="outline"
          >
            Login as Student
          </Button>
        </div>

        <div className="mt-6 text-center">
          <a href="/login" className="text-sm text-primary hover:text-primary-dark">
            Go to regular login
          </a>
        </div>
      </div>
    </div>
  );
};

export default SimpleLoginPage;
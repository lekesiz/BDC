import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { AlertCircle, Mail, CheckCircle, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from '@/components/ui/use-toast';
import api from '@/lib/api';

export function EmailVerificationBanner() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [isResending, setIsResending] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);

  // Don't show if user is verified or not logged in
  if (!user || user.email_verified) {
    return null;
  }

  const handleResendVerification = async () => {
    try {
      setIsResending(true);
      const response = await api.post('/auth/resend-verification');
      
      if (response.data.success) {
        toast({
          title: t('email_verification.resend_success'),
          description: t('email_verification.check_inbox'),
        });
        
        // Set cooldown
        setResendCooldown(60);
        const interval = setInterval(() => {
          setResendCooldown((prev) => {
            if (prev <= 1) {
              clearInterval(interval);
              return 0;
            }
            return prev - 1;
          });
        }, 1000);
      }
    } catch (error) {
      toast({
        title: t('email_verification.resend_error'),
        description: error.response?.data?.message || t('common.error_occurred'),
        variant: 'destructive',
      });
    } finally {
      setIsResending(false);
    }
  };

  return (
    <Alert className="mb-4 border-yellow-200 bg-yellow-50">
      <AlertCircle className="h-4 w-4 text-yellow-600" />
      <AlertDescription className="flex items-center justify-between">
        <div>
          <span className="text-yellow-800">
            {t('email_verification.banner_message')}
          </span>
          <span className="ml-2 text-sm text-yellow-600">
            ({user.email})
          </span>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleResendVerification}
          disabled={isResending || resendCooldown > 0}
          className="ml-4"
        >
          <Mail className="mr-2 h-4 w-4" />
          {resendCooldown > 0
            ? t('email_verification.resend_cooldown', { seconds: resendCooldown })
            : t('email_verification.resend_email')}
        </Button>
      </AlertDescription>
    </Alert>
  );
}

export function EmailVerificationPage() {
  const { t } = useTranslation();
  const [verifying, setVerifying] = useState(false);
  const [verificationStatus, setVerificationStatus] = useState(null);
  
  // Get token from URL
  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get('token');

  React.useEffect(() => {
    if (token) {
      verifyEmail();
    }
  }, [token]);

  const verifyEmail = async () => {
    try {
      setVerifying(true);
      const response = await api.get(`/auth/verify-email/${token}`);
      
      if (response.data.success) {
        setVerificationStatus('success');
        toast({
          title: t('email_verification.success_title'),
          description: t('email_verification.success_message'),
        });
        
        // Redirect to login after 3 seconds
        setTimeout(() => {
          window.location.href = '/login';
        }, 3000);
      }
    } catch (error) {
      setVerificationStatus('error');
      toast({
        title: t('email_verification.error_title'),
        description: error.response?.data?.message || t('email_verification.error_message'),
        variant: 'destructive',
      });
    } finally {
      setVerifying(false);
    }
  };

  if (!token) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <XCircle className="mx-auto h-12 w-12 text-red-500" />
          <h2 className="mt-4 text-lg font-semibold">
            {t('email_verification.invalid_link')}
          </h2>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-md space-y-8 p-8">
        <div className="text-center">
          {verifying && (
            <>
              <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600" />
              <h2 className="mt-4 text-lg font-semibold">
                {t('email_verification.verifying')}
              </h2>
            </>
          )}
          
          {!verifying && verificationStatus === 'success' && (
            <>
              <CheckCircle className="mx-auto h-12 w-12 text-green-500" />
              <h2 className="mt-4 text-lg font-semibold text-green-700">
                {t('email_verification.success_title')}
              </h2>
              <p className="mt-2 text-sm text-gray-600">
                {t('email_verification.redirecting')}
              </p>
            </>
          )}
          
          {!verifying && verificationStatus === 'error' && (
            <>
              <XCircle className="mx-auto h-12 w-12 text-red-500" />
              <h2 className="mt-4 text-lg font-semibold text-red-700">
                {t('email_verification.error_title')}
              </h2>
              <p className="mt-2 text-sm text-gray-600">
                {t('email_verification.try_again')}
              </p>
              <Button
                className="mt-4"
                onClick={() => window.location.href = '/login'}
              >
                {t('common.back_to_login')}
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
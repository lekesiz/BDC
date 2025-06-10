import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Shield, Smartphone, Key, Copy, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from '@/components/ui/use-toast';
import api from '@/lib/api';

export function TwoFactorSetup({ isOpen, onClose, onSuccess }) {
  const { t } = useTranslation();
  const [step, setStep] = useState('setup'); // setup, verify, backup
  const [qrCode, setQrCode] = useState('');
  const [secret, setSecret] = useState('');
  const [backupCodes, setBackupCodes] = useState([]);
  const [verificationCode, setVerificationCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSetup = async () => {
    try {
      setIsLoading(true);
      const response = await api.post('/two-factor/setup');
      
      if (response.data.success) {
        setQrCode(response.data.data.qr_code);
        setSecret(response.data.data.secret);
        setBackupCodes(response.data.data.backup_codes);
        setStep('verify');
      }
    } catch (error) {
      toast({
        title: t('two_factor.setup_error'),
        description: error.response?.data?.message || t('common.error_occurred'),
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerify = async () => {
    try {
      setIsLoading(true);
      const response = await api.post('/two-factor/verify-setup', {
        token: verificationCode
      });
      
      if (response.data.success) {
        setStep('backup');
        toast({
          title: t('two_factor.enabled_success'),
          description: t('two_factor.enabled_description'),
        });
      }
    } catch (error) {
      toast({
        title: t('two_factor.verify_error'),
        description: error.response?.data?.message || t('common.error_occurred'),
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopySecret = () => {
    navigator.clipboard.writeText(secret);
    toast({
      title: t('common.copied'),
      description: t('two_factor.secret_copied'),
    });
  };

  const handleDownloadCodes = () => {
    const content = backupCodes.join('\n');
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'bdc-backup-codes.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleComplete = () => {
    onSuccess?.();
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            {t('two_factor.setup_title')}
          </DialogTitle>
          <DialogDescription>
            {t('two_factor.setup_description')}
          </DialogDescription>
        </DialogHeader>

        {step === 'setup' && (
          <div className="space-y-4">
            <Alert>
              <Smartphone className="h-4 w-4" />
              <AlertDescription>
                {t('two_factor.requirements')}
              </AlertDescription>
            </Alert>
            
            <div className="flex justify-end">
              <Button onClick={handleSetup} disabled={isLoading}>
                {t('two_factor.start_setup')}
              </Button>
            </div>
          </div>
        )}

        {step === 'verify' && (
          <div className="space-y-4">
            <div className="text-center">
              <img src={qrCode} alt="QR Code" className="mx-auto" />
              <p className="mt-2 text-sm text-muted-foreground">
                {t('two_factor.scan_qr')}
              </p>
            </div>

            <div className="space-y-2">
              <Label>{t('two_factor.manual_entry')}</Label>
              <div className="flex gap-2">
                <Input value={secret} readOnly className="font-mono" />
                <Button variant="outline" size="icon" onClick={handleCopySecret}>
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="verification-code">
                {t('two_factor.enter_code')}
              </Label>
              <Input
                id="verification-code"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                placeholder="000000"
                maxLength={6}
                className="text-center text-2xl font-mono"
              />
            </div>

            <Button
              onClick={handleVerify}
              disabled={!verificationCode || verificationCode.length !== 6 || isLoading}
              className="w-full"
            >
              {t('two_factor.verify')}
            </Button>
          </div>
        )}

        {step === 'backup' && (
          <div className="space-y-4">
            <Alert>
              <Key className="h-4 w-4" />
              <AlertDescription>
                {t('two_factor.backup_codes_warning')}
              </AlertDescription>
            </Alert>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">
                  {t('two_factor.backup_codes')}
                </CardTitle>
                <CardDescription>
                  {t('two_factor.backup_codes_description')}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-2">
                  {backupCodes.map((code, index) => (
                    <div
                      key={index}
                      className="p-2 bg-muted rounded font-mono text-sm text-center"
                    >
                      {code}
                    </div>
                  ))}
                </div>
                <Button
                  variant="outline"
                  className="mt-4 w-full"
                  onClick={handleDownloadCodes}
                >
                  <Download className="mr-2 h-4 w-4" />
                  {t('two_factor.download_codes')}
                </Button>
              </CardContent>
            </Card>

            <Button onClick={handleComplete} className="w-full">
              {t('common.done')}
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

export function TwoFactorVerification({ sessionToken, userId, onSuccess }) {
  const { t } = useTranslation();
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [useBackupCode, setUseBackupCode] = useState(false);

  const handleVerify = async () => {
    try {
      setIsLoading(true);
      const response = await api.post('/two-factor/verify-login', {
        token: code,
        session_token: sessionToken,
        user_id: userId
      });
      
      if (response.data.success) {
        onSuccess(response.data);
      }
    } catch (error) {
      toast({
        title: t('two_factor.invalid_code'),
        description: error.response?.data?.message || t('common.error_occurred'),
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Shield className="h-5 w-5" />
          {t('two_factor.verification_title')}
        </CardTitle>
        <CardDescription>
          {useBackupCode 
            ? t('two_factor.enter_backup_code')
            : t('two_factor.enter_auth_code')}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="2fa-code">
            {useBackupCode ? t('two_factor.backup_code') : t('two_factor.verification_code')}
          </Label>
          <Input
            id="2fa-code"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder={useBackupCode ? "XXXXXXXX" : "000000"}
            maxLength={useBackupCode ? 8 : 6}
            className="text-center text-2xl font-mono"
          />
        </div>

        <Button
          onClick={handleVerify}
          disabled={!code || isLoading}
          className="w-full"
        >
          {t('two_factor.verify')}
        </Button>

        <Button
          variant="link"
          onClick={() => setUseBackupCode(!useBackupCode)}
          className="w-full"
        >
          {useBackupCode 
            ? t('two_factor.use_authenticator')
            : t('two_factor.use_backup_code')}
        </Button>
      </CardContent>
    </Card>
  );
}

export function TwoFactorSettings({ user }) {
  const { t } = useTranslation();
  const [status, setStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showSetup, setShowSetup] = useState(false);
  const [showDisable, setShowDisable] = useState(false);
  const [password, setPassword] = useState('');

  React.useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await api.get('/two-factor/status');
      setStatus(response.data.data);
    } catch (error) {
      toast({
        title: t('common.error'),
        description: t('common.error_occurred'),
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDisable = async () => {
    try {
      const response = await api.post('/two-factor/disable', { password });
      
      if (response.data.success) {
        toast({
          title: t('two_factor.disabled_success'),
          description: t('two_factor.disabled_description'),
        });
        setShowDisable(false);
        setPassword('');
        fetchStatus();
      }
    } catch (error) {
      toast({
        title: t('common.error'),
        description: error.response?.data?.message || t('common.error_occurred'),
        variant: 'destructive',
      });
    }
  };

  const handleRegenerateCodes = async () => {
    try {
      const response = await api.post('/two-factor/regenerate-backup-codes');
      
      if (response.data.success) {
        // Show new codes
        toast({
          title: t('two_factor.codes_regenerated'),
          description: t('two_factor.save_new_codes'),
        });
        // You might want to show codes in a dialog
      }
    } catch (error) {
      toast({
        title: t('common.error'),
        description: error.response?.data?.message || t('common.error_occurred'),
        variant: 'destructive',
      });
    }
  };

  if (isLoading) {
    return <div>{t('common.loading')}</div>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('two_factor.settings_title')}</CardTitle>
        <CardDescription>
          {t('two_factor.settings_description')}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {status?.enabled ? (
          <>
            <Alert>
              <Shield className="h-4 w-4" />
              <AlertDescription>
                {t('two_factor.enabled_status')}
              </AlertDescription>
            </Alert>
            
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                {t('two_factor.backup_codes_remaining', { count: status.backup_codes_remaining })}
              </p>
              {status.last_used && (
                <p className="text-sm text-muted-foreground">
                  {t('two_factor.last_used', { date: new Date(status.last_used).toLocaleString() })}
                </p>
              )}
            </div>

            <div className="flex gap-2">
              <Button variant="outline" onClick={handleRegenerateCodes}>
                {t('two_factor.regenerate_codes')}
              </Button>
              <Button variant="destructive" onClick={() => setShowDisable(true)}>
                {t('two_factor.disable')}
              </Button>
            </div>
          </>
        ) : (
          <>
            <Alert>
              <AlertDescription>
                {t('two_factor.disabled_status')}
              </AlertDescription>
            </Alert>
            
            <Button onClick={() => setShowSetup(true)}>
              {t('two_factor.enable')}
            </Button>
          </>
        )}
      </CardContent>

      <TwoFactorSetup
        isOpen={showSetup}
        onClose={() => setShowSetup(false)}
        onSuccess={() => {
          setShowSetup(false);
          fetchStatus();
        }}
      />

      <Dialog open={showDisable} onOpenChange={setShowDisable}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('two_factor.disable_title')}</DialogTitle>
            <DialogDescription>
              {t('two_factor.disable_warning')}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="password">{t('common.password')}</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowDisable(false)}>
                {t('common.cancel')}
              </Button>
              <Button variant="destructive" onClick={handleDisable} disabled={!password}>
                {t('two_factor.disable')}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
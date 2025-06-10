import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Shield, Upload, AlertTriangle, CheckCircle, XCircle, FileX, History, BarChart } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from '@/components/ui/use-toast';
import api from '@/lib/api';

export function VirusScanner() {
  const { t } = useTranslation();
  const [file, setFile] = useState(null);
  const [url, setUrl] = useState('');
  const [scanning, setScanning] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Check file size (50MB limit)
      if (selectedFile.size > 50 * 1024 * 1024) {
        toast({
          title: t('virus_scan.file_too_large'),
          description: t('virus_scan.max_file_size'),
          variant: 'destructive',
        });
        return;
      }
      setFile(selectedFile);
      setScanResult(null);
    }
  };

  const handleFileScan = async () => {
    if (!file) return;

    setScanning(true);
    setScanResult(null);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post('/virus-scan/scan-file', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(progress);
        },
      });

      setScanResult(response.data.scan_result);
      
      if (response.data.scan_result.infected) {
        toast({
          title: t('virus_scan.threat_detected'),
          description: t('virus_scan.file_quarantined'),
          variant: 'destructive',
        });
      } else {
        toast({
          title: t('virus_scan.file_clean'),
          description: t('virus_scan.no_threats'),
        });
      }
    } catch (error) {
      toast({
        title: t('virus_scan.scan_failed'),
        description: error.response?.data?.message || t('common.error_occurred'),
        variant: 'destructive',
      });
    } finally {
      setScanning(false);
      setUploadProgress(0);
    }
  };

  const handleUrlScan = async () => {
    if (!url) return;

    setScanning(true);
    setScanResult(null);

    try {
      const response = await api.post('/virus-scan/scan-url', { url });
      setScanResult(response.data.scan_result);
      
      if (response.data.scan_result.infected) {
        toast({
          title: t('virus_scan.threat_detected'),
          description: t('virus_scan.url_file_infected'),
          variant: 'destructive',
        });
      } else {
        toast({
          title: t('virus_scan.file_clean'),
          description: t('virus_scan.no_threats'),
        });
      }
    } catch (error) {
      toast({
        title: t('virus_scan.scan_failed'),
        description: error.response?.data?.message || t('common.error_occurred'),
        variant: 'destructive',
      });
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            {t('virus_scan.title')}
          </CardTitle>
          <CardDescription>
            {t('virus_scan.description')}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="file">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="file">{t('virus_scan.scan_file')}</TabsTrigger>
              <TabsTrigger value="url">{t('virus_scan.scan_url')}</TabsTrigger>
            </TabsList>
            
            <TabsContent value="file" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="file-upload">{t('virus_scan.select_file')}</Label>
                <Input
                  id="file-upload"
                  type="file"
                  onChange={handleFileChange}
                  disabled={scanning}
                />
                {file && (
                  <p className="text-sm text-muted-foreground">
                    {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                  </p>
                )}
              </div>
              
              {scanning && uploadProgress > 0 && (
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    {t('virus_scan.uploading')}
                  </p>
                  <Progress value={uploadProgress} />
                </div>
              )}
              
              <Button
                onClick={handleFileScan}
                disabled={!file || scanning}
                className="w-full"
              >
                <Upload className="mr-2 h-4 w-4" />
                {scanning ? t('virus_scan.scanning') : t('virus_scan.scan_now')}
              </Button>
            </TabsContent>
            
            <TabsContent value="url" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="url-input">{t('virus_scan.enter_url')}</Label>
                <Input
                  id="url-input"
                  type="url"
                  placeholder="https://example.com/file.pdf"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  disabled={scanning}
                />
              </div>
              
              <Button
                onClick={handleUrlScan}
                disabled={!url || scanning}
                className="w-full"
              >
                <Upload className="mr-2 h-4 w-4" />
                {scanning ? t('virus_scan.scanning') : t('virus_scan.scan_now')}
              </Button>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {scanResult && (
        <Card>
          <CardHeader>
            <CardTitle>{t('virus_scan.scan_results')}</CardTitle>
          </CardHeader>
          <CardContent>
            <ScanResultDisplay result={scanResult} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function ScanResultDisplay({ result }) {
  const { t } = useTranslation();

  if (result.status === 'error') {
    return (
      <Alert variant="destructive">
        <XCircle className="h-4 w-4" />
        <AlertDescription>
          {t('virus_scan.error')}: {result.error}
        </AlertDescription>
      </Alert>
    );
  }

  if (result.infected) {
    return (
      <div className="space-y-4">
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            {t('virus_scan.infected_file')}
          </AlertDescription>
        </Alert>
        
        <div className="space-y-2">
          <h4 className="font-semibold">{t('virus_scan.threats_found')}:</h4>
          <ul className="list-disc list-inside space-y-1">
            {result.threats.map((threat, index) => (
              <li key={index} className="text-sm text-destructive">
                {threat}
              </li>
            ))}
          </ul>
        </div>
        
        <Alert>
          <FileX className="h-4 w-4" />
          <AlertDescription>
            {t('virus_scan.action_taken')}: {t(`virus_scan.${result.action}`)}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <Alert variant="default" className="border-green-200 bg-green-50">
        <CheckCircle className="h-4 w-4 text-green-600" />
        <AlertDescription className="text-green-800">
          {t('virus_scan.clean_file')}
        </AlertDescription>
      </Alert>
      
      {result.file_info && (
        <div className="space-y-2">
          <h4 className="font-semibold">{t('virus_scan.file_info')}:</h4>
          <dl className="grid grid-cols-2 gap-2 text-sm">
            <dt className="text-muted-foreground">{t('virus_scan.file_type')}:</dt>
            <dd>{result.file_info.mime_type}</dd>
            
            <dt className="text-muted-foreground">{t('virus_scan.file_size')}:</dt>
            <dd>{(result.file_info.size / 1024 / 1024).toFixed(2)} MB</dd>
            
            <dt className="text-muted-foreground">{t('virus_scan.sha256')}:</dt>
            <dd className="truncate font-mono text-xs">{result.file_info.sha256}</dd>
          </dl>
        </div>
      )}
      
      {result.scan_results && (
        <div className="space-y-2">
          <h4 className="font-semibold">{t('virus_scan.scan_engines')}:</h4>
          <div className="space-y-1">
            {result.scan_results.map((engine, index) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <span>{engine.scanner}</span>
                <span className={engine.infected ? 'text-destructive' : 'text-green-600'}>
                  {engine.infected ? t('virus_scan.infected') : t('virus_scan.clean')}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export function VirusScanHistory() {
  const { t } = useTranslation();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  React.useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await api.get('/virus-scan/history');
      setHistory(response.data.scans);
    } catch (error) {
      toast({
        title: t('common.error'),
        description: t('common.error_occurred'),
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>{t('common.loading')}</div>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <History className="h-5 w-5" />
          {t('virus_scan.scan_history')}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {history.length === 0 ? (
          <p className="text-center text-muted-foreground py-4">
            {t('virus_scan.no_scan_history')}
          </p>
        ) : (
          <div className="space-y-2">
            {history.map((scan) => (
              <div
                key={scan.id}
                className="flex items-center justify-between p-3 border rounded-lg"
              >
                <div className="space-y-1">
                  <p className="font-medium text-sm">{scan.file_path.split('/').pop()}</p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(scan.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {scan.is_infected ? (
                    <span className="flex items-center gap-1 text-destructive">
                      <XCircle className="h-4 w-4" />
                      {t('virus_scan.infected')}
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-green-600">
                      <CheckCircle className="h-4 w-4" />
                      {t('virus_scan.clean')}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function VirusScanStatistics() {
  const { t } = useTranslation();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  React.useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get('/virus-scan/statistics');
      setStats(response.data.statistics);
    } catch (error) {
      toast({
        title: t('common.error'),
        description: t('common.error_occurred'),
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>{t('common.loading')}</div>;
  }

  if (!stats) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart className="h-5 w-5" />
          {t('virus_scan.statistics')}
        </CardTitle>
        <CardDescription>
          {t('virus_scan.last_n_days', { days: stats.period_days })}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="space-y-1">
            <p className="text-2xl font-bold">{stats.total_scans}</p>
            <p className="text-sm text-muted-foreground">{t('virus_scan.total_scans')}</p>
          </div>
          <div className="space-y-1">
            <p className="text-2xl font-bold text-destructive">{stats.infected_files}</p>
            <p className="text-sm text-muted-foreground">{t('virus_scan.infected_files')}</p>
          </div>
          <div className="space-y-1">
            <p className="text-2xl font-bold">{stats.infection_rate.toFixed(1)}%</p>
            <p className="text-sm text-muted-foreground">{t('virus_scan.infection_rate')}</p>
          </div>
          <div className="space-y-1">
            <p className="text-2xl font-bold">{stats.avg_scan_time.toFixed(2)}s</p>
            <p className="text-sm text-muted-foreground">{t('virus_scan.avg_scan_time')}</p>
          </div>
        </div>

        {stats.top_threats.length > 0 && (
          <div className="space-y-2">
            <h4 className="font-semibold">{t('virus_scan.top_threats')}</h4>
            <div className="space-y-1">
              {stats.top_threats.map((threat, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <span className="text-destructive">{threat.threat}</span>
                  <span className="text-muted-foreground">{threat.count} {t('virus_scan.detections')}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
import { 
  generateComplianceData, 
  generateComplianceMetrics,
  generateComplianceReports 
} from './mockComplianceData';

export const setupComplianceMockApi = (api, originalGet, originalPost, originalPut, originalDelete) => {
  const originalFunctions = {
    get: originalGet || api.get.bind(api),
    post: originalPost || api.post.bind(api),
    put: originalPut || api.put.bind(api),
    delete: originalDelete || api.delete.bind(api)
  };

  // Compliance endpoints
  api.get = function(url, ...args) {
    // Audit logs endpoint
    if (url === '/api/compliance/audit-logs' || url.startsWith('/api/compliance/audit-logs?')) {
      console.log('Mock API: Audit logs request');
      const complianceData = generateComplianceData();
      
      // Parse query parameters
      const urlObj = new URL(url, 'http://localhost');
      const user = urlObj.searchParams.get('user');
      const action = urlObj.searchParams.get('action');
      const resource = urlObj.searchParams.get('resource');
      const startDate = urlObj.searchParams.get('startDate');
      const endDate = urlObj.searchParams.get('endDate');
      const risk = urlObj.searchParams.get('risk');
      
      let logs = complianceData.auditLogs;
      
      // Filter by user
      if (user) {
        logs = logs.filter(log => 
          log.user.toLowerCase().includes(user.toLowerCase()) ||
          log.userId?.toLowerCase().includes(user.toLowerCase())
        );
      }
      
      // Filter by action
      if (action) {
        logs = logs.filter(log => log.action === action);
      }
      
      // Filter by resource
      if (resource) {
        logs = logs.filter(log => log.resource === resource);
      }
      
      // Filter by risk level
      if (risk) {
        logs = logs.filter(log => log.risk === risk);
      }
      
      // Filter by date range
      if (startDate && endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        logs = logs.filter(log => {
          const logDate = new Date(log.timestamp);
          return logDate >= start && logDate <= end;
        });
      }
      
      return Promise.resolve({
        status: 200,
        data: {
          logs,
          total: logs.length,
          filtered: logs.length < complianceData.auditLogs.length
        }
      });
    }
    
    // GDPR compliance endpoint
    if (url === '/api/compliance/gdpr') {
      console.log('Mock API: GDPR compliance request');
      const complianceData = generateComplianceData();
      
      return Promise.resolve({
        status: 200,
        data: complianceData.gdprCompliance
      });
    }
    
    // Security headers endpoint
    if (url === '/api/compliance/security-headers') {
      console.log('Mock API: Security headers request');
      const complianceData = generateComplianceData();
      
      return Promise.resolve({
        status: 200,
        data: complianceData.securityHeaders
      });
    }
    
    // Data backup endpoint
    if (url === '/api/compliance/backups') {
      console.log('Mock API: Data backups request');
      const complianceData = generateComplianceData();
      
      return Promise.resolve({
        status: 200,
        data: complianceData.dataBackup
      });
    }
    
    // Input validation endpoint
    if (url === '/api/compliance/input-validation') {
      console.log('Mock API: Input validation request');
      const complianceData = generateComplianceData();
      
      return Promise.resolve({
        status: 200,
        data: complianceData.inputValidation
      });
    }
    
    // Regulatory compliance endpoint
    if (url === '/api/compliance/regulatory') {
      console.log('Mock API: Regulatory compliance request');
      const complianceData = generateComplianceData();
      
      return Promise.resolve({
        status: 200,
        data: complianceData.regulatoryCompliance
      });
    }
    
    // Risk assessment endpoint
    if (url === '/api/compliance/risk-assessment') {
      console.log('Mock API: Risk assessment request');
      const complianceData = generateComplianceData();
      
      return Promise.resolve({
        status: 200,
        data: complianceData.riskAssessment
      });
    }
    
    // Compliance metrics endpoint
    if (url === '/api/compliance/metrics') {
      console.log('Mock API: Compliance metrics request');
      const metrics = generateComplianceMetrics();
      
      return Promise.resolve({
        status: 200,
        data: metrics
      });
    }
    
    // Compliance reports endpoint
    if (url === '/api/compliance/reports') {
      console.log('Mock API: Compliance reports request');
      const reports = generateComplianceReports();
      
      return Promise.resolve({
        status: 200,
        data: {
          reports,
          total: reports.length
        }
      });
    }
    
    // Specific backup details
    if (url.match(/^\/api\/compliance\/backups\/\d+$/)) {
      console.log('Mock API: Specific backup details');
      const backupId = parseInt(url.split('/').pop());
      const complianceData = generateComplianceData();
      const backup = complianceData.dataBackup.backups.find(b => b.id === backupId);
      
      if (backup) {
        return Promise.resolve({
          status: 200,
          data: backup
        });
      } else {
        return Promise.resolve({
          status: 404,
          data: { error: 'Backup not found' }
        });
      }
    }
    
    // Compliance policies
    if (url === '/api/compliance/policies') {
      console.log('Mock API: Compliance policies request');
      
      const policies = [
        {
          id: 1,
          name: "Data Retention Policy",
          version: "2.1",
          effectiveDate: "2023-01-01",
          lastReview: "2023-12-15",
          nextReview: "2024-06-15",
          status: "active"
        },
        {
          id: 2,
          name: "Privacy Policy",
          version: "3.0",
          effectiveDate: "2023-05-01",
          lastReview: "2024-01-10",
          nextReview: "2024-07-10",
          status: "active"
        },
        {
          id: 3,
          name: "Security Policy",
          version: "2.5",
          effectiveDate: "2023-06-15",
          lastReview: "2023-11-30",
          nextReview: "2024-05-30",
          status: "active"
        },
        {
          id: 4,
          name: "Incident Response Policy",
          version: "1.8",
          effectiveDate: "2023-09-01",
          lastReview: "2023-12-01",
          nextReview: "2024-06-01",
          status: "active"
        }
      ];
      
      return Promise.resolve({
        status: 200,
        data: {
          policies,
          total: policies.length
        }
      });
    }
    
    // Call original get for other endpoints
    return originalFunctions.get.call(api, url, ...args);
  };
  
  // Compliance POST endpoints
  api.post = function(url, data, ...args) {
    // Create audit log entry
    if (url === '/api/compliance/audit-logs') {
      console.log('Mock API: Create audit log', data);
      
      const newLog = {
        id: Date.now(),
        ...data,
        timestamp: new Date().toISOString(),
        status: "success"
      };
      
      return Promise.resolve({
        status: 201,
        data: newLog
      });
    }
    
    // Initiate backup
    if (url === '/api/compliance/backups/initiate') {
      console.log('Mock API: Initiate backup', data);
      
      const backup = {
        id: Date.now(),
        type: data.type || 'manual',
        status: 'in_progress',
        timestamp: new Date().toISOString(),
        location: data.location || 'AWS S3 - eu-west-1',
        encrypted: true,
        progress: 0
      };
      
      return Promise.resolve({
        status: 202,
        data: backup
      });
    }
    
    // Generate compliance report
    if (url === '/api/compliance/reports/generate') {
      console.log('Mock API: Generate compliance report', data);
      
      const report = {
        id: Date.now(),
        title: data.title,
        type: data.type,
        status: 'generating',
        generatedAt: new Date().toISOString(),
        estimatedTime: '5 minutes'
      };
      
      return Promise.resolve({
        status: 202,
        data: report
      });
    }
    
    // Perform security scan
    if (url === '/api/compliance/security/scan') {
      console.log('Mock API: Perform security scan', data);
      
      return Promise.resolve({
        status: 202,
        data: {
          scanId: Date.now(),
          type: data.type || 'full',
          status: 'running',
          startedAt: new Date().toISOString(),
          estimatedDuration: '15 minutes'
        }
      });
    }
    
    // Submit compliance assessment
    if (url === '/api/compliance/assessments') {
      console.log('Mock API: Submit compliance assessment', data);
      
      const assessment = {
        id: Date.now(),
        framework: data.framework,
        score: Math.floor(Math.random() * 20) + 80,
        status: 'completed',
        submittedAt: new Date().toISOString(),
        findings: data.findings || []
      };
      
      return Promise.resolve({
        status: 201,
        data: assessment
      });
    }
    
    // Export compliance data
    if (url === '/api/compliance/export') {
      console.log('Mock API: Export compliance data', data);
      
      return Promise.resolve({
        status: 200,
        data: {
          exportId: Date.now(),
          format: data.format || 'pdf',
          downloadUrl: `/api/downloads/compliance-export-${Date.now()}.${data.format || 'pdf'}`,
          expiresAt: new Date(Date.now() + 3600000).toISOString()
        }
      });
    }
    
    return originalFunctions.post.call(api, url, data, ...args);
  };
  
  // Compliance PUT endpoints
  api.put = function(url, data, ...args) {
    // Update compliance settings
    if (url === '/api/compliance/settings') {
      console.log('Mock API: Update compliance settings', data);
      
      return Promise.resolve({
        status: 200,
        data: {
          ...data,
          updatedAt: new Date().toISOString(),
          message: 'Compliance settings updated successfully'
        }
      });
    }
    
    // Update security headers
    if (url === '/api/compliance/security-headers') {
      console.log('Mock API: Update security headers', data);
      
      return Promise.resolve({
        status: 200,
        data: {
          headers: data.headers,
          updatedAt: new Date().toISOString(),
          message: 'Security headers updated successfully'
        }
      });
    }
    
    // Update backup schedule
    if (url === '/api/compliance/backups/schedule') {
      console.log('Mock API: Update backup schedule', data);
      
      return Promise.resolve({
        status: 200,
        data: {
          schedule: data,
          updatedAt: new Date().toISOString(),
          message: 'Backup schedule updated successfully'
        }
      });
    }
    
    // Update validation rules
    if (url === '/api/compliance/validation-rules') {
      console.log('Mock API: Update validation rules', data);
      
      return Promise.resolve({
        status: 200,
        data: {
          rules: data.rules,
          updatedAt: new Date().toISOString(),
          message: 'Validation rules updated successfully'
        }
      });
    }
    
    // Update policy
    if (url.match(/^\/api\/compliance\/policies\/\d+$/)) {
      console.log('Mock API: Update policy', data);
      const policyId = parseInt(url.split('/').pop());
      
      return Promise.resolve({
        status: 200,
        data: {
          id: policyId,
          ...data,
          updatedAt: new Date().toISOString()
        }
      });
    }
    
    // Mark assessment as reviewed
    if (url.match(/^\/api\/compliance\/assessments\/\d+\/review$/)) {
      console.log('Mock API: Mark assessment as reviewed');
      const assessmentId = parseInt(url.split('/')[3]);
      
      return Promise.resolve({
        status: 200,
        data: {
          id: assessmentId,
          reviewedBy: data.reviewedBy,
          reviewedAt: new Date().toISOString(),
          comments: data.comments
        }
      });
    }
    
    return originalFunctions.put.call(api, url, data, ...args);
  };
  
  // Compliance DELETE endpoints
  api.delete = function(url, ...args) {
    // Delete old audit logs
    if (url === '/api/compliance/audit-logs/old') {
      console.log('Mock API: Delete old audit logs');
      
      return Promise.resolve({
        status: 200,
        data: {
          deleted: Math.floor(Math.random() * 100) + 50,
          message: 'Old audit logs deleted successfully'
        }
      });
    }
    
    // Delete backup
    if (url.match(/^\/api\/compliance\/backups\/\d+$/)) {
      console.log('Mock API: Delete backup');
      const backupId = parseInt(url.split('/').pop());
      
      return Promise.resolve({
        status: 200,
        data: {
          id: backupId,
          deleted: true,
          message: 'Backup deleted successfully'
        }
      });
    }
    
    // Remove validation rule
    if (url.match(/^\/api\/compliance\/validation-rules\/\d+$/)) {
      console.log('Mock API: Remove validation rule');
      const ruleId = parseInt(url.split('/').pop());
      
      return Promise.resolve({
        status: 200,
        data: {
          id: ruleId,
          deleted: true,
          message: 'Validation rule removed successfully'
        }
      });
    }
    
    // Archive policy
    if (url.match(/^\/api\/compliance\/policies\/\d+$/)) {
      console.log('Mock API: Archive policy');
      const policyId = parseInt(url.split('/').pop());
      
      return Promise.resolve({
        status: 200,
        data: {
          id: policyId,
          archived: true,
          archivedAt: new Date().toISOString()
        }
      });
    }
    
    return originalFunctions.delete.call(api, url, ...args);
  };
};
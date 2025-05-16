import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Shield, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Code,
  FileText,
  Settings,
  Eye,
  Play,
  Copy,
  Filter,
  Lock,
  Database,
  RefreshCw,
  Plus
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { useToast } from '../../components/ui/toast';

const validationRules = [
  {
    id: 'sql_injection',
    name: 'SQL Injection Prevention',
    category: 'Database',
    severity: 'critical',
    description: 'Prevents SQL injection attacks by parameterizing queries and escaping special characters',
    enabled: true,
    pattern: /('|"|-{2}|;|\*|<|>|&|\||\\)/g,
    examples: ["'; DROP TABLE users; --", "1' OR '1'='1", "admin'--"]
  },
  {
    id: 'xss_prevention',
    name: 'XSS Attack Prevention',
    category: 'Frontend',
    severity: 'critical',
    description: 'Prevents cross-site scripting attacks by escaping HTML entities',
    enabled: true,
    pattern: /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
    examples: ['<script>alert("XSS")</script>', '<img src=x onerror=alert("XSS")>']
  },
  {
    id: 'email_validation',
    name: 'Email Format Validation',
    category: 'Input',
    severity: 'medium',
    description: 'Validates email format using RFC-compliant regex',
    enabled: true,
    pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
    examples: ['user@example.com', 'test.user+tag@domain.co.uk']
  },
  {
    id: 'phone_validation',
    name: 'Phone Number Validation',
    category: 'Input',
    severity: 'low',
    description: 'Validates international phone number formats',
    enabled: true,
    pattern: /^\+?[1-9]\d{1,14}$/,
    examples: ['+1234567890', '9876543210']
  },
  {
    id: 'url_validation',
    name: 'URL Validation',
    category: 'Input',
    severity: 'medium',
    description: 'Validates URL format and protocol',
    enabled: true,
    pattern: /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/,
    examples: ['https://example.com', 'http://subdomain.site.com/path']
  },
  {
    id: 'file_extension',
    name: 'File Extension Validation',
    category: 'Upload',
    severity: 'high',
    description: 'Validates allowed file extensions for uploads',
    enabled: true,
    allowedExtensions: ['jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx'],
    examples: ['document.pdf', 'image.jpg']
  },
  {
    id: 'password_strength',
    name: 'Password Strength Validation',
    category: 'Authentication',
    severity: 'high',
    description: 'Ensures passwords meet security requirements',
    enabled: true,
    pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
    examples: ['SecurePass123!', 'Str0ng&Password']
  },
  {
    id: 'sanitize_html',
    name: 'HTML Content Sanitization',
    category: 'Content',
    severity: 'high',
    description: 'Sanitizes user-generated HTML content',
    enabled: true,
    allowedTags: ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a'],
    examples: ['<p>Safe content</p>', '<strong>Bold text</strong>']
  }
];

const InputValidationPage = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [rules, setRules] = useState(validationRules);
  const [testInput, setTestInput] = useState('');
  const [testResults, setTestResults] = useState([]);
  const [selectedRule, setSelectedRule] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState({
    totalValidations: 0,
    blockedAttacks: 0,
    falsePositives: 0,
    performanceImpact: 'Low'
  });

  useEffect(() => {
    fetchValidationStats();
    fetchCustomRules();
  }, []);

  const fetchValidationStats = async () => {
    try {
      const response = await fetch('/api/admin/validation/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setStats(data.stats || stats);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchCustomRules = async () => {
    try {
      const response = await fetch('/api/admin/validation/rules', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setRules([...validationRules, ...(data.customRules || [])]);
      }
    } catch (error) {
      console.error('Error fetching custom rules:', error);
    }
  };

  const updateRule = async (ruleId, updates) => {
    try {
      const response = await fetch(`/api/admin/validation/rules/${ruleId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(updates)
      });
      
      if (response.ok) {
        setRules(rules.map(rule => 
          rule.id === ruleId ? { ...rule, ...updates } : rule
        ));
        showToast('Validation rule updated', 'success');
      }
    } catch (error) {
      showToast('Error updating rule', 'error');
    }
  };

  const testValidation = () => {
    const results = [];
    
    rules.forEach(rule => {
      if (!rule.enabled) return;
      
      let isValid = true;
      let message = 'Passed';
      
      switch (rule.id) {
        case 'sql_injection':
        case 'xss_prevention':
          if (rule.pattern.test(testInput)) {
            isValid = false;
            message = `Potential ${rule.name} detected`;
          }
          break;
          
        case 'email_validation':
        case 'phone_validation':
        case 'url_validation':
        case 'password_strength':
          if (!rule.pattern.test(testInput)) {
            isValid = false;
            message = `Invalid ${rule.name.replace(' Validation', '')}`;
          }
          break;
          
        case 'file_extension':
          const ext = testInput.split('.').pop()?.toLowerCase();
          if (!rule.allowedExtensions.includes(ext)) {
            isValid = false;
            message = `File extension '${ext}' not allowed`;
          }
          break;
          
        case 'sanitize_html':
          const tempDiv = document.createElement('div');
          tempDiv.innerHTML = testInput;
          const tags = Array.from(tempDiv.getElementsByTagName('*'));
          const invalidTags = tags.filter(tag => 
            !rule.allowedTags.includes(tag.tagName.toLowerCase())
          );
          if (invalidTags.length > 0) {
            isValid = false;
            message = `Disallowed HTML tags: ${invalidTags.map(t => t.tagName).join(', ')}`;
          }
          break;
      }
      
      results.push({
        rule: rule.name,
        category: rule.category,
        severity: rule.severity,
        isValid,
        message
      });
    });
    
    setTestResults(results);
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'text-red-600 bg-red-100';
      case 'high':
        return 'text-orange-600 bg-orange-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'low':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Validations</p>
              <p className="text-2xl font-bold">{stats.totalValidations.toLocaleString()}</p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Blocked Attacks</p>
              <p className="text-2xl font-bold">{stats.blockedAttacks}</p>
            </div>
            <Shield className="w-8 h-8 text-red-600" />
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">False Positives</p>
              <p className="text-2xl font-bold">{stats.falsePositives}</p>
            </div>
            <AlertTriangle className="w-8 h-8 text-yellow-600" />
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Performance Impact</p>
              <p className="text-lg font-bold">{stats.performanceImpact}</p>
            </div>
            <Database className="w-8 h-8 text-primary" />
          </div>
        </Card>
      </div>

      {/* Active Rules */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">Active Validation Rules</h3>
        <div className="space-y-3">
          {rules.map(rule => (
            <div key={rule.id} className="border rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-1">
                    <h4 className="font-medium">{rule.name}</h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(rule.severity)}`}>
                      {rule.severity}
                    </span>
                    <span className="text-xs text-gray-500">{rule.category}</span>
                  </div>
                  <p className="text-sm text-gray-600">{rule.description}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      className="sr-only peer"
                      checked={rule.enabled}
                      onChange={(e) => updateRule(rule.id, { enabled: e.target.checked })}
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/10 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setSelectedRule(rule)}
                  >
                    <Settings className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Quick Test */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">Quick Validation Test</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Test Input</label>
            <textarea
              className="w-full p-3 border rounded-lg"
              rows="3"
              placeholder="Enter test input to validate against active rules..."
              value={testInput}
              onChange={(e) => setTestInput(e.target.value)}
            />
          </div>
          <Button onClick={testValidation}>
            <Play className="w-4 h-4 mr-2" />
            Test Validation
          </Button>
          
          {testResults.length > 0 && (
            <div className="mt-4 space-y-2">
              <h4 className="font-medium">Test Results</h4>
              {testResults.map((result, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                  <div className="flex items-center space-x-3">
                    {result.isValid ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-500" />
                    )}
                    <span className="font-medium">{result.rule}</span>
                  </div>
                  <span className="text-sm text-gray-600">{result.message}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>
    </div>
  );

  const renderRules = () => (
    <div className="space-y-6">
      <Card>
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold text-lg">Validation Rules Configuration</h3>
          <Button size="sm">
            <Plus className="w-4 h-4 mr-2" />
            Add Custom Rule
          </Button>
        </div>
        
        <div className="space-y-4">
          {rules.map(rule => (
            <div key={rule.id} className="border rounded-lg p-4">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">{rule.name}</h4>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(rule.severity)}`}>
                      {rule.severity}
                    </span>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setSelectedRule(rule)}
                    >
                      <Code className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600 mb-2">{rule.description}</p>
                  
                  {rule.pattern && (
                    <div className="mb-3">
                      <p className="text-xs font-medium text-gray-500 mb-1">Pattern/Regex</p>
                      <code className="block p-2 bg-gray-50 rounded text-xs overflow-x-auto">
                        {rule.pattern.toString()}
                      </code>
                    </div>
                  )}
                  
                  {rule.allowedExtensions && (
                    <div className="mb-3">
                      <p className="text-xs font-medium text-gray-500 mb-1">Allowed Extensions</p>
                      <div className="flex flex-wrap gap-1">
                        {rule.allowedExtensions.map(ext => (
                          <span key={ext} className="px-2 py-1 bg-gray-100 rounded text-xs">
                            .{ext}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {rule.allowedTags && (
                    <div className="mb-3">
                      <p className="text-xs font-medium text-gray-500 mb-1">Allowed HTML Tags</p>
                      <div className="flex flex-wrap gap-1">
                        {rule.allowedTags.map(tag => (
                          <span key={tag} className="px-2 py-1 bg-gray-100 rounded text-xs">
                            &lt;{tag}&gt;
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {rule.examples && (
                    <div>
                      <p className="text-xs font-medium text-gray-500 mb-1">Examples</p>
                      <div className="space-y-1">
                        {rule.examples.map((example, index) => (
                          <code key={index} className="block p-2 bg-gray-50 rounded text-xs">
                            {example}
                          </code>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="flex items-center justify-between pt-3 border-t">
                  <label className="flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      className="mr-2"
                      checked={rule.enabled}
                      onChange={(e) => updateRule(rule.id, { enabled: e.target.checked })}
                    />
                    <span className="text-sm">Enabled</span>
                  </label>
                  <div className="flex items-center space-x-2">
                    <Button size="sm" variant="secondary">
                      Edit Rule
                    </Button>
                    <Button size="sm" variant="ghost" className="text-red-600">
                      Delete
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );

  const renderLogs = () => (
    <Card>
      <h3 className="font-semibold text-lg mb-4">Validation Logs</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rule</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Input</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Result</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            <tr>
              <td className="px-4 py-3 text-sm">2023-05-16 10:30:45</td>
              <td className="px-4 py-3 text-sm">SQL Injection Prevention</td>
              <td className="px-4 py-3 text-sm">Login Attempt</td>
              <td className="px-4 py-3 text-sm">Anonymous</td>
              <td className="px-4 py-3 text-sm font-mono">admin' OR '1'='1</td>
              <td className="px-4 py-3">
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                  Blocked
                </span>
              </td>
            </tr>
            <tr>
              <td className="px-4 py-3 text-sm">2023-05-16 10:25:12</td>
              <td className="px-4 py-3 text-sm">Email Validation</td>
              <td className="px-4 py-3 text-sm">Registration</td>
              <td className="px-4 py-3 text-sm">john_doe</td>
              <td className="px-4 py-3 text-sm font-mono">invalid.email</td>
              <td className="px-4 py-3">
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                  Invalid
                </span>
              </td>
            </tr>
            <tr>
              <td className="px-4 py-3 text-sm">2023-05-16 10:20:34</td>
              <td className="px-4 py-3 text-sm">File Extension Validation</td>
              <td className="px-4 py-3 text-sm">Upload</td>
              <td className="px-4 py-3 text-sm">jane_smith</td>
              <td className="px-4 py-3 text-sm font-mono">document.pdf</td>
              <td className="px-4 py-3">
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Allowed
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>
  );

  const renderImplementation = () => (
    <div className="space-y-6">
      <Card>
        <h3 className="font-semibold text-lg mb-4">Implementation Examples</h3>
        
        <div className="space-y-6">
          {/* Backend Validation */}
          <div>
            <h4 className="font-medium mb-2">Python/Flask Backend Validation</h4>
            <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
              <code>{`from flask import request, jsonify
import re
import html

class InputValidator:
    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def sanitize_html(content):
        return html.escape(content)
    
    @staticmethod
    def prevent_sql_injection(query):
        # Use parameterized queries instead
        return query.replace("'", "''")

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    
    # Validate email
    if not InputValidator.validate_email(data.get('email')):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Sanitize input
    username = InputValidator.sanitize_html(data.get('username'))
    
    # Continue with registration...`}</code>
            </pre>
            <Button
              size="sm"
              variant="secondary"
              className="mt-2"
              onClick={() => copyToClipboard(`from flask import request, jsonify
import re
import html

class InputValidator:
    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def sanitize_html(content):
        return html.escape(content)
    
    @staticmethod
    def prevent_sql_injection(query):
        # Use parameterized queries instead
        return query.replace("'", "''")

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    
    # Validate email
    if not InputValidator.validate_email(data.get('email')):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Sanitize input
    username = InputValidator.sanitize_html(data.get('username'))
    
    # Continue with registration...`)}
            >
              <Copy className="w-4 h-4 mr-2" />
              Copy Code
            </Button>
          </div>

          {/* Frontend Validation */}
          <div>
            <h4 className="font-medium mb-2">React Frontend Validation</h4>
            <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
              <code>{`import React, { useState } from 'react';
import DOMPurify from 'dompurify';

const InputValidation = {
  email: (value) => {
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return pattern.test(value);
  },
  
  password: (value) => {
    const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$/;
    return pattern.test(value);
  },
  
  sanitizeHTML: (dirty) => {
    return DOMPurify.sanitize(dirty, {
      ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li'],
      ALLOWED_ATTR: []
    });
  }
};

const RegistrationForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({});
  
  const handleSubmit = (e) => {
    e.preventDefault();
    const newErrors = {};
    
    if (!InputValidation.email(email)) {
      newErrors.email = 'Invalid email format';
    }
    
    if (!InputValidation.password(password)) {
      newErrors.password = 'Password must be at least 8 characters with uppercase, lowercase, number and special character';
    }
    
    if (Object.keys(newErrors).length === 0) {
      // Submit form
    } else {
      setErrors(newErrors);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className={errors.email ? 'error' : ''}
      />
      {errors.email && <span className="error-message">{errors.email}</span>}
      
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className={errors.password ? 'error' : ''}
      />
      {errors.password && <span className="error-message">{errors.password}</span>}
      
      <button type="submit">Register</button>
    </form>
  );
};`}</code>
            </pre>
            <Button
              size="sm"
              variant="secondary"
              className="mt-2"
              onClick={() => copyToClipboard(`import React, { useState } from 'react';
import DOMPurify from 'dompurify';

const InputValidation = {
  email: (value) => {
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return pattern.test(value);
  },
  
  password: (value) => {
    const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$/;
    return pattern.test(value);
  },
  
  sanitizeHTML: (dirty) => {
    return DOMPurify.sanitize(dirty, {
      ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li'],
      ALLOWED_ATTR: []
    });
  }
};

const RegistrationForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({});
  
  const handleSubmit = (e) => {
    e.preventDefault();
    const newErrors = {};
    
    if (!InputValidation.email(email)) {
      newErrors.email = 'Invalid email format';
    }
    
    if (!InputValidation.password(password)) {
      newErrors.password = 'Password must be at least 8 characters with uppercase, lowercase, number and special character';
    }
    
    if (Object.keys(newErrors).length === 0) {
      // Submit form
    } else {
      setErrors(newErrors);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className={errors.email ? 'error' : ''}
      />
      {errors.email && <span className="error-message">{errors.email}</span>}
      
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className={errors.password ? 'error' : ''}
      />
      {errors.password && <span className="error-message">{errors.password}</span>}
      
      <button type="submit">Register</button>
    </form>
  );
};`)}
            >
              <Copy className="w-4 h-4 mr-2" />
              Copy Code
            </Button>
          </div>

          {/* SQL Injection Prevention */}
          <div>
            <h4 className="font-medium mb-2">SQL Injection Prevention</h4>
            <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
              <code>{`# Bad - Vulnerable to SQL injection
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

# Good - Using parameterized queries
cursor.execute(
    "SELECT * FROM users WHERE username = %s AND password = %s",
    (username, password)
)

# With SQLAlchemy
from sqlalchemy import text
query = text("SELECT * FROM users WHERE username = :username AND password = :password")
result = db.execute(query, {"username": username, "password": password})`}</code>
            </pre>
          </div>
        </div>
      </Card>

      <Card>
        <h3 className="font-semibold text-lg mb-4">Best Practices</h3>
        <ul className="space-y-3">
          <li className="flex items-start space-x-2">
            <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
            <div>
              <p className="font-medium">Always validate on both client and server</p>
              <p className="text-sm text-gray-600">Client-side validation improves UX, server-side ensures security</p>
            </div>
          </li>
          <li className="flex items-start space-x-2">
            <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
            <div>
              <p className="font-medium">Use whitelist approach over blacklist</p>
              <p className="text-sm text-gray-600">Define what's allowed rather than what's forbidden</p>
            </div>
          </li>
          <li className="flex items-start space-x-2">
            <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
            <div>
              <p className="font-medium">Sanitize all user input</p>
              <p className="text-sm text-gray-600">Never trust user input, always escape or sanitize</p>
            </div>
          </li>
          <li className="flex items-start space-x-2">
            <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
            <div>
              <p className="font-medium">Use prepared statements for database queries</p>
              <p className="text-sm text-gray-600">Prevents SQL injection attacks</p>
            </div>
          </li>
          <li className="flex items-start space-x-2">
            <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
            <div>
              <p className="font-medium">Implement rate limiting</p>
              <p className="text-sm text-gray-600">Prevent brute force and DoS attacks</p>
            </div>
          </li>
        </ul>
      </Card>
    </div>
  );

  const renderSelectedRule = () => (
    selectedRule && (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
        <Card className="max-w-2xl w-full max-h-[80vh] overflow-y-auto">
          <div className="flex justify-between items-start mb-4">
            <h3 className="font-semibold text-lg">{selectedRule.name}</h3>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setSelectedRule(null)}
            >
              <XCircle className="w-4 h-4" />
            </Button>
          </div>

          <div className="space-y-4">
            <div>
              <p className="font-medium mb-1">Description</p>
              <p className="text-sm text-gray-600">{selectedRule.description}</p>
            </div>

            <div>
              <p className="font-medium mb-1">Category</p>
              <p className="text-sm">{selectedRule.category}</p>
            </div>

            <div>
              <p className="font-medium mb-1">Severity</p>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(selectedRule.severity)}`}>
                {selectedRule.severity}
              </span>
            </div>

            {selectedRule.pattern && (
              <div>
                <p className="font-medium mb-1">Pattern/Regex</p>
                <pre className="bg-gray-50 p-3 rounded text-sm overflow-x-auto">
                  {selectedRule.pattern.toString()}
                </pre>
              </div>
            )}

            {selectedRule.examples && (
              <div>
                <p className="font-medium mb-1">Examples</p>
                <div className="space-y-2">
                  {selectedRule.examples.map((example, index) => (
                    <div key={index} className="flex items-center justify-between bg-gray-50 p-2 rounded">
                      <code className="text-sm">{example}</code>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => {
                          setTestInput(example);
                          setSelectedRule(null);
                        }}
                      >
                        Test
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="pt-4 border-t">
              <Button
                onClick={() => setSelectedRule(null)}
                variant="secondary"
              >
                Close
              </Button>
            </div>
          </div>
        </Card>
      </div>
    )
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Input Validation & Sanitization</h1>
        <Button
          onClick={() => navigate('/settings')}
          variant="secondary"
        >
          Back to Settings
        </Button>
      </div>

      {/* Tabs */}
      <div className="border-b">
        <nav className="-mb-px flex space-x-8">
          {['overview', 'rules', 'logs', 'implementation'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-2 px-1 border-b-2 font-medium text-sm capitalize
                ${activeTab === tab
                  ? 'border-primary text-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : (
        <>
          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'rules' && renderRules()}
          {activeTab === 'logs' && renderLogs()}
          {activeTab === 'implementation' && renderImplementation()}
        </>
      )}

      {renderSelectedRule()}
    </div>
  );
};

export default InputValidationPage;
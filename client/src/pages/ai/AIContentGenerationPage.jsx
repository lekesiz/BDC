import { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { Button } from '../../components/ui/button';
import { Card } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Textarea } from '../../components/ui/textarea';
import { Select } from '../../components/ui/select';
import { Badge } from '../../components/ui/badge';
import {
  Loader2,
  Wand2,
  FileText,
  MessageSquare,
  Mail,
  BookOpen,
  Download,
  Copy,
  Save,
  RefreshCw,
  Check
} from 'lucide-react';

const AIContentGenerationPage = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [contentType, setContentType] = useState('feedback');
  const [context, setContext] = useState({
    beneficiary_id: '',
    program_id: '',
    test_id: '',
    custom_prompt: ''
  });
  const [generatedContent, setGeneratedContent] = useState('');
  const [contentTitle, setContentTitle] = useState('');
  const [beneficiaries, setBeneficiaries] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [tests, setTests] = useState([]);
  const [savedTemplates, setSavedTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [copied, setCopied] = useState(false);

  const contentTypes = [
    { value: 'feedback', label: 'Test Feedback', icon: MessageSquare },
    { value: 'report', label: 'Progress Report', icon: FileText },
    { value: 'email', label: 'Email Template', icon: Mail },
    { value: 'learning_path', label: 'Learning Path', icon: BookOpen },
    { value: 'announcement', label: 'Announcement', icon: FileText },
    { value: 'custom', label: 'Custom Content', icon: Wand2 }
  ];

  useEffect(() => {
    fetchBeneficiaries();
    fetchPrograms();
    fetchTests();
    fetchTemplates();
  }, []);

  const fetchBeneficiaries = async () => {
    try {
      const res = await fetch('/api/beneficiaries', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!res.ok) throw new Error('Failed to fetch beneficiaries');

      const data = await res.json();
      setBeneficiaries(data);
    } catch (error) {
      console.error('Error fetching beneficiaries:', error);
    }
  };

  const fetchPrograms = async () => {
    try {
      const res = await fetch('/api/programs', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!res.ok) throw new Error('Failed to fetch programs');

      const data = await res.json();
      setPrograms(data);
    } catch (error) {
      console.error('Error fetching programs:', error);
    }
  };

  const fetchTests = async () => {
    try {
      const res = await fetch('/api/tests', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!res.ok) throw new Error('Failed to fetch tests');

      const data = await res.json();
      setTests(data);
    } catch (error) {
      console.error('Error fetching tests:', error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const res = await fetch('/api/ai/content-templates', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!res.ok) throw new Error('Failed to fetch templates');

      const data = await res.json();
      setSavedTemplates(data);
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const handleGenerateContent = async () => {
    if (!contentType || (contentType !== 'custom' && !context.beneficiary_id)) {
      toast({
        title: 'Error',
        description: 'Please select required fields',
        variant: 'destructive'
      });
      return;
    }

    setGenerating(true);
    try {
      const res = await fetch('/api/ai/generate-content', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          content_type: contentType,
          context
        })
      });

      if (!res.ok) throw new Error('Failed to generate content');

      const data = await res.json();
      setGeneratedContent(data.content);
      setContentTitle(data.title || '');

      toast({
        title: 'Success',
        description: 'Content generated successfully'
      });
    } catch (error) {
      console.error('Error generating content:', error);
      toast({
        title: 'Error',
        description: 'Failed to generate content',
        variant: 'destructive'
      });
    } finally {
      setGenerating(false);
    }
  };

  const handleSaveContent = async () => {
    if (!contentTitle || !generatedContent) {
      toast({
        title: 'Error',
        description: 'Please provide a title for the content',
        variant: 'destructive'
      });
      return;
    }

    setSaving(true);
    try {
      const res = await fetch('/api/ai/content-templates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          title: contentTitle,
          content: generatedContent,
          type: contentType,
          context
        })
      });

      if (!res.ok) throw new Error('Failed to save content');

      toast({
        title: 'Success',
        description: 'Content saved as template'
      });

      fetchTemplates();
    } catch (error) {
      console.error('Error saving content:', error);
      toast({
        title: 'Error',
        description: 'Failed to save content',
        variant: 'destructive'
      });
    } finally {
      setSaving(false);
    }
  };

  const handleCopyContent = () => {
    navigator.clipboard.writeText(generatedContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    toast({
      title: 'Success',
      description: 'Content copied to clipboard'
    });
  };

  const handleExportContent = () => {
    const blob = new Blob([generatedContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${contentTitle || 'generated_content'}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const handleSelectTemplate = (templateId) => {
    const template = savedTemplates.find(t => t.id === templateId);
    if (template) {
      setGeneratedContent(template.content);
      setContentTitle(template.title);
      setContentType(template.type);
      setContext(template.context || {});
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Wand2 className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-bold text-gray-900">AI Content Generation</h1>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Settings Panel */}
        <div className="lg:col-span-1">
          <Card className="p-6 space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Content Type
              </label>
              <div className="grid grid-cols-2 gap-2">
                {contentTypes.map((type) => {
                  const Icon = type.icon;
                  return (
                    <button
                      key={type.value}
                      onClick={() => setContentType(type.value)}
                      className={`p-3 border rounded-lg text-center transition-colors ${
                        contentType === type.value
                          ? 'border-primary bg-primary/5 text-primary'
                          : 'border-gray-300 hover:border-gray-400'
                      }`}
                    >
                      <Icon className="h-5 w-5 mx-auto mb-1" />
                      <span className="text-xs">{type.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {contentType !== 'custom' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Beneficiary
                </label>
                <Select
                  value={context.beneficiary_id}
                  onChange={(e) => setContext({ ...context, beneficiary_id: e.target.value })}
                >
                  <option value="">Select beneficiary</option>
                  {beneficiaries.map((beneficiary) => (
                    <option key={beneficiary.id} value={beneficiary.id}>
                      {beneficiary.full_name}
                    </option>
                  ))}
                </Select>
              </div>
            )}

            {(contentType === 'feedback' || contentType === 'report') && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Test (Optional)
                </label>
                <Select
                  value={context.test_id}
                  onChange={(e) => setContext({ ...context, test_id: e.target.value })}
                >
                  <option value="">Select test</option>
                  {tests.map((test) => (
                    <option key={test.id} value={test.id}>
                      {test.title}
                    </option>
                  ))}
                </Select>
              </div>
            )}

            {contentType === 'learning_path' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Program (Optional)
                </label>
                <Select
                  value={context.program_id}
                  onChange={(e) => setContext({ ...context, program_id: e.target.value })}
                >
                  <option value="">Select program</option>
                  {programs.map((program) => (
                    <option key={program.id} value={program.id}>
                      {program.name}
                    </option>
                  ))}
                </Select>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Additional Context (Optional)
              </label>
              <Textarea
                value={context.custom_prompt}
                onChange={(e) => setContext({ ...context, custom_prompt: e.target.value })}
                rows={3}
                placeholder="Provide any additional context or requirements..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Use Template
              </label>
              <Select
                value={selectedTemplate}
                onChange={(e) => {
                  setSelectedTemplate(e.target.value);
                  handleSelectTemplate(e.target.value);
                }}
              >
                <option value="">Select a template</option>
                {savedTemplates.filter(t => t.type === contentType).map((template) => (
                  <option key={template.id} value={template.id}>
                    {template.title}
                  </option>
                ))}
              </Select>
            </div>

            <Button
              onClick={handleGenerateContent}
              disabled={generating}
              className="w-full"
            >
              {generating ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Wand2 className="h-4 w-4 mr-2" />
                  Generate Content
                </>
              )}
            </Button>
          </Card>
        </div>

        {/* Content Area */}
        <div className="lg:col-span-2">
          <Card className="p-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Input
                  type="text"
                  placeholder="Content title..."
                  value={contentTitle}
                  onChange={(e) => setContentTitle(e.target.value)}
                  className="flex-1 mr-3"
                />
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCopyContent}
                    disabled={!generatedContent}
                  >
                    {copied ? (
                      <Check className="h-4 w-4" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleExportContent}
                    disabled={!generatedContent}
                  >
                    <Download className="h-4 w-4" />
                  </Button>
                  <Button
                    size="sm"
                    onClick={handleSaveContent}
                    disabled={!generatedContent || saving}
                  >
                    {saving ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Save className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>

              <Textarea
                value={generatedContent}
                onChange={(e) => setGeneratedContent(e.target.value)}
                rows={20}
                placeholder="AI generated content will appear here..."
                className="font-mono text-sm"
              />

              {generatedContent && (
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <span>{generatedContent.split(/\s+/).length} words</span>
                  <span>{generatedContent.length} characters</span>
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default AIContentGenerationPage;
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { File, Upload, AlertCircle, CheckCircle, X, FileText, Image, Code, Archive, ChevronLeft, ChevronRight } from 'lucide-react';
import axios from '../../../lib/api';
import { toast } from '../../../hooks/useToast';
import { Button } from '../../../components/ui/button';
import { Card } from '../../../components/ui/card';
import { Alert } from '../../../components/ui/alert';
import { Badge } from '../../../components/ui/badge';
import { Tabs } from '../../../components/ui/tabs';
const PortalAssessmentSubmissionPage = () => {
  const { assessmentId, assignmentId } = useParams();
  const navigate = useNavigate();
  const [assessment, setAssessment] = useState(null);
  const [submission, setSubmission] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [files, setFiles] = useState([]);
  const [notes, setNotes] = useState('');
  const [selectedRequirement, setSelectedRequirement] = useState(0);
  const [requirementStatus, setRequirementStatus] = useState({});
  useEffect(() => {
    fetchAssessmentAndSubmission();
  }, [assessmentId, assignmentId]);
  const fetchAssessmentAndSubmission = async () => {
    try {
      const [assessmentRes, submissionRes] = await Promise.all([
        axios.get(`/api/portal/assessments/${assessmentId}/assignments/${assignmentId}`),
        axios.get(`/api/portal/assessments/${assessmentId}/assignments/${assignmentId}/submission`)
      ]);
      setAssessment(assessmentRes.data);
      if (submissionRes.data) {
        setSubmission(submissionRes.data);
        setFiles(submissionRes.data.files || []);
        setNotes(submissionRes.data.notes || '');
        // Initialize requirement status from existing submission
        const status = {};
        submissionRes.data.requirements?.forEach(req => {
          status[req.id] = req.completed;
        });
        setRequirementStatus(status);
      } else {
        // Initialize empty requirement status
        const status = {};
        assessmentRes.data.requirements?.forEach(req => {
          status[req.id] = false;
        });
        setRequirementStatus(status);
      }
    } catch (error) {
      console.error('Error fetching assessment:', error);
      toast({
        title: 'Error',
        description: 'Failed to load assessment details',
        variant: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  const handleFileUpload = (event) => {
    const uploadedFiles = Array.from(event.target.files);
    const newFiles = uploadedFiles.map(file => ({
      id: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      type: file.type,
      file: file,
      uploadedAt: new Date().toISOString()
    }));
    setFiles([...files, ...newFiles]);
  };
  const removeFile = (fileId) => {
    setFiles(files.filter(f => f.id !== fileId));
  };
  const toggleRequirement = (requirementId) => {
    setRequirementStatus(prev => ({
      ...prev,
      [requirementId]: !prev[requirementId]
    }));
  };
  const calculateProgress = () => {
    const totalRequirements = assessment?.requirements?.length || 0;
    const completedRequirements = Object.values(requirementStatus).filter(Boolean).length;
    return totalRequirements > 0 ? (completedRequirements / totalRequirements) * 100 : 0;
  };
  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      // In a real app, you would upload files to a file service first
      const submissionData = {
        assessmentId,
        assignmentId,
        files: files.map(f => ({
          id: f.id,
          name: f.name,
          size: f.size,
          type: f.type,
          url: f.url || `https://storage.example.com/${f.id}` // Mock URL
        })),
        notes,
        requirements: assessment.requirements.map(req => ({
          id: req.id,
          completed: requirementStatus[req.id] || false
        })),
        submittedAt: new Date().toISOString()
      };
      await axios.post(`/api/portal/assessments/${assessmentId}/assignments/${assignmentId}/submit`, submissionData);
      toast({
        title: 'Success',
        description: 'Your assessment has been submitted successfully',
        variant: 'success'
      });
      navigate(`/portal/assessments/results/${assessmentId}/${assignmentId}`);
    } catch (error) {
      console.error('Error submitting assessment:', error);
      toast({
        title: 'Error',
        description: 'Failed to submit assessment',
        variant: 'error'
      });
    } finally {
      setSubmitting(false);
    }
  };
  const handleSaveDraft = async () => {
    try {
      const draftData = {
        files,
        notes,
        requirements: assessment.requirements.map(req => ({
          id: req.id,
          completed: requirementStatus[req.id] || false
        })),
        savedAt: new Date().toISOString()
      };
      await axios.post(`/api/portal/assessments/${assessmentId}/assignments/${assignmentId}/save-draft`, draftData);
      toast({
        title: 'Draft Saved',
        description: 'Your progress has been saved',
        variant: 'success'
      });
    } catch (error) {
      console.error('Error saving draft:', error);
      toast({
        title: 'Error',
        description: 'Failed to save draft',
        variant: 'error'
      });
    }
  };
  const getFileIcon = (type) => {
    if (type.startsWith('image/')) return <Image className="h-5 w-5" />;
    if (type.includes('pdf') || type.includes('document')) return <FileText className="h-5 w-5" />;
    if (type.includes('code') || type.includes('text')) return <Code className="h-5 w-5" />;
    if (type.includes('zip') || type.includes('archive')) return <Archive className="h-5 w-5" />;
    return <File className="h-5 w-5" />;
  };
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };
  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }
  if (!assessment) {
    return (
      <div className="p-6">
        <Alert variant="error">
          <AlertCircle className="h-4 w-4" />
          <div>
            <h3 className="font-semibold">Assessment Not Found</h3>
            <p>The assessment you're looking for doesn't exist or you don't have access to it.</p>
          </div>
        </Alert>
      </div>
    );
  }
  const progress = calculateProgress();
  const currentRequirement = assessment.requirements[selectedRequirement];
  const isOverdue = new Date(assessment.dueDate) < new Date();
  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-1">{assessment.title}</h1>
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <span>Course: {assessment.courseName}</span>
              <span>•</span>
              <span>Due: {new Date(assessment.dueDate).toLocaleDateString()}</span>
              {isOverdue && (
                <>
                  <span>•</span>
                  <Badge variant="error">Overdue</Badge>
                </>
              )}
            </div>
          </div>
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              onClick={handleSaveDraft}
              disabled={submitting}
            >
              Save Draft
            </Button>
            <Button 
              onClick={handleSubmit}
              disabled={submitting || progress < 100}
            >
              Submit Assessment
            </Button>
          </div>
        </div>
        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Progress</span>
            <span className="text-sm text-gray-600">{Math.round(progress)}% Complete</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>
      {/* Main Content */}
      <div className="grid grid-cols-3 gap-6">
        {/* Requirements Panel */}
        <div className="col-span-1">
          <Card>
            <div className="p-4 border-b">
              <h2 className="font-semibold text-gray-900">Requirements</h2>
              <p className="text-sm text-gray-600 mt-1">Complete all requirements to submit</p>
            </div>
            <div className="p-4 space-y-3">
              {assessment.requirements.map((requirement, index) => (
                <div 
                  key={requirement.id}
                  className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                    selectedRequirement === index 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                  onClick={() => setSelectedRequirement(index)}
                >
                  <div className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      checked={requirementStatus[requirement.id] || false}
                      onChange={(e) => {
                        e.stopPropagation();
                        toggleRequirement(requirement.id);
                      }}
                      className="mt-0.5"
                    />
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900 text-sm">{requirement.title}</h3>
                      <p className="text-xs text-gray-600 mt-1">{requirement.points} points</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
        {/* Work Area */}
        <div className="col-span-2 space-y-6">
          {/* Requirement Details */}
          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">{currentRequirement.title}</h2>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSelectedRequirement(Math.max(0, selectedRequirement - 1))}
                    disabled={selectedRequirement === 0}
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <span className="text-sm text-gray-600">
                    {selectedRequirement + 1} of {assessment.requirements.length}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSelectedRequirement(Math.min(assessment.requirements.length - 1, selectedRequirement + 1))}
                    disabled={selectedRequirement === assessment.requirements.length - 1}
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <div className="prose max-w-none">
                <p className="text-gray-700 mb-4">{currentRequirement.description}</p>
                {currentRequirement.rubric && (
                  <div className="bg-gray-50 rounded-lg p-4 mt-4">
                    <h4 className="font-medium text-gray-900 mb-2">Grading Criteria</h4>
                    <ul className="space-y-2">
                      {currentRequirement.rubric.map((criteria, index) => (
                        <li key={index} className="text-sm text-gray-700">
                          <span className="font-medium">{criteria.level}:</span> {criteria.description}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </Card>
          {/* File Upload */}
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Files</h3>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Files
                </label>
                <div className="flex items-center justify-center w-full">
                  <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                    <div className="flex flex-col items-center justify-center pt-2 pb-3">
                      <Upload className="w-8 h-8 mb-2 text-gray-400" />
                      <p className="mb-1 text-sm text-gray-500">
                        <span className="font-semibold">Click to upload</span> or drag and drop
                      </p>
                      <p className="text-xs text-gray-500">Any file type up to 10MB</p>
                    </div>
                    <input 
                      type="file" 
                      className="hidden" 
                      multiple
                      onChange={handleFileUpload}
                    />
                  </label>
                </div>
              </div>
              {files.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-medium text-gray-900">Uploaded Files</h4>
                  {files.map(file => (
                    <div key={file.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="text-gray-500">
                          {getFileIcon(file.type)}
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{file.name}</p>
                          <p className="text-sm text-gray-600">{formatFileSize(file.size)}</p>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFile(file.id)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Card>
          {/* Notes */}
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Additional Notes</h3>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="w-full p-3 border rounded-lg resize-none focus:ring-2 focus:ring-blue-500"
                rows={6}
                placeholder="Add any additional notes or comments for your instructor..."
              />
            </div>
          </Card>
        </div>
      </div>
      {/* Submission Alert */}
      {progress === 100 && (
        <Alert className="mt-6" variant="success">
          <CheckCircle className="h-4 w-4" />
          <div>
            <h3 className="font-semibold">Ready to Submit</h3>
            <p>You've completed all requirements. Review your work and click "Submit Assessment" when ready.</p>
          </div>
        </Alert>
      )}
    </div>
  );
};
export default PortalAssessmentSubmissionPage;
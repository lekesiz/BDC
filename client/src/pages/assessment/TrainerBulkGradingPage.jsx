import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircle, XCircle, AlertCircle, Filter, Download, Upload, Save, CheckSquare, Square, ChevronDown, ChevronRight } from 'lucide-react';
import axios from '../../lib/api';
import { toast } from '../../hooks/useToast';
import { Button } from '../../components/ui/button';
import { Card } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Select } from '../../components/ui/select';
import { Badge } from '../../components/ui/badge';
import { Table } from '../../components/ui/table';
import { Checkbox } from '../../components/ui/checkbox';
import { Tabs } from '../../components/ui/tabs';
import { Textarea } from '../../components/ui';
const TrainerBulkGradingPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const assessmentId = searchParams.get('assessmentId');
  const assignmentId = searchParams.get('assignmentId');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [assessment, setAssessment] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [selectedSubmissions, setSelectedSubmissions] = useState([]);
  const [filters, setFilters] = useState({
    status: 'all',
    gradingStatus: 'pending',
    search: ''
  });
  const [bulkActions, setBulkActions] = useState({
    score: '',
    feedback: '',
    status: ''
  });
  const [expandedRows, setExpandedRows] = useState({});
  const [sortConfig, setSortConfig] = useState({ key: 'studentName', direction: 'asc' });
  const [activeTab, setActiveTab] = useState('individual');
  useEffect(() => {
    fetchData();
  }, [assessmentId, assignmentId]);
  const fetchData = async () => {
    try {
      setLoading(true);
      const [assessmentRes, submissionsRes] = await Promise.all([
        axios.get(`/api/assessments/${assessmentId}/assignments/${assignmentId}`),
        axios.get(`/api/assessments/${assessmentId}/assignments/${assignmentId}/submissions`)
      ]);
      setAssessment(assessmentRes.data);
      setSubmissions(submissionsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast({
        title: 'Error',
        description: 'Failed to load grading data',
        variant: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  const handleSelectAll = () => {
    if (selectedSubmissions.length === filteredSubmissions.length) {
      setSelectedSubmissions([]);
    } else {
      setSelectedSubmissions(filteredSubmissions.map(s => s.id));
    }
  };
  const handleSelectSubmission = (submissionId) => {
    if (selectedSubmissions.includes(submissionId)) {
      setSelectedSubmissions(selectedSubmissions.filter(id => id !== submissionId));
    } else {
      setSelectedSubmissions([...selectedSubmissions, submissionId]);
    }
  };
  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };
  const handleQuickScore = (submissionId, score) => {
    setSubmissions(submissions.map(sub => 
      sub.id === submissionId ? { ...sub, score, gradingStatus: 'graded' } : sub
    ));
  };
  const handleBulkGrade = async () => {
    if (selectedSubmissions.length === 0) {
      toast({
        title: 'Error',
        description: 'No submissions selected',
        variant: 'error'
      });
      return;
    }
    setSaving(true);
    try {
      const updates = selectedSubmissions.map(submissionId => ({
        submissionId,
        score: bulkActions.score ? parseFloat(bulkActions.score) : undefined,
        feedback: bulkActions.feedback || undefined,
        status: bulkActions.status || undefined
      }));
      await axios.post(`/api/assessments/${assessmentId}/assignments/${assignmentId}/bulk-grade`, {
        updates
      });
      toast({
        title: 'Success',
        description: `${selectedSubmissions.length} submissions graded successfully`,
        variant: 'success'
      });
      fetchData();
      setSelectedSubmissions([]);
      setBulkActions({ score: '', feedback: '', status: '' });
    } catch (error) {
      console.error('Error bulk grading:', error);
      toast({
        title: 'Error',
        description: 'Failed to save grades',
        variant: 'error'
      });
    } finally {
      setSaving(false);
    }
  };
  const handleExportResults = async () => {
    try {
      const response = await axios.get(
        `/api/assessments/${assessmentId}/assignments/${assignmentId}/export`,
        { responseType: 'blob' }
      );
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${assessment.title}-grades.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast({
        title: 'Success',
        description: 'Grades exported successfully',
        variant: 'success'
      });
    } catch (error) {
      console.error('Error exporting results:', error);
      toast({
        title: 'Error',
        description: 'Failed to export grades',
        variant: 'error'
      });
    }
  };
  const handleImportGrades = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      await axios.post(
        `/api/assessments/${assessmentId}/assignments/${assignmentId}/import-grades`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      toast({
        title: 'Success',
        description: 'Grades imported successfully',
        variant: 'success'
      });
      fetchData();
    } catch (error) {
      console.error('Error importing grades:', error);
      toast({
        title: 'Error',
        description: 'Failed to import grades',
        variant: 'error'
      });
    }
  };
  const toggleRowExpansion = (submissionId) => {
    setExpandedRows(prev => ({
      ...prev,
      [submissionId]: !prev[submissionId]
    }));
  };
  // Filter and sort submissions
  const filteredSubmissions = submissions.filter(submission => {
    if (filters.status !== 'all' && submission.status !== filters.status) return false;
    if (filters.gradingStatus !== 'all' && submission.gradingStatus !== filters.gradingStatus) return false;
    if (filters.search && !submission.studentName.toLowerCase().includes(filters.search.toLowerCase())) return false;
    return true;
  }).sort((a, b) => {
    const aValue = a[sortConfig.key];
    const bValue = b[sortConfig.key];
    if (sortConfig.direction === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });
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
  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Bulk Grading</h1>
            <p className="text-gray-600 mt-1">
              {assessment.title} - {filteredSubmissions.length} submissions
            </p>
          </div>
          <div className="flex gap-2">
            <label htmlFor="import-file">
              <Button variant="outline" as="span">
                <Upload className="h-4 w-4 mr-2" />
                Import Grades
              </Button>
              <input
                id="import-file"
                type="file"
                accept=".csv,.xlsx"
                className="hidden"
                onChange={handleImportGrades}
              />
            </label>
            <Button onClick={handleExportResults} variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export Results
            </Button>
            <Button onClick={() => navigate(-1)} variant="outline">
              Back
            </Button>
          </div>
        </div>
      </div>
      {/* Filters */}
      <Card className="mb-6">
        <div className="p-4 flex items-center gap-4">
          <div className="flex-1">
            <Input
              placeholder="Search students..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="max-w-xs"
            />
          </div>
          <Select
            value={filters.status}
            onValueChange={(value) => setFilters({ ...filters, status: value })}
          >
            <Select.Option value="all">All Submissions</Select.Option>
            <Select.Option value="submitted">Submitted</Select.Option>
            <Select.Option value="late">Late</Select.Option>
            <Select.Option value="missing">Missing</Select.Option>
          </Select>
          <Select
            value={filters.gradingStatus}
            onValueChange={(value) => setFilters({ ...filters, gradingStatus: value })}
          >
            <Select.Option value="all">All Grading Status</Select.Option>
            <Select.Option value="pending">Pending</Select.Option>
            <Select.Option value="graded">Graded</Select.Option>
            <Select.Option value="reviewed">Reviewed</Select.Option>
          </Select>
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4 mr-2" />
            More Filters
          </Button>
        </div>
      </Card>
      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <Tabs.TabsList>
          <Tabs.TabTrigger value="individual">Individual Grading</Tabs.TabTrigger>
          <Tabs.TabTrigger value="bulk">Bulk Actions</Tabs.TabTrigger>
          <Tabs.TabTrigger value="overview">Overview</Tabs.TabTrigger>
        </Tabs.TabsList>
        {/* Individual Grading Tab */}
        <Tabs.TabContent value="individual">
          <Card>
            <div className="overflow-x-auto">
              <Table>
                <Table.Header>
                  <Table.Row>
                    <Table.Head className="w-12">
                      <Checkbox
                        checked={selectedSubmissions.length === filteredSubmissions.length}
                        onCheckedChange={handleSelectAll}
                      />
                    </Table.Head>
                    <Table.Head className="w-12"></Table.Head>
                    <Table.Head 
                      onClick={() => handleSort('studentName')}
                      className="cursor-pointer"
                    >
                      Student {sortConfig.key === 'studentName' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                    </Table.Head>
                    <Table.Head>Status</Table.Head>
                    <Table.Head 
                      onClick={() => handleSort('submittedAt')}
                      className="cursor-pointer"
                    >
                      Submitted {sortConfig.key === 'submittedAt' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                    </Table.Head>
                    <Table.Head 
                      onClick={() => handleSort('score')}
                      className="cursor-pointer"
                    >
                      Score {sortConfig.key === 'score' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                    </Table.Head>
                    <Table.Head>Quick Grade</Table.Head>
                    <Table.Head>Actions</Table.Head>
                  </Table.Row>
                </Table.Header>
                <Table.Body>
                  {filteredSubmissions.map(submission => (
                    <React.Fragment key={submission.id}>
                      <Table.Row>
                        <Table.Cell>
                          <Checkbox
                            checked={selectedSubmissions.includes(submission.id)}
                            onCheckedChange={() => handleSelectSubmission(submission.id)}
                          />
                        </Table.Cell>
                        <Table.Cell>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => toggleRowExpansion(submission.id)}
                          >
                            {expandedRows[submission.id] ? 
                              <ChevronDown className="h-4 w-4" /> : 
                              <ChevronRight className="h-4 w-4" />
                            }
                          </Button>
                        </Table.Cell>
                        <Table.Cell className="font-medium">
                          {submission.studentName}
                        </Table.Cell>
                        <Table.Cell>
                          <Badge
                            variant={
                              submission.status === 'submitted' ? 'success' :
                              submission.status === 'late' ? 'warning' :
                              'error'
                            }
                          >
                            {submission.status}
                          </Badge>
                        </Table.Cell>
                        <Table.Cell>
                          {new Date(submission.submittedAt).toLocaleDateString()}
                        </Table.Cell>
                        <Table.Cell>
                          {submission.score !== null ? (
                            <Badge variant="default">{submission.score}%</Badge>
                          ) : (
                            <span className="text-gray-500">-</span>
                          )}
                        </Table.Cell>
                        <Table.Cell>
                          <div className="flex items-center gap-2">
                            <Input
                              type="number"
                              min="0"
                              max="100"
                              value={submission.score || ''}
                              onChange={(e) => handleQuickScore(submission.id, e.target.value)}
                              className="w-20"
                              placeholder="Score"
                            />
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleQuickScore(submission.id, submission.autoScore)}
                              disabled={!submission.autoScore}
                            >
                              Auto
                            </Button>
                          </div>
                        </Table.Cell>
                        <Table.Cell>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => navigate(`/assessment/submission/${submission.id}`)}
                          >
                            View
                          </Button>
                        </Table.Cell>
                      </Table.Row>
                      {/* Expanded Row */}
                      {expandedRows[submission.id] && (
                        <Table.Row>
                          <Table.Cell colSpan={8} className="bg-gray-50">
                            <div className="p-4 space-y-4">
                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <h4 className="font-medium mb-2">Submission Details</h4>
                                  <div className="space-y-1 text-sm">
                                    <p>Email: {submission.studentEmail}</p>
                                    <p>Course: {submission.courseName}</p>
                                    <p>Attempts: {submission.attempts}</p>
                                    {submission.gradedBy && (
                                      <p>Graded by: {submission.gradedBy}</p>
                                    )}
                                  </div>
                                </div>
                                <div>
                                  <h4 className="font-medium mb-2">Quick Feedback</h4>
                                  <Textarea
                                    value={submission.feedback || ''}
                                    onChange={(e) => {
                                      setSubmissions(submissions.map(s => 
                                        s.id === submission.id ? { ...s, feedback: e.target.value } : s
                                      ));
                                    }}
                                    placeholder="Add feedback..."
                                    rows={3}
                                  />
                                  <Button size="sm" className="mt-2">
                                    Save Feedback
                                  </Button>
                                </div>
                              </div>
                              {submission.answers && (
                                <div>
                                  <h4 className="font-medium mb-2">Answer Summary</h4>
                                  <div className="flex items-center gap-4">
                                    <div className="flex items-center gap-2">
                                      <CheckCircle className="h-4 w-4 text-green-600" />
                                      <span>{submission.correctAnswers} Correct</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <XCircle className="h-4 w-4 text-red-600" />
                                      <span>{submission.incorrectAnswers} Incorrect</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <AlertCircle className="h-4 w-4 text-yellow-600" />
                                      <span>{submission.skippedAnswers} Skipped</span>
                                    </div>
                                  </div>
                                </div>
                              )}
                            </div>
                          </Table.Cell>
                        </Table.Row>
                      )}
                    </React.Fragment>
                  ))}
                </Table.Body>
              </Table>
            </div>
          </Card>
        </Tabs.TabContent>
        {/* Bulk Actions Tab */}
        <Tabs.TabContent value="bulk">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Bulk Actions</h3>
            <p className="text-gray-600 mb-6">
              {selectedSubmissions.length} submission{selectedSubmissions.length !== 1 ? 's' : ''} selected
            </p>
            <div className="space-y-4 max-w-2xl">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Set Score
                </label>
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    min="0"
                    max="100"
                    value={bulkActions.score}
                    onChange={(e) => setBulkActions({ ...bulkActions, score: e.target.value })}
                    placeholder="Enter score (0-100)"
                    className="w-32"
                  />
                  <span className="text-gray-600">%</span>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Set Feedback
                </label>
                <Textarea
                  value={bulkActions.feedback}
                  onChange={(e) => setBulkActions({ ...bulkActions, feedback: e.target.value })}
                  placeholder="Enter feedback to apply to all selected submissions..."
                  rows={4}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Set Status
                </label>
                <Select
                  value={bulkActions.status}
                  onValueChange={(value) => setBulkActions({ ...bulkActions, status: value })}
                >
                  <Select.Option value="">No Change</Select.Option>
                  <Select.Option value="graded">Graded</Select.Option>
                  <Select.Option value="reviewed">Reviewed</Select.Option>
                  <Select.Option value="pending">Pending Review</Select.Option>
                </Select>
              </div>
              <div className="flex gap-2 pt-4">
                <Button 
                  onClick={handleBulkGrade}
                  disabled={saving || selectedSubmissions.length === 0}
                >
                  <Save className="h-4 w-4 mr-2" />
                  Apply to {selectedSubmissions.length} Submission{selectedSubmissions.length !== 1 ? 's' : ''}
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => {
                    setBulkActions({ score: '', feedback: '', status: '' });
                    setSelectedSubmissions([]);
                  }}
                >
                  Clear Selection
                </Button>
              </div>
            </div>
          </Card>
        </Tabs.TabContent>
        {/* Overview Tab */}
        <Tabs.TabContent value="overview">
          <div className="grid grid-cols-3 gap-6">
            <Card className="p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Grading Progress</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-gray-600">Graded</span>
                    <span className="text-sm text-gray-900">
                      {submissions.filter(s => s.gradingStatus === 'graded').length} / {submissions.length}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full"
                      style={{ 
                        width: `${(submissions.filter(s => s.gradingStatus === 'graded').length / submissions.length) * 100}%` 
                      }}
                    />
                  </div>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Pending</span>
                    <span>{submissions.filter(s => s.gradingStatus === 'pending').length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Reviewed</span>
                    <span>{submissions.filter(s => s.gradingStatus === 'reviewed').length}</span>
                  </div>
                </div>
              </div>
            </Card>
            <Card className="p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Score Distribution</h3>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Average Score</span>
                  <span className="font-medium">
                    {(submissions.reduce((sum, s) => sum + (s.score || 0), 0) / submissions.filter(s => s.score !== null).length).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Highest Score</span>
                  <span className="font-medium">
                    {Math.max(...submissions.map(s => s.score || 0))}%
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Lowest Score</span>
                  <span className="font-medium">
                    {Math.min(...submissions.filter(s => s.score !== null).map(s => s.score))}%
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Pass Rate</span>
                  <span className="font-medium">
                    {((submissions.filter(s => s.score >= assessment.passingScore).length / submissions.filter(s => s.score !== null).length) * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            </Card>
            <Card className="p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Submission Status</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-green-600 rounded-full"></div>
                    <span className="text-sm text-gray-600">On Time</span>
                  </div>
                  <span className="font-medium">{submissions.filter(s => s.status === 'submitted').length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-yellow-600 rounded-full"></div>
                    <span className="text-sm text-gray-600">Late</span>
                  </div>
                  <span className="font-medium">{submissions.filter(s => s.status === 'late').length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-red-600 rounded-full"></div>
                    <span className="text-sm text-gray-600">Missing</span>
                  </div>
                  <span className="font-medium">{submissions.filter(s => s.status === 'missing').length}</span>
                </div>
              </div>
            </Card>
          </div>
        </Tabs.TabContent>
      </Tabs>
    </div>
  );
};
export default TrainerBulkGradingPage;
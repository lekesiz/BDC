// TODO: i18n - processed
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, Download, Search, Filter, Eye, BarChart2, Clock,
  Users, Calendar, CheckCircle, XCircle, AlertTriangle, FileText,
  Brain, Award, PieChart, TrendingUp, User, SortAsc, SortDesc } from
'lucide-react';
import { format } from 'date-fns';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs } from '@/components/ui/tabs';
import { Select } from '@/components/ui/select';
import { useToast } from '@/components/ui/toast';
import { Progress } from '@/components/ui/progress';
import { Table } from '@/components/ui/table';
/**
 * TrainerAssessmentResultsPage displays detailed results and analytics
 * for an assigned assessment
 */import { useTranslation } from "react-i18next";
const TrainerAssessmentResultsPage = () => {const { t } = useTranslation();
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  // State for assessment data
  const [assessment, setAssessment] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  // State for search and filters
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [selectedScore, setSelectedScore] = useState('all');
  const [sortField, setSortField] = useState('submitted_at');
  const [sortDirection, setSortDirection] = useState('desc');
  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        // Fetch assessment details
        const assessmentResponse = await fetch(`/api/assessment/assigned/${id}`);
        if (!assessmentResponse.ok) throw new Error('Failed to fetch assessment details');
        const assessmentData = await assessmentResponse.json();
        setAssessment(assessmentData);
        // Fetch submissions
        const submissionsResponse = await fetch(`/api/assessment/assigned/${id}/submissions`);
        if (!submissionsResponse.ok) throw new Error('Failed to fetch submissions');
        const submissionsData = await submissionsResponse.json();
        setSubmissions(submissionsData);
        // Fetch analytics
        const analyticsResponse = await fetch(`/api/assessment/analytics/assignments/${id}`);
        if (!analyticsResponse.ok) throw new Error('Failed to fetch analytics');
        const analyticsData = await analyticsResponse.json();
        setAnalytics(analyticsData);
      } catch (err) {
        console.error('Error fetching assessment data:', err);
        setError(err.message);
        toast({
          title: 'Error',
          description: 'Failed to load assessment results',
          type: 'error'
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, [id, toast]);
  // Filter and sort submissions
  const filteredSubmissions = submissions.filter((submission) => {
    // Apply search filter
    const matchesSearch =
    searchTerm === '' ||
    submission.student_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    submission.student_id.toLowerCase().includes(searchTerm.toLowerCase());
    // Apply status filter
    const matchesStatus =
    selectedStatus === 'all' ||
    selectedStatus === 'passed' && submission.passed ||
    selectedStatus === 'failed' && !submission.passed ||
    selectedStatus === 'completed' && submission.completed ||
    selectedStatus === 'in_progress' && !submission.completed;
    // Apply score filter
    let matchesScore = true;
    if (selectedScore !== 'all') {
      const score = submission.percentage || 0;
      switch (selectedScore) {
        case '90-100':
          matchesScore = score >= 90 && score <= 100;
          break;
        case '80-89':
          matchesScore = score >= 80 && score < 90;
          break;
        case '70-79':
          matchesScore = score >= 70 && score < 80;
          break;
        case '60-69':
          matchesScore = score >= 60 && score < 70;
          break;
        case 'below-60':
          matchesScore = score < 60;
          break;
        default:
          matchesScore = true;
      }
    }
    return matchesSearch && matchesStatus && matchesScore;
  }).sort((a, b) => {
    // Apply sorting
    let aValue, bValue;
    switch (sortField) {
      case 'student_name':
        aValue = a.student_name || '';
        bValue = b.student_name || '';
        break;
      case 'score':
        aValue = a.score || 0;
        bValue = b.score || 0;
        break;
      case 'time_spent':
        aValue = a.time_spent || 0;
        bValue = b.time_spent || 0;
        break;
      case 'submitted_at':
      default:
        aValue = new Date(a.submitted_at || 0).getTime();
        bValue = new Date(b.submitted_at || 0).getTime();
    }
    if (sortDirection === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });
  // Handle view submission
  const handleViewSubmission = (submissionId) => {
    navigate(`/assessment/submissions/${submissionId}`);
  };
  // Handle sort change
  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };
  // Handle exporting results
  const handleExportCSV = async () => {
    try {
      // Simple function to create CSV content
      const createCSV = (data, fields) => {
        const header = fields.map((f) => f.label).join(',') + '\n';
        const rows = data.map((item) => {
          return fields.map((field) => {
            let value = field.value(item);
            // Wrap string values that may contain commas in quotes
            if (typeof value === 'string' && value.includes(',')) {
              value = `"${value}"`;
            }
            return value;
          }).join(',');
        }).join('\n');
        return header + rows;
      };
      // Define fields for export
      const fields = [
      { label: 'Student ID', value: (item) => item.student_id },
      { label: 'Student Name', value: (item) => item.student_name },
      { label: 'Score', value: (item) => item.score || 0 },
      { label: 'Percentage', value: (item) => item.percentage ? `${item.percentage}%` : '0%' },
      { label: 'Passed', value: (item) => item.passed ? 'Yes' : 'No' },
      { label: 'Completed', value: (item) => item.completed ? 'Yes' : 'No' },
      { label: 'Time Spent (minutes)', value: (item) => item.time_spent || 0 },
      { label: 'Submitted At', value: (item) => item.submitted_at ? new Date(item.submitted_at).toLocaleString() : 'Not submitted' }];

      // Create CSV content
      const csvContent = createCSV(submissions, fields);
      // Create a blob and download it
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `${assessment.title}_results.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      toast({
        title: 'Success',
        description: 'Results exported successfully',
        type: 'success'
      });
    } catch (err) {
      console.error('Error exporting results:', err);
      toast({
        title: 'Error',
        description: 'Failed to export results',
        type: 'error'
      });
    }
  };
  // Handle exporting detailed analytics
  const handleExportDetailedCSV = async () => {
    try {
      // Create a more comprehensive report with analytics
      // This would include question-by-question analysis, etc.
      toast({
        title: 'Exporting',
        description: 'Generating detailed report...',
        type: 'info'
      });
      // In a real implementation, this might call an API endpoint
      // For now, simulate a delay and then download a basic report
      setTimeout(() => {
        handleExportCSV();
        toast({
          title: 'Success',
          description: 'Detailed analytics report generated',
          type: 'success'
        });
      }, 1500);
    } catch (err) {
      console.error('Error exporting detailed analytics:', err);
      toast({
        title: 'Error',
        description: 'Failed to export detailed analytics',
        type: 'error'
      });
    }
  };
  // Render loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
      </div>);

  }
  // Render error state
  if (error || !assessment) {
    return (
      <div className="container mx-auto py-6">
        <div className="flex items-center mb-6">
          <Button
            variant="ghost"
            onClick={() => navigate('/assessment')}
            className="flex items-center">

            <ArrowLeft className="w-4 h-4 mr-2" />{t("pages.back_to_assessments")}

          </Button>
        </div>
        <Card className="p-6 text-center">
          <div className="text-red-500 mb-4">
            <AlertTriangle className="w-12 h-12 mx-auto" />
          </div>
          <h2 className="text-xl font-semibold mb-2">{t("pages.assessment_not_found")}</h2>
          <p className="text-gray-600 mb-4">
            {error || "The requested assessment could not be found or has been deleted."}
          </p>
          <Button onClick={() => navigate('/assessment')}>{t("pages.back_to_assessments")}</Button>
        </Card>
      </div>);

  }
  return (
    <div className="container mx-auto py-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
        <div className="flex items-center mb-4 md:mb-0">
          <Button
            variant="ghost"
            onClick={() => navigate('/assessment')}
            className="flex items-center mr-4">

            <ArrowLeft className="w-4 h-4 mr-2" />{t("components.back")}

          </Button>
          <div>
            <h1 className="text-2xl font-bold">{assessment.title}</h1>
            <p className="text-gray-600">{t("pages.results_and_analytics")}</p>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            onClick={handleExportCSV}
            className="flex items-center">

            <Download className="w-4 h-4 mr-2" />{t("components.export_csv")}

          </Button>
          <Button
            variant="outline"
            onClick={handleExportDetailedCSV}
            className="flex items-center">

            <BarChart2 className="w-4 h-4 mr-2" />{t("pages.detailed_report")}

          </Button>
        </div>
      </div>
      {/* Assessment Info Card */}
      <Card className="p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="flex items-center">
            <Calendar className="w-8 h-8 text-primary mr-4" />
            <div>
              <p className="text-sm text-gray-600">{t("pages.due_date")}</p>
              <p className="font-semibold">
                {new Date(assessment.due_date).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric'
                })}
              </p>
            </div>
          </div>
          <div className="flex items-center">
            <Users className="w-8 h-8 text-primary mr-4" />
            <div>
              <p className="text-sm text-gray-600">{t("pages.assigned_to")}</p>
              <p className="font-semibold">{assessment.assigned_to.name}</p>
              <p className="text-xs text-gray-500">
                {assessment.assigned_to.type === 'cohort' ? 'Cohort' : 'Individual'}
              </p>
            </div>
          </div>
          <div className="flex items-center">
            <CheckCircle className="w-8 h-8 text-green-500 mr-4" />
            <div>
              <p className="text-sm text-gray-600">{t("pages.submissions")}</p>
              <p className="font-semibold">
                {assessment.submissions.completed} / {assessment.submissions.total} completed
              </p>
              <p className="text-xs text-gray-500">
                {Math.round(assessment.submissions.completed / assessment.submissions.total * 100)}{t("pages._completion_rate")}
              </p>
            </div>
          </div>
          <div className="flex items-center">
            <Award className="w-8 h-8 text-amber-500 mr-4" />
            <div>
              <p className="text-sm text-gray-600">{t("components.average_score")}</p>
              <p className="font-semibold">
                {assessment.submissions.averageScore !== null ?
                `${assessment.submissions.averageScore}%` :
                'No submissions yet'}
              </p>
            </div>
          </div>
        </div>
      </Card>
      {/* Tabs */}
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="mb-6">

        <Tabs.TabsList className="mb-6">
          <Tabs.TabTrigger value="overview">
            <BarChart2 className="w-4 h-4 mr-2" />{t("components.overview")}

          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="submissions">
            <FileText className="w-4 h-4 mr-2" />{t("pages.submissions_")}
            {submissions.length})
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="analytics">
            <Brain className="w-4 h-4 mr-2" />{t("pages.detailed_analytics")}

          </Tabs.TabTrigger>
        </Tabs.TabsList>
        {/* Overview Tab */}
        <Tabs.TabContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Completion Status Card */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <CheckCircle className="w-5 h-5 mr-2 text-primary" />{t("pages.completion_status")}

              </h3>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm font-medium">{t("components.completed")}</span>
                    <span className="text-sm text-gray-500">
                      {assessment.submissions.completed} / {assessment.submissions.total} 
                      ({Math.round(assessment.submissions.completed / assessment.submissions.total * 100)}%)
                    </span>
                  </div>
                  <Progress value={assessment.submissions.completed / assessment.submissions.total * 100} className="h-2 bg-gray-200" />
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm font-medium">{t("archive-components.in_progress")}</span>
                    <span className="text-sm text-gray-500">
                      {assessment.submissions.inProgress} / {assessment.submissions.total}
                      ({Math.round(assessment.submissions.inProgress / assessment.submissions.total * 100)}%)
                    </span>
                  </div>
                  <Progress value={assessment.submissions.inProgress / assessment.submissions.total * 100} className="h-2 bg-gray-200 [&>div]:bg-amber-500" />
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm font-medium">{t("components.not_started")}</span>
                    <span className="text-sm text-gray-500">
                      {assessment.submissions.notStarted} / {assessment.submissions.total}
                      ({Math.round(assessment.submissions.notStarted / assessment.submissions.total * 100)}%)
                    </span>
                  </div>
                  <Progress value={assessment.submissions.notStarted / assessment.submissions.total * 100} className="h-2 bg-gray-200 [&>div]:bg-gray-500" />
                </div>
              </div>
              {/* Status counts as bubbles */}
              <div className="flex justify-center space-x-4 mt-8">
                <div className="flex flex-col items-center">
                  <div className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center mb-2">
                    <span className="text-xl font-bold text-green-600">{assessment.submissions.completed}</span>
                  </div>
                  <span className="text-sm text-gray-600">{t("components.completed")}</span>
                </div>
                <div className="flex flex-col items-center">
                  <div className="w-20 h-20 rounded-full bg-amber-100 flex items-center justify-center mb-2">
                    <span className="text-xl font-bold text-amber-600">{assessment.submissions.inProgress}</span>
                  </div>
                  <span className="text-sm text-gray-600">{t("archive-components.in_progress")}</span>
                </div>
                <div className="flex flex-col items-center">
                  <div className="w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center mb-2">
                    <span className="text-xl font-bold text-gray-600">{assessment.submissions.notStarted}</span>
                  </div>
                  <span className="text-sm text-gray-600">{t("components.not_started")}</span>
                </div>
              </div>
            </Card>
            {/* Score Distribution Card */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <PieChart className="w-5 h-5 mr-2 text-primary" />{t("components.score_distribution")}

              </h3>
              {analytics &&
              <div className="space-y-6">
                  {analytics.score_distribution.map((range) =>
                <div key={range.range}>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium">{range.range}%</span>
                        <span className="text-sm text-gray-500">
                          {range.count}{t("pages.students_")}{Math.round(range.count / assessment.submissions.completed * 100)}%)
                        </span>
                      </div>
                      <Progress
                    value={range.count / assessment.submissions.completed * 100}
                    className={`h-4 bg-gray-200 ${
                    range.range === "90-100" ? "[&>div]:bg-green-500" :
                    range.range === "80-89" ? "[&>div]:bg-blue-500" :
                    range.range === "70-79" ? "[&>div]:bg-yellow-500" :
                    range.range === "60-69" ? "[&>div]:bg-orange-500" :
                    "[&>div]:bg-red-500"}`
                    } />

                    </div>
                )}
                </div>
              }
              {/* Average score indicator */}
              {assessment.submissions.averageScore !== null &&
              <div className="mt-8 p-4 bg-purple-50 rounded-lg text-center">
                  <h4 className="text-sm font-medium text-gray-700 mb-1">{t("components.average_score")}</h4>
                  <div className="text-2xl font-bold text-purple-700">{assessment.submissions.averageScore}%</div>
                  <p className="text-sm text-gray-600 mt-1">
                    {assessment.submissions.averageScore >= 90 ? "Excellent" :
                  assessment.submissions.averageScore >= 80 ? "Very Good" :
                  assessment.submissions.averageScore >= 70 ? "Good" :
                  assessment.submissions.averageScore >= 60 ? "Satisfactory" :
                  "Needs Improvement"}
                  </p>
                </div>
              }
            </Card>
            {/* Recent Submissions */}
            <Card className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold flex items-center">
                  <User className="w-5 h-5 mr-2 text-primary" />{t("pages.recent_submissions")}

                </h3>
                <Button
                  variant="link"
                  onClick={() => setActiveTab('submissions')}
                  className="text-sm">{t("archive-components.view_all")}


                </Button>
              </div>
              <div className="space-y-4">
                {submissions.
                filter((s) => s.completed).
                sort((a, b) => new Date(b.submitted_at) - new Date(a.submitted_at)).
                slice(0, 5).
                map((submission) =>
                <div key={submission.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center mr-3 ${
                    submission.passed ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`
                    }>
                          {submission.passed ?
                      <CheckCircle className="w-5 h-5" /> :

                      <XCircle className="w-5 h-5" />
                      }
                        </div>
                        <div>
                          <p className="font-medium">{submission.student_name}</p>
                          <p className="text-sm text-gray-600">
                            {format(new Date(submission.submitted_at), "MMM d, yyyy 'at' h:mm a")}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className={`font-bold ${
                    submission.percentage >= 90 ? 'text-green-600' :
                    submission.percentage >= 80 ? 'text-blue-600' :
                    submission.percentage >= 70 ? 'text-yellow-600' :
                    submission.percentage >= 60 ? 'text-orange-600' :
                    'text-red-600'}`
                    }>
                          {submission.percentage}%
                        </p>
                        <p className="text-sm text-gray-600">{submission.time_spent} mins</p>
                      </div>
                    </div>
                )}
                {submissions.filter((s) => s.completed).length === 0 &&
                <div className="text-center py-6 text-gray-500">{t("pages.no_completed_submissions_yet")}

                </div>
                }
              </div>
            </Card>
            {/* Top Performers */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <TrendingUp className="w-5 h-5 mr-2 text-primary" />{t("components.top_performers")}

              </h3>
              <div className="space-y-4">
                {submissions.
                filter((s) => s.completed).
                sort((a, b) => (b.percentage || 0) - (a.percentage || 0)).
                slice(0, 5).
                map((submission, index) =>
                <div key={submission.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center">
                        <div className="w-8 h-8 rounded-full bg-amber-100 text-amber-800 flex items-center justify-center mr-3 font-bold">
                          {index + 1}
                        </div>
                        <p className="font-medium">{submission.student_name}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-green-600">{submission.percentage}%</p>
                        <p className="text-sm text-gray-600">{submission.time_spent} mins</p>
                      </div>
                    </div>
                )}
                {submissions.filter((s) => s.completed).length === 0 &&
                <div className="text-center py-6 text-gray-500">{t("pages.no_completed_submissions_yet")}

                </div>
                }
              </div>
            </Card>
          </div>
        </Tabs.TabContent>
        {/* Submissions Tab */}
        <Tabs.TabContent value="submissions">
          {/* Filters */}
          <div className="flex flex-col md:flex-row gap-4 items-center mb-6">
            <div className="relative flex-grow">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
              <Input
                type="text"
                placeholder="Search by student name or ID..."
                className="pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)} />

            </div>
            <Select
              value={selectedStatus}
              onValueChange={setSelectedStatus}
              className="w-full md:w-40">

              <Select.Trigger>
                <div className="flex items-center">
                  <Filter className="w-4 h-4 mr-2" />
                  <span>{selectedStatus === 'all' ? 'All Statuses' :
                    selectedStatus === 'passed' ? 'Passed' :
                    selectedStatus === 'failed' ? 'Failed' :
                    selectedStatus === 'completed' ? 'Completed' :
                    'In Progress'}</span>
                </div>
              </Select.Trigger>
              <Select.Content>
                <Select.Item value="all">{t("pages.all_statuses")}</Select.Item>
                <Select.Item value="passed">{t("pages.passed")}</Select.Item>
                <Select.Item value="failed">{t("pages.failed")}</Select.Item>
                <Select.Item value="completed">{t("components.completed")}</Select.Item>
                <Select.Item value="in_progress">{t("archive-components.in_progress")}</Select.Item>
              </Select.Content>
            </Select>
            <Select
              value={selectedScore}
              onValueChange={setSelectedScore}
              className="w-full md:w-40">

              <Select.Trigger>
                <div className="flex items-center">
                  <BarChart2 className="w-4 h-4 mr-2" />
                  <span>{selectedScore === 'all' ? 'All Scores' : selectedScore}</span>
                </div>
              </Select.Trigger>
              <Select.Content>
                <Select.Item value="all">{t("pages.all_scores")}</Select.Item>
                <Select.Item value="90-100">90-100%</Select.Item>
                <Select.Item value="80-89">80-89%</Select.Item>
                <Select.Item value="70-79">70-79%</Select.Item>
                <Select.Item value="60-69">60-69%</Select.Item>
                <Select.Item value="below-60">{t("pages.below_60")}</Select.Item>
              </Select.Content>
            </Select>
          </div>
          {/* Submissions Table */}
          <Card className="mb-6 overflow-hidden">
            <div className="overflow-x-auto">
              <Table>
                <Table.Header>
                  <Table.Row>
                    <Table.Head onClick={() => handleSort('student_name')} className="cursor-pointer">
                      <div className="flex items-center">{t("components.student")}

                        {sortField === 'student_name' && (
                        sortDirection === 'asc' ?
                        <SortAsc className="w-4 h-4 ml-1" /> :
                        <SortDesc className="w-4 h-4 ml-1" />)
                        }
                      </div>
                    </Table.Head>
                    <Table.Head onClick={() => handleSort('score')} className="cursor-pointer">
                      <div className="flex items-center">{t("components.score")}

                        {sortField === 'score' && (
                        sortDirection === 'asc' ?
                        <SortAsc className="w-4 h-4 ml-1" /> :
                        <SortDesc className="w-4 h-4 ml-1" />)
                        }
                      </div>
                    </Table.Head>
                    <Table.Head>{t("components.status")}</Table.Head>
                    <Table.Head onClick={() => handleSort('time_spent')} className="cursor-pointer">
                      <div className="flex items-center">{t("pages.time")}

                        {sortField === 'time_spent' && (
                        sortDirection === 'asc' ?
                        <SortAsc className="w-4 h-4 ml-1" /> :
                        <SortDesc className="w-4 h-4 ml-1" />)
                        }
                      </div>
                    </Table.Head>
                    <Table.Head onClick={() => handleSort('submitted_at')} className="cursor-pointer">
                      <div className="flex items-center">{t("pages.submitted")}

                        {sortField === 'submitted_at' && (
                        sortDirection === 'asc' ?
                        <SortAsc className="w-4 h-4 ml-1" /> :
                        <SortDesc className="w-4 h-4 ml-1" />)
                        }
                      </div>
                    </Table.Head>
                    <Table.Head>{t("components.actions")}</Table.Head>
                  </Table.Row>
                </Table.Header>
                <Table.Body>
                  {filteredSubmissions.length > 0 ?
                  filteredSubmissions.map((submission) =>
                  <Table.Row key={submission.id}>
                        <Table.Cell>
                          <div className="font-medium">{submission.student_name}</div>
                          <div className="text-sm text-gray-500">{submission.student_id}</div>
                        </Table.Cell>
                        <Table.Cell>
                          {submission.completed ?
                      <div className="flex items-center">
                              <span className={`font-medium ${
                        submission.percentage >= 90 ? 'text-green-600' :
                        submission.percentage >= 80 ? 'text-blue-600' :
                        submission.percentage >= 70 ? 'text-yellow-600' :
                        submission.percentage >= 60 ? 'text-orange-600' :
                        'text-red-600'}`
                        }>
                                {submission.score}/{submission.percentage}%
                              </span>
                            </div> :

                      <span className="text-gray-500">-</span>
                      }
                        </Table.Cell>
                        <Table.Cell>
                          {submission.completed ?
                      submission.passed ?
                      <Badge className="bg-green-100 text-green-800">{t("pages.passed")}</Badge> :

                      <Badge className="bg-red-100 text-red-800">{t("pages.failed")}</Badge> :


                      <Badge className="bg-amber-100 text-amber-800">{t("archive-components.in_progress")}</Badge>
                      }
                        </Table.Cell>
                        <Table.Cell>
                          {submission.time_spent ?
                      <div className="flex items-center">
                              <Clock className="w-4 h-4 mr-1 text-gray-500" />
                              <span>{submission.time_spent} mins</span>
                            </div> :

                      <span className="text-gray-500">-</span>
                      }
                        </Table.Cell>
                        <Table.Cell>
                          {submission.submitted_at ?
                      format(new Date(submission.submitted_at), "MMM d, yyyy") :

                      <span className="text-gray-500">{t("pages.not_submitted")}</span>
                      }
                        </Table.Cell>
                        <Table.Cell>
                          <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleViewSubmission(submission.id)}
                        className="flex items-center"
                        disabled={!submission.completed}>

                            <Eye className="w-4 h-4 mr-1" />{t("mobile.view")}

                      </Button>
                        </Table.Cell>
                      </Table.Row>
                  ) :

                  <Table.Row>
                      <Table.Cell colSpan={6} className="text-center py-6 text-gray-500">{t("pages.no_submissions_match_your_filters")}

                    </Table.Cell>
                    </Table.Row>
                  }
                </Table.Body>
              </Table>
            </div>
          </Card>
          {/* Submissions Summary */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="p-4 bg-green-50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{t("pages.passed")}</p>
                  <p className="text-2xl font-bold text-green-700">
                    {submissions.filter((s) => s.completed && s.passed).length}
                  </p>
                </div>
                <CheckCircle className="w-10 h-10 text-green-500" />
              </div>
            </Card>
            <Card className="p-4 bg-red-50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{t("pages.failed")}</p>
                  <p className="text-2xl font-bold text-red-700">
                    {submissions.filter((s) => s.completed && !s.passed).length}
                  </p>
                </div>
                <XCircle className="w-10 h-10 text-red-500" />
              </div>
            </Card>
            <Card className="p-4 bg-amber-50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{t("archive-components.in_progress")}</p>
                  <p className="text-2xl font-bold text-amber-700">
                    {submissions.filter((s) => !s.completed).length}
                  </p>
                </div>
                <Clock className="w-10 h-10 text-amber-500" />
              </div>
            </Card>
            <Card className="p-4 bg-blue-50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{t("pages.average_time")}</p>
                  <p className="text-2xl font-bold text-blue-700">
                    {analytics?.average_time || '-'} mins
                  </p>
                </div>
                <Clock className="w-10 h-10 text-blue-500" />
              </div>
            </Card>
          </div>
        </Tabs.TabContent>
        {/* Analytics Tab */}
        <Tabs.TabContent value="analytics">
          <div className="grid grid-cols-1 gap-6">
            {/* Question Analysis */}
            {analytics &&
            <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">{t("pages.question_analysis")}</h3>
                <div className="overflow-x-auto">
                  <Table>
                    <Table.Header>
                      <Table.Row>
                        <Table.Head>{t("components.question")}</Table.Head>
                        <Table.Head>{t("pages.correct_rate")}</Table.Head>
                        <Table.Head>{t("pages.avg_time")}</Table.Head>
                        <Table.Head>{t("pages.difficulty")}</Table.Head>
                      </Table.Row>
                    </Table.Header>
                    <Table.Body>
                      {analytics.question_analysis.map((question, index) =>
                    <Table.Row key={question.question_id}>
                          <Table.Cell>
                            <div className="font-medium">{t("components.question")}{index + 1}</div>
                            <div className="text-xs text-gray-500">{question.question_id}</div>
                          </Table.Cell>
                          <Table.Cell>
                            <div className="flex items-center">
                              <div className="w-24 bg-gray-200 rounded-full h-2.5 mr-2">
                                <div
                              className={`h-2.5 rounded-full ${
                              question.correct_rate >= 80 ? 'bg-green-500' :
                              question.correct_rate >= 60 ? 'bg-yellow-500' :
                              'bg-red-500'}`
                              }
                              style={{ width: `${question.correct_rate}%` }}>
                            </div>
                              </div>
                              <span>{question.correct_rate}%</span>
                            </div>
                          </Table.Cell>
                          <Table.Cell>
                            <div className="flex items-center">
                              <Clock className="w-4 h-4 mr-1 text-gray-500" />
                              <span>{question.average_time} sec</span>
                            </div>
                          </Table.Cell>
                          <Table.Cell>
                            <Badge className={
                        question.difficulty_rating === 'easy' ? 'bg-green-100 text-green-800' :
                        question.difficulty_rating === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                        }>
                              {question.difficulty_rating}
                            </Badge>
                          </Table.Cell>
                        </Table.Row>
                    )}
                    </Table.Body>
                  </Table>
                </div>
              </Card>
            }
            {/* Common Mistakes */}
            {analytics && analytics.common_mistakes && analytics.common_mistakes.length > 0 &&
            <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">{t("pages.common_mistakes")}</h3>
                <div className="space-y-4">
                  {analytics.common_mistakes.map((mistake) =>
                <div key={mistake.question_id} className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <p className="font-medium">{t("pages.question_id")}{mistake.question_id}</p>
                          <p className="text-sm text-gray-600">{mistake.description}</p>
                        </div>
                        <Badge className="bg-red-100 text-red-800">{mistake.frequency}{t("pages._of_students")}</Badge>
                      </div>
                    </div>
                )}
                </div>
              </Card>
            }
            {/* Skills Performance */}
            {analytics?.type === 'quiz' &&
            <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">{t("pages.skills_performance")}</h3>
                <div className="space-y-6">
                  {assessment.skills?.map((skill) => {
                  // Find analytics for this skill
                  const skillPerformance = assessment.skills_performance?.find((s) => s.skill === skill);
                  const percentage = skillPerformance?.average_score || 0;
                  return (
                    <div key={skill}>
                        <div className="flex justify-between mb-2">
                          <span className="text-sm font-medium">{skill}</span>
                          <span className="text-sm text-gray-500">{percentage}%</span>
                        </div>
                        <Progress
                        value={percentage}
                        className={`h-3 bg-gray-200 ${
                        percentage >= 90 ? '[&>div]:bg-green-500' :
                        percentage >= 80 ? '[&>div]:bg-blue-500' :
                        percentage >= 70 ? '[&>div]:bg-yellow-500' :
                        percentage >= 60 ? '[&>div]:bg-orange-500' :
                        '[&>div]:bg-red-500'}`
                        } />

                      </div>);

                })}
                </div>
              </Card>
            }
            {/* Time Distribution */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">{t("pages.time_distribution")}</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <p className="font-medium">{t("pages.fastest_completion")}</p>
                  <p className="font-bold text-green-600">
                    {submissions.
                    filter((s) => s.completed).
                    reduce((min, s) => s.time_spent < min ? s.time_spent : min,
                    submissions.filter((s) => s.completed)[0]?.time_spent || 0)
                    } mins
                  </p>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <p className="font-medium">{t("pages.slowest_completion")}</p>
                  <p className="font-bold text-red-600">
                    {submissions.
                    filter((s) => s.completed).
                    reduce((max, s) => s.time_spent > max ? s.time_spent : max, 0)
                    } mins
                  </p>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <p className="font-medium">{t("pages.average_completion_time")}</p>
                  <p className="font-bold text-blue-600">
                    {analytics?.average_time || '-'} mins
                  </p>
                </div>
              </div>
              {/* Time ranges distribution */}
              <div className="mt-6">
                <h4 className="text-sm font-medium mb-4">{t("pages.completion_time_ranges")}</h4>
                {/* Simulate time ranges - in a real app, this would come from analytics */}
                {!analytics?.time_ranges ?
                <div className="text-center py-6 text-gray-500">{t("pages.time_distribution_data_not_available")}

                </div> :

                // Sample rendering of time ranges
                <div className="space-y-4">
                    {[
                  { range: 'Under 15 mins', count: 3 },
                  { range: '15-30 mins', count: 7 },
                  { range: 'Over 30 mins', count: 2 }].
                  map((range) =>
                  <div key={range.range}>
                        <div className="flex justify-between mb-2">
                          <span className="text-sm font-medium">{range.range}</span>
                          <span className="text-sm text-gray-500">
                            {range.count}{t("pages.students_")}{Math.round(range.count / assessment.submissions.completed * 100)}%)
                          </span>
                        </div>
                        <Progress
                      value={range.count / assessment.submissions.completed * 100}
                      className="h-3 bg-gray-200 [&>div]:bg-blue-500" />

                      </div>
                  )}
                  </div>
                }
              </div>
            </Card>
            {/* Students Requiring Attention */}
            {submissions.filter((s) => s.completed && !s.passed).length > 0 &&
            <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <AlertTriangle className="w-5 h-5 mr-2 text-amber-500" />{t("pages.students_requiring_attention")}

              </h3>
                <div className="space-y-4">
                  {submissions.
                filter((s) => s.completed && !s.passed).
                sort((a, b) => (a.percentage || 0) - (b.percentage || 0)).
                map((submission) =>
                <div key={submission.id} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                        <div>
                          <p className="font-medium">{submission.student_name}</p>
                          <p className="text-sm text-gray-600">{submission.student_id}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-red-600">{submission.percentage}%</p>
                          <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleViewSubmission(submission.id)}
                      className="flex items-center mt-2">

                            <Eye className="w-4 h-4 mr-1" />{t("pages.view_submission")}

                    </Button>
                        </div>
                      </div>
                )}
                </div>
              </Card>
            }
          </div>
        </Tabs.TabContent>
      </Tabs>
    </div>);

};
export default TrainerAssessmentResultsPage;
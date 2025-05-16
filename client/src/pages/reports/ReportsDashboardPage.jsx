import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  FileText, 
  Calendar, 
  Users, 
  BarChart, 
  Clock,
  Download,
  Filter,
  ChevronDown,
  Plus,
  Loader,
  ClipboardList,
  Briefcase,
  Target,
  BookOpen
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';
import { mockReports } from './mockReportsData';

/**
 * ReportsDashboardPage provides a central hub for accessing and generating reports
 */
const ReportsDashboardPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [recentReports, setRecentReports] = useState([]);
  const [savedReports, setSavedReports] = useState([]);
  const [scheduledReports, setScheduledReports] = useState([]);
  const [filterOpen, setFilterOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [reportType, setReportType] = useState('all');
  
  // Fetch report data
  useEffect(() => {
    const fetchReportData = async () => {
      try {
        setIsLoading(true);
        
        // Use mock data for development
        if (process.env.NODE_ENV === 'development') {
          setRecentReports(mockReports.recent);
          setSavedReports(mockReports.saved);
          setScheduledReports(mockReports.scheduled);
        } else {
          // Fetch recent, saved, and scheduled reports
          const [recentResponse, savedResponse, scheduledResponse] = await Promise.all([
            api.get('/api/reports/recent'),
            api.get('/api/reports/saved'),
            api.get('/api/reports/scheduled')
          ]);
          
          setRecentReports(recentResponse.data);
          setSavedReports(savedResponse.data);
          setScheduledReports(scheduledResponse.data);
        }
      } catch (error) {
        console.error('Error fetching report data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load report data',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchReportData();
  }, [toast]);
  
  // Filter reports based on search term and report type
  const filteredRecentReports = recentReports.filter(report => {
    const matchesSearch = report.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                         (report.description && report.description.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesType = reportType === 'all' || report.type === reportType;
    return matchesSearch && matchesType;
  });
  
  const filteredSavedReports = savedReports.filter(report => {
    const matchesSearch = report.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                         (report.description && report.description.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesType = reportType === 'all' || report.type === reportType;
    return matchesSearch && matchesType;
  });
  
  // Handle report download
  const handleDownloadReport = async (reportId, format = 'pdf') => {
    try {
      const response = await api.get(`/api/reports/${reportId}/download`, {
        params: { format },
        responseType: 'blob'
      });
      
      // Create a URL for the blob
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report_${reportId}_${new Date().toISOString().split('T')[0]}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast({
        title: 'Success',
        description: `Report downloaded successfully as ${format.toUpperCase()}`,
        type: 'success',
      });
    } catch (error) {
      console.error('Error downloading report:', error);
      toast({
        title: 'Error',
        description: `Failed to download report as ${format.toUpperCase()}`,
        type: 'error',
      });
    }
  };
  
  // Handle report type icon
  const getReportTypeIcon = (type) => {
    switch(type) {
      case 'beneficiary':
        return <Users className="w-5 h-5 text-blue-500" />;
      case 'program':
        return <Briefcase className="w-5 h-5 text-purple-500" />;
      case 'trainer':
        return <BookOpen className="w-5 h-5 text-green-500" />;
      case 'analytics':
        return <BarChart className="w-5 h-5 text-orange-500" />;
      case 'performance':
        return <Target className="w-5 h-5 text-red-500" />;
      default:
        return <FileText className="w-5 h-5 text-gray-500" />;
    }
  };
  
  // Format date for display
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader className="w-10 h-10 text-primary animate-spin" />
      </div>
    );
  }
  
  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Reports Dashboard</h1>
        
        <div className="flex space-x-2">
          <div className="relative">
            <Button
              variant="outline"
              onClick={() => setFilterOpen(!filterOpen)}
              className="flex items-center"
            >
              <Filter className="w-4 h-4 mr-2" />
              Filter
              <ChevronDown className="w-4 h-4 ml-2" />
            </Button>
            
            {filterOpen && (
              <div className="absolute right-0 mt-2 w-56 bg-white rounded-md shadow-lg z-10 border p-4">
                <h3 className="text-sm font-medium mb-2">Report Type</h3>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <input
                      type="radio"
                      id="type-all"
                      name="report-type"
                      checked={reportType === 'all'}
                      onChange={() => setReportType('all')}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <label htmlFor="type-all" className="ml-2 block text-sm text-gray-700">
                      All Reports
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      type="radio"
                      id="type-beneficiary"
                      name="report-type"
                      checked={reportType === 'beneficiary'}
                      onChange={() => setReportType('beneficiary')}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <label htmlFor="type-beneficiary" className="ml-2 block text-sm text-gray-700">
                      Beneficiary Reports
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      type="radio"
                      id="type-program"
                      name="report-type"
                      checked={reportType === 'program'}
                      onChange={() => setReportType('program')}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <label htmlFor="type-program" className="ml-2 block text-sm text-gray-700">
                      Program Reports
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      type="radio"
                      id="type-trainer"
                      name="report-type"
                      checked={reportType === 'trainer'}
                      onChange={() => setReportType('trainer')}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <label htmlFor="type-trainer" className="ml-2 block text-sm text-gray-700">
                      Trainer Reports
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      type="radio"
                      id="type-analytics"
                      name="report-type"
                      checked={reportType === 'analytics'}
                      onChange={() => setReportType('analytics')}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <label htmlFor="type-analytics" className="ml-2 block text-sm text-gray-700">
                      Analytics Reports
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      type="radio"
                      id="type-performance"
                      name="report-type"
                      checked={reportType === 'performance'}
                      onChange={() => setReportType('performance')}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <label htmlFor="type-performance" className="ml-2 block text-sm text-gray-700">
                      Performance Reports
                    </label>
                  </div>
                </div>
                
                <div className="flex justify-end mt-4">
                  <Button
                    variant="default"
                    size="sm"
                    onClick={() => setFilterOpen(false)}
                  >
                    Apply Filters
                  </Button>
                </div>
              </div>
            )}
          </div>
          
          <Button
            variant="default"
            onClick={() => navigate('/reports/create')}
            className="flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create Report
          </Button>
        </div>
      </div>
      
      {/* Search Bar */}
      <div className="mb-6 flex">
        <div className="relative flex-1">
          <Input
            type="text"
            placeholder="Search reports..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full"
          />
        </div>
      </div>
      
      {/* Report Type Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6 mb-6">
        <Card 
          className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${reportType === 'all' ? 'border-primary border-2' : ''}`}
          onClick={() => setReportType('all')}
        >
          <div className="flex flex-col items-center justify-center">
            <div className="p-3 bg-gray-100 rounded-full mb-3">
              <ClipboardList className="w-6 h-6 text-gray-600" />
            </div>
            <h3 className="font-medium">All Reports</h3>
          </div>
        </Card>
        
        <Card 
          className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${reportType === 'beneficiary' ? 'border-primary border-2' : ''}`}
          onClick={() => setReportType('beneficiary')}
        >
          <div className="flex flex-col items-center justify-center">
            <div className="p-3 bg-blue-50 rounded-full mb-3">
              <Users className="w-6 h-6 text-blue-500" />
            </div>
            <h3 className="font-medium">Beneficiary</h3>
          </div>
        </Card>
        
        <Card 
          className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${reportType === 'program' ? 'border-primary border-2' : ''}`}
          onClick={() => setReportType('program')}
        >
          <div className="flex flex-col items-center justify-center">
            <div className="p-3 bg-purple-50 rounded-full mb-3">
              <Briefcase className="w-6 h-6 text-purple-500" />
            </div>
            <h3 className="font-medium">Program</h3>
          </div>
        </Card>
        
        <Card 
          className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${reportType === 'trainer' ? 'border-primary border-2' : ''}`}
          onClick={() => setReportType('trainer')}
        >
          <div className="flex flex-col items-center justify-center">
            <div className="p-3 bg-green-50 rounded-full mb-3">
              <BookOpen className="w-6 h-6 text-green-500" />
            </div>
            <h3 className="font-medium">Trainer</h3>
          </div>
        </Card>
        
        <Card 
          className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${reportType === 'analytics' ? 'border-primary border-2' : ''}`}
          onClick={() => setReportType('analytics')}
        >
          <div className="flex flex-col items-center justify-center">
            <div className="p-3 bg-orange-50 rounded-full mb-3">
              <BarChart className="w-6 h-6 text-orange-500" />
            </div>
            <h3 className="font-medium">Analytics</h3>
          </div>
        </Card>
      </div>
      
      {/* Recent Reports */}
      <h2 className="text-xl font-semibold mb-4">Recent Reports</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {filteredRecentReports.length > 0 ? (
          filteredRecentReports.map(report => (
            <Card key={report.id} className="overflow-hidden">
              <div className="p-5">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4">
                    <div className="p-2 bg-gray-100 rounded-full">
                      {getReportTypeIcon(report.type)}
                    </div>
                    <div>
                      <h3 className="font-medium line-clamp-1">{report.name}</h3>
                      <p className="text-sm text-gray-500 mt-1 line-clamp-2">{report.description}</p>
                    </div>
                  </div>
                </div>
                
                <div className="mt-4 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Generated</span>
                    <span>{formatDate(report.generated_at)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Format</span>
                    <span className="uppercase">{report.format || 'PDF'}</span>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 px-5 py-3 flex justify-between items-center">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate(`/reports/${report.id}`)}
                >
                  View
                </Button>
                
                <div className="relative">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {}}
                    className="flex items-center"
                  >
                    <Download className="w-4 h-4 mr-1" />
                    Download
                    <ChevronDown className="w-3 h-3 ml-1" />
                  </Button>
                  
                  <div className="absolute right-0 bottom-full mb-1 w-32 bg-white rounded-md shadow-lg z-10 border p-1 hidden group-hover:block">
                    <button
                      className="block w-full text-left px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900 rounded"
                      onClick={() => handleDownloadReport(report.id, 'pdf')}
                    >
                      PDF
                    </button>
                    <button
                      className="block w-full text-left px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900 rounded"
                      onClick={() => handleDownloadReport(report.id, 'xlsx')}
                    >
                      Excel
                    </button>
                    <button
                      className="block w-full text-left px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900 rounded"
                      onClick={() => handleDownloadReport(report.id, 'csv')}
                    >
                      CSV
                    </button>
                  </div>
                </div>
              </div>
            </Card>
          ))
        ) : (
          <div className="col-span-full py-8 text-center text-gray-500">
            <FileText className="w-12 h-12 mx-auto text-gray-300 mb-3" />
            <p>No recent reports found</p>
            <p className="text-sm mt-1">
              {searchTerm ? 'Try adjusting your search or filters' : 'Create a new report to get started'}
            </p>
          </div>
        )}
      </div>
      
      {/* Saved Reports */}
      <h2 className="text-xl font-semibold mb-4">Saved Reports</h2>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Report Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created By</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Generated</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Times Run</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {filteredSavedReports.length > 0 ? (
              filteredSavedReports.map((report, index) => (
                <tr key={report.id} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="mr-3">
                        {getReportTypeIcon(report.type)}
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">{report.name}</div>
                        <div className="text-sm text-gray-500 line-clamp-1">{report.description}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      report.type === 'beneficiary' 
                        ? 'bg-blue-100 text-blue-800' 
                        : report.type === 'program' 
                        ? 'bg-purple-100 text-purple-800'
                        : report.type === 'trainer'
                        ? 'bg-green-100 text-green-800'
                        : report.type === 'analytics'
                        ? 'bg-orange-100 text-orange-800'
                        : report.type === 'performance'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {report.type.charAt(0).toUpperCase() + report.type.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {report.created_by}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(report.last_generated)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {report.run_count}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                    <div className="flex justify-end space-x-3">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => navigate(`/reports/${report.id}`)}
                      >
                        View
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => navigate(`/reports/${report.id}/run`)}
                      >
                        Run
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => navigate(`/reports/${report.id}/edit`)}
                      >
                        Edit
                      </Button>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="px-6 py-10 text-center text-gray-500">
                  <FileText className="w-12 h-12 mx-auto text-gray-300 mb-3" />
                  <p>No saved reports found</p>
                  <p className="text-sm mt-1">
                    {searchTerm ? 'Try adjusting your search or filters' : 'Save a report to access it easily later'}
                  </p>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      
      {/* Scheduled Reports */}
      <h2 className="text-xl font-semibold mt-8 mb-4">Scheduled Reports</h2>
      <Card className="p-6">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Report Name</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Frequency</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Recipients</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Next Run</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {scheduledReports.length > 0 ? (
                scheduledReports.map((schedule, index) => (
                  <tr key={schedule.id} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="px-4 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="mr-3">
                          {getReportTypeIcon(schedule.report.type)}
                        </div>
                        <div className="text-sm font-medium text-gray-900">{schedule.report.name}</div>
                      </div>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                      {schedule.frequency}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                      {schedule.recipients_count} recipients
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(schedule.next_run)}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        schedule.status === 'active' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {schedule.status.charAt(0).toUpperCase() + schedule.status.slice(1)}
                      </span>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-right text-sm">
                      <div className="flex justify-end space-x-3">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => navigate(`/reports/schedules/${schedule.id}`)}
                        >
                          View
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => navigate(`/reports/schedules/${schedule.id}/edit`)}
                        >
                          Edit
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="px-4 py-8 text-center text-gray-500">
                    <Calendar className="w-12 h-12 mx-auto text-gray-300 mb-3" />
                    <p>No scheduled reports</p>
                    <p className="text-sm mt-1">Schedule reports to automatically generate and send at regular intervals</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        {scheduledReports.length > 0 && (
          <div className="mt-4 flex justify-end">
            <Button
              variant="outline"
              onClick={() => navigate('/reports/schedules')}
            >
              Manage Scheduled Reports
            </Button>
          </div>
        )}
      </Card>
    </div>
  );
};

export default ReportsDashboardPage;
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  ArrowLeft,
  ChevronDown,
  ChevronRight,
  Calendar,
  Users,
  BarChart,
  FileText,
  Save,
  Download,
  Clock,
  Mail,
  Loader,
  CheckCircle,
  Briefcase,
  BookOpen,
  Target,
  TrendingUp
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';
import { mockReports } from './mockReportsData';
/**
 * ReportCreationPage allows users to create custom reports
 */
const ReportCreationPage = () => {
  const { id } = useParams(); // Optional report ID for editing
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [step, setStep] = useState(1);
  const [reportData, setReportData] = useState({
    name: '',
    description: '',
    type: '',
    format: 'pdf',
    filters: {},
    fields: [],
    groupBy: [],
    sortBy: [],
    dateRange: '30days'
  });
  const [availableFields, setAvailableFields] = useState([]);
  const [availableFilters, setAvailableFilters] = useState([]);
  const [reportPreview, setReportPreview] = useState(null);
  const [editMode, setEditMode] = useState(false);
  // Fetch data for report creation or editing
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        // If ID is provided, fetch the report for editing
        if (id) {
          const reportResponse = await api.get(`/api/reports/${id}`);
          setReportData(reportResponse.data);
          setEditMode(true);
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
    fetchData();
  }, [id, toast]);
  // Load available fields when report type changes
  useEffect(() => {
    const fetchAvailableFields = async () => {
      if (!reportData.type) return;
      try {
        // Use mock data for development
        if (process.env.NODE_ENV === 'development') {
          setAvailableFields(mockReports.fields[reportData.type] || []);
          setAvailableFilters(mockReports.filters[reportData.type] || []);
        } else {
          const fieldsResponse = await api.get(`/api/reports/fields/${reportData.type}`);
          setAvailableFields(fieldsResponse.data);
          const filtersResponse = await api.get(`/api/reports/filters/${reportData.type}`);
          setAvailableFilters(filtersResponse.data);
        }
      } catch (error) {
        console.error('Error fetching available fields and filters:', error);
        toast({
          title: 'Error',
          description: 'Failed to load report options',
          type: 'error',
        });
      }
    };
    fetchAvailableFields();
  }, [reportData.type, toast]);
  // Generate report preview
  const generatePreview = async () => {
    try {
      setIsGenerating(true);
      // Use mock data for development
      if (process.env.NODE_ENV === 'development') {
        setTimeout(() => {
          setReportPreview(mockReports.previewData[reportData.type] || mockReports.previewData.beneficiary);
          setStep(4); // Move to preview step
          setIsGenerating(false);
        }, 1500);
      } else {
        const response = await api.post('/api/reports/preview', reportData);
        setReportPreview(response.data);
        setStep(4); // Move to preview step
        setIsGenerating(false);
      }
    } catch (error) {
      console.error('Error generating report preview:', error);
      toast({
        title: 'Error',
        description: 'Failed to generate report preview',
        type: 'error',
      });
      setIsGenerating(false);
    }
  };
  // Save report
  const saveReport = async () => {
    try {
      setIsSaving(true);
      let response;
      if (editMode) {
        response = await api.put(`/api/reports/${id}`, reportData);
      } else {
        response = await api.post('/api/reports', reportData);
      }
      toast({
        title: 'Success',
        description: editMode ? 'Report updated successfully' : 'Report created successfully',
        type: 'success',
      });
      // Navigate to the report details page
      navigate(`/reports/${response.data.id}`);
    } catch (error) {
      console.error('Error saving report:', error);
      toast({
        title: 'Error',
        description: 'Failed to save report',
        type: 'error',
      });
    } finally {
      setIsSaving(false);
    }
  };
  // Download report
  const downloadReport = async (format = 'pdf') => {
    try {
      setIsGenerating(true);
      const response = await api.post('/api/reports/generate', {
        ...reportData,
        format
      }, {
        responseType: 'blob'
      });
      // Create a URL for the blob
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report_${new Date().toISOString().split('T')[0]}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast({
        title: 'Success',
        description: `Report downloaded as ${format.toUpperCase()}`,
        type: 'success',
      });
    } catch (error) {
      console.error('Error downloading report:', error);
      toast({
        title: 'Error',
        description: 'Failed to download report',
        type: 'error',
      });
    } finally {
      setIsGenerating(false);
    }
  };
  // Schedule report
  const scheduleReport = () => {
    // Save the report first
    saveReport().then(() => {
      navigate(`/reports/schedules/create?reportId=${id || 'new'}`);
    });
  };
  // Handle input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setReportData({
      ...reportData,
      [name]: value
    });
  };
  // Toggle field selection
  const toggleField = (field) => {
    const isSelected = reportData.fields.includes(field.id);
    if (isSelected) {
      setReportData({
        ...reportData,
        fields: reportData.fields.filter(id => id !== field.id)
      });
    } else {
      setReportData({
        ...reportData,
        fields: [...reportData.fields, field.id]
      });
    }
  };
  // Handle filter changes
  const handleFilterChange = (filterId, value) => {
    setReportData({
      ...reportData,
      filters: {
        ...reportData.filters,
        [filterId]: value
      }
    });
  };
  // Add a groupBy field
  const addGroupBy = (field) => {
    if (!reportData.groupBy.includes(field.id)) {
      setReportData({
        ...reportData,
        groupBy: [...reportData.groupBy, field.id]
      });
    }
  };
  // Remove a groupBy field
  const removeGroupBy = (fieldId) => {
    setReportData({
      ...reportData,
      groupBy: reportData.groupBy.filter(id => id !== fieldId)
    });
  };
  // Add a sortBy field
  const addSortBy = (field, direction = 'asc') => {
    const existingIndex = reportData.sortBy.findIndex(sort => sort.field === field.id);
    if (existingIndex >= 0) {
      // Update the existing sort
      const updatedSortBy = [...reportData.sortBy];
      updatedSortBy[existingIndex] = { field: field.id, direction };
      setReportData({
        ...reportData,
        sortBy: updatedSortBy
      });
    } else {
      // Add a new sort
      setReportData({
        ...reportData,
        sortBy: [...reportData.sortBy, { field: field.id, direction }]
      });
    }
  };
  // Remove a sortBy field
  const removeSortBy = (fieldId) => {
    setReportData({
      ...reportData,
      sortBy: reportData.sortBy.filter(sort => sort.field !== fieldId)
    });
  };
  // Get field name by ID
  const getFieldName = (fieldId) => {
    const field = availableFields.find(f => f.id === fieldId);
    return field ? field.name : fieldId;
  };
  // Get filter name by ID
  const getFilterName = (filterId) => {
    const filter = availableFilters.find(f => f.id === filterId);
    return filter ? filter.name : filterId;
  };
  // Render report type icon
  const getReportTypeIcon = (type) => {
    switch(type) {
      case 'beneficiary':
        return <Users className="w-6 h-6 text-blue-500" />;
      case 'program':
        return <Briefcase className="w-6 h-6 text-purple-500" />;
      case 'trainer':
        return <BookOpen className="w-6 h-6 text-green-500" />;
      case 'analytics':
        return <BarChart className="w-6 h-6 text-orange-500" />;
      case 'performance':
        return <Target className="w-6 h-6 text-red-500" />;
      default:
        return <FileText className="w-6 h-6 text-gray-500" />;
    }
  };
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader className="w-10 h-10 text-primary animate-spin" />
      </div>
    );
  }
  // Render step 1: Report Type and Basic Info
  const renderStep1 = () => (
    <div className="space-y-6">
      <div className="space-y-4">
        <h2 className="text-lg font-medium">Report Information</h2>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Report Name</label>
          <Input
            type="text"
            name="name"
            value={reportData.name}
            onChange={handleInputChange}
            placeholder="Enter report name"
            className="w-full"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description (Optional)</label>
          <textarea
            name="description"
            value={reportData.description}
            onChange={handleInputChange}
            placeholder="Enter report description"
            className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            rows={3}
          />
        </div>
      </div>
      <div className="space-y-4">
        <h2 className="text-lg font-medium">Report Type</h2>
        <p className="text-sm text-gray-500">Select the type of report you want to create</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card 
            className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${reportData.type === 'beneficiary' ? 'border-primary border-2' : ''}`}
            onClick={() => setReportData({ ...reportData, type: 'beneficiary' })}
          >
            <div className="flex flex-col items-center justify-center p-4">
              <div className="p-3 bg-blue-50 rounded-full mb-3">
                <Users className="w-8 h-8 text-blue-500" />
              </div>
              <h3 className="font-medium">Beneficiary Report</h3>
              <p className="text-sm text-gray-500 text-center mt-2">Information about beneficiaries and their progress</p>
            </div>
          </Card>
          <Card 
            className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${reportData.type === 'program' ? 'border-primary border-2' : ''}`}
            onClick={() => setReportData({ ...reportData, type: 'program' })}
          >
            <div className="flex flex-col items-center justify-center p-4">
              <div className="p-3 bg-purple-50 rounded-full mb-3">
                <Briefcase className="w-8 h-8 text-purple-500" />
              </div>
              <h3 className="font-medium">Program Report</h3>
              <p className="text-sm text-gray-500 text-center mt-2">Information about training programs and their metrics</p>
            </div>
          </Card>
          <Card 
            className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${reportData.type === 'trainer' ? 'border-primary border-2' : ''}`}
            onClick={() => setReportData({ ...reportData, type: 'trainer' })}
          >
            <div className="flex flex-col items-center justify-center p-4">
              <div className="p-3 bg-green-50 rounded-full mb-3">
                <BookOpen className="w-8 h-8 text-green-500" />
              </div>
              <h3 className="font-medium">Trainer Report</h3>
              <p className="text-sm text-gray-500 text-center mt-2">Information about trainers and their performance</p>
            </div>
          </Card>
          <Card 
            className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${reportData.type === 'analytics' ? 'border-primary border-2' : ''}`}
            onClick={() => setReportData({ ...reportData, type: 'analytics' })}
          >
            <div className="flex flex-col items-center justify-center p-4">
              <div className="p-3 bg-orange-50 rounded-full mb-3">
                <BarChart className="w-8 h-8 text-orange-500" />
              </div>
              <h3 className="font-medium">Analytics Report</h3>
              <p className="text-sm text-gray-500 text-center mt-2">Statistical analysis and visualizations</p>
            </div>
          </Card>
          <Card 
            className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${reportData.type === 'performance' ? 'border-primary border-2' : ''}`}
            onClick={() => setReportData({ ...reportData, type: 'performance' })}
          >
            <div className="flex flex-col items-center justify-center p-4">
              <div className="p-3 bg-red-50 rounded-full mb-3">
                <Target className="w-8 h-8 text-red-500" />
              </div>
              <h3 className="font-medium">Performance Report</h3>
              <p className="text-sm text-gray-500 text-center mt-2">Performance metrics and KPIs</p>
            </div>
          </Card>
        </div>
      </div>
      <div className="space-y-4">
        <h2 className="text-lg font-medium">Report Format</h2>
        <div className="flex space-x-4">
          <div className="flex items-center">
            <input
              type="radio"
              id="format-pdf"
              name="format"
              value="pdf"
              checked={reportData.format === 'pdf'}
              onChange={handleInputChange}
              className="h-4 w-4 text-primary focus:ring-primary border-gray-300"
            />
            <label htmlFor="format-pdf" className="ml-2 block text-sm text-gray-700">
              PDF
            </label>
          </div>
          <div className="flex items-center">
            <input
              type="radio"
              id="format-xlsx"
              name="format"
              value="xlsx"
              checked={reportData.format === 'xlsx'}
              onChange={handleInputChange}
              className="h-4 w-4 text-primary focus:ring-primary border-gray-300"
            />
            <label htmlFor="format-xlsx" className="ml-2 block text-sm text-gray-700">
              Excel (XLSX)
            </label>
          </div>
          <div className="flex items-center">
            <input
              type="radio"
              id="format-csv"
              name="format"
              value="csv"
              checked={reportData.format === 'csv'}
              onChange={handleInputChange}
              className="h-4 w-4 text-primary focus:ring-primary border-gray-300"
            />
            <label htmlFor="format-csv" className="ml-2 block text-sm text-gray-700">
              CSV
            </label>
          </div>
        </div>
      </div>
      <div className="space-y-4">
        <h2 className="text-lg font-medium">Time Period</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="flex items-center">
            <input
              type="radio"
              id="dateRange-7days"
              name="dateRange"
              value="7days"
              checked={reportData.dateRange === '7days'}
              onChange={handleInputChange}
              className="h-4 w-4 text-primary focus:ring-primary border-gray-300"
            />
            <label htmlFor="dateRange-7days" className="ml-2 block text-sm text-gray-700">
              Last 7 Days
            </label>
          </div>
          <div className="flex items-center">
            <input
              type="radio"
              id="dateRange-30days"
              name="dateRange"
              value="30days"
              checked={reportData.dateRange === '30days'}
              onChange={handleInputChange}
              className="h-4 w-4 text-primary focus:ring-primary border-gray-300"
            />
            <label htmlFor="dateRange-30days" className="ml-2 block text-sm text-gray-700">
              Last 30 Days
            </label>
          </div>
          <div className="flex items-center">
            <input
              type="radio"
              id="dateRange-90days"
              name="dateRange"
              value="90days"
              checked={reportData.dateRange === '90days'}
              onChange={handleInputChange}
              className="h-4 w-4 text-primary focus:ring-primary border-gray-300"
            />
            <label htmlFor="dateRange-90days" className="ml-2 block text-sm text-gray-700">
              Last 90 Days
            </label>
          </div>
          <div className="flex items-center">
            <input
              type="radio"
              id="dateRange-year"
              name="dateRange"
              value="year"
              checked={reportData.dateRange === 'year'}
              onChange={handleInputChange}
              className="h-4 w-4 text-primary focus:ring-primary border-gray-300"
            />
            <label htmlFor="dateRange-year" className="ml-2 block text-sm text-gray-700">
              This Year
            </label>
          </div>
          <div className="flex items-center">
            <input
              type="radio"
              id="dateRange-allTime"
              name="dateRange"
              value="allTime"
              checked={reportData.dateRange === 'allTime'}
              onChange={handleInputChange}
              className="h-4 w-4 text-primary focus:ring-primary border-gray-300"
            />
            <label htmlFor="dateRange-allTime" className="ml-2 block text-sm text-gray-700">
              All Time
            </label>
          </div>
          <div className="flex items-center">
            <input
              type="radio"
              id="dateRange-custom"
              name="dateRange"
              value="custom"
              checked={reportData.dateRange === 'custom'}
              onChange={handleInputChange}
              className="h-4 w-4 text-primary focus:ring-primary border-gray-300"
            />
            <label htmlFor="dateRange-custom" className="ml-2 block text-sm text-gray-700">
              Custom Range
            </label>
          </div>
        </div>
        {reportData.dateRange === 'custom' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
              <Input
                type="date"
                name="startDate"
                value={reportData.startDate || ''}
                onChange={handleInputChange}
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
              <Input
                type="date"
                name="endDate"
                value={reportData.endDate || ''}
                onChange={handleInputChange}
                className="w-full"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
  // Render step 2: Select Fields
  const renderStep2 = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-medium">Select Fields</h2>
        <p className="text-sm text-gray-500 mt-1">Choose the fields to include in your report</p>
      </div>
      {availableFields.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {availableFields.map(field => (
            <div key={field.id} className="flex items-center p-3 border rounded-md hover:bg-gray-50">
              <input
                type="checkbox"
                id={`field-${field.id}`}
                checked={reportData.fields.includes(field.id)}
                onChange={() => toggleField(field)}
                className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
              />
              <label htmlFor={`field-${field.id}`} className="ml-3 flex flex-col">
                <span className="text-sm font-medium text-gray-700">{field.name}</span>
                <span className="text-xs text-gray-500">{field.description}</span>
              </label>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center p-8 border rounded-md bg-gray-50">
          <p className="text-gray-500">Please select a report type to view available fields</p>
        </div>
      )}
      {reportData.fields.length > 0 && (
        <div className="mt-6 p-4 bg-gray-50 rounded-md">
          <h3 className="text-sm font-medium mb-2">Selected Fields ({reportData.fields.length})</h3>
          <div className="flex flex-wrap gap-2">
            {reportData.fields.map(fieldId => (
              <div key={fieldId} className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm flex items-center">
                {getFieldName(fieldId)}
                <button
                  type="button"
                  onClick={() => toggleField({ id: fieldId })}
                  className="ml-2 text-primary/70 hover:text-primary"
                >
                  &times;
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
  // Render step 3: Filters and Options
  const renderStep3 = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-medium">Filters</h2>
        <p className="text-sm text-gray-500 mt-1">Apply filters to refine your report results</p>
      </div>
      {availableFilters.length > 0 ? (
        <div className="space-y-4">
          {availableFilters.map(filter => (
            <div key={filter.id} className="p-4 border rounded-md">
              <h3 className="text-sm font-medium mb-2">{filter.name}</h3>
              {filter.type === 'select' && (
                <select
                  value={reportData.filters[filter.id] || ''}
                  onChange={(e) => handleFilterChange(filter.id, e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                >
                  <option value="">All</option>
                  {filter.options.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              )}
              {filter.type === 'multiselect' && (
                <div className="space-y-2">
                  {filter.options.map(option => (
                    <div key={option.value} className="flex items-center">
                      <input
                        type="checkbox"
                        id={`filter-${filter.id}-${option.value}`}
                        checked={(reportData.filters[filter.id] || []).includes(option.value)}
                        onChange={() => {
                          const currentValues = reportData.filters[filter.id] || [];
                          if (currentValues.includes(option.value)) {
                            handleFilterChange(filter.id, currentValues.filter(v => v !== option.value));
                          } else {
                            handleFilterChange(filter.id, [...currentValues, option.value]);
                          }
                        }}
                        className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                      />
                      <label htmlFor={`filter-${filter.id}-${option.value}`} className="ml-2 text-sm text-gray-700">
                        {option.label}
                      </label>
                    </div>
                  ))}
                </div>
              )}
              {filter.type === 'range' && (
                <div className="flex space-x-4">
                  <div className="flex-1">
                    <label className="block text-xs text-gray-500 mb-1">Minimum</label>
                    <Input
                      type="number"
                      value={(reportData.filters[filter.id]?.min || '')}
                      onChange={(e) => {
                        const currentRange = reportData.filters[filter.id] || {};
                        handleFilterChange(filter.id, { ...currentRange, min: e.target.value });
                      }}
                      className="w-full"
                    />
                  </div>
                  <div className="flex-1">
                    <label className="block text-xs text-gray-500 mb-1">Maximum</label>
                    <Input
                      type="number"
                      value={(reportData.filters[filter.id]?.max || '')}
                      onChange={(e) => {
                        const currentRange = reportData.filters[filter.id] || {};
                        handleFilterChange(filter.id, { ...currentRange, max: e.target.value });
                      }}
                      className="w-full"
                    />
                  </div>
                </div>
              )}
              {filter.type === 'text' && (
                <Input
                  type="text"
                  value={(reportData.filters[filter.id] || '')}
                  onChange={(e) => handleFilterChange(filter.id, e.target.value)}
                  placeholder={`Filter by ${filter.name.toLowerCase()}`}
                  className="w-full"
                />
              )}
              {filter.type === 'date' && (
                <div className="flex space-x-4">
                  <div className="flex-1">
                    <label className="block text-xs text-gray-500 mb-1">From</label>
                    <Input
                      type="date"
                      value={(reportData.filters[filter.id]?.from || '')}
                      onChange={(e) => {
                        const currentRange = reportData.filters[filter.id] || {};
                        handleFilterChange(filter.id, { ...currentRange, from: e.target.value });
                      }}
                      className="w-full"
                    />
                  </div>
                  <div className="flex-1">
                    <label className="block text-xs text-gray-500 mb-1">To</label>
                    <Input
                      type="date"
                      value={(reportData.filters[filter.id]?.to || '')}
                      onChange={(e) => {
                        const currentRange = reportData.filters[filter.id] || {};
                        handleFilterChange(filter.id, { ...currentRange, to: e.target.value });
                      }}
                      className="w-full"
                    />
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center p-8 border rounded-md bg-gray-50">
          <p className="text-gray-500">No filters available for this report type</p>
        </div>
      )}
      <div className="mt-8">
        <h2 className="text-lg font-medium mb-4">Group and Sort Options</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Group By</h3>
            <p className="text-xs text-gray-500">Organize your data by grouping on specific fields</p>
            <div className="p-3 border rounded-md bg-gray-50">
              <select
                value=""
                onChange={(e) => {
                  if (e.target.value) {
                    const field = availableFields.find(f => f.id === e.target.value);
                    if (field) {
                      addGroupBy(field);
                    }
                    e.target.value = '';  // Reset the select
                  }
                }}
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              >
                <option value="">Add group by field...</option>
                {availableFields
                  .filter(field => reportData.fields.includes(field.id) && !reportData.groupBy.includes(field.id))
                  .map(field => (
                    <option key={field.id} value={field.id}>
                      {field.name}
                    </option>
                  ))}
              </select>
              {reportData.groupBy.length > 0 && (
                <div className="mt-3 space-y-2">
                  {reportData.groupBy.map((fieldId, index) => (
                    <div key={fieldId} className="flex items-center justify-between p-2 bg-white rounded border">
                      <div className="flex items-center">
                        <span className="inline-flex items-center justify-center w-5 h-5 bg-primary text-white rounded-full text-xs mr-2">
                          {index + 1}
                        </span>
                        <span className="text-sm">{getFieldName(fieldId)}</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeGroupBy(fieldId)}
                        className="text-gray-400 hover:text-red-500"
                      >
                        &times;
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Sort By</h3>
            <p className="text-xs text-gray-500">Define how your data should be ordered</p>
            <div className="p-3 border rounded-md bg-gray-50">
              <div className="flex space-x-2">
                <select
                  value=""
                  onChange={(e) => {
                    if (e.target.value) {
                      const field = availableFields.find(f => f.id === e.target.value);
                      if (field) {
                        addSortBy(field, 'asc');
                      }
                      e.target.value = '';  // Reset the select
                    }
                  }}
                  className="flex-1 p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                >
                  <option value="">Add sort field...</option>
                  {availableFields
                    .filter(field => reportData.fields.includes(field.id) && !reportData.sortBy.some(sort => sort.field === field.id))
                    .map(field => (
                      <option key={field.id} value={field.id}>
                        {field.name}
                      </option>
                    ))}
                </select>
              </div>
              {reportData.sortBy.length > 0 && (
                <div className="mt-3 space-y-2">
                  {reportData.sortBy.map((sort, index) => (
                    <div key={sort.field} className="flex items-center justify-between p-2 bg-white rounded border">
                      <div className="flex items-center">
                        <span className="inline-flex items-center justify-center w-5 h-5 bg-primary text-white rounded-full text-xs mr-2">
                          {index + 1}
                        </span>
                        <span className="text-sm">{getFieldName(sort.field)}</span>
                        <span className="ml-2 text-xs text-gray-500">
                          ({sort.direction === 'asc' ? 'Ascending' : 'Descending'})
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          type="button"
                          onClick={() => addSortBy({ id: sort.field }, sort.direction === 'asc' ? 'desc' : 'asc')}
                          className="text-gray-400 hover:text-primary"
                          title="Toggle sort direction"
                        >
                          <ChevronDown className={`w-4 h-4 ${sort.direction === 'desc' ? 'transform rotate-180' : ''}`} />
                        </button>
                        <button
                          type="button"
                          onClick={() => removeSortBy(sort.field)}
                          className="text-gray-400 hover:text-red-500"
                        >
                          &times;
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
  // Render step 4: Preview
  const renderStep4 = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-medium">Report Preview</h2>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            onClick={() => setStep(3)}
            className="flex items-center"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Edit Report
          </Button>
          <div className="relative inline-block group">
            <Button
              variant="outline"
              className="flex items-center"
            >
              <Download className="w-4 h-4 mr-2" />
              Download
              <ChevronDown className="w-4 h-4 ml-1" />
            </Button>
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border p-1 hidden group-hover:block">
              <button
                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900 rounded"
                onClick={() => downloadReport('pdf')}
              >
                Download as PDF
              </button>
              <button
                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900 rounded"
                onClick={() => downloadReport('xlsx')}
              >
                Download as Excel
              </button>
              <button
                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900 rounded"
                onClick={() => downloadReport('csv')}
              >
                Download as CSV
              </button>
            </div>
          </div>
          <Button
            variant="default"
            onClick={saveReport}
            className="flex items-center"
            disabled={isSaving}
          >
            {isSaving ? (
              <>
                <Loader className="w-4 h-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                Save Report
              </>
            )}
          </Button>
        </div>
      </div>
      <div className="bg-white border rounded-md overflow-hidden">
        <div className="p-4 border-b bg-gray-50">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <div className="p-2 rounded-full bg-gray-100 mr-3">
                {getReportTypeIcon(reportData.type)}
              </div>
              <div>
                <h3 className="font-medium">{reportData.name}</h3>
                <p className="text-sm text-gray-500">{reportData.description}</p>
              </div>
            </div>
            <div className="flex flex-col items-end text-sm text-gray-500">
              <div className="flex items-center">
                <Calendar className="w-4 h-4 mr-1" />
                <span>
                  {reportData.dateRange === 'custom' 
                    ? `${reportData.startDate} to ${reportData.endDate}`
                    : reportData.dateRange === '7days' 
                    ? 'Last 7 Days'
                    : reportData.dateRange === '30days'
                    ? 'Last 30 Days'
                    : reportData.dateRange === '90days'
                    ? 'Last 90 Days'
                    : reportData.dateRange === 'year'
                    ? 'This Year'
                    : 'All Time'
                  }
                </span>
              </div>
              <div className="flex items-center mt-1">
                <Clock className="w-4 h-4 mr-1" />
                <span>Generated on {new Date().toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        </div>
        {isGenerating ? (
          <div className="flex flex-col items-center justify-center p-16">
            <Loader className="w-12 h-12 text-primary animate-spin mb-4" />
            <p className="text-gray-500">Generating report preview...</p>
          </div>
        ) : reportPreview ? (
          <div className="p-6">
            {reportPreview.sections.map((section, index) => (
              <div key={index} className="mb-8">
                <h3 className="text-lg font-medium mb-4">{section.title}</h3>
                {section.type === 'table' && (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50">
                        <tr>
                          {section.columns.map(column => (
                            <th key={column.id} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              {column.name}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {section.data.map((row, rowIndex) => (
                          <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                            {section.columns.map(column => (
                              <td key={column.id} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {row[column.id]}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
                {section.type === 'chart' && (
                  <div className="bg-gray-100 p-8 rounded-md text-center">
                    <p className="text-gray-500">[Chart Visualization: {section.chartType}]</p>
                  </div>
                )}
                {section.type === 'summary' && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {section.metrics.map(metric => (
                      <Card key={metric.id} className="p-4">
                        <p className="text-gray-500 text-sm">{metric.name}</p>
                        <h3 className="text-2xl font-bold mt-1">{metric.value}</h3>
                        {metric.change && (
                          <p className={`text-sm mt-1 ${metric.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            <span className="inline-flex items-center">
                              <TrendingUp className={`w-3 h-3 mr-1 ${metric.change >= 0 ? '' : 'transform rotate-180'}`} />
                              {Math.abs(metric.change)}% from previous period
                            </span>
                          </p>
                        )}
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center p-16">
            <Button
              variant="default"
              onClick={generatePreview}
              className="flex items-center"
              disabled={isGenerating}
            >
              {isGenerating ? (
                <>
                  <Loader className="w-4 h-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <BarChart className="w-4 h-4 mr-2" />
                  Generate Preview
                </>
              )}
            </Button>
            <p className="text-sm text-gray-500 mt-2">Click to generate a preview of your report</p>
          </div>
        )}
      </div>
      <div className="flex justify-between items-center pt-6">
        <div className="flex items-center">
          <div className="p-2 rounded-full bg-primary/10 mr-3">
            <Mail className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3 className="font-medium">Schedule Report Delivery</h3>
            <p className="text-sm text-gray-500">Set up automatic generation and delivery</p>
          </div>
        </div>
        <Button
          variant="outline"
          onClick={scheduleReport}
          className="flex items-center"
        >
          <Clock className="w-4 h-4 mr-2" />
          Schedule
        </Button>
      </div>
    </div>
  );
  return (
    <div className="container mx-auto py-6">
      <div className="flex items-center mb-6">
        <button
          className="mr-4 p-2 rounded-full hover:bg-gray-100"
          onClick={() => navigate('/reports')}
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold">
            {editMode ? 'Edit Report' : 'Create New Report'}
          </h1>
          <p className="text-gray-500">
            {editMode 
              ? 'Modify your existing report configuration'
              : 'Configure a new report with customized fields and filters'
            }
          </p>
        </div>
      </div>
      <div className="grid grid-cols-12 gap-6">
        {/* Step Sidebar */}
        <div className="col-span-12 md:col-span-3">
          <Card className="p-0 overflow-hidden">
            <div 
              className={`p-4 flex items-center cursor-pointer hover:bg-gray-50 ${step === 1 ? 'bg-primary/10 border-l-4 border-primary' : ''}`}
              onClick={() => step > 1 && setStep(1)}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${step === 1 ? 'bg-primary text-white' : 'bg-gray-200 text-gray-500'}`}>
                1
              </div>
              <div>
                <h3 className={`font-medium ${step === 1 ? 'text-primary' : 'text-gray-700'}`}>Report Type</h3>
                <p className="text-xs text-gray-500">Basic information and format</p>
              </div>
            </div>
            <div 
              className={`p-4 flex items-center cursor-pointer hover:bg-gray-50 ${step === 2 ? 'bg-primary/10 border-l-4 border-primary' : ''}`}
              onClick={() => (step > 2 || reportData.type) && setStep(2)}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${
                step === 2 
                  ? 'bg-primary text-white' 
                  : step > 2 
                  ? 'bg-green-500 text-white' 
                  : 'bg-gray-200 text-gray-500'
              }`}>
                {step > 2 ? <CheckCircle className="w-5 h-5" /> : 2}
              </div>
              <div>
                <h3 className={`font-medium ${step === 2 ? 'text-primary' : 'text-gray-700'}`}>Select Fields</h3>
                <p className="text-xs text-gray-500">Choose data to include</p>
              </div>
            </div>
            <div 
              className={`p-4 flex items-center cursor-pointer hover:bg-gray-50 ${step === 3 ? 'bg-primary/10 border-l-4 border-primary' : ''}`}
              onClick={() => (step > 3 || (reportData.type && reportData.fields.length > 0)) && setStep(3)}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${
                step === 3 
                  ? 'bg-primary text-white' 
                  : step > 3 
                  ? 'bg-green-500 text-white' 
                  : 'bg-gray-200 text-gray-500'
              }`}>
                {step > 3 ? <CheckCircle className="w-5 h-5" /> : 3}
              </div>
              <div>
                <h3 className={`font-medium ${step === 3 ? 'text-primary' : 'text-gray-700'}`}>Filters & Options</h3>
                <p className="text-xs text-gray-500">Refine and organize data</p>
              </div>
            </div>
            <div 
              className={`p-4 flex items-center cursor-pointer hover:bg-gray-50 ${step === 4 ? 'bg-primary/10 border-l-4 border-primary' : ''}`}
              onClick={() => reportPreview && setStep(4)}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${step === 4 ? 'bg-primary text-white' : 'bg-gray-200 text-gray-500'}`}>
                4
              </div>
              <div>
                <h3 className={`font-medium ${step === 4 ? 'text-primary' : 'text-gray-700'}`}>Preview & Save</h3>
                <p className="text-xs text-gray-500">Review and finalize report</p>
              </div>
            </div>
          </Card>
          <div className="mt-6">
            <Button
              variant="outline"
              className="w-full justify-center"
              onClick={() => navigate('/reports')}
            >
              Cancel
            </Button>
          </div>
        </div>
        {/* Main Content */}
        <div className="col-span-12 md:col-span-9">
          <Card className="p-6">
            {step === 1 && renderStep1()}
            {step === 2 && renderStep2()}
            {step === 3 && renderStep3()}
            {step === 4 && renderStep4()}
            {step < 4 && (
              <div className="mt-8 flex justify-between">
                {step > 1 ? (
                  <Button
                    variant="outline"
                    onClick={() => setStep(step - 1)}
                    className="flex items-center"
                  >
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Previous
                  </Button>
                ) : (
                  <div></div>
                )}
                <Button
                  variant="default"
                  onClick={() => {
                    if (step === 1 && !reportData.type) {
                      toast({
                        title: 'Error',
                        description: 'Please select a report type',
                        type: 'error',
                      });
                      return;
                    }
                    if (step === 2 && reportData.fields.length === 0) {
                      toast({
                        title: 'Error',
                        description: 'Please select at least one field',
                        type: 'error',
                      });
                      return;
                    }
                    if (step === 3) {
                      generatePreview();
                    } else {
                      setStep(step + 1);
                    }
                  }}
                  className="flex items-center"
                >
                  {step === 3 ? (
                    <>
                      Generate Preview
                      <BarChart className="w-4 h-4 ml-2" />
                    </>
                  ) : (
                    <>
                      Next
                      <ChevronRight className="w-4 h-4 ml-2" />
                    </>
                  )}
                </Button>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};
export default ReportCreationPage;
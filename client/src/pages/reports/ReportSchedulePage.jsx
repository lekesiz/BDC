import { useState, useEffect } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import {
  ArrowLeft,
  Clock,
  Calendar,
  Mail,
  Users,
  Save,
  Trash,
  AlertCircle,
  Loader,
  CheckCircle
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';

/**
 * ReportSchedulePage allows users to schedule automated report generation and delivery
 */
const ReportSchedulePage = () => {
  const { id } = useParams(); // Optional schedule ID for editing
  const [searchParams] = useSearchParams();
  const reportId = searchParams.get('reportId');
  
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [report, setReport] = useState(null);
  const [scheduleData, setScheduleData] = useState({
    name: '',
    description: '',
    frequency: 'weekly',
    dayOfWeek: '1', // Monday
    dayOfMonth: '1',
    time: '08:00',
    formats: ['pdf'],
    recipients: [],
    active: true
  });
  const [editMode, setEditMode] = useState(false);
  const [selectedUser, setSelectedUser] = useState('');
  const [users, setUsers] = useState([]);
  const [userSearchTerm, setUserSearchTerm] = useState('');
  
  // Fetch data for schedule creation or editing
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        
        // Fetch users for recipient selection
        const usersResponse = await api.get('/api/users');
        setUsers(usersResponse.data);
        
        // If we have a report ID from query params, fetch the report
        if (reportId && reportId !== 'new') {
          const reportResponse = await api.get(`/api/reports/${reportId}`);
          setReport(reportResponse.data);
          
          // Pre-populate schedule name based on report
          if (!editMode) {
            setScheduleData(prev => ({
              ...prev,
              name: `${reportResponse.data.name} Schedule`
            }));
          }
        }
        
        // If ID is provided, fetch the schedule for editing
        if (id && id !== 'create') {
          const scheduleResponse = await api.get(`/api/reports/schedules/${id}`);
          setScheduleData(scheduleResponse.data);
          
          // Also fetch the associated report
          const reportResponse = await api.get(`/api/reports/${scheduleResponse.data.reportId}`);
          setReport(reportResponse.data);
          
          setEditMode(true);
        }
        
      } catch (error) {
        console.error('Error fetching schedule data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load schedule data',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [id, reportId, toast, editMode]);
  
  // Save schedule
  const saveSchedule = async () => {
    // Validate inputs
    if (!scheduleData.name) {
      toast({
        title: 'Error',
        description: 'Please enter a schedule name',
        type: 'error',
      });
      return;
    }
    
    if (scheduleData.formats.length === 0) {
      toast({
        title: 'Error',
        description: 'Please select at least one export format',
        type: 'error',
      });
      return;
    }
    
    if (scheduleData.recipients.length === 0) {
      toast({
        title: 'Error',
        description: 'Please add at least one recipient',
        type: 'error',
      });
      return;
    }
    
    try {
      setIsSaving(true);
      
      const dataToSubmit = {
        ...scheduleData,
        reportId: report.id
      };
      
      let response;
      if (editMode) {
        response = await api.put(`/api/reports/schedules/${id}`, dataToSubmit);
      } else {
        response = await api.post('/api/reports/schedules', dataToSubmit);
      }
      
      toast({
        title: 'Success',
        description: editMode ? 'Schedule updated successfully' : 'Schedule created successfully',
        type: 'success',
      });
      
      // Navigate back to reports page
      navigate('/reports');
      
    } catch (error) {
      console.error('Error saving schedule:', error);
      toast({
        title: 'Error',
        description: 'Failed to save schedule',
        type: 'error',
      });
    } finally {
      setIsSaving(false);
    }
  };
  
  // Delete schedule
  const deleteSchedule = async () => {
    if (!confirm('Are you sure you want to delete this schedule?')) return;
    
    try {
      setIsDeleting(true);
      
      await api.delete(`/api/reports/schedules/${id}`);
      
      toast({
        title: 'Success',
        description: 'Schedule deleted successfully',
        type: 'success',
      });
      
      // Navigate back to reports page
      navigate('/reports');
      
    } catch (error) {
      console.error('Error deleting schedule:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete schedule',
        type: 'error',
      });
    } finally {
      setIsDeleting(false);
    }
  };
  
  // Handle input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setScheduleData({
      ...scheduleData,
      [name]: value
    });
  };
  
  // Toggle format selection
  const toggleFormat = (format) => {
    if (scheduleData.formats.includes(format)) {
      setScheduleData({
        ...scheduleData,
        formats: scheduleData.formats.filter(f => f !== format)
      });
    } else {
      setScheduleData({
        ...scheduleData,
        formats: [...scheduleData.formats, format]
      });
    }
  };
  
  // Add a recipient
  const addRecipient = () => {
    if (!selectedUser) return;
    
    const userToAdd = users.find(user => user.id === selectedUser);
    
    if (userToAdd && !scheduleData.recipients.some(r => r.id === userToAdd.id)) {
      setScheduleData({
        ...scheduleData,
        recipients: [...scheduleData.recipients, userToAdd]
      });
    }
    
    setSelectedUser('');
  };
  
  // Remove a recipient
  const removeRecipient = (userId) => {
    setScheduleData({
      ...scheduleData,
      recipients: scheduleData.recipients.filter(r => r.id !== userId)
    });
  };
  
  // Filter users based on search term
  const filteredUsers = users.filter(user => 
    user.name.toLowerCase().includes(userSearchTerm.toLowerCase()) ||
    (user.email && user.email.toLowerCase().includes(userSearchTerm.toLowerCase()))
  );
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader className="w-10 h-10 text-primary animate-spin" />
      </div>
    );
  }
  
  if (!report && !isLoading) {
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
            <h1 className="text-2xl font-bold">Schedule Report</h1>
          </div>
        </div>
        
        <Card className="p-6">
          <div className="flex items-center p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <AlertCircle className="w-6 h-6 text-amber-500 mr-3" />
            <div>
              <h3 className="font-medium text-amber-800">No report selected</h3>
              <p className="text-sm text-amber-700 mt-1">
                Please select a report to schedule from the reports dashboard.
              </p>
            </div>
          </div>
          
          <div className="mt-4 flex justify-end">
            <Button
              variant="default"
              onClick={() => navigate('/reports')}
            >
              Go to Reports
            </Button>
          </div>
        </Card>
      </div>
    );
  }
  
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
            {editMode ? 'Edit Schedule' : 'Schedule Report'}
          </h1>
          <p className="text-gray-500">
            Configure automatic generation and delivery
          </p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card className="p-6">
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-medium mb-4">Schedule Information</h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Schedule Name
                    </label>
                    <Input
                      type="text"
                      name="name"
                      value={scheduleData.name}
                      onChange={handleInputChange}
                      placeholder="Enter a name for this schedule"
                      className="w-full"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Description (Optional)
                    </label>
                    <textarea
                      name="description"
                      value={scheduleData.description}
                      onChange={handleInputChange}
                      placeholder="Add a description for this schedule"
                      className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                      rows={2}
                    />
                  </div>
                  
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="active"
                      checked={scheduleData.active}
                      onChange={(e) => setScheduleData({
                        ...scheduleData,
                        active: e.target.checked
                      })}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <label htmlFor="active" className="ml-2 block text-sm text-gray-700">
                      Schedule is active
                    </label>
                  </div>
                </div>
              </div>
              
              <div>
                <h2 className="text-lg font-medium mb-4">Frequency</h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      How often should this report be generated?
                    </label>
                    <select
                      name="frequency"
                      value={scheduleData.frequency}
                      onChange={handleInputChange}
                      className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                    >
                      <option value="daily">Daily</option>
                      <option value="weekly">Weekly</option>
                      <option value="monthly">Monthly</option>
                      <option value="quarterly">Quarterly</option>
                    </select>
                  </div>
                  
                  {scheduleData.frequency === 'weekly' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Day of Week
                      </label>
                      <select
                        name="dayOfWeek"
                        value={scheduleData.dayOfWeek}
                        onChange={handleInputChange}
                        className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                      >
                        <option value="1">Monday</option>
                        <option value="2">Tuesday</option>
                        <option value="3">Wednesday</option>
                        <option value="4">Thursday</option>
                        <option value="5">Friday</option>
                        <option value="6">Saturday</option>
                        <option value="0">Sunday</option>
                      </select>
                    </div>
                  )}
                  
                  {(scheduleData.frequency === 'monthly' || scheduleData.frequency === 'quarterly') && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Day of Month
                      </label>
                      <select
                        name="dayOfMonth"
                        value={scheduleData.dayOfMonth}
                        onChange={handleInputChange}
                        className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                      >
                        {[...Array(31)].map((_, i) => (
                          <option key={i + 1} value={i + 1}>
                            {i + 1}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Time
                    </label>
                    <Input
                      type="time"
                      name="time"
                      value={scheduleData.time}
                      onChange={handleInputChange}
                      className="w-full"
                    />
                  </div>
                </div>
              </div>
              
              <div>
                <h2 className="text-lg font-medium mb-4">Export Formats</h2>
                
                <div className="space-y-2">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="format-pdf"
                      checked={scheduleData.formats.includes('pdf')}
                      onChange={() => toggleFormat('pdf')}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <label htmlFor="format-pdf" className="ml-2 block text-sm text-gray-700">
                      PDF
                    </label>
                  </div>
                  
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="format-xlsx"
                      checked={scheduleData.formats.includes('xlsx')}
                      onChange={() => toggleFormat('xlsx')}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <label htmlFor="format-xlsx" className="ml-2 block text-sm text-gray-700">
                      Excel (XLSX)
                    </label>
                  </div>
                  
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="format-csv"
                      checked={scheduleData.formats.includes('csv')}
                      onChange={() => toggleFormat('csv')}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <label htmlFor="format-csv" className="ml-2 block text-sm text-gray-700">
                      CSV
                    </label>
                  </div>
                </div>
              </div>
              
              <div>
                <h2 className="text-lg font-medium mb-4">Recipients</h2>
                
                <div className="space-y-4">
                  <div className="flex space-x-2">
                    <div className="flex-1">
                      <Input
                        type="text"
                        placeholder="Search for users..."
                        value={userSearchTerm}
                        onChange={(e) => setUserSearchTerm(e.target.value)}
                        className="w-full"
                      />
                    </div>
                    
                    <div className="flex-1">
                      <select
                        value={selectedUser}
                        onChange={(e) => setSelectedUser(e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                      >
                        <option value="">Select a user...</option>
                        {filteredUsers.map(user => (
                          <option key={user.id} value={user.id}>
                            {user.name} ({user.email})
                          </option>
                        ))}
                      </select>
                    </div>
                    
                    <Button
                      variant="outline"
                      onClick={addRecipient}
                      disabled={!selectedUser}
                    >
                      Add
                    </Button>
                  </div>
                  
                  {scheduleData.recipients.length > 0 ? (
                    <div className="border rounded-md overflow-hidden">
                      <table className="w-full">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {scheduleData.recipients.map((recipient, index) => (
                            <tr key={recipient.id} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                              <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                                {recipient.name}
                              </td>
                              <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                                {recipient.email}
                              </td>
                              <td className="px-4 py-3 whitespace-nowrap text-right text-sm">
                                <button
                                  type="button"
                                  onClick={() => removeRecipient(recipient.id)}
                                  className="text-red-500 hover:text-red-700"
                                >
                                  Remove
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="text-center p-4 bg-gray-50 rounded-md">
                      <Users className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                      <p className="text-gray-500">No recipients added</p>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="pt-4 border-t flex justify-between">
                {editMode ? (
                  <Button
                    variant="destructive"
                    onClick={deleteSchedule}
                    className="flex items-center"
                    disabled={isDeleting}
                  >
                    {isDeleting ? (
                      <>
                        <Loader className="w-4 h-4 mr-2 animate-spin" />
                        Deleting...
                      </>
                    ) : (
                      <>
                        <Trash className="w-4 h-4 mr-2" />
                        Delete Schedule
                      </>
                    )}
                  </Button>
                ) : (
                  <div></div>
                )}
                
                <div className="flex space-x-3">
                  <Button
                    variant="outline"
                    onClick={() => navigate('/reports')}
                  >
                    Cancel
                  </Button>
                  
                  <Button
                    variant="default"
                    onClick={saveSchedule}
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
                        {editMode ? 'Update Schedule' : 'Create Schedule'}
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        </div>
        
        <div className="lg:col-span-1">
          <Card className="p-6">
            <h2 className="text-lg font-medium mb-4">Report Details</h2>
            
            {report ? (
              <div className="space-y-4">
                <div className="flex items-center">
                  <div className="p-2 bg-gray-100 rounded-full mr-3">
                    {report.type === 'beneficiary' ? (
                      <Users className="w-5 h-5 text-blue-500" />
                    ) : report.type === 'program' ? (
                      <Users className="w-5 h-5 text-purple-500" />
                    ) : report.type === 'trainer' ? (
                      <Users className="w-5 h-5 text-green-500" />
                    ) : (
                      <Users className="w-5 h-5 text-gray-500" />
                    )}
                  </div>
                  <div>
                    <h3 className="font-medium">{report.name}</h3>
                    <p className="text-sm text-gray-500">{report.description}</p>
                  </div>
                </div>
                
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-500">Report Type</span>
                    <span className="font-medium capitalize">{report.type}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-500">Created By</span>
                    <span className="font-medium">{report.createdBy?.name || 'Unknown'}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-500">Last Run</span>
                    <span className="font-medium">{report.lastRun ? new Date(report.lastRun).toLocaleDateString() : 'Never'}</span>
                  </div>
                  <div className="flex justify-between py-2">
                    <span className="text-gray-500">Scheduled Runs</span>
                    <span className="font-medium">{report.scheduledRuns || 0}</span>
                  </div>
                </div>
                
                <div className="mt-2">
                  <h3 className="text-sm font-medium mb-2">Next Run Information</h3>
                  
                  {scheduleData.active ? (
                    <div className="bg-green-50 p-3 rounded-md">
                      <div className="flex items-start">
                        <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="text-sm font-medium text-green-800">
                            {scheduleData.frequency === 'daily' && 'Daily at '}
                            {scheduleData.frequency === 'weekly' && (
                              <>
                                Every {
                                  scheduleData.dayOfWeek === '0' ? 'Sunday' :
                                  scheduleData.dayOfWeek === '1' ? 'Monday' :
                                  scheduleData.dayOfWeek === '2' ? 'Tuesday' :
                                  scheduleData.dayOfWeek === '3' ? 'Wednesday' :
                                  scheduleData.dayOfWeek === '4' ? 'Thursday' :
                                  scheduleData.dayOfWeek === '5' ? 'Friday' : 'Saturday'
                                } at 
                              </>
                            )}
                            {scheduleData.frequency === 'monthly' && `Monthly on day ${scheduleData.dayOfMonth} at `}
                            {scheduleData.frequency === 'quarterly' && `Quarterly on day ${scheduleData.dayOfMonth} at `}
                            {scheduleData.time}
                          </p>
                          <p className="text-xs text-green-600 mt-1">
                            Will be sent to {scheduleData.recipients.length} recipient(s)
                          </p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-gray-50 p-3 rounded-md">
                      <div className="flex items-start">
                        <Clock className="w-5 h-5 text-gray-400 mr-2 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="text-sm font-medium text-gray-700">
                            Schedule is currently inactive
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            No reports will be generated automatically
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="flex items-center justify-between pt-4">
                  <div className="flex items-center">
                    <Mail className="w-5 h-5 text-primary mr-2" />
                    <span className="text-sm font-medium">Email Delivery</span>
                  </div>
                  
                  <div className="flex items-center">
                    <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                      {scheduleData.formats.map(f => f.toUpperCase()).join(', ')}
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-6">
                <p className="text-gray-500">No report selected</p>
              </div>
            )}
          </Card>
          
          <div className="mt-4 bg-amber-50 border border-amber-200 p-4 rounded-md">
            <div className="flex items-start">
              <AlertCircle className="w-5 h-5 text-amber-500 mr-2 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-amber-800">About Scheduled Reports</p>
                <ul className="text-xs text-amber-700 mt-2 space-y-1 list-disc list-inside">
                  <li>Reports will be generated automatically according to your schedule</li>
                  <li>All recipients will receive an email with the report attached</li>
                  <li>Reports can be generated in multiple formats simultaneously</li>
                  <li>You can update or cancel this schedule at any time</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportSchedulePage;
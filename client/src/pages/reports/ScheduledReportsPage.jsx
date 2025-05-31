import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import {
  Calendar,
  Clock,
  Mail,
  FileText,
  Plus,
  Edit,
  Trash2,
  Play,
  Pause,
  Search,
  Filter,
  Download
} from 'lucide-react';
import { useToast } from '../../hooks/useToast';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../../components/ui/table';

const ScheduledReportsPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [schedules, setSchedules] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterFrequency, setFilterFrequency] = useState('all');

  useEffect(() => {
    fetchScheduledReports();
  }, []);

  const fetchScheduledReports = async () => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSchedules([
        {
          id: 1,
          name: 'Weekly Performance Report',
          report_type: 'Performance Analytics',
          frequency: 'weekly',
          next_run: '2025-06-02 09:00',
          last_run: '2025-05-26 09:00',
          status: 'active',
          recipients: ['admin@bdc.com', 'manager@bdc.com'],
          format: 'PDF',
          created_by: 'Admin User',
          created_at: '2025-04-15'
        },
        {
          id: 2,
          name: 'Monthly Beneficiary Progress',
          report_type: 'Beneficiary Report',
          frequency: 'monthly',
          next_run: '2025-06-01 08:00',
          last_run: '2025-05-01 08:00',
          status: 'active',
          recipients: ['trainer@bdc.com'],
          format: 'Excel',
          created_by: 'Trainer User',
          created_at: '2025-03-20'
        },
        {
          id: 3,
          name: 'Daily Attendance Summary',
          report_type: 'Attendance Report',
          frequency: 'daily',
          next_run: '2025-05-29 07:00',
          last_run: '2025-05-28 07:00',
          status: 'active',
          recipients: ['admin@bdc.com'],
          format: 'PDF',
          created_by: 'Admin User',
          created_at: '2025-05-01'
        },
        {
          id: 4,
          name: 'Quarterly Financial Report',
          report_type: 'Financial Report',
          frequency: 'quarterly',
          next_run: '2025-07-01 10:00',
          last_run: '2025-04-01 10:00',
          status: 'paused',
          recipients: ['finance@bdc.com', 'admin@bdc.com'],
          format: 'PDF',
          created_by: 'Finance Manager',
          created_at: '2025-01-10'
        },
        {
          id: 5,
          name: 'Custom Training Report',
          report_type: 'Custom Report',
          frequency: 'custom',
          next_run: '2025-06-15 14:00',
          last_run: null,
          status: 'active',
          recipients: ['trainer@bdc.com', 'admin@bdc.com'],
          format: 'CSV',
          created_by: 'Admin User',
          created_at: '2025-05-20'
        }
      ]);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load scheduled reports",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleToggleStatus = async (schedule) => {
    try {
      const newStatus = schedule.status === 'active' ? 'paused' : 'active';
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setSchedules(schedules.map(s => 
        s.id === schedule.id 
          ? { ...s, status: newStatus }
          : s
      ));
      
      toast({
        title: "Success",
        description: `Report schedule ${newStatus === 'active' ? 'activated' : 'paused'}`
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update schedule status",
        variant: "destructive"
      });
    }
  };

  const handleDeleteSchedule = async (scheduleId) => {
    if (!confirm('Are you sure you want to delete this scheduled report?')) return;

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setSchedules(schedules.filter(s => s.id !== scheduleId));
      
      toast({
        title: "Success",
        description: "Scheduled report deleted successfully"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete scheduled report",
        variant: "destructive"
      });
    }
  };

  const handleRunNow = async (schedule) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast({
        title: "Report Generation Started",
        description: `${schedule.name} is being generated and will be sent to recipients shortly.`
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to generate report",
        variant: "destructive"
      });
    }
  };

  const getFrequencyBadgeVariant = (frequency) => {
    switch (frequency) {
      case 'daily': return 'default';
      case 'weekly': return 'secondary';
      case 'monthly': return 'outline';
      case 'quarterly': return 'outline';
      case 'custom': return 'secondary';
      default: return 'default';
    }
  };

  const filteredSchedules = schedules.filter(schedule => {
    const matchesSearch = 
      schedule.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      schedule.report_type.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || schedule.status === filterStatus;
    const matchesFrequency = filterFrequency === 'all' || schedule.frequency === filterFrequency;
    return matchesSearch && matchesStatus && matchesFrequency;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Scheduled Reports</h1>
          <p className="text-gray-600 mt-1">Manage automated report generation and delivery</p>
        </div>
        <Button onClick={() => navigate('/reports/schedules/create')}>
          <Plus className="h-4 w-4 mr-2" />
          Create Schedule
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Schedules</p>
                <p className="text-2xl font-bold">
                  {schedules.filter(s => s.status === 'active').length}
                </p>
              </div>
              <Play className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Paused Schedules</p>
                <p className="text-2xl font-bold">
                  {schedules.filter(s => s.status === 'paused').length}
                </p>
              </div>
              <Pause className="h-8 w-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Daily Reports</p>
                <p className="text-2xl font-bold">
                  {schedules.filter(s => s.frequency === 'daily').length}
                </p>
              </div>
              <Calendar className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Recipients</p>
                <p className="text-2xl font-bold">
                  {schedules.reduce((acc, s) => acc + s.recipients.length, 0)}
                </p>
              </div>
              <Mail className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search schedules..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-[180px]">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="paused">Paused</SelectItem>
              </SelectContent>
            </Select>
            <Select value={filterFrequency} onValueChange={setFilterFrequency}>
              <SelectTrigger className="w-[180px]">
                <Clock className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Filter by frequency" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Frequencies</SelectItem>
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="weekly">Weekly</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
                <SelectItem value="quarterly">Quarterly</SelectItem>
                <SelectItem value="custom">Custom</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Schedules Table */}
      <Card>
        <CardHeader>
          <CardTitle>Report Schedules</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Report Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Frequency</TableHead>
                <TableHead>Next Run</TableHead>
                <TableHead>Recipients</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredSchedules.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-8">
                    <p className="text-gray-500">No scheduled reports found</p>
                  </TableCell>
                </TableRow>
              ) : (
                filteredSchedules.map((schedule) => (
                  <TableRow key={schedule.id}>
                    <TableCell>
                      <div>
                        <p className="font-medium">{schedule.name}</p>
                        <p className="text-sm text-gray-500">
                          Created by {schedule.created_by}
                        </p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-gray-400" />
                        <span>{schedule.report_type}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getFrequencyBadgeVariant(schedule.frequency)}>
                        {schedule.frequency}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div>
                        <p className="text-sm">{schedule.next_run}</p>
                        {schedule.last_run && (
                          <p className="text-xs text-gray-500">
                            Last: {schedule.last_run}
                          </p>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Mail className="h-4 w-4 text-gray-400" />
                        <span>{schedule.recipients.length}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant={schedule.status === 'active' ? 'success' : 'secondary'}
                      >
                        {schedule.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRunNow(schedule)}
                          title="Run now"
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleToggleStatus(schedule)}
                          title={schedule.status === 'active' ? 'Pause' : 'Activate'}
                        >
                          {schedule.status === 'active' ? (
                            <Pause className="h-4 w-4" />
                          ) : (
                            <Play className="h-4 w-4" />
                          )}
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => navigate(`/reports/schedules/${schedule.id}/edit`)}
                          title="Edit"
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteSchedule(schedule.id)}
                          className="text-red-600 hover:text-red-700"
                          title="Delete"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default ScheduledReportsPage;
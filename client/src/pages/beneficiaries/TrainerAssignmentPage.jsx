import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Search, 
  Users, 
  CheckCircle, 
  XCircle, 
  UserX, 
  UserCheck, 
  AlertTriangle, 
  FileText,
  Calendar,
  Clock,
  Filter
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ui/toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Tabs, TabsList, TabTrigger, TabContent } from '@/components/ui/tabs';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '@/components/ui/modal';
import { Alert } from '@/components/ui/alert';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { formatDate } from '@/lib/utils';
import api from '@/lib/api';
/**
 * TrainerAssignmentPage component for managing trainer assignments for a beneficiary
 */
const TrainerAssignmentPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { hasRole } = useAuth();
  const { addToast } = useToast();
  // State
  const [beneficiary, setBeneficiary] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('current');
  const [isTabLoading, setIsTabLoading] = useState(false);
  // Assignment state
  const [currentTrainers, setCurrentTrainers] = useState([]);
  const [availableTrainers, setAvailableTrainers] = useState([]);
  const [historyTrainers, setHistoryTrainers] = useState([]);
  const [selectedTrainers, setSelectedTrainers] = useState([]);
  // Filters and search
  const [searchTerm, setSearchTerm] = useState('');
  const [specialtyFilter, setSpecialtyFilter] = useState('all');
  const [availabilityFilter, setAvailabilityFilter] = useState('all');
  const [filteredTrainers, setFilteredTrainers] = useState([]);
  // Modal state
  const [isRemoveModalOpen, setIsRemoveModalOpen] = useState(false);
  const [trainerToRemove, setTrainerToRemove] = useState(null);
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
  const [assignmentNote, setAssignmentNote] = useState('');
  // Check if user can manage trainers
  const canManage = hasRole(['super_admin', 'tenant_admin', 'trainer']);
  // Fetch beneficiary data
  useEffect(() => {
    const fetchBeneficiary = async () => {
      try {
        setIsLoading(true);
        const response = await api.get(`/api/beneficiaries/${id}`);
        setBeneficiary(response.data);
      } catch (error) {
        console.error('Error fetching beneficiary:', error);
        addToast({
          type: 'error',
          title: 'Failed to load beneficiary',
          message: error.response?.data?.message || 'An unexpected error occurred'
        });
        // Navigate back on error
        navigate('/beneficiaries');
      } finally {
        setIsLoading(false);
      }
    };
    fetchBeneficiary();
  }, [id, navigate, addToast]);
  // Fetch current trainers
  useEffect(() => {
    if (beneficiary && activeTab === 'current') {
      const fetchCurrentTrainers = async () => {
        try {
          setIsTabLoading(true);
          const response = await api.get(`/api/beneficiaries/${id}/trainers`);
          setCurrentTrainers(response.data);
        } catch (error) {
          console.error('Error fetching current trainers:', error);
          addToast({
            type: 'error',
            title: 'Failed to load trainers',
            message: 'Could not fetch current trainers.'
          });
        } finally {
          setIsTabLoading(false);
        }
      };
      fetchCurrentTrainers();
    }
  }, [beneficiary, id, activeTab, addToast]);
  // Fetch available trainers
  useEffect(() => {
    if (beneficiary && activeTab === 'available') {
      const fetchAvailableTrainers = async () => {
        try {
          setIsTabLoading(true);
          const response = await api.get('/api/trainers', {
            params: {
              available_for_assignment: true,
              exclude_beneficiary: id
            }
          });
          setAvailableTrainers(response.data.items || []);
          setFilteredTrainers(response.data.items || []);
        } catch (error) {
          console.error('Error fetching available trainers:', error);
          addToast({
            type: 'error',
            title: 'Failed to load trainers',
            message: 'Could not fetch available trainers.'
          });
        } finally {
          setIsTabLoading(false);
        }
      };
      fetchAvailableTrainers();
    }
  }, [beneficiary, id, activeTab, addToast]);
  // Fetch assignment history
  useEffect(() => {
    if (beneficiary && activeTab === 'history') {
      const fetchHistoryTrainers = async () => {
        try {
          setIsTabLoading(true);
          const response = await api.get(`/api/beneficiaries/${id}/trainers/history`);
          setHistoryTrainers(response.data);
        } catch (error) {
          console.error('Error fetching trainer history:', error);
          addToast({
            type: 'error',
            title: 'Failed to load history',
            message: 'Could not fetch trainer assignment history.'
          });
        } finally {
          setIsTabLoading(false);
        }
      };
      fetchHistoryTrainers();
    }
  }, [beneficiary, id, activeTab, addToast]);
  // Apply filters to available trainers
  useEffect(() => {
    if (availableTrainers.length > 0) {
      let filtered = [...availableTrainers];
      // Apply search filter
      if (searchTerm) {
        const term = searchTerm.toLowerCase();
        filtered = filtered.filter(trainer => 
          trainer.first_name.toLowerCase().includes(term) || 
          trainer.last_name.toLowerCase().includes(term) || 
          trainer.email.toLowerCase().includes(term)
        );
      }
      // Apply specialty filter
      if (specialtyFilter !== 'all') {
        filtered = filtered.filter(trainer => 
          trainer.specialties && trainer.specialties.includes(specialtyFilter)
        );
      }
      // Apply availability filter
      if (availabilityFilter !== 'all') {
        filtered = filtered.filter(trainer => {
          if (availabilityFilter === 'high') {
            return trainer.availability_score >= 70;
          } else if (availabilityFilter === 'medium') {
            return trainer.availability_score >= 40 && trainer.availability_score < 70;
          } else {
            return trainer.availability_score < 40;
          }
        });
      }
      setFilteredTrainers(filtered);
    }
  }, [searchTerm, specialtyFilter, availabilityFilter, availableTrainers]);
  // Handle trainer selection
  const toggleTrainerSelection = (trainerId) => {
    setSelectedTrainers(prev => {
      if (prev.includes(trainerId)) {
        return prev.filter(id => id !== trainerId);
      } else {
        return [...prev, trainerId];
      }
    });
  };
  // Handle remove trainer
  const handleRemoveTrainer = (trainer) => {
    setTrainerToRemove(trainer);
    setIsRemoveModalOpen(true);
  };
  // Confirm remove trainer
  const confirmRemoveTrainer = async () => {
    if (!trainerToRemove) return;
    try {
      setIsLoading(true);
      await api.delete(`/api/beneficiaries/${id}/trainers/${trainerToRemove.id}`);
      addToast({
        type: 'success',
        title: 'Trainer removed',
        message: `${trainerToRemove.first_name} ${trainerToRemove.last_name} has been unassigned from this beneficiary.`
      });
      // Update current trainers list
      setCurrentTrainers(prev => prev.filter(trainer => trainer.id !== trainerToRemove.id));
      // Close modal
      setIsRemoveModalOpen(false);
      setTrainerToRemove(null);
    } catch (error) {
      console.error('Error removing trainer:', error);
      addToast({
        type: 'error',
        title: 'Failed to remove trainer',
        message: error.response?.data?.message || 'An unexpected error occurred'
      });
    } finally {
      setIsLoading(false);
    }
  };
  // Handle assign trainers
  const handleAssignTrainers = () => {
    if (selectedTrainers.length === 0) {
      addToast({
        type: 'error',
        title: 'No trainers selected',
        message: 'Please select at least one trainer to assign.'
      });
      return;
    }
    setIsAssignModalOpen(true);
  };
  // Confirm assign trainers
  const confirmAssignTrainers = async () => {
    try {
      setIsLoading(true);
      // Assign trainers with the assignment note
      await api.post(`/api/beneficiaries/${id}/trainers`, {
        trainer_ids: selectedTrainers,
        note: assignmentNote
      });
      addToast({
        type: 'success',
        title: 'Trainers assigned',
        message: `${selectedTrainers.length} trainer(s) have been assigned to this beneficiary.`
      });
      // Reset state
      setSelectedTrainers([]);
      setAssignmentNote('');
      setIsAssignModalOpen(false);
      // Refresh current trainers and switch to current tab
      const response = await api.get(`/api/beneficiaries/${id}/trainers`);
      setCurrentTrainers(response.data);
      setActiveTab('current');
    } catch (error) {
      console.error('Error assigning trainers:', error);
      addToast({
        type: 'error',
        title: 'Failed to assign trainers',
        message: error.response?.data?.message || 'An unexpected error occurred'
      });
    } finally {
      setIsLoading(false);
    }
  };
  // Render loading state
  if (isLoading && !beneficiary) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }
  // Render not found state
  if (!beneficiary) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Beneficiary Not Found</h1>
          <p className="text-gray-600 mb-6">The beneficiary you're looking for doesn't exist or has been removed.</p>
          <Button 
            onClick={() => navigate('/beneficiaries')}
            leftIcon={<ArrowLeft className="h-4 w-4" />}
          >
            Back to Beneficiaries
          </Button>
        </div>
      </div>
    );
  }
  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header with navigation */}
      <div className="mb-6">
        <Button
          variant="outline"
          onClick={() => navigate(`/beneficiaries/${id}`)}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Beneficiary
        </Button>
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
          <div>
            <h1 className="text-2xl font-bold">Manage Trainers</h1>
            <p className="text-gray-600">
              Assign or remove trainers for {beneficiary.first_name} {beneficiary.last_name}
            </p>
          </div>
          {activeTab === 'available' && selectedTrainers.length > 0 && (
            <Button
              onClick={handleAssignTrainers}
              className="mt-4 md:mt-0"
            >
              <UserCheck className="h-4 w-4 mr-2" />
              Assign Selected ({selectedTrainers.length})
            </Button>
          )}
        </div>
      </div>
      {/* Beneficiary summary card */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row items-center md:items-start gap-4">
            <Avatar 
              src={beneficiary.profile_picture}
              alt={`${beneficiary.first_name} ${beneficiary.last_name}`}
              initials={`${beneficiary.first_name?.[0] || ''}${beneficiary.last_name?.[0] || ''}`}
              size="lg"
            />
            <div className="flex-1 text-center md:text-left">
              <h2 className="text-xl font-semibold">
                {beneficiary.first_name} {beneficiary.last_name}
              </h2>
              <p className="text-gray-600">{beneficiary.email}</p>
              <div className="flex flex-wrap gap-2 mt-2 justify-center md:justify-start">
                <Badge color={
                  beneficiary.status === 'active' ? 'green' :
                  beneficiary.status === 'inactive' ? 'gray' :
                  beneficiary.status === 'pending' ? 'yellow' :
                  beneficiary.status === 'completed' ? 'blue' : 'gray'
                }>
                  {beneficiary.status.charAt(0).toUpperCase() + beneficiary.status.slice(1)}
                </Badge>
                {beneficiary.category && (
                  <Badge color="purple">{beneficiary.category}</Badge>
                )}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4 text-center">
              <div className="bg-gray-50 p-3 rounded-md">
                <div className="text-xl font-semibold">{currentTrainers?.length || 0}</div>
                <div className="text-xs text-gray-500">Assigned Trainers</div>
              </div>
              <div className="bg-gray-50 p-3 rounded-md">
                <div className="text-xl font-semibold">{beneficiary.session_count || 0}</div>
                <div className="text-xs text-gray-500">Total Sessions</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      {/* Tabs container */}
      <Card>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <CardHeader className="pb-0">
            <TabsList>
              <TabTrigger value="current">
                <Users className="h-4 w-4 mr-2" />
                Current Trainers
              </TabTrigger>
              <TabTrigger value="available">
                <UserCheck className="h-4 w-4 mr-2" />
                Available Trainers
              </TabTrigger>
              <TabTrigger value="history">
                <Clock className="h-4 w-4 mr-2" />
                Assignment History
              </TabTrigger>
            </TabsList>
          </CardHeader>
          {/* Current Trainers Tab */}
          <TabContent value="current">
            <CardContent className="pt-6">
              {isTabLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                  <p className="text-gray-500">Loading trainers...</p>
                </div>
              ) : currentTrainers.length === 0 ? (
                <div className="text-center py-8 border rounded-md">
                  <Users className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                  <h4 className="font-medium text-gray-500">No trainers assigned</h4>
                  <p className="text-gray-400 text-sm mt-1">This beneficiary doesn't have any trainers assigned yet.</p>
                  <Button 
                    variant="outline" 
                    className="mt-4"
                    onClick={() => setActiveTab('available')}
                  >
                    Assign Trainers
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {currentTrainers.map((trainer) => (
                    <Card key={trainer.id} className="overflow-hidden">
                      <div className="flex flex-col md:flex-row">
                        <div className="p-4 md:p-6 flex-1">
                          <div className="flex flex-col md:flex-row items-center md:items-start gap-4">
                            <Avatar 
                              src={trainer.profile_picture}
                              alt={`${trainer.first_name} ${trainer.last_name}`}
                              initials={`${trainer.first_name?.[0] || ''}${trainer.last_name?.[0] || ''}`}
                              size="md"
                            />
                            <div className="flex-1 text-center md:text-left">
                              <h3 className="font-semibold">{trainer.first_name} {trainer.last_name}</h3>
                              <p className="text-gray-600">{trainer.email}</p>
                              <div className="flex flex-wrap gap-2 mt-2 justify-center md:justify-start">
                                {trainer.specialties?.map((specialty, index) => (
                                  <Badge key={index}>{specialty}</Badge>
                                ))}
                              </div>
                            </div>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                            <div className="text-sm">
                              <p className="text-gray-500">Assigned Since</p>
                              <p className="font-medium">{formatDate(trainer.assigned_date)}</p>
                            </div>
                            <div className="text-sm">
                              <p className="text-gray-500">Sessions Conducted</p>
                              <p className="font-medium">{trainer.session_count || 0} sessions</p>
                            </div>
                            <div className="text-sm">
                              <p className="text-gray-500">Last Session</p>
                              <p className="font-medium">
                                {trainer.last_session_date ? formatDate(trainer.last_session_date) : 'No sessions yet'}
                              </p>
                            </div>
                          </div>
                          {trainer.assignment_note && (
                            <div className="mt-4 p-3 bg-gray-50 rounded-md text-sm">
                              <p className="font-medium">Assignment Note:</p>
                              <p className="text-gray-600 mt-1">{trainer.assignment_note}</p>
                            </div>
                          )}
                        </div>
                        <div className="bg-gray-50 p-4 md:w-48 flex flex-row md:flex-col justify-between items-center md:items-start gap-2">
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => navigate(`/users/${trainer.id}`)}
                          >
                            View Profile
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => navigate(`/schedule/${trainer.id}`)}
                          >
                            View Schedule
                          </Button>
                          {canManage && (
                            <Button 
                              variant="ghost" 
                              size="sm"
                              className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              onClick={() => handleRemoveTrainer(trainer)}
                            >
                              <UserX className="h-4 w-4 mr-2" />
                              Remove
                            </Button>
                          )}
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </TabContent>
          {/* Available Trainers Tab */}
          <TabContent value="available">
            <CardContent className="pt-6">
              {/* Filters and search */}
              <div className="mb-6 space-y-4">
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1">
                    <Input
                      placeholder="Search by name or email..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      leftIcon={<Search className="h-4 w-4 text-gray-400" />}
                    />
                  </div>
                  <div className="flex gap-2">
                    <select
                      value={specialtyFilter}
                      onChange={(e) => setSpecialtyFilter(e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="all">All Specialties</option>
                      <option value="language">Language</option>
                      <option value="mathematics">Mathematics</option>
                      <option value="science">Science</option>
                      <option value="technology">Technology</option>
                      <option value="arts">Arts</option>
                      <option value="social">Social Skills</option>
                    </select>
                    <select
                      value={availabilityFilter}
                      onChange={(e) => setAvailabilityFilter(e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="all">All Availability</option>
                      <option value="high">High Availability</option>
                      <option value="medium">Medium Availability</option>
                      <option value="low">Low Availability</option>
                    </select>
                  </div>
                </div>
                {selectedTrainers.length > 0 && (
                  <div className="bg-primary bg-opacity-10 p-3 rounded-md flex justify-between items-center">
                    <span className="text-sm">
                      <strong>{selectedTrainers.length}</strong> trainer(s) selected
                    </span>
                    <div className="flex gap-2">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => setSelectedTrainers([])}
                      >
                        Clear All
                      </Button>
                      <Button 
                        size="sm"
                        onClick={handleAssignTrainers}
                      >
                        Assign Selected
                      </Button>
                    </div>
                  </div>
                )}
              </div>
              {/* Trainers list */}
              {isTabLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                  <p className="text-gray-500">Loading available trainers...</p>
                </div>
              ) : filteredTrainers.length === 0 ? (
                <div className="text-center py-8 border rounded-md">
                  <Filter className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                  <h4 className="font-medium text-gray-500">No trainers found</h4>
                  <p className="text-gray-400 text-sm mt-1">Try changing your search criteria or filters.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {filteredTrainers.map((trainer) => (
                    <Card 
                      key={trainer.id} 
                      className={`cursor-pointer ${
                        selectedTrainers.includes(trainer.id) ? 'ring-2 ring-primary' : ''
                      }`}
                      onClick={() => toggleTrainerSelection(trainer.id)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start gap-4">
                          <div className="relative">
                            <Avatar 
                              src={trainer.profile_picture}
                              alt={`${trainer.first_name} ${trainer.last_name}`}
                              initials={`${trainer.first_name?.[0] || ''}${trainer.last_name?.[0] || ''}`}
                              size="md"
                            />
                            {selectedTrainers.includes(trainer.id) && (
                              <div className="absolute -top-2 -right-2 bg-primary text-white rounded-full p-0.5">
                                <CheckCircle className="h-4 w-4" />
                              </div>
                            )}
                          </div>
                          <div className="flex-1">
                            <h3 className="font-semibold">{trainer.first_name} {trainer.last_name}</h3>
                            <p className="text-sm text-gray-600">{trainer.email}</p>
                            <div className="flex flex-wrap gap-1 mt-2">
                              {trainer.specialties?.map((specialty, index) => (
                                <Badge key={index} className="text-xs">{specialty}</Badge>
                              ))}
                            </div>
                            <div className="grid grid-cols-2 gap-2 mt-3 text-xs">
                              <div>
                                <p className="text-gray-500">Beneficiaries</p>
                                <p className="font-medium">{trainer.beneficiary_count || 0}</p>
                              </div>
                              <div>
                                <p className="text-gray-500">Availability</p>
                                <div className="flex items-center">
                                  <div className="w-16 h-2 bg-gray-200 rounded-full mr-2">
                                    <div 
                                      className={`h-2 rounded-full ${
                                        trainer.availability_score >= 70 ? 'bg-green-500' :
                                        trainer.availability_score >= 40 ? 'bg-yellow-500' :
                                        'bg-red-500'
                                      }`}
                                      style={{ width: `${trainer.availability_score}%` }}
                                    ></div>
                                  </div>
                                  <span className="font-medium">{trainer.availability_score}%</span>
                                </div>
                              </div>
                              <div>
                                <p className="text-gray-500">Experience</p>
                                <p className="font-medium">{trainer.experience_years || 0} years</p>
                              </div>
                              <div>
                                <p className="text-gray-500">Languages</p>
                                <p className="font-medium">{(trainer.languages || []).join(', ') || 'N/A'}</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </TabContent>
          {/* Assignment History Tab */}
          <TabContent value="history">
            <CardContent className="pt-6">
              {isTabLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                  <p className="text-gray-500">Loading assignment history...</p>
                </div>
              ) : historyTrainers.length === 0 ? (
                <div className="text-center py-8 border rounded-md">
                  <Clock className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                  <h4 className="font-medium text-gray-500">No assignment history</h4>
                  <p className="text-gray-400 text-sm mt-1">There is no trainer assignment history for this beneficiary.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {historyTrainers.map((record) => (
                    <div key={record.id} className="border-b pb-4 last:border-b-0 last:pb-0">
                      <div className="flex flex-col md:flex-row items-start gap-4">
                        <div className="w-16 text-center flex-shrink-0">
                          <div className="text-xs font-medium text-gray-500">
                            {formatDate(record.assigned_date).split(' ')[0]}
                          </div>
                          <div className="text-sm font-medium">
                            {formatDate(record.assigned_date).split(' ')[1]}
                          </div>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-start gap-3">
                            <Avatar 
                              src={record.trainer.profile_picture}
                              alt={`${record.trainer.first_name} ${record.trainer.last_name}`}
                              initials={`${record.trainer.first_name?.[0] || ''}${record.trainer.last_name?.[0] || ''}`}
                              size="sm"
                            />
                            <div>
                              <h3 className="font-medium">{record.trainer.first_name} {record.trainer.last_name}</h3>
                              <p className="text-sm text-gray-600">{record.trainer.email}</p>
                            </div>
                          </div>
                          <div className="ml-10 mt-2">
                            <Badge color={record.status === 'active' ? 'green' : 'red'}>
                              {record.status === 'active' ? 'Assigned' : 'Removed'}
                            </Badge>
                            {record.end_date && (
                              <span className="text-sm text-gray-500 ml-2">
                                {record.status === 'active' ? 'Since' : 'Until'} {formatDate(record.status === 'active' ? record.assigned_date : record.end_date)}
                              </span>
                            )}
                          </div>
                          {record.note && (
                            <div className="ml-10 mt-2 text-sm text-gray-600 bg-gray-50 p-2 rounded-md">
                              {record.note}
                            </div>
                          )}
                          {record.sessions_count > 0 && (
                            <div className="ml-10 mt-2 text-sm text-gray-600">
                              <span className="font-medium">{record.sessions_count}</span> sessions conducted
                              {record.last_session_date && `, last session on ${formatDate(record.last_session_date)}`}
                            </div>
                          )}
                        </div>
                        <div className="flex-shrink-0">
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => navigate(`/users/${record.trainer.id}`)}
                          >
                            View Profile
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </TabContent>
        </Tabs>
      </Card>
      {/* Remove trainer confirmation modal */}
      <Modal
        isOpen={isRemoveModalOpen}
        onClose={() => setIsRemoveModalOpen(false)}
      >
        <ModalHeader>
          <h3 className="text-lg font-medium">Remove Trainer</h3>
        </ModalHeader>
        <ModalBody>
          {trainerToRemove && (
            <>
              <Alert type="warning" title="Are you sure?">
                You're about to remove <strong>{trainerToRemove.first_name} {trainerToRemove.last_name}</strong> from this beneficiary. 
                This will end the current training relationship.
              </Alert>
              <div className="mt-4 p-4 bg-gray-50 rounded-md">
                <div className="flex items-center gap-3">
                  <Avatar 
                    src={trainerToRemove.profile_picture}
                    alt={`${trainerToRemove.first_name} ${trainerToRemove.last_name}`}
                    initials={`${trainerToRemove.first_name?.[0] || ''}${trainerToRemove.last_name?.[0] || ''}`}
                    size="md"
                  />
                  <div>
                    <h4 className="font-medium">{trainerToRemove.first_name} {trainerToRemove.last_name}</h4>
                    <p className="text-sm text-gray-600">{trainerToRemove.email}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      Assigned since {formatDate(trainerToRemove.assigned_date)}
                    </p>
                  </div>
                </div>
              </div>
            </>
          )}
        </ModalBody>
        <ModalFooter>
          <Button
            variant="outline"
            onClick={() => setIsRemoveModalOpen(false)}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={confirmRemoveTrainer}
            isLoading={isLoading}
            disabled={isLoading}
          >
            <UserX className="h-4 w-4 mr-2" />
            Remove Trainer
          </Button>
        </ModalFooter>
      </Modal>
      {/* Assign trainers modal */}
      <Modal
        isOpen={isAssignModalOpen}
        onClose={() => setIsAssignModalOpen(false)}
      >
        <ModalHeader>
          <h3 className="text-lg font-medium">Assign Trainers</h3>
        </ModalHeader>
        <ModalBody>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-600">
                You're about to assign <strong>{selectedTrainers.length}</strong> trainer(s) to:
              </p>
              <p className="font-medium mt-1">
                {beneficiary.first_name} {beneficiary.last_name}
              </p>
            </div>
            <div className="bg-gray-50 p-3 rounded-md max-h-48 overflow-y-auto">
              {availableTrainers
                .filter(trainer => selectedTrainers.includes(trainer.id))
                .map(trainer => (
                  <div key={trainer.id} className="flex items-center gap-2 mb-2 last:mb-0">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span>{trainer.first_name} {trainer.last_name}</span>
                  </div>
                ))
              }
            </div>
            <div>
              <label htmlFor="assignment-note" className="block text-sm font-medium text-gray-700 mb-1">
                Assignment Note (Optional)
              </label>
              <textarea
                id="assignment-note"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                rows={3}
                placeholder="Enter any notes about this assignment"
                value={assignmentNote}
                onChange={(e) => setAssignmentNote(e.target.value)}
              ></textarea>
              <p className="text-xs text-gray-500 mt-1">
                This note will be visible in the assignment history.
              </p>
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <Button
            variant="outline"
            onClick={() => setIsAssignModalOpen(false)}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            onClick={confirmAssignTrainers}
            isLoading={isLoading}
            disabled={isLoading}
          >
            <UserCheck className="h-4 w-4 mr-2" />
            Confirm Assignment
          </Button>
        </ModalFooter>
      </Modal>
    </div>
  );
};
export default TrainerAssignmentPage;
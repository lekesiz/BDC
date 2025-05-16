import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Edit, 
  Trash, 
  Mail, 
  Phone, 
  Calendar, 
  MapPin, 
  Globe, 
  FileText, 
  PieChart, 
  Clock, 
  ChevronRight,
  Users,
  BarChart2,
  Award,
  AlertTriangle
} from 'lucide-react';

import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ui/toast';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabTrigger, TabContent } from '@/components/ui/tabs';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '@/components/ui/modal';
import { Alert } from '@/components/ui/alert';
import { Avatar } from '@/components/ui/avatar';
import { formatDate, formatDateTime } from '@/lib/utils';
import api from '@/lib/api';

/**
 * Beneficiary detail page displaying comprehensive information and related data
 */
const BeneficiaryDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { hasRole } = useAuth();
  const { addToast } = useToast();
  
  // State
  const [beneficiary, setBeneficiary] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingTab, setIsLoadingTab] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  
  // Data for different tabs
  const [evaluations, setEvaluations] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [trainers, setTrainers] = useState([]);
  const [progress, setProgress] = useState({});
  const [documents, setDocuments] = useState([]);
  
  // Check if user can edit beneficiaries
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
  
  // Fetch tab data when tab changes
  useEffect(() => {
    if (!beneficiary) return;
    
    const fetchTabData = async () => {
      setIsLoadingTab(true);
      
      try {
        switch (activeTab) {
          case 'evaluations':
            const evaluationsResponse = await api.get(`/api/beneficiaries/${id}/evaluations`);
            setEvaluations(evaluationsResponse.data);
            break;
            
          case 'sessions':
            const sessionsResponse = await api.get(`/api/beneficiaries/${id}/sessions`);
            setSessions(sessionsResponse.data);
            break;
            
          case 'trainers':
            const trainersResponse = await api.get(`/api/beneficiaries/${id}/trainers`);
            setTrainers(trainersResponse.data);
            break;
            
          case 'progress':
            const progressResponse = await api.get(`/api/beneficiaries/${id}/progress`);
            setProgress(progressResponse.data);
            break;
            
          case 'documents':
            const documentsResponse = await api.get(`/api/beneficiaries/${id}/documents`);
            setDocuments(documentsResponse.data);
            break;
            
          default:
            break;
        }
      } catch (error) {
        console.error(`Error fetching ${activeTab} data:`, error);
        addToast({
          type: 'error',
          title: `Failed to load ${activeTab}`,
          message: error.response?.data?.message || 'An unexpected error occurred'
        });
      } finally {
        setIsLoadingTab(false);
      }
    };
    
    if (activeTab !== 'overview') {
      fetchTabData();
    }
  }, [activeTab, id, beneficiary, addToast]);
  
  // Handle edit beneficiary
  const handleEdit = () => {
    navigate(`/beneficiaries/${id}/edit`);
  };
  
  // Handle delete confirmation
  const handleDeleteConfirm = async () => {
    try {
      setIsLoading(true);
      
      await api.delete(`/api/beneficiaries/${id}`);
      
      addToast({
        type: 'success',
        title: 'Beneficiary deleted',
        message: 'The beneficiary has been successfully deleted.'
      });
      
      navigate('/beneficiaries');
    } catch (error) {
      console.error('Error deleting beneficiary:', error);
      addToast({
        type: 'error',
        title: 'Failed to delete',
        message: error.response?.data?.message || 'An unexpected error occurred'
      });
      setIsDeleteModalOpen(false);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Render status badge
  const renderStatusBadge = (status) => {
    const statusStyles = {
      active: 'bg-green-100 text-green-800',
      inactive: 'bg-gray-100 text-gray-800',
      pending: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-blue-100 text-blue-800'
    };
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusStyles[status] || 'bg-gray-100 text-gray-800'}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };
  
  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  // Not found state
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
      {/* Header with navigation and actions */}
      <div className="mb-6">
        <Button
          variant="outline"
          onClick={() => navigate('/beneficiaries')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Beneficiaries
        </Button>
        
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold">{beneficiary.first_name} {beneficiary.last_name}</h1>
            <div className="flex items-center mt-1">
              <p className="text-gray-600 mr-2">{beneficiary.email}</p>
              {renderStatusBadge(beneficiary.status)}
            </div>
          </div>
          
          {canManage && (
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => setIsDeleteModalOpen(true)}
              >
                <Trash className="h-4 w-4 mr-2" />
                Delete
              </Button>
              
              <Button onClick={handleEdit}>
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Button>
            </div>
          )}
        </div>
      </div>
      
      {/* Main content with sidebar and tabs */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col items-center text-center">
                <Avatar 
                  src={beneficiary.profile_picture}
                  alt={`${beneficiary.first_name} ${beneficiary.last_name}`}
                  initials={`${beneficiary.first_name?.[0] || ''}${beneficiary.last_name?.[0] || ''}`}
                  size="xl"
                  className="mb-4"
                />
                
                <h2 className="text-xl font-semibold">
                  {beneficiary.first_name} {beneficiary.last_name}
                </h2>
                
                <p className="text-muted-foreground">{beneficiary.email}</p>
                
                <div className="mt-2">
                  {renderStatusBadge(beneficiary.status)}
                </div>
              </div>
              
              <div className="mt-6 border-t pt-6 space-y-4">
                {beneficiary.phone && (
                  <div className="flex items-center">
                    <Phone className="h-4 w-4 text-gray-500 mr-3" />
                    <div>
                      <p className="text-sm font-medium">Phone</p>
                      <p className="text-sm text-muted-foreground">{beneficiary.phone}</p>
                    </div>
                  </div>
                )}
                
                {beneficiary.address && (
                  <div className="flex items-center">
                    <MapPin className="h-4 w-4 text-gray-500 mr-3" />
                    <div>
                      <p className="text-sm font-medium">Address</p>
                      <p className="text-sm text-muted-foreground">
                        {beneficiary.address}, 
                        {beneficiary.city && ` ${beneficiary.city},`}
                        {beneficiary.state && ` ${beneficiary.state}`}
                        {beneficiary.zip_code && ` ${beneficiary.zip_code}`}
                        {beneficiary.country && `, ${beneficiary.country}`}
                      </p>
                    </div>
                  </div>
                )}
                
                {beneficiary.birth_date && (
                  <div className="flex items-center">
                    <Calendar className="h-4 w-4 text-gray-500 mr-3" />
                    <div>
                      <p className="text-sm font-medium">Birth Date</p>
                      <p className="text-sm text-muted-foreground">{formatDate(beneficiary.birth_date)}</p>
                    </div>
                  </div>
                )}
                
                <div className="flex items-center">
                  <Clock className="h-4 w-4 text-gray-500 mr-3" />
                  <div>
                    <p className="text-sm font-medium">Registered</p>
                    <p className="text-sm text-muted-foreground">{formatDate(beneficiary.created_at)}</p>
                  </div>
                </div>
                
                {beneficiary.nationality && (
                  <div className="flex items-center">
                    <Globe className="h-4 w-4 text-gray-500 mr-3" />
                    <div>
                      <p className="text-sm font-medium">Nationality</p>
                      <p className="text-sm text-muted-foreground">{beneficiary.nationality}</p>
                    </div>
                  </div>
                )}
              </div>
              
              {/* Quick stats */}
              <div className="mt-6 border-t pt-6">
                <h3 className="text-sm font-medium mb-4">Quick Stats</h3>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 p-3 rounded-md">
                    <div className="text-xl font-semibold">{beneficiary.evaluation_count || 0}</div>
                    <div className="text-xs text-gray-500">Evaluations</div>
                  </div>
                  
                  <div className="bg-gray-50 p-3 rounded-md">
                    <div className="text-xl font-semibold">{beneficiary.completed_evaluation_count || 0}</div>
                    <div className="text-xs text-gray-500">Completed</div>
                  </div>
                  
                  <div className="bg-gray-50 p-3 rounded-md">
                    <div className="text-xl font-semibold">{beneficiary.session_count || 0}</div>
                    <div className="text-xs text-gray-500">Sessions</div>
                  </div>
                  
                  <div className="bg-gray-50 p-3 rounded-md">
                    <div className="text-xl font-semibold">{beneficiary.trainer_count || 0}</div>
                    <div className="text-xs text-gray-500">Trainers</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Main content tabs */}
        <div className="lg:col-span-3">
          <Card>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <CardHeader className="pb-0">
                <TabsList>
                  <TabTrigger value="overview">Overview</TabTrigger>
                  <TabTrigger value="evaluations">Evaluations</TabTrigger>
                  <TabTrigger value="sessions">Sessions</TabTrigger>
                  <TabTrigger value="trainers">Trainers</TabTrigger>
                  <TabTrigger value="progress">Progress</TabTrigger>
                  <TabTrigger value="documents">Documents</TabTrigger>
                </TabsList>
              </CardHeader>
              
              {/* Overview tab */}
              <TabContent value="overview">
                <CardContent className="pt-6">
                  {/* About section */}
                  <div className="mb-6">
                    <h3 className="text-lg font-medium mb-3">About</h3>
                    {beneficiary.bio ? (
                      <p className="text-gray-600">{beneficiary.bio}</p>
                    ) : (
                      <p className="text-gray-500 italic">No bio information available.</p>
                    )}
                  </div>
                  
                  {/* Additional details */}
                  {beneficiary.additional_details && Object.keys(beneficiary.additional_details).length > 0 && (
                    <div className="mb-6">
                      <h3 className="text-lg font-medium mb-3">Additional Details</h3>
                      <div className="bg-gray-50 rounded-md p-4">
                        <dl className="grid grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-2">
                          {Object.entries(beneficiary.additional_details).map(([key, value]) => (
                            <div key={key} className="py-2">
                              <dt className="text-sm font-medium text-gray-500">
                                {key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                              </dt>
                              <dd className="mt-1 text-sm text-gray-900">{value}</dd>
                            </div>
                          ))}
                        </dl>
                      </div>
                    </div>
                  )}
                  
                  {/* Notes section */}
                  <div className="mb-6">
                    <div className="flex justify-between items-center mb-3">
                      <h3 className="text-lg font-medium">Notes</h3>
                      {canManage && (
                        <Button variant="outline" size="sm">
                          Add Note
                        </Button>
                      )}
                    </div>
                    
                    {beneficiary.notes && beneficiary.notes.length > 0 ? (
                      <div className="space-y-4">
                        {beneficiary.notes.map((note) => (
                          <div key={note.id} className="bg-gray-50 rounded-md p-4">
                            <div className="flex justify-between items-start">
                              <p className="text-sm font-medium">{note.title}</p>
                              <span className="text-xs text-gray-500">{formatDate(note.created_at)}</span>
                            </div>
                            <p className="text-sm text-gray-600 mt-1">{note.content}</p>
                            <div className="mt-2 text-xs text-gray-500">
                              Added by {note.created_by_name}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 italic">No notes have been added yet.</p>
                    )}
                  </div>
                  
                  {/* Recent activity */}
                  <div>
                    <div className="flex justify-between items-center mb-3">
                      <h3 className="text-lg font-medium">Recent Activity</h3>
                      <Button variant="ghost" size="sm">
                        View All
                      </Button>
                    </div>
                    
                    {beneficiary.recent_activities && beneficiary.recent_activities.length > 0 ? (
                      <div className="space-y-4">
                        {beneficiary.recent_activities.map((activity, index) => (
                          <div key={index} className="flex items-start">
                            <div className="flex-shrink-0 mt-1">
                              <div className="h-8 w-8 rounded-full bg-primary bg-opacity-10 flex items-center justify-center">
                                <activity.icon className="h-4 w-4 text-primary" />
                              </div>
                            </div>
                            <div className="ml-3">
                              <p className="text-sm font-medium">{activity.description}</p>
                              <p className="text-xs text-gray-500">{formatDateTime(activity.timestamp)}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 italic">No recent activity.</p>
                    )}
                  </div>
                </CardContent>
              </TabContent>
              
              {/* Evaluations tab */}
              <TabContent value="evaluations">
                <CardContent className="pt-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-medium">Evaluations</h3>
                    {canManage && (
                      <Button>
                        New Evaluation
                      </Button>
                    )}
                  </div>
                  
                  {isLoadingTab ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                      <p className="text-gray-500">Loading evaluations...</p>
                    </div>
                  ) : evaluations.length === 0 ? (
                    <div className="text-center py-8 border rounded-md">
                      <PieChart className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                      <h4 className="font-medium text-gray-500">No evaluations found</h4>
                      <p className="text-gray-400 text-sm mt-1">This beneficiary hasn't completed any evaluations yet.</p>
                      {canManage && (
                        <Button variant="outline" className="mt-4">
                          Create First Evaluation
                        </Button>
                      )}
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {evaluations.map((evaluation) => (
                        <Card key={evaluation.id} className="overflow-hidden">
                          <div className="flex flex-col md:flex-row">
                            <div className="p-4 md:p-6 flex-1">
                              <div className="flex justify-between items-start">
                                <div>
                                  <h4 className="font-medium">{evaluation.title}</h4>
                                  <p className="text-sm text-gray-500 mt-1">{evaluation.description}</p>
                                </div>
                                <div>
                                  <Badge color={
                                    evaluation.status === 'completed' ? 'green' :
                                    evaluation.status === 'in_progress' ? 'yellow' :
                                    evaluation.status === 'pending' ? 'blue' : 'gray'
                                  }>
                                    {evaluation.status === 'in_progress' ? 'In Progress' : 
                                     evaluation.status.charAt(0).toUpperCase() + evaluation.status.slice(1)}
                                  </Badge>
                                </div>
                              </div>
                              
                              <div className="grid grid-cols-2 gap-4 mt-4">
                                <div className="text-sm">
                                  <p className="text-gray-500">Date</p>
                                  <p className="font-medium">{formatDate(evaluation.evaluation_date)}</p>
                                </div>
                                <div className="text-sm">
                                  <p className="text-gray-500">Evaluated By</p>
                                  <p className="font-medium">{evaluation.evaluator_name || 'System'}</p>
                                </div>
                                {evaluation.score !== undefined && (
                                  <div className="text-sm">
                                    <p className="text-gray-500">Score</p>
                                    <p className="font-medium">{evaluation.score} / {evaluation.max_score}</p>
                                  </div>
                                )}
                                {evaluation.time_taken && (
                                  <div className="text-sm">
                                    <p className="text-gray-500">Time Taken</p>
                                    <p className="font-medium">{evaluation.time_taken}</p>
                                  </div>
                                )}
                              </div>
                            </div>
                            
                            <div className="bg-gray-50 p-4 md:w-48 flex flex-row md:flex-col justify-between items-center md:items-start gap-2">
                              {evaluation.status === 'completed' && (
                                <div className="md:mb-4">
                                  <div className="text-3xl font-bold text-primary">
                                    {evaluation.percentage_score}%
                                  </div>
                                  <div className="text-xs text-gray-500">Overall Score</div>
                                </div>
                              )}
                              
                              <Link 
                                to={`/evaluations/${evaluation.id}`}
                                className="flex items-center text-primary hover:underline text-sm md:mt-auto"
                              >
                                View Details
                                <ChevronRight className="h-4 w-4 ml-1" />
                              </Link>
                            </div>
                          </div>
                        </Card>
                      ))}
                    </div>
                  )}
                </CardContent>
              </TabContent>
              
              {/* Sessions tab */}
              <TabContent value="sessions">
                <CardContent className="pt-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-medium">Training Sessions</h3>
                    {canManage && (
                      <Button>
                        Schedule Session
                      </Button>
                    )}
                  </div>
                  
                  {isLoadingTab ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                      <p className="text-gray-500">Loading sessions...</p>
                    </div>
                  ) : sessions.length === 0 ? (
                    <div className="text-center py-8 border rounded-md">
                      <Calendar className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                      <h4 className="font-medium text-gray-500">No sessions scheduled</h4>
                      <p className="text-gray-400 text-sm mt-1">No training sessions have been scheduled yet.</p>
                      {canManage && (
                        <Button variant="outline" className="mt-4">
                          Schedule First Session
                        </Button>
                      )}
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {sessions.map((session) => (
                        <Card key={session.id} className="overflow-hidden">
                          <div className="flex flex-col md:flex-row">
                            <div className="p-4 md:p-6 flex-1">
                              <div className="flex justify-between items-start">
                                <div>
                                  <h4 className="font-medium">{session.title}</h4>
                                  <p className="text-sm text-gray-500 mt-1">{session.description}</p>
                                </div>
                                <div>
                                  <Badge color={
                                    session.status === 'completed' ? 'green' :
                                    session.status === 'scheduled' ? 'blue' :
                                    session.status === 'cancelled' ? 'red' : 'gray'
                                  }>
                                    {session.status.charAt(0).toUpperCase() + session.status.slice(1)}
                                  </Badge>
                                </div>
                              </div>
                              
                              <div className="grid grid-cols-2 gap-4 mt-4">
                                <div className="text-sm">
                                  <p className="text-gray-500">Date</p>
                                  <p className="font-medium">{formatDate(session.scheduled_at)}</p>
                                </div>
                                <div className="text-sm">
                                  <p className="text-gray-500">Duration</p>
                                  <p className="font-medium">{session.duration} minutes</p>
                                </div>
                                <div className="text-sm">
                                  <p className="text-gray-500">Trainer</p>
                                  <p className="font-medium">{session.trainer_name}</p>
                                </div>
                                <div className="text-sm">
                                  <p className="text-gray-500">Location</p>
                                  <p className="font-medium">{session.location || 'Online'}</p>
                                </div>
                              </div>
                            </div>
                            
                            <div className="bg-gray-50 p-4 md:w-48 flex flex-row md:flex-col justify-between items-center md:items-start gap-2">
                              {session.status === 'scheduled' && (
                                <div className="md:mb-4">
                                  <div className="text-sm font-semibold text-green-600">
                                    {new Date(session.scheduled_at) > new Date() ? 'Upcoming' : 'Today'}
                                  </div>
                                </div>
                              )}
                              
                              <Link 
                                to={`/sessions/${session.id}`}
                                className="flex items-center text-primary hover:underline text-sm md:mt-auto"
                              >
                                View Details
                                <ChevronRight className="h-4 w-4 ml-1" />
                              </Link>
                            </div>
                          </div>
                        </Card>
                      ))}
                    </div>
                  )}
                </CardContent>
              </TabContent>
              
              {/* Trainers tab */}
              <TabContent value="trainers">
                <CardContent className="pt-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-medium">Assigned Trainers</h3>
                    {canManage && (
                      <Button
                        onClick={() => navigate(`/beneficiaries/${id}/trainers`)}
                      >
                        Assign Trainer
                      </Button>
                    )}
                  </div>
                  
                  {isLoadingTab ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                      <p className="text-gray-500">Loading trainers...</p>
                    </div>
                  ) : trainers.length === 0 ? (
                    <div className="text-center py-8 border rounded-md">
                      <Users className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                      <h4 className="font-medium text-gray-500">No trainers assigned</h4>
                      <p className="text-gray-400 text-sm mt-1">This beneficiary doesn't have any trainers assigned yet.</p>
                      {canManage && (
                        <Button variant="outline" className="mt-4">
                          Assign Trainer
                        </Button>
                      )}
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {trainers.map((trainer) => (
                        <Card key={trainer.id} className="p-4">
                          <div className="flex items-start">
                            <Avatar 
                              src={trainer.profile_picture}
                              alt={`${trainer.first_name} ${trainer.last_name}`}
                              initials={`${trainer.first_name?.[0] || ''}${trainer.last_name?.[0] || ''}`}
                              size="md"
                              className="mr-4"
                            />
                            <div className="flex-1">
                              <h4 className="font-medium">{trainer.first_name} {trainer.last_name}</h4>
                              <p className="text-sm text-gray-500">{trainer.email}</p>
                              <div className="mt-2 flex items-center text-xs text-gray-500">
                                <Calendar className="h-3.5 w-3.5 mr-1" />
                                Assigned since {formatDate(trainer.assigned_date)}
                              </div>
                              <div className="mt-1 flex items-center text-xs text-gray-500">
                                <FileText className="h-3.5 w-3.5 mr-1" />
                                {trainer.session_count} sessions conducted
                              </div>
                            </div>
                            
                            {canManage && (
                              <Button variant="ghost" size="sm">
                                Manage
                              </Button>
                            )}
                          </div>
                        </Card>
                      ))}
                    </div>
                  )}
                </CardContent>
              </TabContent>
              
              {/* Progress tab */}
              <TabContent value="progress">
                <CardContent className="pt-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-medium">Progress Overview</h3>
                    {canManage && (
                      <Button
                        onClick={() => navigate(`/beneficiaries/${id}/progress`)}
                      >
                        View Detailed Progress
                      </Button>
                    )}
                  </div>
                  
                  {isLoadingTab ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                      <p className="text-gray-500">Loading progress data...</p>
                    </div>
                  ) : !progress || Object.keys(progress).length === 0 ? (
                    <div className="text-center py-8 border rounded-md">
                      <BarChart2 className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                      <h4 className="font-medium text-gray-500">No progress data yet</h4>
                      <p className="text-gray-400 text-sm mt-1">
                        This beneficiary hasn't completed enough evaluations to show progress data.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-6">
                      {/* Overall progress */}
                      <div className="bg-gray-50 rounded-md p-4">
                        <div className="flex justify-between items-center mb-2">
                          <h4 className="font-medium">Overall Progress</h4>
                          <span className="text-gray-500 text-sm">
                            {progress.overall_percentage}% Complete
                          </span>
                        </div>
                        
                        <div className="w-full bg-gray-200 rounded-full h-2.5">
                          <div 
                            className="bg-primary h-2.5 rounded-full" 
                            style={{ width: `${progress.overall_percentage}%` }}
                          ></div>
                        </div>
                        
                        <div className="grid grid-cols-3 gap-4 mt-4 text-center">
                          <div>
                            <div className="text-2xl font-bold text-primary">
                              {progress.completed_evaluations}
                            </div>
                            <div className="text-xs text-gray-500">Evaluations Completed</div>
                          </div>
                          
                          <div>
                            <div className="text-2xl font-bold text-primary">
                              {progress.average_score}%
                            </div>
                            <div className="text-xs text-gray-500">Average Score</div>
                          </div>
                          
                          <div>
                            <div className="text-2xl font-bold text-primary">
                              {progress.improvement_rate > 0 ? '+' : ''}{progress.improvement_rate}%
                            </div>
                            <div className="text-xs text-gray-500">Improvement Rate</div>
                          </div>
                        </div>
                      </div>
                      
                      {/* Skills progress */}
                      <div>
                        <h4 className="font-medium mb-3">Skills Progress</h4>
                        
                        {progress.skills && progress.skills.length > 0 ? (
                          <div className="space-y-4">
                            {progress.skills.map((skill) => (
                              <div key={skill.id} className="bg-white border rounded-md p-4">
                                <div className="flex justify-between items-center mb-2">
                                  <div className="flex items-center">
                                    <Award className="h-5 w-5 text-primary mr-2" />
                                    <h5 className="font-medium">{skill.name}</h5>
                                  </div>
                                  <span className="text-sm font-medium">
                                    {skill.proficiency_level}
                                  </span>
                                </div>
                                
                                <div className="w-full bg-gray-200 rounded-full h-2.5 mb-2">
                                  <div 
                                    className="bg-primary h-2.5 rounded-full" 
                                    style={{ width: `${skill.progress_percentage}%` }}
                                  ></div>
                                </div>
                                
                                <div className="flex justify-between text-xs text-gray-500">
                                  <span>{skill.progress_percentage}% Mastered</span>
                                  <span>{skill.last_evaluated_at ? `Last evaluated: ${formatDate(skill.last_evaluated_at)}` : 'Not evaluated yet'}</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-gray-500 italic">No skills data available.</p>
                        )}
                      </div>
                      
                      {/* Growth areas */}
                      {progress.growth_areas && progress.growth_areas.length > 0 && (
                        <div>
                          <h4 className="font-medium mb-3">Areas for Improvement</h4>
                          
                          <div className="bg-white border rounded-md p-4 space-y-3">
                            {progress.growth_areas.map((area, index) => (
                              <div key={index} className="flex items-start">
                                <AlertTriangle className="h-5 w-5 text-yellow-500 mr-2 flex-shrink-0 mt-0.5" />
                                <div>
                                  <p className="font-medium">{area.title}</p>
                                  <p className="text-sm text-gray-600 mt-1">{area.description}</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </TabContent>
              
              {/* Documents tab */}
              <TabContent value="documents">
                <CardContent className="pt-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-medium">Documents</h3>
                    {canManage && (
                      <Button>
                        Upload Document
                      </Button>
                    )}
                  </div>
                  
                  {isLoadingTab ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                      <p className="text-gray-500">Loading documents...</p>
                    </div>
                  ) : documents.length === 0 ? (
                    <div className="text-center py-8 border rounded-md">
                      <FileText className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                      <h4 className="font-medium text-gray-500">No documents</h4>
                      <p className="text-gray-400 text-sm mt-1">No documents have been uploaded for this beneficiary.</p>
                      {canManage && (
                        <Button variant="outline" className="mt-4">
                          Upload First Document
                        </Button>
                      )}
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {documents.map((document) => (
                        <Card key={document.id} className="overflow-hidden">
                          <div className="flex flex-col md:flex-row">
                            <div className="p-4 md:p-6 flex-1">
                              <div className="flex justify-between items-start">
                                <div>
                                  <h4 className="font-medium">{document.name}</h4>
                                  <p className="text-sm text-gray-500 mt-1">{document.description}</p>
                                </div>
                                <div>
                                  <Badge color={
                                    document.type === 'evaluation_report' ? 'green' :
                                    document.type === 'certificate' ? 'blue' :
                                    document.type === 'application' ? 'purple' : 'gray'
                                  }>
                                    {document.type.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                                  </Badge>
                                </div>
                              </div>
                              
                              <div className="grid grid-cols-2 gap-4 mt-4">
                                <div className="text-sm">
                                  <p className="text-gray-500">Uploaded</p>
                                  <p className="font-medium">{formatDate(document.created_at)}</p>
                                </div>
                                <div className="text-sm">
                                  <p className="text-gray-500">Size</p>
                                  <p className="font-medium">{document.size_formatted}</p>
                                </div>
                                <div className="text-sm">
                                  <p className="text-gray-500">File Type</p>
                                  <p className="font-medium">{document.file_type.toUpperCase()}</p>
                                </div>
                                <div className="text-sm">
                                  <p className="text-gray-500">Uploaded By</p>
                                  <p className="font-medium">{document.uploaded_by_name}</p>
                                </div>
                              </div>
                            </div>
                            
                            <div className="bg-gray-50 p-4 md:w-48 flex flex-row md:flex-col justify-center md:justify-start items-center md:items-start gap-2">
                              <a 
                                href={document.view_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center text-primary hover:underline text-sm"
                              >
                                View Document
                              </a>
                              
                              <a 
                                href={document.download_url}
                                className="flex items-center text-primary hover:underline text-sm"
                                download
                              >
                                Download
                              </a>
                              
                              {canManage && (
                                <button 
                                  className="flex items-center text-red-600 hover:underline text-sm"
                                >
                                  Delete
                                </button>
                              )}
                            </div>
                          </div>
                        </Card>
                      ))}
                    </div>
                  )}
                </CardContent>
              </TabContent>
            </Tabs>
          </Card>
        </div>
      </div>
      
      {/* Delete confirmation modal */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
      >
        <ModalHeader>
          <h3 className="text-lg font-medium text-red-600">Delete Beneficiary</h3>
        </ModalHeader>
        
        <ModalBody>
          <Alert type="error" title="Warning: This action cannot be undone">
            <p>
              Are you sure you want to delete the beneficiary <strong>{beneficiary.first_name} {beneficiary.last_name}</strong>?
              This will permanently remove their profile, evaluations, and all associated data.
            </p>
          </Alert>
          
          <div className="mt-4">
            <p className="text-sm text-gray-600 font-medium">This will delete:</p>
            <ul className="mt-2 text-sm text-gray-600 list-disc list-inside space-y-1">
              <li>Personal information and profile data</li>
              <li>All evaluation reports and results</li>
              <li>Session history and records</li>
              <li>Uploaded documents and files</li>
              <li>Notes and progress tracking data</li>
            </ul>
          </div>
        </ModalBody>
        
        <ModalFooter>
          <Button
            variant="outline"
            onClick={() => setIsDeleteModalOpen(false)}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleDeleteConfirm}
            isLoading={isLoading}
            disabled={isLoading}
          >
            Delete Beneficiary
          </Button>
        </ModalFooter>
      </Modal>
    </div>
  );
};

export default BeneficiaryDetailPage;
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Edit, Mail, Phone, Calendar, Clock, Building, MapPin, User, Shield, Activity, FileText, AlignLeft } from 'lucide-react';

import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ui/toast';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Tabs, TabsList, TabTrigger, TabContent } from '@/components/ui/tabs';
import { Avatar } from '@/components/ui/avatar';
import { Table, TableHeader, TableBody, TableRow, TableCell } from '@/components/ui/table';
import { formatDate, formatDateTime } from '@/lib/utils';
import api from '@/lib/api';

/**
 * User detail page
 */
const UserDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { hasRole } = useAuth();
  const { addToast } = useToast();
  
  // State
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [activities, setActivities] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [isLoadingActivities, setIsLoadingActivities] = useState(false);
  
  // Check if user can edit this user
  const canManageUsers = hasRole(['super_admin', 'tenant_admin']);
  
  // Fetch user data
  useEffect(() => {
    const fetchUser = async () => {
      try {
        setIsLoading(true);
        
        const response = await api.get(`/api/users/${id}`);
        setUser(response.data);
        
      } catch (error) {
        console.error('Error fetching user:', error);
        addToast({
          type: 'error',
          title: 'Failed to load user',
          message: error.response?.data?.message || 'An error occurred while loading user data.',
        });
        
        // Navigate back to users list on error
        navigate('/users');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchUser();
  }, [id, navigate, addToast]);
  
  // Fetch user activities when tab changes
  useEffect(() => {
    if (activeTab === 'activity' && user) {
      const fetchActivities = async () => {
        try {
          setIsLoadingActivities(true);
          
          const response = await api.get(`/api/users/${id}/activities`);
          setActivities(response.data);
          
        } catch (error) {
          console.error('Error fetching user activities:', error);
          addToast({
            type: 'error',
            title: 'Failed to load activities',
            message: 'An error occurred while loading user activities.',
          });
        } finally {
          setIsLoadingActivities(false);
        }
      };
      
      fetchActivities();
    }
  }, [activeTab, id, user, addToast]);
  
  // Fetch user sessions when tab changes
  useEffect(() => {
    if (activeTab === 'sessions' && user) {
      const fetchSessions = async () => {
        try {
          setIsLoadingActivities(true);
          
          const response = await api.get(`/api/users/${id}/sessions`);
          setSessions(response.data);
          
        } catch (error) {
          console.error('Error fetching user sessions:', error);
          addToast({
            type: 'error',
            title: 'Failed to load sessions',
            message: 'An error occurred while loading user sessions.',
          });
        } finally {
          setIsLoadingActivities(false);
        }
      };
      
      fetchSessions();
    }
  }, [activeTab, id, user, addToast]);
  
  // Fetch user documents when tab changes
  useEffect(() => {
    if (activeTab === 'documents' && user) {
      const fetchDocuments = async () => {
        try {
          setIsLoadingActivities(true);
          
          const response = await api.get(`/api/users/${id}/documents`);
          setDocuments(response.data);
          
        } catch (error) {
          console.error('Error fetching user documents:', error);
          addToast({
            type: 'error',
            title: 'Failed to load documents',
            message: 'An error occurred while loading user documents.',
          });
        } finally {
          setIsLoadingActivities(false);
        }
      };
      
      fetchDocuments();
    }
  }, [activeTab, id, user, addToast]);
  
  // Render role badge
  const renderRoleBadge = (role) => {
    let color;
    let label;
    
    switch (role) {
      case 'super_admin':
        color = 'red';
        label = 'Super Admin';
        break;
      case 'tenant_admin':
        color = 'purple';
        label = 'Admin';
        break;
      case 'trainer':
        color = 'blue';
        label = 'Trainer';
        break;
      case 'trainee':
        color = 'green';
        label = 'Trainee';
        break;
      default:
        color = 'gray';
        label = role;
    }
    
    return <Badge color={color}>{label}</Badge>;
  };
  
  // Render status badge
  const renderStatusBadge = (status) => {
    let color;
    
    switch (status) {
      case 'active':
        color = 'green';
        break;
      case 'inactive':
        color = 'gray';
        break;
      case 'suspended':
        color = 'yellow';
        break;
      default:
        color = 'gray';
    }
    
    return <Badge color={color}>{status}</Badge>;
  };
  
  // Handle edit user
  const handleEditUser = () => {
    navigate(`/users/${id}/edit`);
  };
  
  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  // If user not found
  if (!user) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold">User Not Found</h1>
          <p className="text-gray-600 mt-2">The requested user could not be found.</p>
          <Button
            onClick={() => navigate('/users')}
            className="mt-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Users
          </Button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto py-8 px-4">
      <div className="mb-6">
        <Button
          variant="outline"
          onClick={() => navigate('/users')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Users
        </Button>
        
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
          <div>
            <h1 className="text-2xl font-bold">{user.first_name} {user.last_name}</h1>
            <p className="text-gray-600">{user.email}</p>
          </div>
          
          {canManageUsers && (
            <Button
              onClick={handleEditUser}
              className="mt-4 md:mt-0"
            >
              <Edit className="h-4 w-4 mr-2" />
              Edit User
            </Button>
          )}
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col items-center text-center">
                <Avatar 
                  src={user.profile_picture}
                  alt={`${user.first_name} ${user.last_name}`}
                  initials={`${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`}
                  size="xl"
                  className="mb-4"
                />
                
                <h2 className="text-xl font-semibold">
                  {user.first_name} {user.last_name}
                </h2>
                
                <p className="text-muted-foreground">{user.email}</p>
                
                <div className="mt-2">
                  {renderRoleBadge(user.role)}
                  {renderStatusBadge(user.status)}
                </div>
                
                {user.organization && (
                  <p className="text-sm text-muted-foreground mt-2 flex items-center justify-center">
                    <Building className="h-4 w-4 mr-1" />
                    {user.organization}
                  </p>
                )}
              </div>
              
              <div className="mt-6 border-t pt-6 space-y-4">
                <div className="flex items-center">
                  <Mail className="h-4 w-4 text-gray-500 mr-3" />
                  <div>
                    <p className="text-sm font-medium">Email</p>
                    <p className="text-sm text-muted-foreground">{user.email}</p>
                  </div>
                </div>
                
                {user.phone && (
                  <div className="flex items-center">
                    <Phone className="h-4 w-4 text-gray-500 mr-3" />
                    <div>
                      <p className="text-sm font-medium">Phone</p>
                      <p className="text-sm text-muted-foreground">{user.phone}</p>
                    </div>
                  </div>
                )}
                
                {user.address && (
                  <div className="flex items-center">
                    <MapPin className="h-4 w-4 text-gray-500 mr-3" />
                    <div>
                      <p className="text-sm font-medium">Address</p>
                      <p className="text-sm text-muted-foreground">
                        {user.address}
                        {user.city && `, ${user.city}`}
                        {user.state && `, ${user.state}`}
                        {user.zip_code && ` ${user.zip_code}`}
                        {user.country && `, ${user.country}`}
                      </p>
                    </div>
                  </div>
                )}
                
                <div className="flex items-center">
                  <Calendar className="h-4 w-4 text-gray-500 mr-3" />
                  <div>
                    <p className="text-sm font-medium">Created</p>
                    <p className="text-sm text-muted-foreground">{formatDate(user.created_at)}</p>
                  </div>
                </div>
                
                <div className="flex items-center">
                  <Clock className="h-4 w-4 text-gray-500 mr-3" />
                  <div>
                    <p className="text-sm font-medium">Last Login</p>
                    <p className="text-sm text-muted-foreground">
                      {user.last_login ? formatDateTime(user.last_login) : 'Never'}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Main content */}
        <div className="lg:col-span-2">
          <Card>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <CardHeader className="pb-0">
                <TabsList>
                  <TabTrigger value="overview">
                    <User className="h-4 w-4 mr-2" />
                    Overview
                  </TabTrigger>
                  <TabTrigger value="activity">
                    <Activity className="h-4 w-4 mr-2" />
                    Activity
                  </TabTrigger>
                  <TabTrigger value="sessions">
                    <Calendar className="h-4 w-4 mr-2" />
                    Sessions
                  </TabTrigger>
                  <TabTrigger value="documents">
                    <FileText className="h-4 w-4 mr-2" />
                    Documents
                  </TabTrigger>
                </TabsList>
              </CardHeader>
              
              <TabContent value="overview">
                <CardContent className="pt-6">
                  {user.bio ? (
                    <div className="mb-6">
                      <h3 className="text-lg font-medium mb-2">About</h3>
                      <p className="text-gray-600">{user.bio}</p>
                    </div>
                  ) : (
                    <div className="mb-6">
                      <h3 className="text-lg font-medium mb-2">About</h3>
                      <p className="text-gray-500 italic">No bio provided</p>
                    </div>
                  )}
                  
                  <div>
                    <h3 className="text-lg font-medium mb-2">Permissions & Access</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="border rounded-md p-4">
                        <div className="flex items-center mb-2">
                          <Shield className="h-5 w-5 text-primary mr-2" />
                          <h4 className="font-medium">Role</h4>
                        </div>
                        <p className="text-gray-600">{renderRoleBadge(user.role)}</p>
                        <p className="text-sm text-gray-500 mt-1">
                          {user.role === 'super_admin' && 'Full system access and management'}
                          {user.role === 'tenant_admin' && 'Organization management and user administration'}
                          {user.role === 'trainer' && 'Can manage trainees and conduct sessions'}
                          {user.role === 'trainee' && 'Basic user with limited access'}
                        </p>
                      </div>
                      
                      <div className="border rounded-md p-4">
                        <div className="flex items-center mb-2">
                          <User className="h-5 w-5 text-primary mr-2" />
                          <h4 className="font-medium">Account Status</h4>
                        </div>
                        <p className="text-gray-600">{renderStatusBadge(user.status)}</p>
                        <p className="text-sm text-gray-500 mt-1">
                          {user.status === 'active' && 'User can access the system'}
                          {user.status === 'inactive' && 'User cannot log in'}
                          {user.status === 'suspended' && 'Account temporarily disabled'}
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </TabContent>
              
              <TabContent value="activity">
                <CardContent className="pt-6">
                  <h3 className="text-lg font-medium mb-4">User Activity</h3>
                  
                  {isLoadingActivities ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                      <p className="text-gray-500">Loading activity data...</p>
                    </div>
                  ) : activities.length === 0 ? (
                    <div className="text-center py-8 border rounded-md">
                      <AlignLeft className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                      <h4 className="text-lg font-medium text-gray-500">No activity recorded</h4>
                      <p className="text-gray-400">This user hasn't performed any actions yet</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {activities.map((activity) => (
                        <div key={activity.id} className="border-b pb-4 last:border-b-0 last:pb-0">
                          <div className="flex items-start">
                            <div className="flex-shrink-0 mt-1">
                              <div className="h-8 w-8 rounded-full bg-primary bg-opacity-10 flex items-center justify-center">
                                <activity.icon className="h-4 w-4 text-primary" />
                              </div>
                            </div>
                            <div className="ml-3">
                              <p className="text-sm font-medium">{activity.description}</p>
                              <p className="text-xs text-gray-500">{formatDateTime(activity.timestamp)}</p>
                              {activity.details && (
                                <p className="text-sm text-gray-600 mt-1">{activity.details}</p>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </TabContent>
              
              <TabContent value="sessions">
                <CardContent className="pt-6">
                  <h3 className="text-lg font-medium mb-4">Training Sessions</h3>
                  
                  {isLoadingActivities ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                      <p className="text-gray-500">Loading session data...</p>
                    </div>
                  ) : sessions.length === 0 ? (
                    <div className="text-center py-8 border rounded-md">
                      <Calendar className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                      <h4 className="text-lg font-medium text-gray-500">No sessions found</h4>
                      <p className="text-gray-400">This user hasn't participated in any sessions yet</p>
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableCell>Session Name</TableCell>
                            <TableCell>Date</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Duration</TableCell>
                            <TableCell>Actions</TableCell>
                          </TableRow>
                        </TableHeader>
                        
                        <TableBody>
                          {sessions.map((session) => (
                            <TableRow key={session.id}>
                              <TableCell className="font-medium">{session.title}</TableCell>
                              <TableCell>{formatDate(session.scheduled_at)}</TableCell>
                              <TableCell>
                                <Badge color={
                                  session.status === 'completed' ? 'green' :
                                  session.status === 'scheduled' ? 'blue' :
                                  session.status === 'cancelled' ? 'red' : 'gray'
                                }>
                                  {session.status}
                                </Badge>
                              </TableCell>
                              <TableCell>{session.duration} minutes</TableCell>
                              <TableCell>
                                <Link 
                                  to={`/sessions/${session.id}`}
                                  className="text-primary hover:underline text-sm"
                                >
                                  View Details
                                </Link>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  )}
                </CardContent>
              </TabContent>
              
              <TabContent value="documents">
                <CardContent className="pt-6">
                  <h3 className="text-lg font-medium mb-4">Documents</h3>
                  
                  {isLoadingActivities ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                      <p className="text-gray-500">Loading documents...</p>
                    </div>
                  ) : documents.length === 0 ? (
                    <div className="text-center py-8 border rounded-md">
                      <FileText className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                      <h4 className="text-lg font-medium text-gray-500">No documents found</h4>
                      <p className="text-gray-400">This user doesn't have any documents yet</p>
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableCell>Name</TableCell>
                            <TableCell>Type</TableCell>
                            <TableCell>Uploaded</TableCell>
                            <TableCell>Size</TableCell>
                            <TableCell>Actions</TableCell>
                          </TableRow>
                        </TableHeader>
                        
                        <TableBody>
                          {documents.map((document) => (
                            <TableRow key={document.id}>
                              <TableCell className="font-medium">{document.name}</TableCell>
                              <TableCell>{document.type}</TableCell>
                              <TableCell>{formatDate(document.created_at)}</TableCell>
                              <TableCell>{document.size_formatted}</TableCell>
                              <TableCell>
                                <Link 
                                  to={`/documents/${document.id}`}
                                  className="text-primary hover:underline text-sm mr-3"
                                >
                                  View
                                </Link>
                                <a 
                                  href={document.download_url}
                                  className="text-primary hover:underline text-sm"
                                  target="_blank"
                                  rel="noopener noreferrer"
                                >
                                  Download
                                </a>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  )}
                </CardContent>
              </TabContent>
            </Tabs>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default UserDetailPage;
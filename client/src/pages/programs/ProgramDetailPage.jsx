import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { Button } from '../../components/ui/button';
import { Card } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import {
  Loader2,
  ArrowLeft,
  Edit,
  Users,
  Calendar,
  Clock,
  Award,
  BookOpen,
  Target,
  ChevronRight
} from 'lucide-react';

const ProgramDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [program, setProgram] = useState(null);
  const [enrolledStudents, setEnrolledStudents] = useState([]);
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    fetchProgramDetails();
    fetchEnrolledStudents();
    fetchProgramSessions();
  }, [id]);

  const fetchProgramDetails = async () => {
    try {
      const res = await fetch(`/api/programs/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!res.ok) throw new Error('Failed to fetch program');

      const data = await res.json();
      setProgram(data);
    } catch (error) {
      console.error('Error fetching program:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch program details',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchEnrolledStudents = async () => {
    try {
      const res = await fetch(`/api/programs/${id}/students`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!res.ok) throw new Error('Failed to fetch students');

      const data = await res.json();
      setEnrolledStudents(data);
    } catch (error) {
      console.error('Error fetching students:', error);
    }
  };

  const fetchProgramSessions = async () => {
    try {
      const res = await fetch(`/api/programs/${id}/sessions`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!res.ok) throw new Error('Failed to fetch sessions');

      const data = await res.json();
      setSessions(data);
    } catch (error) {
      console.error('Error fetching sessions:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'published':
        return 'bg-blue-100 text-blue-800';
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      case 'archived':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!program) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Program not found</p>
        <Button
          variant="outline"
          className="mt-4"
          onClick={() => navigate('/programs')}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Programs
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/programs')}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <h1 className="text-2xl font-bold text-gray-900">{program.name}</h1>
          <Badge className={getStatusColor(program.status)}>
            {program.status}
          </Badge>
        </div>
        
        {(user.role === 'super_admin' || user.role === 'tenant_admin') && (
          <Button onClick={() => navigate(`/programs/${id}/edit`)}>
            <Edit className="h-4 w-4 mr-2" />
            Edit Program
          </Button>
        )}
      </div>

      {/* Overview Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6 md:col-span-2">
          <h2 className="text-lg font-semibold mb-4">Program Overview</h2>
          <p className="text-gray-600 mb-6">{program.description}</p>
          
          <div className="space-y-4">
            <div>
              <h3 className="font-medium text-gray-900 mb-2 flex items-center">
                <Target className="h-4 w-4 mr-2" />
                Learning Objectives
              </h3>
              <p className="text-gray-600">{program.objectives || 'No objectives specified'}</p>
            </div>
            
            <div>
              <h3 className="font-medium text-gray-900 mb-2 flex items-center">
                <BookOpen className="h-4 w-4 mr-2" />
                Prerequisites
              </h3>
              <p className="text-gray-600">{program.requirements || 'No prerequisites'}</p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Program Details</h2>
          <div className="space-y-3">
            <div className="flex items-center text-gray-600">
              <Award className="h-4 w-4 mr-2" />
              <span className="font-medium">Category:</span>
              <span className="ml-2">{program.category}</span>
            </div>
            <div className="flex items-center text-gray-600">
              <Target className="h-4 w-4 mr-2" />
              <span className="font-medium">Level:</span>
              <span className="ml-2">{program.level}</span>
            </div>
            <div className="flex items-center text-gray-600">
              <Clock className="h-4 w-4 mr-2" />
              <span className="font-medium">Duration:</span>
              <span className="ml-2">{program.duration_weeks} weeks</span>
            </div>
            <div className="flex items-center text-gray-600">
              <Users className="h-4 w-4 mr-2" />
              <span className="font-medium">Max Participants:</span>
              <span className="ml-2">{program.max_participants}</span>
            </div>
            {program.price > 0 && (
              <div className="flex items-center text-gray-600">
                <span className="font-medium">Price:</span>
                <span className="ml-2">{program.price} {program.currency}</span>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Modules Section */}
      {program.modules && program.modules.length > 0 && (
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Program Modules</h2>
          <div className="space-y-3">
            {program.modules.map((module, index) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                <div>
                  <h3 className="font-medium text-gray-900">
                    Module {index + 1}: {module.name}
                  </h3>
                  {module.description && (
                    <p className="text-sm text-gray-600 mt-1">{module.description}</p>
                  )}
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm text-gray-500">
                    {module.duration_hours} hours
                  </span>
                  <ChevronRight className="h-4 w-4 text-gray-400" />
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Enrolled Students */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Enrolled Students ({enrolledStudents.length})</h2>
          {(user.role === 'super_admin' || user.role === 'tenant_admin' || user.role === 'trainer') && (
            <Button onClick={() => navigate(`/programs/${id}/beneficiaries`)}>
              Manage Students
            </Button>
          )}
        </div>
        
        {enrolledStudents.length === 0 ? (
          <p className="text-gray-500">No students enrolled yet</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {enrolledStudents.slice(0, 6).map((student) => (
              <div key={student.id} className="flex items-center gap-3 p-3 border rounded-lg">
                <div className="w-10 h-10 bg-blue-500 text-white rounded-full flex items-center justify-center font-medium">
                  {student.full_name?.charAt(0).toUpperCase()}
                </div>
                <div>
                  <p className="font-medium text-gray-900">{student.full_name}</p>
                  <p className="text-sm text-gray-500">{student.email}</p>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {enrolledStudents.length > 6 && (
          <p className="text-sm text-gray-500 mt-4">
            And {enrolledStudents.length - 6} more students...
          </p>
        )}
      </Card>

      {/* Upcoming Sessions */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Upcoming Sessions</h2>
          {(user.role === 'super_admin' || user.role === 'tenant_admin' || user.role === 'trainer') && (
            <Button onClick={() => navigate(`/programs/${id}/schedule`)}>
              Manage Schedule
            </Button>
          )}
        </div>
        
        {sessions.length === 0 ? (
          <p className="text-gray-500">No sessions scheduled</p>
        ) : (
          <div className="space-y-3">
            {sessions.slice(0, 5).map((session) => (
              <div key={session.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h3 className="font-medium text-gray-900">{session.title}</h3>
                  <p className="text-sm text-gray-600">
                    <Calendar className="h-3 w-3 inline mr-1" />
                    {new Date(session.date).toLocaleDateString()} at {session.time}
                  </p>
                </div>
                <Badge variant="outline">{session.type}</Badge>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};

export default ProgramDetailPage;
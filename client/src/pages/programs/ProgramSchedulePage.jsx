import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useToast } from '../../components/ui/use-toast';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Select } from '../../components/ui/select';
import { Textarea } from '../../components/ui/textarea';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Calendar } from '../../components/ui/calendar';
import {
  Loader2,
  ArrowLeft,
  Plus,
  Trash2,
  Calendar as CalendarIcon,
  Clock,
  MapPin,
  Video,
  Edit
} from 'lucide-react';
const ProgramSchedulePage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [program, setProgram] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [editingSession, setEditingSession] = useState(null);
  const [showAddSession, setShowAddSession] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    type: 'lecture',
    date: '',
    start_time: '',
    end_time: '',
    location: '',
    instructor_id: '',
    meeting_link: '',
    capacity: 30
  });
  useEffect(() => {
    fetchProgramDetails();
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
      toast({
        title: 'Error',
        description: 'Failed to fetch program sessions',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const url = editingSession
        ? `/api/programs/${id}/sessions/${editingSession.id}`
        : `/api/programs/${id}/sessions`;
      const method = editingSession ? 'PUT' : 'POST';
      const res = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(formData)
      });
      if (!res.ok) throw new Error('Failed to save session');
      toast({
        title: 'Success',
        description: editingSession ? 'Session updated successfully' : 'Session created successfully'
      });
      fetchProgramSessions();
      resetForm();
    } catch (error) {
      console.error('Error saving session:', error);
      toast({
        title: 'Error',
        description: 'Failed to save session',
        variant: 'destructive'
      });
    } finally {
      setSaving(false);
    }
  };
  const handleEditSession = (session) => {
    setEditingSession(session);
    setFormData({
      title: session.title,
      description: session.description || '',
      type: session.type,
      date: session.date,
      start_time: session.start_time,
      end_time: session.end_time,
      location: session.location || '',
      instructor_id: session.instructor_id || '',
      meeting_link: session.meeting_link || '',
      capacity: session.capacity || 30
    });
    setShowAddSession(true);
  };
  const handleDeleteSession = async (sessionId) => {
    if (!confirm('Are you sure you want to delete this session?')) return;
    try {
      const res = await fetch(`/api/programs/${id}/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to delete session');
      toast({
        title: 'Success',
        description: 'Session deleted successfully'
      });
      fetchProgramSessions();
    } catch (error) {
      console.error('Error deleting session:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete session',
        variant: 'destructive'
      });
    }
  };
  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      type: 'lecture',
      date: '',
      start_time: '',
      end_time: '',
      location: '',
      instructor_id: '',
      meeting_link: '',
      capacity: 30
    });
    setEditingSession(null);
    setShowAddSession(false);
  };
  const getTypeColor = (type) => {
    switch (type) {
      case 'lecture':
        return 'bg-blue-100 text-blue-800';
      case 'workshop':
        return 'bg-purple-100 text-purple-800';
      case 'lab':
        return 'bg-green-100 text-green-800';
      case 'exam':
        return 'bg-red-100 text-red-800';
      case 'online':
        return 'bg-yellow-100 text-yellow-800';
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
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate(`/programs/${id}`)}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <h1 className="text-2xl font-bold text-gray-900">
            Schedule for {program?.name}
          </h1>
        </div>
        <Button onClick={() => setShowAddSession(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Session
        </Button>
      </div>
      {/* Add/Edit Session Form */}
      {showAddSession && (
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">
            {editingSession ? 'Edit Session' : 'Add New Session'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Session Title *
                </label>
                <Input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  required
                  placeholder="Enter session title"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Type *
                </label>
                <Select
                  name="type"
                  value={formData.type}
                  onChange={handleChange}
                  required
                >
                  <option value="lecture">Lecture</option>
                  <option value="workshop">Workshop</option>
                  <option value="lab">Lab</option>
                  <option value="exam">Exam</option>
                  <option value="online">Online</option>
                </Select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date *
                </label>
                <Input
                  type="date"
                  name="date"
                  value={formData.date}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Start Time *
                  </label>
                  <Input
                    type="time"
                    name="start_time"
                    value={formData.start_time}
                    onChange={handleChange}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    End Time *
                  </label>
                  <Input
                    type="time"
                    name="end_time"
                    value={formData.end_time}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Location
                </label>
                <Input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleChange}
                  placeholder="Enter location"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Meeting Link
                </label>
                <Input
                  type="url"
                  name="meeting_link"
                  value={formData.meeting_link}
                  onChange={handleChange}
                  placeholder="Enter online meeting link"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Capacity
                </label>
                <Input
                  type="number"
                  name="capacity"
                  value={formData.capacity}
                  onChange={handleChange}
                  min="1"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <Textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={3}
                placeholder="Enter session description"
              />
            </div>
            <div className="flex gap-3">
              <Button type="submit" disabled={saving}>
                {saving ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  editingSession ? 'Update Session' : 'Add Session'
                )}
              </Button>
              <Button type="button" variant="outline" onClick={resetForm}>
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      )}
      {/* Sessions List */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">
          Sessions ({sessions.length})
        </h2>
        {sessions.length === 0 ? (
          <div className="text-center py-12">
            <CalendarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No sessions scheduled yet</p>
            <p className="text-sm text-gray-400 mt-2">Click "Add Session" to create your first session</p>
          </div>
        ) : (
          <div className="space-y-4">
            {sessions.map((session) => (
              <div
                key={session.id}
                className="border rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-gray-900">{session.title}</h3>
                      <Badge className={getTypeColor(session.type)}>
                        {session.type}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <div className="flex items-center">
                        <CalendarIcon className="h-4 w-4 mr-1" />
                        {new Date(session.date).toLocaleDateString()}
                      </div>
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        {session.start_time} - {session.end_time}
                      </div>
                      {session.location && (
                        <div className="flex items-center">
                          <MapPin className="h-4 w-4 mr-1" />
                          {session.location}
                        </div>
                      )}
                      {session.meeting_link && (
                        <div className="flex items-center">
                          <Video className="h-4 w-4 mr-1" />
                          <a href={session.meeting_link} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                            Join Online
                          </a>
                        </div>
                      )}
                    </div>
                    {session.description && (
                      <p className="text-sm text-gray-500 mt-2">{session.description}</p>
                    )}
                  </div>
                  <div className="flex gap-2 ml-4">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleEditSession(session)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteSession(session.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};
export default ProgramSchedulePage;
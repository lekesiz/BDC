import { useState, useEffect } from 'react';
import { 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Calendar, 
  Clock, 
  BookOpen, 
  Award,
  Briefcase,
  Loader,
  Pencil,
  Save,
  X,
  Camera
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';

/**
 * PortalProfilePage displays and allows editing of the student's profile
 */
const PortalProfilePage = () => {
  const { toast } = useToast();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [profileData, setProfileData] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editableFields, setEditableFields] = useState({
    phone: '',
    address: '',
    bio: '',
    education: '',
    interests: '',
    goals: ''
  });
  
  // Fetch profile data
  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/api/portal/profile');
        setProfileData(response.data);
        setEditableFields({
          phone: response.data.contact.phone,
          address: response.data.contact.address,
          bio: response.data.bio,
          education: response.data.education,
          interests: response.data.interests,
          goals: response.data.goals
        });
      } catch (error) {
        console.error('Error fetching profile data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load profile data',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchProfileData();
  }, [toast]);
  
  // Handle field change
  const handleFieldChange = (field, value) => {
    setEditableFields(prev => ({
      ...prev,
      [field]: value
    }));
  };
  
  // Handle save changes
  const handleSaveChanges = async () => {
    try {
      // In a real app, this would submit changes to the server
      await api.put('/api/portal/profile', editableFields);
      
      // Update local state
      setProfileData(prev => ({
        ...prev,
        contact: {
          ...prev.contact,
          phone: editableFields.phone,
          address: editableFields.address
        },
        bio: editableFields.bio,
        education: editableFields.education,
        interests: editableFields.interests,
        goals: editableFields.goals
      }));
      
      setIsEditing(false);
      
      toast({
        title: 'Success',
        description: 'Profile updated successfully',
        type: 'success',
      });
    } catch (error) {
      console.error('Error updating profile:', error);
      toast({
        title: 'Error',
        description: 'Failed to update profile',
        type: 'error',
      });
    }
  };
  
  // Format date
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
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
      {/* Page header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold mb-2">My Profile</h1>
          <p className="text-gray-600">
            View and manage your personal information
          </p>
        </div>
        {isEditing ? (
          <div className="space-x-2">
            <Button variant="outline" onClick={() => setIsEditing(false)}>
              <X className="h-4 w-4 mr-2" />
              Cancel
            </Button>
            <Button onClick={handleSaveChanges}>
              <Save className="h-4 w-4 mr-2" />
              Save Changes
            </Button>
          </div>
        ) : (
          <Button onClick={() => setIsEditing(true)}>
            <Pencil className="h-4 w-4 mr-2" />
            Edit Profile
          </Button>
        )}
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left column: Basic info and summary */}
        <div className="space-y-6">
          {/* Profile card */}
          <Card className="overflow-hidden">
            <div className="bg-gradient-to-r from-primary/80 to-primary p-6 relative">
              <div className="absolute top-4 right-4">
                {isEditing && (
                  <Button size="sm" variant="secondary">
                    <Camera className="h-4 w-4 mr-2" />
                    Change Photo
                  </Button>
                )}
              </div>
              <div className="flex flex-col items-center mt-8 mb-4">
                <div className="w-24 h-24 bg-white rounded-full mb-4 flex items-center justify-center border-4 border-white">
                  {profileData.avatar ? (
                    <img 
                      src={profileData.avatar} 
                      alt={profileData.name}
                      className="w-full h-full rounded-full object-cover"
                    />
                  ) : (
                    <User className="h-12 w-12 text-gray-400" />
                  )}
                </div>
                <h2 className="text-xl font-bold text-white">{profileData.name}</h2>
                <p className="text-white/80">{profileData.role}</p>
              </div>
            </div>
            <div className="p-6 divide-y">
              <div className="py-3 flex items-center">
                <Mail className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <p className="text-sm text-gray-500">Email</p>
                  <p className="font-medium">{profileData.contact.email}</p>
                </div>
              </div>
              <div className="py-3 flex items-center">
                <Phone className="h-5 w-5 text-gray-400 mr-3" />
                <div className="flex-1">
                  <p className="text-sm text-gray-500">Phone</p>
                  {isEditing ? (
                    <Input 
                      value={editableFields.phone}
                      onChange={(e) => handleFieldChange('phone', e.target.value)}
                      className="mt-1"
                    />
                  ) : (
                    <p className="font-medium">{profileData.contact.phone}</p>
                  )}
                </div>
              </div>
              <div className="py-3 flex items-center">
                <MapPin className="h-5 w-5 text-gray-400 mr-3" />
                <div className="flex-1">
                  <p className="text-sm text-gray-500">Address</p>
                  {isEditing ? (
                    <Input 
                      value={editableFields.address}
                      onChange={(e) => handleFieldChange('address', e.target.value)}
                      className="mt-1"
                    />
                  ) : (
                    <p className="font-medium">{profileData.contact.address}</p>
                  )}
                </div>
              </div>
              <div className="py-3 flex items-center">
                <Calendar className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <p className="text-sm text-gray-500">Date Joined</p>
                  <p className="font-medium">{formatDate(profileData.dateJoined)}</p>
                </div>
              </div>
            </div>
          </Card>
          
          {/* Program info */}
          <Card className="overflow-hidden">
            <div className="p-6 border-b">
              <h3 className="text-lg font-medium">Program Information</h3>
            </div>
            <div className="p-6 divide-y">
              <div className="py-3">
                <p className="text-sm text-gray-500">Current Program</p>
                <p className="font-medium">{profileData.program.name}</p>
              </div>
              <div className="py-3">
                <p className="text-sm text-gray-500">Start Date</p>
                <p className="font-medium">{formatDate(profileData.program.startDate)}</p>
              </div>
              <div className="py-3">
                <p className="text-sm text-gray-500">Expected Completion</p>
                <p className="font-medium">{formatDate(profileData.program.expectedEndDate)}</p>
              </div>
              <div className="py-3">
                <p className="text-sm text-gray-500">Program Status</p>
                <div className="flex items-center mt-1">
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div 
                      className="bg-primary h-2.5 rounded-full" 
                      style={{ width: `${profileData.program.progress}%` }}
                    ></div>
                  </div>
                  <span className="ml-2 text-sm font-medium">{profileData.program.progress}%</span>
                </div>
              </div>
            </div>
          </Card>
        </div>
        
        {/* Right column: Detailed information */}
        <div className="lg:col-span-2 space-y-6">
          {/* Bio */}
          <Card className="overflow-hidden">
            <div className="p-6 border-b">
              <h3 className="text-lg font-medium">Biography</h3>
            </div>
            <div className="p-6">
              {isEditing ? (
                <div>
                  <textarea
                    value={editableFields.bio}
                    onChange={(e) => handleFieldChange('bio', e.target.value)}
                    className="w-full h-32 border rounded-md p-3 focus:outline-none focus:ring-2 focus:ring-primary/50"
                  ></textarea>
                </div>
              ) : (
                <p className="text-gray-700">{profileData.bio}</p>
              )}
            </div>
          </Card>
          
          {/* Education */}
          <Card className="overflow-hidden">
            <div className="p-6 border-b">
              <h3 className="text-lg font-medium">Education Background</h3>
            </div>
            <div className="p-6">
              {isEditing ? (
                <div>
                  <textarea
                    value={editableFields.education}
                    onChange={(e) => handleFieldChange('education', e.target.value)}
                    className="w-full h-32 border rounded-md p-3 focus:outline-none focus:ring-2 focus:ring-primary/50"
                  ></textarea>
                </div>
              ) : (
                <p className="text-gray-700">{profileData.education}</p>
              )}
            </div>
          </Card>
          
          {/* Skills */}
          <Card className="overflow-hidden">
            <div className="p-6 border-b">
              <h3 className="text-lg font-medium">Skills Development</h3>
            </div>
            <div className="p-6 space-y-4">
              {profileData.skills.map(skill => (
                <div key={skill.id} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <h4 className="font-medium">{skill.name}</h4>
                    <span className="text-sm text-gray-500">
                      Level {skill.currentLevel} / {skill.maxLevel}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div 
                      className="bg-primary h-2.5 rounded-full" 
                      style={{ width: `${(skill.currentLevel / skill.maxLevel) * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
          
          {/* Interests */}
          <Card className="overflow-hidden">
            <div className="p-6 border-b">
              <h3 className="text-lg font-medium">Interests</h3>
            </div>
            <div className="p-6">
              {isEditing ? (
                <div>
                  <textarea
                    value={editableFields.interests}
                    onChange={(e) => handleFieldChange('interests', e.target.value)}
                    className="w-full h-20 border rounded-md p-3 focus:outline-none focus:ring-2 focus:ring-primary/50"
                  ></textarea>
                </div>
              ) : (
                <p className="text-gray-700">{profileData.interests}</p>
              )}
            </div>
          </Card>
          
          {/* Goals */}
          <Card className="overflow-hidden">
            <div className="p-6 border-b">
              <h3 className="text-lg font-medium">Learning Goals</h3>
            </div>
            <div className="p-6">
              {isEditing ? (
                <div>
                  <textarea
                    value={editableFields.goals}
                    onChange={(e) => handleFieldChange('goals', e.target.value)}
                    className="w-full h-32 border rounded-md p-3 focus:outline-none focus:ring-2 focus:ring-primary/50"
                  ></textarea>
                </div>
              ) : (
                <p className="text-gray-700">{profileData.goals}</p>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default PortalProfilePage;
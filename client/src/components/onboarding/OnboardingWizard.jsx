import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ChevronRight, 
  ChevronLeft, 
  CheckCircle2, 
  User, 
  Settings, 
  Users, 
  Calendar,
  FileText,
  Play,
  Book,
  Lightbulb,
  Target,
  Star
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ResponsiveContainer, ResponsiveCard } from '@/components/responsive/ResponsiveContainer';
import { useAuth } from '@/hooks/useAuth';
import api from '@/lib/api';

const OnboardingWizard = ({ onComplete }) => {
  const navigate = useNavigate();
  const { user, updateProfile } = useAuth();
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState(new Set());
  const [userData, setUserData] = useState({
    firstName: user?.first_name || '',
    lastName: user?.last_name || '',
    role: user?.role || '',
    department: '',
    phoneNumber: '',
    preferences: {
      language: 'en',
      notifications: true,
      theme: 'light',
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
    },
    interests: [],
    goals: []
  });

  const steps = [
    {
      id: 'welcome',
      title: 'Welcome to BDC Platform',
      description: 'Let\'s get you started with a quick setup',
      icon: Star,
      component: WelcomeStep
    },
    {
      id: 'profile',
      title: 'Complete Your Profile',
      description: 'Help us personalize your experience',
      icon: User,
      component: ProfileStep
    },
    {
      id: 'preferences',
      title: 'Set Your Preferences',
      description: 'Configure your system settings',
      icon: Settings,
      component: PreferencesStep
    },
    {
      id: 'features',
      title: 'Explore Key Features',
      description: 'Learn about the main features',
      icon: Lightbulb,
      component: FeaturesStep
    },
    {
      id: 'goals',
      title: 'Set Your Goals',
      description: 'Define what you want to achieve',
      icon: Target,
      component: GoalsStep
    },
    {
      id: 'complete',
      title: 'You\'re All Set!',
      description: 'Ready to start using BDC Platform',
      icon: CheckCircle2,
      component: CompletionStep
    }
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCompletedSteps(prev => new Set([...prev, currentStep]));
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleStepClick = (stepIndex) => {
    if (stepIndex <= Math.max(...completedSteps) + 1) {
      setCurrentStep(stepIndex);
    }
  };

  const handleComplete = async () => {
    try {
      // Save user preferences and profile data
      await api.put('/api/profile', userData);
      
      // Mark onboarding as completed
      await api.post('/api/user/onboarding-completed');
      
      // Update local user data
      await updateProfile();
      
      // Call completion callback
      if (onComplete) {
        onComplete();
      } else {
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Failed to complete onboarding:', error);
    }
  };

  const updateUserData = (updates) => {
    setUserData(prev => ({ ...prev, ...updates }));
  };

  const currentStepData = steps[currentStep];
  const StepComponent = currentStepData.component;

  return (
    <ResponsiveContainer>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Progress Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h1 className="text-3xl font-bold text-gray-900">Getting Started</h1>
              <Badge variant="outline">
                Step {currentStep + 1} of {steps.length}
              </Badge>
            </div>
            
            {/* Progress Bar */}
            <div className="flex items-center space-x-2">
              {steps.map((step, index) => {
                const Icon = step.icon;
                const isCompleted = completedSteps.has(index);
                const isCurrent = index === currentStep;
                const isAccessible = index <= Math.max(...completedSteps) + 1;
                
                return (
                  <React.Fragment key={step.id}>
                    <button
                      onClick={() => handleStepClick(index)}
                      disabled={!isAccessible}
                      className={`
                        flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all
                        ${isCompleted 
                          ? 'bg-green-500 border-green-500 text-white' 
                          : isCurrent 
                            ? 'bg-blue-500 border-blue-500 text-white' 
                            : isAccessible
                              ? 'bg-white border-gray-300 text-gray-400 hover:border-blue-300'
                              : 'bg-gray-100 border-gray-200 text-gray-300 cursor-not-allowed'
                        }
                      `}
                      aria-label={`${step.title} - ${isCompleted ? 'Completed' : isCurrent ? 'Current' : 'Pending'}`}
                    >
                      {isCompleted ? (
                        <CheckCircle2 className="h-5 w-5" />
                      ) : (
                        <Icon className="h-5 w-5" />
                      )}
                    </button>
                    
                    {index < steps.length - 1 && (
                      <div className={`
                        flex-1 h-0.5 transition-colors
                        ${isCompleted ? 'bg-green-500' : 'bg-gray-300'}
                      `} />
                    )}
                  </React.Fragment>
                );
              })}
            </div>
            
            {/* Step Labels */}
            <div className="hidden md:flex items-center justify-between mt-2">
              {steps.map((step, index) => (
                <div key={step.id} className="text-center max-w-24">
                  <p className={`
                    text-xs font-medium truncate
                    ${index === currentStep ? 'text-blue-600' : 'text-gray-500'}
                  `}>
                    {step.title}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Step Content */}
          <ResponsiveCard className="mb-8">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg">
                  <currentStepData.icon className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <CardTitle className="text-xl">{currentStepData.title}</CardTitle>
                  <p className="text-gray-600 mt-1">{currentStepData.description}</p>
                </div>
              </div>
            </CardHeader>
            
            <CardContent>
              <StepComponent
                userData={userData}
                updateUserData={updateUserData}
                onNext={handleNext}
                onPrevious={handlePrevious}
                onComplete={handleComplete}
                isLastStep={currentStep === steps.length - 1}
              />
            </CardContent>
          </ResponsiveCard>

          {/* Navigation */}
          <div className="flex items-center justify-between">
            <Button
              variant="outline"
              onClick={handlePrevious}
              disabled={currentStep === 0}
              className="flex items-center space-x-2"
            >
              <ChevronLeft className="h-4 w-4" />
              <span>Previous</span>
            </Button>

            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                onClick={() => navigate('/dashboard')}
                className="text-gray-600"
              >
                Skip for now
              </Button>

              {currentStep === steps.length - 1 ? (
                <Button onClick={handleComplete} className="flex items-center space-x-2">
                  <CheckCircle2 className="h-4 w-4" />
                  <span>Complete Setup</span>
                </Button>
              ) : (
                <Button onClick={handleNext} className="flex items-center space-x-2">
                  <span>Next</span>
                  <ChevronRight className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </ResponsiveContainer>
  );
};

// Welcome Step Component
const WelcomeStep = ({ userData, onNext }) => {
  return (
    <div className="text-center py-8">
      <div className="mb-6">
        <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <Star className="h-12 w-12 text-white" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Welcome to BDC Platform, {userData.firstName || 'there'}!
        </h2>
        <p className="text-gray-600 max-w-2xl mx-auto leading-relaxed">
          We're excited to have you on board. This quick setup will help us personalize your experience 
          and get you familiar with the key features of our platform. It will only take a few minutes.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="text-center p-4">
          <Users className="h-8 w-8 text-blue-500 mx-auto mb-2" />
          <h3 className="font-semibold text-gray-900">Manage Beneficiaries</h3>
          <p className="text-sm text-gray-600">Track progress and manage evaluations</p>
        </div>
        <div className="text-center p-4">
          <Calendar className="h-8 w-8 text-green-500 mx-auto mb-2" />
          <h3 className="font-semibold text-gray-900">Schedule Appointments</h3>
          <p className="text-sm text-gray-600">Coordinate sessions and meetings</p>
        </div>
        <div className="text-center p-4">
          <FileText className="h-8 w-8 text-purple-500 mx-auto mb-2" />
          <h3 className="font-semibold text-gray-900">Generate Reports</h3>
          <p className="text-sm text-gray-600">Create comprehensive assessments</p>
        </div>
      </div>

      <Button onClick={onNext} size="lg" className="px-8">
        Let's Get Started
      </Button>
    </div>
  );
};

// Profile Step Component
const ProfileStep = ({ userData, updateUserData }) => {
  const handleInputChange = (field, value) => {
    updateUserData({ [field]: value });
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-1">
            First Name *
          </label>
          <Input
            id="firstName"
            value={userData.firstName}
            onChange={(e) => handleInputChange('firstName', e.target.value)}
            placeholder="Enter your first name"
            required
          />
        </div>
        
        <div>
          <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 mb-1">
            Last Name *
          </label>
          <Input
            id="lastName"
            value={userData.lastName}
            onChange={(e) => handleInputChange('lastName', e.target.value)}
            placeholder="Enter your last name"
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="department" className="block text-sm font-medium text-gray-700 mb-1">
            Department
          </label>
          <select
            id="department"
            value={userData.department}
            onChange={(e) => handleInputChange('department', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select department</option>
            <option value="psychology">Psychology</option>
            <option value="education">Education</option>
            <option value="therapy">Therapy</option>
            <option value="administration">Administration</option>
            <option value="research">Research</option>
          </select>
        </div>
        
        <div>
          <label htmlFor="phoneNumber" className="block text-sm font-medium text-gray-700 mb-1">
            Phone Number
          </label>
          <Input
            id="phoneNumber"
            value={userData.phoneNumber}
            onChange={(e) => handleInputChange('phoneNumber', e.target.value)}
            placeholder="Enter your phone number"
            type="tel"
          />
        </div>
      </div>

      <div className="bg-blue-50 p-4 rounded-lg">
        <div className="flex items-start space-x-3">
          <User className="h-5 w-5 text-blue-600 mt-0.5" />
          <div>
            <h3 className="font-medium text-blue-900">Profile Tip</h3>
            <p className="text-sm text-blue-700 mt-1">
              Completing your profile helps us provide personalized recommendations and 
              enables better collaboration with your team members.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Preferences Step Component
const PreferencesStep = ({ userData, updateUserData }) => {
  const handlePreferenceChange = (field, value) => {
    updateUserData({
      preferences: {
        ...userData.preferences,
        [field]: value
      }
    });
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Language
          </label>
          <select
            value={userData.preferences.language}
            onChange={(e) => handlePreferenceChange('language', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="en">English</option>
            <option value="tr">Türkçe</option>
            <option value="es">Español</option>
            <option value="fr">Français</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Theme
          </label>
          <select
            value={userData.preferences.theme}
            onChange={(e) => handlePreferenceChange('theme', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="auto">Auto (System)</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Timezone
        </label>
        <select
          value={userData.preferences.timezone}
          onChange={(e) => handlePreferenceChange('timezone', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="America/New_York">Eastern Time</option>
          <option value="America/Chicago">Central Time</option>
          <option value="America/Denver">Mountain Time</option>
          <option value="America/Los_Angeles">Pacific Time</option>
          <option value="Europe/London">London</option>
          <option value="Europe/Paris">Paris</option>
          <option value="Europe/Istanbul">Istanbul</option>
          <option value="Asia/Tokyo">Tokyo</option>
        </select>
      </div>

      <div className="space-y-4">
        <h3 className="font-medium text-gray-900">Notification Preferences</h3>
        
        <label className="flex items-center space-x-3">
          <input
            type="checkbox"
            checked={userData.preferences.notifications}
            onChange={(e) => handlePreferenceChange('notifications', e.target.checked)}
            className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <span className="text-sm text-gray-700">Enable email notifications</span>
        </label>
      </div>
    </div>
  );
};

// Features Step Component
const FeaturesStep = () => {
  const features = [
    {
      icon: Users,
      title: 'Beneficiary Management',
      description: 'Comprehensive tools for managing beneficiary information, progress tracking, and evaluation scheduling.',
      color: 'blue'
    },
    {
      icon: Calendar,
      title: 'Appointment Scheduling',
      description: 'Flexible scheduling system with calendar integration and automated reminders.',
      color: 'green'
    },
    {
      icon: FileText,
      title: 'Report Generation',
      description: 'AI-powered report generation with customizable templates and export options.',
      color: 'purple'
    },
    {
      icon: Book,
      title: 'Evaluation Tools',
      description: 'Standardized assessment tools with real-time scoring and progress tracking.',
      color: 'orange'
    }
  ];

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Explore What You Can Do
        </h3>
        <p className="text-gray-600">
          Here are the key features that will help you manage your work efficiently.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {features.map((feature, index) => {
          const Icon = feature.icon;
          const colorClasses = {
            blue: 'bg-blue-100 text-blue-600',
            green: 'bg-green-100 text-green-600',
            purple: 'bg-purple-100 text-purple-600',
            orange: 'bg-orange-100 text-orange-600'
          };

          return (
            <div key={index} className="p-4 border rounded-lg hover:shadow-md transition-shadow">
              <div className="flex items-start space-x-3">
                <div className={`p-2 rounded-lg ${colorClasses[feature.color]}`}>
                  <Icon className="h-5 w-5" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 mb-1">{feature.title}</h4>
                  <p className="text-sm text-gray-600">{feature.description}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg">
        <div className="flex items-center space-x-3">
          <Play className="h-5 w-5 text-blue-600" />
          <div>
            <h3 className="font-medium text-gray-900">Ready to explore?</h3>
            <p className="text-sm text-gray-600">
              Each feature has interactive tutorials and help documentation to get you started quickly.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Goals Step Component
const GoalsStep = ({ userData, updateUserData }) => {
  const availableGoals = [
    'Improve evaluation efficiency',
    'Enhance beneficiary engagement',
    'Streamline reporting process',
    'Better progress tracking',
    'Increase collaboration',
    'Reduce administrative tasks',
    'Improve data accuracy',
    'Enhance communication'
  ];

  const toggleGoal = (goal) => {
    const currentGoals = userData.goals || [];
    const updatedGoals = currentGoals.includes(goal)
      ? currentGoals.filter(g => g !== goal)
      : [...currentGoals, goal];
    
    updateUserData({ goals: updatedGoals });
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          What are your main goals?
        </h3>
        <p className="text-gray-600">
          Select the goals that matter most to you. This helps us customize your experience.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {availableGoals.map((goal, index) => {
          const isSelected = userData.goals?.includes(goal);
          
          return (
            <button
              key={index}
              onClick={() => toggleGoal(goal)}
              className={`
                p-3 text-left border rounded-lg transition-all
                ${isSelected 
                  ? 'border-blue-500 bg-blue-50 text-blue-700' 
                  : 'border-gray-300 hover:border-blue-300 hover:bg-gray-50'
                }
              `}
            >
              <div className="flex items-center space-x-2">
                <div className={`
                  w-4 h-4 rounded border-2 flex items-center justify-center
                  ${isSelected ? 'border-blue-500 bg-blue-500' : 'border-gray-300'}
                `}>
                  {isSelected && <CheckCircle2 className="h-3 w-3 text-white" />}
                </div>
                <span className="text-sm font-medium">{goal}</span>
              </div>
            </button>
          );
        })}
      </div>

      <div className="bg-green-50 p-4 rounded-lg">
        <div className="flex items-start space-x-3">
          <Target className="h-5 w-5 text-green-600 mt-0.5" />
          <div>
            <h3 className="font-medium text-green-900">Goal Tracking</h3>
            <p className="text-sm text-green-700 mt-1">
              Based on your selected goals, we'll provide personalized recommendations and 
              track your progress over time.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Completion Step Component
const CompletionStep = ({ userData }) => {
  return (
    <div className="text-center py-8">
      <div className="mb-6">
        <div className="w-24 h-24 bg-gradient-to-br from-green-500 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle2 className="h-12 w-12 text-white" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Welcome aboard, {userData.firstName}!
        </h2>
        <p className="text-gray-600 max-w-2xl mx-auto leading-relaxed">
          Your account is now set up and ready to use. You can always update your preferences 
          and settings later from your profile page.
        </p>
      </div>

      <div className="bg-gradient-to-r from-blue-50 to-green-50 p-6 rounded-lg mb-6">
        <h3 className="font-semibold text-gray-900 mb-3">What's next?</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <Users className="h-8 w-8 text-blue-600 mx-auto mb-2" />
            <p className="text-sm font-medium">Start by adding beneficiaries</p>
          </div>
          <div className="text-center">
            <Calendar className="h-8 w-8 text-green-600 mx-auto mb-2" />
            <p className="text-sm font-medium">Schedule your first appointment</p>
          </div>
          <div className="text-center">
            <FileText className="h-8 w-8 text-purple-600 mx-auto mb-2" />
            <p className="text-sm font-medium">Explore evaluation tools</p>
          </div>
        </div>
      </div>

      <div className="text-sm text-gray-500">
        <p>Need help getting started? Check out our tutorials and documentation.</p>
      </div>
    </div>
  );
};

export default OnboardingWizard;
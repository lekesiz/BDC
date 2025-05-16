import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import api from '@/lib/api';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  BookOpen,
  Calendar,
  Award,
  TrendingUp,
  Clock,
  CheckCircle2,
  Target,
  Brain,
  FileText,
  Users,
  Loader2,
  ArrowRight,
  BarChart3,
  GraduationCap
} from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const PortalDashboardV2 = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/api/portal/dashboard');
        setDashboardData(response.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setError(error.response?.data?.message || 'Failed to load dashboard');
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="w-12 h-12 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Card className="p-6">
          <p className="text-red-600">{error}</p>
          <Button 
            onClick={() => window.location.reload()} 
            className="mt-4"
          >
            Retry
          </Button>
        </Card>
      </div>
    );
  }

  const { user: userData, beneficiary, stats, upcoming_sessions, recent_tests } = dashboardData;

  return (
    <div className="space-y-6 p-6">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-primary to-primary-dark rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">Welcome back, {userData.name}!</h1>
        <p className="text-primary-lighter">Track your progress and achieve your goals</p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Enrolled Programs"
          value={stats.enrolled_programs}
          icon={<BookOpen className="w-6 h-6" />}
          color="bg-blue-500"
        />
        <StatsCard
          title="Completed Programs"
          value={stats.completed_programs}
          icon={<GraduationCap className="w-6 h-6" />}
          color="bg-green-500"
        />
        <StatsCard
          title="Average Progress"
          value={`${stats.average_progress}%`}
          icon={<TrendingUp className="w-6 h-6" />}
          color="bg-purple-500"
        />
        <StatsCard
          title="Attendance Rate"
          value={`${stats.total_attendance_rate}%`}
          icon={<CheckCircle2 className="w-6 h-6" />}
          color="bg-orange-500"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Progress Overview */}
        <div className="lg:col-span-2 space-y-6">
          {/* Active Programs */}
          <Card className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Active Programs</h2>
              <Link to="/portal/courses">
                <Button variant="ghost" size="sm">
                  View All <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              </Link>
            </div>
            
            {/* Mock active programs - replace with real data */}
            <div className="space-y-4">
              <ProgramProgressCard
                title="Web Development Fundamentals"
                progress={75}
                nextSession="Today at 2:00 PM"
                moduleProgress="Module 8 of 12"
              />
              <ProgramProgressCard
                title="JavaScript Advanced Concepts"
                progress={45}
                nextSession="Tomorrow at 10:00 AM"
                moduleProgress="Module 5 of 10"
              />
              <ProgramProgressCard
                title="React & Modern Frontend"
                progress={30}
                nextSession="Friday at 3:00 PM"
                moduleProgress="Module 3 of 15"
              />
            </div>
          </Card>

          {/* Recent Assessments */}
          <Card className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Recent Assessments</h2>
              <Link to="/portal/assessments">
                <Button variant="ghost" size="sm">
                  View All <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              </Link>
            </div>
            
            <div className="space-y-3">
              {recent_tests.map((test) => (
                <AssessmentCard
                  key={test.id}
                  title={test.evaluation?.title || 'Assessment'}
                  date={new Date(test.created_at).toLocaleDateString()}
                  score={test.score}
                  status={test.status}
                />
              ))}
            </div>
          </Card>
        </div>

        {/* Right Column - Schedule & Skills */}
        <div className="space-y-6">
          {/* Upcoming Schedule */}
          <Card className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Upcoming Schedule</h2>
              <Link to="/portal/calendar">
                <Button variant="ghost" size="sm">
                  View Calendar <Calendar className="w-4 h-4 ml-1" />
                </Button>
              </Link>
            </div>
            
            <div className="space-y-3">
              {upcoming_sessions.map((session) => (
                <ScheduleItem
                  key={session.id}
                  title={session.module?.name || 'Training Session'}
                  date={new Date(session.session_date).toLocaleDateString()}
                  time={new Date(session.session_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  location={session.location}
                />
              ))}
            </div>
          </Card>

          {/* Skills Progress */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Skills Development</h2>
            <ResponsiveContainer width="100%" height={250}>
              <RadarChart data={mockSkillsData}>
                <PolarGrid strokeDasharray="3 3" />
                <PolarAngleAxis dataKey="skill" />
                <PolarRadiusAxis angle={30} domain={[0, 100]} />
                <Radar name="Progress" dataKey="value" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
              </RadarChart>
            </ResponsiveContainer>
            <Link to="/portal/skills" className="block mt-4">
              <Button variant="outline" className="w-full">
                View Detailed Progress
              </Button>
            </Link>
          </Card>

          {/* Quick Actions */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
            <div className="grid grid-cols-2 gap-3">
              <QuickActionButton
                icon={<FileText className="w-5 h-5" />}
                label="Resources"
                to="/portal/resources"
              />
              <QuickActionButton
                icon={<Award className="w-5 h-5" />}
                label="Achievements"
                to="/portal/achievements"
              />
              <QuickActionButton
                icon={<Brain className="w-5 h-5" />}
                label="Assessments"
                to="/portal/assessments"
              />
              <QuickActionButton
                icon={<Users className="w-5 h-5" />}
                label="Profile"
                to="/portal/profile"
              />
            </div>
          </Card>
        </div>
      </div>

      {/* Performance Analytics */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Performance Analytics</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={mockPerformanceData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="assessments" stroke="#8884d8" name="Assessment Scores" />
            <Line type="monotone" dataKey="attendance" stroke="#82ca9d" name="Attendance Rate" />
          </LineChart>
        </ResponsiveContainer>
      </Card>
    </div>
  );
};

// Component Helpers
const StatsCard = ({ title, value, icon, color }) => (
  <Card className="p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-gray-600">{title}</p>
        <p className="text-2xl font-bold mt-1">{value}</p>
      </div>
      <div className={`p-3 rounded-lg ${color} bg-opacity-10`}>
        <div className={`${color} text-white`}>{icon}</div>
      </div>
    </div>
  </Card>
);

const ProgramProgressCard = ({ title, progress, nextSession, moduleProgress }) => (
  <div className="border rounded-lg p-4">
    <h3 className="font-medium text-gray-900 mb-2">{title}</h3>
    <Progress value={progress} className="h-2 mb-2" />
    <div className="flex justify-between text-sm text-gray-600">
      <span>{moduleProgress}</span>
      <span>{progress}% Complete</span>
    </div>
    <p className="text-sm text-gray-500 mt-2">Next: {nextSession}</p>
  </div>
);

const AssessmentCard = ({ title, date, score, status }) => (
  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
    <div>
      <h4 className="font-medium text-gray-900">{title}</h4>
      <p className="text-sm text-gray-500">{date}</p>
    </div>
    <div className="text-right">
      {status === 'completed' ? (
        <p className="text-lg font-semibold text-gray-900">{score}%</p>
      ) : (
        <span className="text-sm text-yellow-600">In Progress</span>
      )}
    </div>
  </div>
);

const ScheduleItem = ({ title, date, time, location }) => (
  <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
    <div className="flex-shrink-0 mt-1">
      <Clock className="w-5 h-5 text-gray-400" />
    </div>
    <div className="flex-1 min-w-0">
      <p className="font-medium text-gray-900">{title}</p>
      <p className="text-sm text-gray-500">{date} at {time}</p>
      {location && <p className="text-sm text-gray-500">{location}</p>}
    </div>
  </div>
);

const QuickActionButton = ({ icon, label, to }) => (
  <Link to={to}>
    <Button variant="outline" className="w-full h-20 flex flex-col items-center justify-center space-y-2">
      {icon}
      <span className="text-xs">{label}</span>
    </Button>
  </Link>
);

// Mock data - replace with real data from API
const mockSkillsData = [
  { skill: 'Frontend', value: 80 },
  { skill: 'Backend', value: 65 },
  { skill: 'Database', value: 70 },
  { skill: 'DevOps', value: 45 },
  { skill: 'Testing', value: 75 },
  { skill: 'Security', value: 55 }
];

const mockPerformanceData = [
  { month: 'Jan', assessments: 75, attendance: 90 },
  { month: 'Feb', assessments: 82, attendance: 95 },
  { month: 'Mar', assessments: 78, attendance: 88 },
  { month: 'Apr', assessments: 85, attendance: 92 },
  { month: 'May', assessments: 88, attendance: 96 },
  { month: 'Jun', assessments: 92, attendance: 98 }
];

export default PortalDashboardV2;
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import api from '@/lib/api';
import { AnimatedCard, AnimatedButton, AnimatedPage, AnimatedList, AnimatedListItem } from '@/components/animations';
import { OptimizedAnimation, BatchAnimation } from '@/components/animations/OptimizedAnimation';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';
import { fadeInUp, staggerContainer, staggerItem } from '@/lib/animations';
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
  GraduationCap,
  Activity,
  Star
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

const PortalDashboardV3 = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [coursesData, setCoursesData] = useState([]);
  const [progressData, setProgressData] = useState(null);
  const [achievementsData, setAchievementsData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        
        // Fetch dashboard overview
        const [dashboard, courses, progress, achievements] = await Promise.all([
          api.get('/api/portal/dashboard'),
          api.get('/api/portal/courses'),
          api.get('/api/portal/progress'),
          api.get('/api/portal/achievements')
        ]);
        
        setDashboardData(dashboard.data);
        setCoursesData(courses.data.courses || []);
        setProgressData(progress.data);
        setAchievementsData(achievements.data.achievements || []);
        
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        // Set default data structures to prevent errors
        setDashboardData({
          user: {
            name: user?.first_name || 'Student',
            email: user?.email || '',
            profile_picture: user?.profile_picture || ''
          },
          beneficiary: {},
          stats: {
            enrolled_programs: 0,
            completed_programs: 0,
            average_progress: 0,
            total_attendance_rate: 0
          },
          upcoming_sessions: [],
          recent_tests: []
        });
        setCoursesData([]);
        setProgressData({
          overall_progress: 0,
          current_level: 'Beginner',
          skills_distribution: [],
          monthly_progress: []
        });
        setAchievementsData([]);
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

  // Process skills data from progress
  const skillsData = progressData?.skills_distribution || [];
  
  // Process performance data from progress
  const performanceData = progressData?.monthly_progress || [];

  return (
    <AnimatedPage className="space-y-6 p-6">
      {/* Welcome Header */}
      <motion.div 
        className="bg-gradient-to-r from-primary to-primary-dark rounded-lg p-6 text-white"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold mb-2">Welcome back, {userData.name}!</h1>
            <p className="text-primary-lighter">Track your progress and achieve your goals</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-primary-lighter">Current Level</p>
            <p className="text-2xl font-bold">{progressData?.current_level || 'Beginner'}</p>
          </div>
        </div>
      </motion.div>

      {/* Stats Overview */}
      <motion.div 
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
        variants={staggerContainer}
        initial="initial"
        animate="animate"
      >
        <StatsCard
          title="Enrolled Programs"
          value={stats.enrolled_programs}
          icon={<BookOpen className="w-6 h-6" />}
          color="bg-blue-500"
          subtitle={`${stats.completed_programs} completed`}
        />
        <StatsCard
          title="Average Progress"
          value={`${Math.round(stats.average_progress)}%`}
          icon={<TrendingUp className="w-6 h-6" />}
          color="bg-purple-500"
          subtitle="Across all programs"
        />
        <StatsCard
          title="Attendance Rate"
          value={`${Math.round(stats.total_attendance_rate || 0)}%`}
          icon={<CheckCircle2 className="w-6 h-6" />}
          color="bg-green-500"
          subtitle="Keep it up!"
        />
        <StatsCard
          title="Achievements"
          value={achievementsData.length}
          icon={<Award className="w-6 h-6" />}
          color="bg-orange-500"
          subtitle="Badges earned"
        />
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Progress Overview */}
        <div className="lg:col-span-2 space-y-6">
          {/* Active Programs */}
          <AnimatedCard className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Active Programs</h2>
              <Link to="/portal/courses">
                <AnimatedButton variant="ghost" size="sm">
                  View All <ArrowRight className="w-4 h-4 ml-1" />
                </AnimatedButton>
              </Link>
            </div>
            
            <div className="space-y-4">
              {coursesData.filter(course => course.enrollment_status === 'enrolled').map(course => (
                <ProgramProgressCard
                  key={course.id}
                  title={course.name}
                  progress={course.progress || 0}
                  nextSession={getNextSession(course)}
                  moduleProgress={`Module ${course.current_module || 1} of ${course.total_modules || 1}`}
                  instructor={course.instructor}
                />
              ))}
              
              {coursesData.filter(course => course.enrollment_status === 'enrolled').length === 0 && (
                <p className="text-gray-500 text-center py-8">No active programs</p>
              )}
            </div>
          </AnimatedCard>

          {/* Recent Assessments */}
          <AnimatedCard className="p-6">
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
                  feedback={test.ai_feedback}
                />
              ))}
              
              {recent_tests.length === 0 && (
                <p className="text-gray-500 text-center py-8">No recent assessments</p>
              )}
            </div>
          </AnimatedCard>

          {/* Performance Analytics */}
          <AnimatedCard className="p-6">
            <h2 className="text-xl font-semibold mb-4">Performance Trend</h2>
            {performanceData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="average_score" stroke="#8884d8" name="Assessment Score" />
                  <Line type="monotone" dataKey="completion_rate" stroke="#82ca9d" name="Completion Rate" />
                  <Line type="monotone" dataKey="attendance_rate" stroke="#ffc658" name="Attendance Rate" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-500 text-center py-8">No performance data available</p>
            )}
          </AnimatedCard>
        </div>

        {/* Right Column - Schedule & Skills */}
        <div className="space-y-6">
          {/* Upcoming Schedule */}
          <AnimatedCard className="p-6">
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
                  title={session.module?.name || session.title || 'Training Session'}
                  date={new Date(session.session_date || session.datetime).toLocaleDateString()}
                  time={new Date(session.session_date || session.datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  location={session.location}
                  type={session.type}
                />
              ))}
              
              {upcoming_sessions.length === 0 && (
                <p className="text-gray-500 text-center py-8">No upcoming sessions</p>
              )}
            </div>
          </AnimatedCard>

          {/* Skills Progress */}
          <OptimizedAnimation threshold={0.3}>
            <AnimatedCard className="p-6">
              <h2 className="text-xl font-semibold mb-4">Skills Development</h2>
              {skillsData.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <RadarChart data={skillsData}>
                    <PolarGrid strokeDasharray="3 3" />
                    <PolarAngleAxis dataKey="skill" />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} />
                    <Radar name="Progress" dataKey="value" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                  </RadarChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-gray-500 text-center py-8">No skills data available</p>
              )}
            <Link to="/portal/skills" className="block mt-4">
              <Button variant="outline" className="w-full">
                View Detailed Progress
              </Button>
            </Link>
          </AnimatedCard>

          {/* Achievements */}
          <AnimatedCard className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Recent Achievements</h2>
              <Link to="/portal/achievements">
                <Button variant="ghost" size="sm">
                  View All <Award className="w-4 h-4 ml-1" />
                </Button>
              </Link>
            </div>
            
            <div className="space-y-3">
              {achievementsData.slice(0, 3).map((achievement) => (
                <AchievementBadge
                  key={achievement.id}
                  icon={getAchievementIcon(achievement.type)}
                  title={achievement.title}
                  description={achievement.description}
                  earnedDate={new Date(achievement.earned_date).toLocaleDateString()}
                />
              ))}
              
              {achievementsData.length === 0 && (
                <p className="text-gray-500 text-center py-8">No achievements yet</p>
              )}
            </div>
          </AnimatedCard>

          {/* Quick Actions */}
          <AnimatedCard className="p-6">
            <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
            <div className="grid grid-cols-2 gap-3">
              <QuickActionButton
                icon={<FileText className="w-5 h-5" />}
                label="Resources"
                to="/portal/resources"
              />
              <QuickActionButton
                icon={<Brain className="w-5 h-5" />}
                label="Take Test"
                to="/portal/assessments"
              />
              <QuickActionButton
                icon={<Activity className="w-5 h-5" />}
                label="Progress"
                to="/portal/progress"
              />
              <QuickActionButton
                icon={<Users className="w-5 h-5" />}
                label="Profile"
                to="/portal/profile"
              />
            </div>
          </AnimatedCard>
        </div>
      </div>
    </AnimatedPage>
  );
};

// Helper Components
const StatsCard = ({ title, value, icon, color, subtitle }) => (
  <motion.div variants={staggerItem}>
    <AnimatedCard className="p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
        <p className="text-2xl font-bold mt-1">{value}</p>
        {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
      </div>
      <div className={`p-3 rounded-lg ${color} bg-opacity-10`}>
        <div className={`${color} text-white`}>{icon}</div>
      </div>
    </div>
    </AnimatedCard>
  </motion.div>
);

const ProgramProgressCard = ({ title, progress, nextSession, moduleProgress, instructor }) => (
  <div className="border rounded-lg p-4">
    <div className="flex justify-between items-start mb-2">
      <h3 className="font-medium text-gray-900">{title}</h3>
      <span className="text-sm text-gray-500">{progress}%</span>
    </div>
    <Progress value={progress} className="h-2 mb-2" />
    <div className="flex justify-between text-sm text-gray-600">
      <span>{moduleProgress}</span>
      {instructor && <span>by {instructor}</span>}
    </div>
    {nextSession && (
      <p className="text-sm text-gray-500 mt-2">Next: {nextSession}</p>
    )}
  </div>
);

const AssessmentCard = ({ title, date, score, status, feedback }) => (
  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
    <div className="flex-1">
      <h4 className="font-medium text-gray-900">{title}</h4>
      <p className="text-sm text-gray-500">{date}</p>
      {feedback && <p className="text-xs text-blue-600 mt-1">AI Feedback Available</p>}
    </div>
    <div className="text-right">
      {status === 'completed' ? (
        <>
          <p className="text-lg font-semibold text-gray-900">{score}%</p>
          <span className={`text-xs ${getScoreColor(score)}`}>
            {getScoreLabel(score)}
          </span>
        </>
      ) : (
        <span className="text-sm text-yellow-600 font-medium">In Progress</span>
      )}
    </div>
  </div>
);

const ScheduleItem = ({ title, date, time, location, type }) => (
  <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
    <div className="flex-shrink-0 mt-1">
      {type === 'online' ? (
        <Activity className="w-5 h-5 text-blue-500" />
      ) : (
        <Clock className="w-5 h-5 text-gray-400" />
      )}
    </div>
    <div className="flex-1 min-w-0">
      <p className="font-medium text-gray-900">{title}</p>
      <p className="text-sm text-gray-500">{date} at {time}</p>
      {location && <p className="text-sm text-gray-500">{location}</p>}
    </div>
  </div>
);

const AchievementBadge = ({ icon, title, description, earnedDate }) => (
  <div className="flex items-center space-x-3 p-3 bg-yellow-50 rounded-lg">
    <div className="flex-shrink-0">
      {icon}
    </div>
    <div className="flex-1 min-w-0">
      <p className="font-medium text-gray-900">{title}</p>
      <p className="text-xs text-gray-600">{description}</p>
      <p className="text-xs text-gray-500 mt-1">Earned: {earnedDate}</p>
    </div>
  </div>
);

const QuickActionButton = ({ icon, label, to }) => (
  <Link to={to}>
    <AnimatedButton variant="outline" className="w-full h-20 flex flex-col items-center justify-center space-y-2 hover:bg-primary-50 transition-colors">
      {icon}
      <span className="text-xs">{label}</span>
    </AnimatedButton>
  </Link>
);

// Helper Functions
const getNextSession = (course) => {
  if (!course.next_session) return null;
  const date = new Date(course.next_session);
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);
  
  if (date.toDateString() === today.toDateString()) {
    return `Today at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
  } else if (date.toDateString() === tomorrow.toDateString()) {
    return `Tomorrow at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
  } else {
    return `${date.toLocaleDateString()} at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
  }
};

const getAchievementIcon = (type) => {
  switch (type) {
    case 'completion':
      return <CheckCircle2 className="w-8 h-8 text-green-500" />;
    case 'high_score':
      return <Star className="w-8 h-8 text-yellow-500" />;
    case 'attendance':
      return <Calendar className="w-8 h-8 text-blue-500" />;
    default:
      return <Award className="w-8 h-8 text-purple-500" />;
  }
};

const getScoreColor = (score) => {
  if (score >= 90) return 'text-green-600 font-medium';
  if (score >= 80) return 'text-blue-600';
  if (score >= 70) return 'text-yellow-600';
  return 'text-red-600';
};

const getScoreLabel = (score) => {
  if (score >= 90) return 'Excellent';
  if (score >= 80) return 'Very Good';
  if (score >= 70) return 'Good';
  if (score >= 60) return 'Satisfactory';
  return 'Needs Improvement';
};

export default PortalDashboardV3;
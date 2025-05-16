import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Download, Users, Calendar, CheckCircle, Target, TrendingUp, Award } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import api from '@/lib/api';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const ProgramAnalyticsPageV2 = () => {
  const { id } = useParams();
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalytics();
  }, [id]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/analytics/programs?program_id=${id}`);
      setAnalyticsData(response.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async () => {
    try {
      const response = await api.get(`/api/reports/program/${id}/download`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `program-report-${id}.pdf`);
      document.body.appendChild(link);
      link.click();
    } catch (err) {
      console.error('Failed to download report:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
          <p className="font-semibold">Error loading analytics</p>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!analyticsData) {
    return <div>No data available</div>;
  }

  const { program, enrollments, sessions, attendance, modules, test_performance } = analyticsData;

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  const enrollmentChartData = [
    { name: 'Active', value: enrollments.active },
    { name: 'Completed', value: enrollments.completed },
    { name: 'Inactive', value: enrollments.total - enrollments.active - enrollments.completed }
  ];

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <Link to="/analytics">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Analytics
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold">{program.name}</h1>
            <p className="text-gray-500">{program.description}</p>
          </div>
        </div>
        <Button onClick={downloadReport}>
          <Download className="w-4 h-4 mr-2" />
          Download Report
        </Button>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          icon={<Users className="w-6 h-6" />}
          title="Total Enrollments"
          value={enrollments.total}
          subtitle={`${enrollments.active} active`}
          color="bg-blue-500"
        />
        <StatsCard
          icon={<CheckCircle className="w-6 h-6" />}
          title="Completion Rate"
          value={`${Math.round(enrollments.completion_rate)}%`}
          subtitle={`${enrollments.completed} completed`}
          color="bg-green-500"
        />
        <StatsCard
          icon={<Calendar className="w-6 h-6" />}
          title="Sessions"
          value={sessions.total}
          subtitle={`${sessions.completed} completed`}
          color="bg-purple-500"
        />
        <StatsCard
          icon={<Target className="w-6 h-6" />}
          title="Avg Test Score"
          value={`${Math.round(test_performance.average_score)}%`}
          subtitle={`${test_performance.total_tests} tests`}
          color="bg-orange-500"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Enrollment Distribution */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Enrollment Status</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={enrollmentChartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={renderCustomizedLabel}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {enrollmentChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        {/* Module Progress */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Module Progress</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={modules}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="module_name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="completion_rate" fill="#8884d8" name="Completion %" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Module Details */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Module Details</h3>
        <div className="space-y-4">
          {modules.map((module) => (
            <div key={module.module_id} className="border rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <h4 className="font-medium">{module.module_name}</h4>
                <span className="text-sm text-gray-500">
                  {module.completed_sessions}/{module.total_sessions} sessions
                </span>
              </div>
              <Progress value={module.completion_rate} className="h-2" />
              <p className="text-sm text-gray-600 mt-1">
                {Math.round(module.completion_rate)}% complete
              </p>
            </div>
          ))}
        </div>
      </Card>

      {/* Performance Metrics */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Performance Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <MetricCard
            title="Average Attendance"
            value={`${Math.round(attendance.average_rate)}%`}
            icon={<Users className="w-5 h-5" />}
            trend="up"
          />
          <MetricCard
            title="Session Completion"
            value={`${Math.round(sessions.completion_rate)}%`}
            icon={<Calendar className="w-5 h-5" />}
            trend="stable"
          />
          <MetricCard
            title="Student Satisfaction"
            value="92%"
            icon={<Award className="w-5 h-5" />}
            trend="up"
          />
        </div>
      </Card>
    </div>
  );
};

// Component Helpers
const StatsCard = ({ icon, title, value, subtitle, color }) => (
  <Card className="p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-gray-600">{title}</p>
        <p className="text-2xl font-bold mt-1">{value}</p>
        <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
      </div>
      <div className={`p-3 rounded-lg ${color} bg-opacity-10`}>
        <div className={`${color} text-white`}>{icon}</div>
      </div>
    </div>
  </Card>
);

const MetricCard = ({ title, value, icon, trend }) => (
  <div className="text-center">
    <div className="flex justify-center mb-2">
      <div className="p-2 bg-gray-100 rounded-lg">
        {icon}
      </div>
    </div>
    <p className="text-2xl font-bold">{value}</p>
    <p className="text-sm text-gray-600">{title}</p>
    {trend === 'up' && <TrendingUp className="w-4 h-4 text-green-500 mx-auto mt-1" />}
  </div>
);

const renderCustomizedLabel = ({
  cx, cy, midAngle, innerRadius, outerRadius, percent
}) => {
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * Math.PI / 180);
  const y = cy + radius * Math.sin(-midAngle * Math.PI / 180);

  return (
    <text
      x={x}
      y={y}
      fill="white"
      textAnchor={x > cx ? 'start' : 'end'}
      dominantBaseline="central"
    >
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
};

export default ProgramAnalyticsPageV2;
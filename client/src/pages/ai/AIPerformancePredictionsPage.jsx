// TODO: i18n - processed
import { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { Button } from '../../components/ui/button';
import { Card } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Select } from '../../components/ui/select';
import {
  Loader2,
  TrendingUp,
  TrendingDown,
  Target,
  AlertTriangle,
  Calendar,
  User,
  BarChart,
  LineChart,
  Lock } from
'lucide-react';
import {
  LineChart as RechartsLineChart,
  Line,
  AreaChart,
  Area,
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer } from
'recharts';import { useTranslation } from "react-i18next";
const AIPerformancePredictionsPage = () => {const { t } = useTranslation();
  const { user, hasRole } = useAuth();
  const { toast } = useToast();
  // AI Performance Predictions are restricted to admin and trainer roles only
  const canAccessPredictions = hasRole(['super_admin', 'tenant_admin', 'trainer']);
  // If user doesn't have permission, show access denied
  if (!canAccessPredictions) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="p-8 text-center max-w-md">
          <Lock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">{t("components.access_restricted")}</h2>
          <p className="text-gray-600 mb-4">{t("pages.ai_performance_predictions_are_only_available_to_a")}

          </p>
          <p className="text-sm text-gray-500">{t("components.current_role")}
            <span className="font-medium">{user?.role}</span>
          </p>
        </Card>
      </div>);

  }
  const [loading, setLoading] = useState(true);
  const [predictions, setPredictions] = useState(null);
  const [selectedBeneficiary, setSelectedBeneficiary] = useState('');
  const [selectedProgram, setSelectedProgram] = useState('');
  const [selectedTimeframe, setSelectedTimeframe] = useState('3_months');
  const [beneficiaries, setBeneficiaries] = useState([]);
  const [programs, setPrograms] = useState([]);
  useEffect(() => {
    fetchBeneficiaries();
    fetchPrograms();
  }, []);
  useEffect(() => {
    if (selectedBeneficiary || selectedProgram) {
      fetchPredictions();
    }
  }, [selectedBeneficiary, selectedProgram, selectedTimeframe]);
  const fetchBeneficiaries = async () => {
    try {
      const res = await fetch('/api/beneficiaries', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to fetch beneficiaries');
      const data = await res.json();
      setBeneficiaries(data);
    } catch (error) {
      console.error('Error fetching beneficiaries:', error);
    }
  };
  const fetchPrograms = async () => {
    try {
      const res = await fetch('/api/programs', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to fetch programs');
      const data = await res.json();
      setPrograms(data);
    } catch (error) {
      console.error('Error fetching programs:', error);
    }
  };
  const fetchPredictions = async () => {
    // Additional permission check for fetching predictions
    if (!hasRole(['super_admin', 'tenant_admin', 'trainer'])) {
      toast({
        title: 'Access Denied',
        description: 'Performance predictions access is restricted to administrators and trainers only',
        variant: 'destructive'
      });
      return;
    }
    setLoading(true);
    try {
      const params = new URLSearchParams({
        timeframe: selectedTimeframe
      });
      if (selectedBeneficiary) params.append('beneficiary_id', selectedBeneficiary);
      if (selectedProgram) params.append('program_id', selectedProgram);
      const res = await fetch(`/api/ai/performance-predictions?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to fetch predictions');
      const data = await res.json();
      setPredictions(data);
    } catch (error) {
      console.error('Error fetching predictions:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch performance predictions',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };
  const getTrendIcon = (trend) => {
    if (trend > 0) return <TrendingUp className="h-4 w-4 text-green-600" />;
    if (trend < 0) return <TrendingDown className="h-4 w-4 text-red-600" />;
    return null;
  };
  if (loading && predictions === null) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>);

  }
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <LineChart className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-bold text-gray-900">{t("pages.performance_predictions")}</h1>
        </div>
      </div>
      {/* Filters */}
      <Card className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t("components.beneficiary")}

            </label>
            <Select
              value={selectedBeneficiary}
              onChange={(e) => setSelectedBeneficiary(e.target.value)}>

              <option value="">{t("components.all_beneficiaries")}</option>
              {beneficiaries.map((beneficiary) =>
              <option key={beneficiary.id} value={beneficiary.id}>
                  {beneficiary.full_name}
                </option>
              )}
            </Select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t("components.program")}

            </label>
            <Select
              value={selectedProgram}
              onChange={(e) => setSelectedProgram(e.target.value)}>

              <option value="">{t("lib.all_programs")}</option>
              {programs.map((program) =>
              <option key={program.id} value={program.id}>
                  {program.name}
                </option>
              )}
            </Select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t("pages.timeframe")}

            </label>
            <Select
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value)}>

              <option value="1_month">{t("pages.next_1_month")}</option>
              <option value="3_months">{t("pages.next_3_months")}</option>
              <option value="6_months">{t("pages.next_6_months")}</option>
              <option value="1_year">{t("pages.next_1_year")}</option>
            </Select>
          </div>
        </div>
      </Card>
      {predictions &&
      <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card className="p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">{t("pages.predicted_average_score")}</p>
                <Target className="h-4 w-4 text-primary" />
              </div>
              <p className={`text-2xl font-bold ${getScoreColor(predictions.summary.predicted_average_score)}`}>
                {predictions.summary.predicted_average_score}%
              </p>
              <div className="flex items-center gap-1 mt-1">
                {getTrendIcon(predictions.summary.score_trend)}
                <span className="text-sm text-gray-600">
                  {Math.abs(predictions.summary.score_trend)}{t("pages._from_current")}
              </span>
              </div>
            </Card>
            <Card className="p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">{t("pages.completion_probability")}</p>
                <BarChart className="h-4 w-4 text-blue-600" />
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {predictions.summary.completion_probability}%
              </p>
              <p className="text-sm text-gray-600 mt-1">
                {predictions.summary.at_risk_count}{t("pages.at_risk")}
            </p>
            </Card>
            <Card className="p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">{t("components.success_rate")}</p>
                <TrendingUp className="h-4 w-4 text-green-600" />
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {predictions.summary.success_rate}%
              </p>
              <div className="flex items-center gap-1 mt-1">
                {getTrendIcon(predictions.summary.success_trend)}
                <span className="text-sm text-gray-600">
                  {Math.abs(predictions.summary.success_trend)}{t("pages._change")}
              </span>
              </div>
            </Card>
            <Card className="p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">{t("pages.risk_level")}</p>
                <AlertTriangle className="h-4 w-4 text-amber-600" />
              </div>
              <Badge variant={predictions.summary.risk_level === 'high' ? 'destructive' : 'warning'} className="text-lg py-1 px-3">
                {predictions.summary.risk_level.toUpperCase()}
              </Badge>
              <p className="text-sm text-gray-600 mt-1">
                {predictions.summary.risk_factors.length}{t("pages.risk_factors")}
            </p>
            </Card>
          </div>
          {/* Performance Trend Chart */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold mb-4">{t("pages.performance_trend_prediction")}</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={predictions.performance_trend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Area
                  type="monotone"
                  dataKey="predicted_score"
                  stroke="#0088FE"
                  fill="#0088FE"
                  fillOpacity={0.6}
                  name="Predicted Score" />

                  <Area
                  type="monotone"
                  dataKey="confidence_upper"
                  stroke="#00C49F"
                  fill="#00C49F"
                  fillOpacity={0.3}
                  name="Upper Bound" />

                  <Area
                  type="monotone"
                  dataKey="confidence_lower"
                  stroke="#FFBB28"
                  fill="#FFBB28"
                  fillOpacity={0.3}
                  name="Lower Bound" />

                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>
          {/* Individual Predictions */}
          {selectedBeneficiary && predictions.individual_predictions &&
        <Card className="p-6">
              <h2 className="text-lg font-semibold mb-4">Individual Skill Predictions</h2>
              <div className="space-y-4">
                {predictions.individual_predictions.map((skill, index) =>
            <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">{skill.skill_name}</h3>
                      <p className="text-sm text-gray-600">Current: {skill.current_level}%</p>
                    </div>
                    <div className="text-right">
                      <p className={`font-bold ${getScoreColor(skill.predicted_level)}`}>
                        {skill.predicted_level}%
                      </p>
                      <div className="flex items-center justify-end gap-1">
                        {getTrendIcon(skill.predicted_level - skill.current_level)}
                        <span className="text-sm text-gray-600">
                          {Math.abs(skill.predicted_level - skill.current_level)}%
                        </span>
                      </div>
                    </div>
                  </div>
            )}
              </div>
            </Card>
        }
          {/* Risk Factors */}
          {predictions.risk_analysis && predictions.risk_analysis.length > 0 &&
        <Card className="p-6 border-amber-200 bg-amber-50">
              <div className="flex items-center gap-3 mb-4">
                <AlertTriangle className="h-5 w-5 text-amber-600" />
                <h2 className="text-lg font-semibold text-gray-900">{t("pages.risk_analysis")}</h2>
              </div>
              <div className="space-y-3">
                {predictions.risk_analysis.map((risk, index) =>
            <div key={index} className="flex items-start gap-3">
                    <div className="w-1.5 h-1.5 bg-amber-600 rounded-full mt-2" />
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{risk.factor}</p>
                      <p className="text-sm text-gray-600">{risk.description}</p>
                      <p className="text-sm text-amber-700 mt-1">{t("pages.mitigation")}
                  {risk.mitigation}
                      </p>
                    </div>
                    <Badge variant="warning">
                      {risk.severity} risk
                    </Badge>
                  </div>
            )}
              </div>
            </Card>
        }
          {/* Recommendations */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold mb-4">{t("pages.ai_recommendations")}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {predictions.recommendations.map((rec, index) =>
            <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <Target className="h-5 w-5 text-primary mt-0.5" />
                    <div>
                      <h3 className="font-medium text-gray-900">{rec.title}</h3>
                      <p className="text-sm text-gray-600 mt-1">{rec.description}</p>
                      <p className="text-sm text-gray-500 mt-2">{t("pages.expected_impact")}
                    {rec.expected_impact}%
                      </p>
                    </div>
                  </div>
                </div>
            )}
            </div>
          </Card>
        </>
      }
    </div>);

};
export default AIPerformancePredictionsPage;
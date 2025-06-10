// TODO: i18n - processed
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  Clock,
  Calendar,
  Award,
  CheckCircle,
  AlertTriangle,
  Loader,
  ChevronRight } from
'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
/**
 * Displays upcoming and recent assessments for the student
 */import { useTranslation } from "react-i18next";
const AssessmentsWidget = ({ data, isLoading, error }) => {const { t } = useTranslation();
  const navigate = useNavigate();
  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'No due date';
    const date = new Date(dateString);
    const now = new Date();
    // If it's today
    if (date.toDateString() === now.toDateString()) {
      return 'Today';
    }
    // If it's tomorrow
    const tomorrow = new Date(now);
    tomorrow.setDate(now.getDate() + 1);
    if (date.toDateString() === tomorrow.toDateString()) {
      return 'Tomorrow';
    }
    // If it's within a week
    const oneWeek = new Date(now);
    oneWeek.setDate(now.getDate() + 7);
    if (date < oneWeek) {
      return date.toLocaleDateString(undefined, { weekday: 'long' });
    }
    // Otherwise, return the full date
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  };
  // Format score with color
  const formatScore = (score, passingScore) => {
    const passed = score >= (passingScore || 0);
    return (
      <span className={`font-medium ${passed ? 'text-green-600' : 'text-red-600'}`}>
        {score}%
      </span>);

  };
  // Get icon and color for assessment type
  const getAssessmentTypeIcon = (type) => {
    switch (type) {
      case 'quiz':
        return <FileText className="h-5 w-5 text-blue-500" />;
      case 'exam':
        return <FileText className="h-5 w-5 text-purple-500" />;
      case 'project':
        return <Award className="h-5 w-5 text-green-500" />;
      case 'evaluation':
        return <Award className="h-5 w-5 text-orange-500" />;
      default:
        return <FileText className="h-5 w-5 text-gray-500" />;
    }
  };
  if (isLoading) {
    return (
      <Card className="overflow-hidden h-full">
        <div className="p-6 flex justify-between items-center border-b">
          <h2 className="text-lg font-medium">{t("archive-components.assessments")}</h2>
        </div>
        <div className="flex justify-center items-center p-12">
          <Loader className="h-8 w-8 text-primary animate-spin" />
        </div>
      </Card>);

  }
  if (error) {
    return (
      <Card className="overflow-hidden h-full">
        <div className="p-6 flex justify-between items-center border-b">
          <h2 className="text-lg font-medium">{t("archive-components.assessments")}</h2>
        </div>
        <div className="p-6 text-center text-red-500">{t("components.failed_to_load_assessments")}

        </div>
      </Card>);

  }
  // Helper to get upcoming assessments (available and upcoming)
  const getUpcomingAssessments = () => {
    if (!data) return [];
    // Combine all assessments
    const allAssessments = [
    ...(data.moduleAssessments || []),
    ...(data.programAssessments || []),
    ...(data.skillAssessments || [])];

    // Filter to only available or upcoming assessments
    return allAssessments.
    filter((a) => a.status === 'available' || a.status === 'upcoming').
    sort((a, b) => {
      // Sort by due date (nulls last)
      if (!a.dueDate && !b.dueDate) return 0;
      if (!a.dueDate) return 1;
      if (!b.dueDate) return -1;
      return new Date(a.dueDate) - new Date(b.dueDate);
    }).
    slice(0, 3); // Limit to 3 items
  };
  // Helper to get recently completed assessments
  const getRecentAssessments = () => {
    if (!data) return [];
    // Combine all assessments
    const allAssessments = [
    ...(data.moduleAssessments || []),
    ...(data.programAssessments || []),
    ...(data.skillAssessments || [])];

    // Filter to only completed assessments and sort by completion date
    return allAssessments.
    filter((a) => a.status === 'completed' && a.completedDate).
    sort((a, b) => new Date(b.completedDate) - new Date(a.completedDate)).
    slice(0, 2); // Limit to 2 items
  };
  const upcomingAssessments = getUpcomingAssessments();
  const recentAssessments = getRecentAssessments();
  return (
    <Card className="overflow-hidden h-full">
      <div className="p-6 flex justify-between items-center border-b">
        <h2 className="text-lg font-medium">{t("archive-components.assessments")}</h2>
        <Button
          variant="outline"
          size="sm"
          onClick={() => navigate('/portal/assessment')}>{t("archive-components.view_all")}


        </Button>
      </div>
      <div className="p-4">
        {/* Upcoming assessments */}
        {upcomingAssessments.length > 0 &&
        <div className="mb-4">
            <h3 className="text-sm font-medium text-gray-500 mb-2">{t("components.upcoming")}</h3>
            <div className="space-y-3">
              {upcomingAssessments.map((assessment) =>
            <div
              key={assessment.id}
              className="flex items-start p-3 border rounded-md hover:bg-gray-50 cursor-pointer"
              onClick={() => navigate(`/portal/assessment/${assessment.id}`)}>

                  <div className="p-2 rounded-md bg-blue-50 mr-3">
                    {getAssessmentTypeIcon(assessment.type)}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-sm">{assessment.title}</h4>
                    <div className="flex items-center mt-1">
                      <Clock className="h-3.5 w-3.5 text-gray-400 mr-1" />
                      <span className="text-xs text-gray-500 mr-3">
                        {assessment.duration ? `${assessment.duration} min` : 'No time limit'}
                      </span>
                      <Calendar className="h-3.5 w-3.5 text-gray-400 mr-1" />
                      <span className="text-xs text-gray-500">
                        Due: {formatDate(assessment.dueDate)}
                      </span>
                    </div>
                  </div>
                  <ChevronRight className="h-4 w-4 text-gray-400 mt-1" />
                </div>
            )}
            </div>
          </div>
        }
        {/* Recent assessments */}
        {recentAssessments.length > 0 &&
        <div>
            <h3 className="text-sm font-medium text-gray-500 mb-2">{t("components.recently_completed")}</h3>
            <div className="space-y-3">
              {recentAssessments.map((assessment) =>
            <div
              key={assessment.id}
              className="flex items-start p-3 border rounded-md hover:bg-gray-50 cursor-pointer"
              onClick={() => navigate(`/portal/assessment/${assessment.id}/results`)}>

                  <div className="p-2 rounded-md bg-green-50 mr-3">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-sm">{assessment.title}</h4>
                    <div className="flex items-center mt-1">
                      <span className="text-xs text-gray-500 mr-2">
                        Score: {formatScore(assessment.attempts.bestScore, assessment.passingScore)}
                      </span>
                      <Calendar className="h-3.5 w-3.5 text-gray-400 mr-1" />
                      <span className="text-xs text-gray-500">
                        {formatDate(assessment.completedDate)}
                      </span>
                    </div>
                  </div>
                  <ChevronRight className="h-4 w-4 text-gray-400 mt-1" />
                </div>
            )}
            </div>
          </div>
        }
        {upcomingAssessments.length === 0 && recentAssessments.length === 0 &&
        <div className="text-center py-6">
            <FileText className="h-12 w-12 text-gray-300 mx-auto mb-2" />
            <p className="text-gray-500">{t("components.no_assessments_available")}</p>
            <Button
            variant="link"
            onClick={() => navigate('/portal/assessment')}
            className="mt-2">{t("components.view_all_assessments")}


          </Button>
          </div>
        }
      </div>
    </Card>);

};
export default AssessmentsWidget;
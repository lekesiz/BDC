import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Progress } from '../../components/ui/progress';
import { Target, TrendingUp, Calendar, CheckCircle, Clock } from 'lucide-react';

const ProgressTracker = ({ progressData = {}, learningPaths = {} }) => {
  const { overall_progress = {}, recent_milestones = [] } = progressData;
  const { active_count = 0, completed_count = 0, paths = [] } = learningPaths;

  const getProgressColor = (percentage) => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-blue-600';
    if (percentage >= 40) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const getProgressBgColor = (percentage) => {
    if (percentage >= 80) return 'bg-green-100';
    if (percentage >= 60) return 'bg-blue-100';
    if (percentage >= 40) return 'bg-yellow-100';
    return 'bg-gray-100';
  };

  return (
    <div className=\"space-y-6\">
      {/* Overall Progress Overview */}
      <div className=\"grid grid-cols-1 md:grid-cols-4 gap-4\">
        <Card>
          <CardContent className=\"p-4 text-center\">
            <div className={`w-16 h-16 mx-auto rounded-full flex items-center justify-center mb-3 ${getProgressBgColor(overall_progress.percentage || 0)}`}>
              <TrendingUp className={`h-8 w-8 ${getProgressColor(overall_progress.percentage || 0)}`} />
            </div>
            <div className={`text-2xl font-bold ${getProgressColor(overall_progress.percentage || 0)}`}>
              {Math.round(overall_progress.percentage || 0)}%
            </div>
            <div className=\"text-sm text-gray-600\">Overall Progress</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className=\"p-4 text-center\">
            <div className=\"w-16 h-16 mx-auto rounded-full bg-blue-100 flex items-center justify-center mb-3\">
              <Target className=\"h-8 w-8 text-blue-600\" />
            </div>
            <div className=\"text-2xl font-bold text-blue-600\">
              {overall_progress.completed || 0}
            </div>
            <div className=\"text-sm text-gray-600\">Completed Goals</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className=\"p-4 text-center\">
            <div className=\"w-16 h-16 mx-auto rounded-full bg-yellow-100 flex items-center justify-center mb-3\">
              <Clock className=\"h-8 w-8 text-yellow-600\" />
            </div>
            <div className=\"text-2xl font-bold text-yellow-600\">
              {active_count}
            </div>
            <div className=\"text-sm text-gray-600\">Active Paths</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className=\"p-4 text-center\">
            <div className=\"w-16 h-16 mx-auto rounded-full bg-green-100 flex items-center justify-center mb-3\">
              <CheckCircle className=\"h-8 w-8 text-green-600\" />
            </div>
            <div className=\"text-2xl font-bold text-green-600\">
              {completed_count}
            </div>
            <div className=\"text-sm text-gray-600\">Paths Completed</div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Progress Breakdown */}
      <div className=\"grid grid-cols-1 lg:grid-cols-2 gap-6\">
        {/* Recent Milestones */}
        <Card>
          <CardHeader>
            <CardTitle className=\"flex items-center space-x-2\">
              <Target className=\"h-5 w-5\" />
              <span>Recent Milestones</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {recent_milestones.length > 0 ? (
              <div className=\"space-y-4\">
                {recent_milestones.map((milestone, index) => (
                  <div key={index} className=\"flex items-center space-x-3 p-3 bg-gray-50 rounded-lg\">
                    <div className=\"p-2 bg-green-100 rounded-lg\">
                      <CheckCircle className=\"h-5 w-5 text-green-600\" />
                    </div>
                    <div className=\"flex-1\">
                      <p className=\"font-medium\">{milestone.milestone.name}</p>
                      <p className=\"text-sm text-gray-600\">{milestone.milestone.description}</p>
                      <div className=\"flex items-center space-x-2 mt-1\">
                        <Calendar className=\"h-3 w-3 text-gray-400\" />
                        <span className=\"text-xs text-gray-500\">
                          {new Date(milestone.achieved_at).toLocaleDateString()}
                        </span>
                        <Badge variant=\"outline\" className=\"text-xs\">
                          {milestone.milestone.category}
                        </Badge>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className=\"text-center py-8\">
                <Target className=\"h-12 w-12 mx-auto text-gray-400 mb-4\" />
                <p className=\"text-gray-500\">No milestones achieved yet</p>
                <p className=\"text-sm text-gray-400\">Keep learning to unlock your first milestone!</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Learning Path Progress */}
        <Card>
          <CardHeader>
            <CardTitle className=\"flex items-center space-x-2\">
              <TrendingUp className=\"h-5 w-5\" />
              <span>Learning Path Progress</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {paths.length > 0 ? (
              <div className=\"space-y-4\">
                {paths.slice(0, 5).map((path, index) => (
                  <div key={index} className=\"space-y-2\">
                    <div className=\"flex justify-between items-center\">
                      <span className=\"font-medium text-sm truncate\">{path.name}</span>
                      <Badge 
                        variant=\"outline\" 
                        className={
                          path.status === 'completed' ? 'bg-green-100 text-green-700' :
                          path.status === 'in_progress' ? 'bg-blue-100 text-blue-700' :
                          'bg-gray-100 text-gray-700'
                        }
                      >
                        {path.status.replace('_', ' ')}
                      </Badge>
                    </div>
                    <div className=\"flex items-center space-x-2\">
                      <Progress value={path.progress_percentage || 0} className=\"h-2 flex-1\" />
                      <span className=\"text-xs text-gray-600 min-w-0\">
                        {Math.round(path.progress_percentage || 0)}%
                      </span>
                    </div>
                    <div className=\"flex justify-between text-xs text-gray-500\">
                      <span>{path.category}</span>
                      <span>{path.difficulty_level}</span>
                    </div>
                  </div>
                ))}
                
                {paths.length > 5 && (
                  <div className=\"text-center pt-3 border-t\">
                    <button className=\"text-blue-600 hover:text-blue-800 text-sm font-medium\">
                      View all {paths.length} paths
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className=\"text-center py-8\">
                <TrendingUp className=\"h-12 w-12 mx-auto text-gray-400 mb-4\" />
                <p className=\"text-gray-500\">No learning paths started</p>
                <p className=\"text-sm text-gray-400\">Start a learning path to track your progress!</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Progress Statistics */}
      <Card>
        <CardHeader>
          <CardTitle>Progress Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className=\"grid grid-cols-1 md:grid-cols-3 gap-6\">
            {/* Overall Completion Rate */}
            <div className=\"text-center\">
              <div className=\"relative w-24 h-24 mx-auto mb-4\">
                <svg className=\"w-24 h-24 transform -rotate-90\" viewBox=\"0 0 36 36\">
                  <path
                    className=\"text-gray-200\"
                    stroke=\"currentColor\"
                    strokeWidth=\"3\"
                    fill=\"none\"
                    d=\"M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831\"
                  />
                  <path
                    className={getProgressColor(overall_progress.completion_rate || 0)}
                    stroke=\"currentColor\"
                    strokeWidth=\"3\"
                    strokeLinecap=\"round\"
                    fill=\"none\"
                    strokeDasharray={`${(overall_progress.completion_rate || 0)}, 100`}
                    d=\"M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831\"
                  />
                </svg>
                <div className=\"absolute inset-0 flex items-center justify-center\">
                  <span className={`text-lg font-bold ${getProgressColor(overall_progress.completion_rate || 0)}`}>
                    {Math.round(overall_progress.completion_rate || 0)}%
                  </span>
                </div>
              </div>
              <p className=\"text-sm font-medium text-gray-700\">Completion Rate</p>
              <p className=\"text-xs text-gray-500\">
                {overall_progress.completed || 0} of {overall_progress.total || 0} goals
              </p>
            </div>

            {/* Weekly Progress */}
            <div className=\"text-center\">
              <div className=\"w-24 h-24 mx-auto mb-4 bg-blue-100 rounded-full flex items-center justify-center\">
                <Calendar className=\"h-8 w-8 text-blue-600\" />
              </div>
              <p className=\"text-sm font-medium text-gray-700\">This Week</p>
              <p className=\"text-lg font-bold text-blue-600\">
                {recent_milestones.filter(m => {
                  const weekAgo = new Date();
                  weekAgo.setDate(weekAgo.getDate() - 7);
                  return new Date(m.achieved_at) >= weekAgo;
                }).length}
              </p>
              <p className=\"text-xs text-gray-500\">milestones achieved</p>
            </div>

            {/* Average Progress */}
            <div className=\"text-center\">
              <div className=\"w-24 h-24 mx-auto mb-4 bg-purple-100 rounded-full flex items-center justify-center\">
                <TrendingUp className=\"h-8 w-8 text-purple-600\" />
              </div>
              <p className=\"text-sm font-medium text-gray-700\">Average Progress</p>
              <p className=\"text-lg font-bold text-purple-600\">
                {Math.round(overall_progress.percentage || 0)}%
              </p>
              <p className=\"text-xs text-gray-500\">across all goals</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProgressTracker;
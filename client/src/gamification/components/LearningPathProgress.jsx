import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Button } from '../../components/ui/button';
import { Progress } from '../../components/ui/progress';
import { BookOpen, Play, CheckCircle, Clock, Target } from 'lucide-react';

const LearningPathProgress = ({ paths = [], recommendations = [] }) => {
  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed': return 'text-green-600 bg-green-100 border-green-200';
      case 'in_progress': return 'text-blue-600 bg-blue-100 border-blue-200';
      case 'not_started': return 'text-gray-600 bg-gray-100 border-gray-200';
      case 'paused': return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      default: return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed': return CheckCircle;
      case 'in_progress': return Play;
      case 'paused': return Clock;
      default: return BookOpen;
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'beginner': return 'bg-green-100 text-green-700';
      case 'intermediate': return 'bg-yellow-100 text-yellow-700';
      case 'advanced': return 'bg-orange-100 text-orange-700';
      case 'expert': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const formatDuration = (hours) => {
    if (!hours) return 'Unknown';
    if (hours < 1) return `${Math.round(hours * 60)}m`;
    if (hours < 24) return `${Math.round(hours)}h`;
    return `${Math.round(hours / 24)}d`;
  };

  const PathCard = ({ path, isRecommendation = false }) => {
    const StatusIcon = getStatusIcon(path.status);
    const statusColor = getStatusColor(path.status);

    return (
      <Card className=\"hover:shadow-md transition-shadow\">
        <CardContent className=\"p-4\">
          <div className=\"flex items-start justify-between mb-3\">
            <div className=\"flex-1\">
              <h3 className=\"font-semibold text-lg mb-1\">{path.name}</h3>
              <p className=\"text-sm text-gray-600 mb-2\">{path.description}</p>
              
              <div className=\"flex items-center space-x-2 mb-3\">
                <Badge variant=\"outline\" className={getDifficultyColor(path.difficulty_level)}>
                  {path.difficulty_level}
                </Badge>
                <Badge variant=\"outline\">
                  {path.category}
                </Badge>
                {path.estimated_duration && (
                  <Badge variant=\"outline\">
                    {formatDuration(path.estimated_duration)}
                  </Badge>
                )}
              </div>
            </div>
            
            {!isRecommendation && (
              <div className={`p-2 rounded-lg ${statusColor}`}>
                <StatusIcon className=\"h-5 w-5\" />
              </div>
            )}
          </div>

          {/* Progress Section */}
          {!isRecommendation ? (
            <div className=\"space-y-3\">
              <div className=\"flex justify-between items-center text-sm\">
                <span className=\"text-gray-600\">Progress</span>
                <span className=\"font-medium\">{Math.round(path.progress_percentage || 0)}%</span>
              </div>
              <Progress value={path.progress_percentage || 0} className=\"h-2\" />
              
              {path.current_node && (
                <div className=\"bg-blue-50 p-3 rounded-lg border border-blue-200\">
                  <p className=\"text-sm font-medium text-blue-800\">Current: {path.current_node.name}</p>
                  <p className=\"text-xs text-blue-600\">{path.current_node.description}</p>
                </div>
              )}
              
              <div className=\"flex justify-between items-center text-xs text-gray-500\">
                <span>Started: {path.started_at ? new Date(path.started_at).toLocaleDateString() : 'Not started'}</span>
                {path.estimated_completion && (
                  <span>Est. completion: {new Date(path.estimated_completion).toLocaleDateString()}</span>
                )}
              </div>
            </div>
          ) : (
            <div className=\"space-y-3\">
              {/* Skills Covered */}
              {path.skills_covered && path.skills_covered.length > 0 && (
                <div>
                  <p className=\"text-sm font-medium text-gray-700 mb-2\">Skills you'll learn:</p>
                  <div className=\"flex flex-wrap gap-1\">
                    {path.skills_covered.slice(0, 3).map((skill, index) => (
                      <Badge key={index} variant=\"secondary\" className=\"text-xs\">
                        {skill}
                      </Badge>
                    ))}
                    {path.skills_covered.length > 3 && (
                      <Badge variant=\"secondary\" className=\"text-xs\">
                        +{path.skills_covered.length - 3} more
                      </Badge>
                    )}
                  </div>
                </div>
              )}
              
              {/* Relevance Score */}
              {path.relevance_score && (
                <div className=\"flex items-center justify-between text-sm\">
                  <span className=\"text-gray-600\">Match</span>
                  <Badge variant=\"outline\" className=\"bg-green-50 text-green-700\">
                    {Math.round(path.relevance_score * 100)}%
                  </Badge>
                </div>
              )}
              
              {path.recommendation_reason && (
                <p className=\"text-xs text-gray-600 italic\">{path.recommendation_reason}</p>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div className=\"flex space-x-2 mt-4\">
            {isRecommendation ? (
              <Button size=\"sm\" className=\"flex-1\">
                Start Learning
              </Button>
            ) : (
              <>
                {path.status === 'not_started' && (
                  <Button size=\"sm\" className=\"flex-1\">
                    <Play className=\"h-4 w-4 mr-1\" />
                    Start
                  </Button>
                )}
                {path.status === 'in_progress' && (
                  <Button size=\"sm\" className=\"flex-1\">
                    Continue
                  </Button>
                )}
                {path.status === 'paused' && (
                  <Button size=\"sm\" className=\"flex-1\">
                    Resume
                  </Button>
                )}
                {path.status === 'completed' && (
                  <Button size=\"sm\" variant=\"outline\" className=\"flex-1\">
                    Review
                  </Button>
                )}
              </>
            )}
            <Button size=\"sm\" variant=\"outline\">
              Details
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className=\"space-y-6\">
      {/* Active Paths */}
      {paths.length > 0 && (
        <div>
          <h2 className=\"text-xl font-semibold mb-4 flex items-center space-x-2\">
            <BookOpen className=\"h-5 w-5\" />
            <span>Your Learning Paths</span>
          </h2>
          <div className=\"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4\">
            {paths.map((path, index) => (
              <PathCard key={path.id || index} path={path} />
            ))}
          </div>
        </div>
      )}

      {/* Recommended Paths */}
      {recommendations.length > 0 && (
        <div>
          <h2 className=\"text-xl font-semibold mb-4 flex items-center space-x-2\">
            <Target className=\"h-5 w-5\" />
            <span>Recommended for You</span>
          </h2>
          <div className=\"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4\">
            {recommendations.map((path, index) => (
              <PathCard key={path.id || index} path={path} isRecommendation={true} />
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {paths.length === 0 && recommendations.length === 0 && (
        <Card>
          <CardContent className=\"p-8 text-center\">
            <BookOpen className=\"h-12 w-12 mx-auto text-gray-400 mb-4\" />
            <h3 className=\"text-lg font-semibold text-gray-600 mb-2\">
              No Learning Paths Yet
            </h3>
            <p className=\"text-gray-500 mb-4\">
              Start your learning journey by exploring available paths or creating a custom one.
            </p>
            <div className=\"space-x-3\">
              <Button>Browse Paths</Button>
              <Button variant=\"outline\">Create Custom Path</Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default LearningPathProgress;
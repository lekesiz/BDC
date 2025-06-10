import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Trophy, Star, Target, Users, BookOpen, TrendingUp, Zap, Award } from 'lucide-react';
import XPProgressBar from './components/XPProgressBar';
import LevelDisplay from './components/LevelDisplay';
import BadgeShowcase from './components/BadgeShowcase';
import AchievementsList from './components/AchievementsList';
import LeaderboardWidget from './components/LeaderboardWidget';
import SocialFeed from './components/SocialFeed';
import LearningPathProgress from './components/LearningPathProgress';
import ProgressTracker from './components/ProgressTracker';

const GamificationDashboard = ({ userId }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchGamificationData();
  }, [userId]);

  const fetchGamificationData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/gamification/dashboard/${userId}`);
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error('Error fetching gamification data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className=\"flex items-center justify-center h-64\">
        <div className=\"animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600\"></div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className=\"text-center py-8\">
        <p className=\"text-gray-500\">Failed to load gamification data</p>
      </div>
    );
  }

  const { summary, recommendations, social, leaderboards, quick_stats } = dashboardData;

  return (
    <div className=\"max-w-7xl mx-auto p-6 space-y-6\">
      {/* Header Section */}
      <div className=\"bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-6\">
        <div className=\"flex items-center justify-between\">
          <div>
            <h1 className=\"text-3xl font-bold mb-2\">Gamification Dashboard</h1>
            <p className=\"text-blue-100\">Track your learning journey and achievements</p>
          </div>
          <div className=\"text-right\">
            <div className=\"text-2xl font-bold\">{summary?.overall_score || 0}%</div>
            <div className=\"text-sm text-blue-100\">Overall Score</div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className=\"grid grid-cols-1 md:grid-cols-4 gap-4\">
        <Card>
          <CardContent className=\"p-4\">
            <div className=\"flex items-center space-x-3\">
              <div className=\"p-2 bg-yellow-100 rounded-lg\">
                <Zap className=\"h-5 w-5 text-yellow-600\" />
              </div>
              <div>
                <p className=\"text-sm text-gray-600\">Total XP</p>
                <p className=\"text-2xl font-bold\">{summary?.xp?.total?.toLocaleString() || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className=\"p-4\">
            <div className=\"flex items-center space-x-3\">
              <div className=\"p-2 bg-blue-100 rounded-lg\">
                <Star className=\"h-5 w-5 text-blue-600\" />
              </div>
              <div>
                <p className=\"text-sm text-gray-600\">Level</p>
                <p className=\"text-2xl font-bold\">{summary?.level?.current || 1}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className=\"p-4\">
            <div className=\"flex items-center space-x-3\">
              <div className=\"p-2 bg-purple-100 rounded-lg\">
                <Award className=\"h-5 w-5 text-purple-600\" />
              </div>
              <div>
                <p className=\"text-sm text-gray-600\">Badges</p>
                <p className=\"text-2xl font-bold\">{summary?.badges?.total_count || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className=\"p-4\">
            <div className=\"flex items-center space-x-3\">
              <div className=\"p-2 bg-green-100 rounded-lg\">
                <Trophy className=\"h-5 w-5 text-green-600\" />
              </div>
              <div>
                <p className=\"text-sm text-gray-600\">Achievements</p>
                <p className=\"text-2xl font-bold\">{summary?.achievements?.total_count || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className=\"w-full\">
        <TabsList className=\"grid w-full grid-cols-6\">
          <TabsTrigger value=\"overview\">Overview</TabsTrigger>
          <TabsTrigger value=\"progress\">Progress</TabsTrigger>
          <TabsTrigger value=\"achievements\">Achievements</TabsTrigger>
          <TabsTrigger value=\"social\">Social</TabsTrigger>
          <TabsTrigger value=\"leaderboards\">Leaderboards</TabsTrigger>
          <TabsTrigger value=\"learning\">Learning Paths</TabsTrigger>
        </TabsList>

        <TabsContent value=\"overview\" className=\"mt-6\">
          <div className=\"grid grid-cols-1 lg:grid-cols-3 gap-6\">
            {/* Left Column */}
            <div className=\"lg:col-span-2 space-y-6\">
              {/* XP and Level Progress */}
              <Card>
                <CardHeader>
                  <CardTitle className=\"flex items-center space-x-2\">
                    <Zap className=\"h-5 w-5\" />
                    <span>Experience & Level Progress</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className=\"space-y-4\">
                    <XPProgressBar 
                      currentXP={summary?.xp?.total || 0}
                      weeklyXP={summary?.xp?.this_week || 0}
                      todayXP={summary?.xp?.today || 0}
                    />
                    <LevelDisplay 
                      level={summary?.level || {}}
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Recent Activity */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className=\"space-y-3\">
                    {summary?.progress?.recent_milestones?.map((milestone, index) => (
                      <div key={index} className=\"flex items-center space-x-3 p-3 bg-gray-50 rounded-lg\">
                        <Trophy className=\"h-5 w-5 text-yellow-600\" />
                        <div className=\"flex-1\">
                          <p className=\"font-medium\">{milestone.milestone.name}</p>
                          <p className=\"text-sm text-gray-600\">{milestone.milestone.description}</p>
                        </div>
                        <Badge variant=\"secondary\">
                          {new Date(milestone.achieved_at).toLocaleDateString()}
                        </Badge>
                      </div>
                    )) || (
                      <p className=\"text-gray-500 text-center py-4\">No recent activity</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Right Column */}
            <div className=\"space-y-6\">
              {/* Badge Showcase */}
              <Card>
                <CardHeader>
                  <CardTitle className=\"flex items-center space-x-2\">
                    <Award className=\"h-5 w-5\" />
                    <span>Badge Showcase</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <BadgeShowcase badges={summary?.badges?.showcase || []} />
                </CardContent>
              </Card>

              {/* Quick Leaderboard */}
              <Card>
                <CardHeader>
                  <CardTitle className=\"flex items-center space-x-2\">
                    <TrendingUp className=\"h-5 w-5\" />
                    <span>Your Rankings</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className=\"space-y-2\">
                    {Object.entries(summary?.rankings || {}).map(([type, ranking]) => (
                      <div key={type} className=\"flex justify-between items-center p-2 bg-gray-50 rounded\">
                        <span className=\"text-sm font-medium capitalize\">{type}</span>
                        <Badge variant=\"outline\">#{ranking.rank}</Badge>
                      </div>
                    )) || (
                      <p className=\"text-gray-500 text-center py-4\">No rankings available</p>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Recommendations */}
              <Card>
                <CardHeader>
                  <CardTitle className=\"flex items-center space-x-2\">
                    <Target className=\"h-5 w-5\" />
                    <span>Recommendations</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className=\"space-y-3\">
                    {recommendations?.achievements?.slice(0, 3).map((achievement, index) => (
                      <div key={index} className=\"p-3 border rounded-lg hover:bg-gray-50 cursor-pointer\">
                        <p className=\"font-medium text-sm\">{achievement.name}</p>
                        <p className=\"text-xs text-gray-600\">{achievement.description}</p>
                        <div className=\"mt-2\">
                          <Progress value={achievement.progress?.percentage || 0} className=\"h-2\" />
                        </div>
                      </div>
                    )) || (
                      <p className=\"text-gray-500 text-center py-4\">No recommendations</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value=\"progress\" className=\"mt-6\">
          <ProgressTracker 
            progressData={summary?.progress}
            learningPaths={summary?.learning_paths}
          />
        </TabsContent>

        <TabsContent value=\"achievements\" className=\"mt-6\">
          <AchievementsList 
            achievements={summary?.achievements}
            recommendations={recommendations?.achievements}
          />
        </TabsContent>

        <TabsContent value=\"social\" className=\"mt-6\">
          <div className=\"grid grid-cols-1 lg:grid-cols-3 gap-6\">
            <div className=\"lg:col-span-2\">
              <SocialFeed feed={social?.feed || []} />
            </div>
            <div className=\"space-y-6\">
              <Card>
                <CardHeader>
                  <CardTitle className=\"flex items-center space-x-2\">
                    <Users className=\"h-5 w-5\" />
                    <span>Your Teams</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className=\"space-y-3\">
                    {summary?.social?.teams?.map((team, index) => (
                      <div key={index} className=\"p-3 border rounded-lg\">
                        <p className=\"font-medium\">{team.name}</p>
                        <p className=\"text-sm text-gray-600\">{team.member_count} members</p>
                        <Badge variant=\"secondary\" className=\"mt-2\">{team.user_role}</Badge>
                      </div>
                    )) || (
                      <p className=\"text-gray-500 text-center py-4\">No teams joined</p>
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Active Competitions</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className=\"space-y-3\">
                    {social?.competitions?.map((competition, index) => (
                      <div key={index} className=\"p-3 border rounded-lg\">
                        <p className=\"font-medium\">{competition.name}</p>
                        <p className=\"text-sm text-gray-600\">{competition.description}</p>
                        <div className=\"flex justify-between items-center mt-2\">
                          <Badge variant=\"outline\">{competition.type}</Badge>
                          <Button size=\"sm\">Join</Button>
                        </div>
                      </div>
                    )) || (
                      <p className=\"text-gray-500 text-center py-4\">No active competitions</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value=\"leaderboards\" className=\"mt-6\">
          <div className=\"grid grid-cols-1 lg:grid-cols-2 gap-6\">
            {Object.entries(leaderboards || {}).map(([type, leaderboard]) => (
              <LeaderboardWidget 
                key={type}
                title={type.charAt(0).toUpperCase() + type.slice(1).replace('_', ' ')}
                data={leaderboard}
                userRank={summary?.rankings?.[type]?.rank}
              />
            ))}
          </div>
        </TabsContent>

        <TabsContent value=\"learning\" className=\"mt-6\">
          <div className=\"space-y-6\">
            <div className=\"grid grid-cols-1 lg:grid-cols-3 gap-6\">
              <Card>
                <CardContent className=\"p-6 text-center\">
                  <BookOpen className=\"h-12 w-12 mx-auto text-blue-600 mb-4\" />
                  <h3 className=\"text-lg font-semibold mb-2\">Active Paths</h3>
                  <p className=\"text-3xl font-bold text-blue-600\">
                    {summary?.learning_paths?.active_count || 0}
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className=\"p-6 text-center\">
                  <Trophy className=\"h-12 w-12 mx-auto text-green-600 mb-4\" />
                  <h3 className=\"text-lg font-semibold mb-2\">Completed</h3>
                  <p className=\"text-3xl font-bold text-green-600\">
                    {summary?.learning_paths?.completed_count || 0}
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className=\"p-6 text-center\">
                  <Target className=\"h-12 w-12 mx-auto text-purple-600 mb-4\" />
                  <h3 className=\"text-lg font-semibold mb-2\">Recommended</h3>
                  <p className=\"text-3xl font-bold text-purple-600\">
                    {recommendations?.learning_paths?.length || 0}
                  </p>
                </CardContent>
              </Card>
            </div>

            <LearningPathProgress 
              paths={summary?.learning_paths?.paths || []}
              recommendations={recommendations?.learning_paths || []}
            />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default GamificationDashboard;
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Button } from '../../components/ui/button';
import { Progress } from '../../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Trophy, Target, Clock, Star, Lock, CheckCircle, AlertCircle } from 'lucide-react';

const AchievementsList = ({ achievements = {}, recommendations = [] }) => {
  const [activeTab, setActiveTab] = useState('earned');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const earnedAchievements = achievements.recent || [];
  const totalEarned = achievements.total_count || 0;

  const getCategoryIcon = (category) => {
    switch (category?.toLowerCase()) {
      case 'completion': return CheckCircle;
      case 'performance': return Star;
      case 'streak': return Target;
      case 'social': return Trophy;
      case 'milestone': return AlertCircle;
      default: return Trophy;
    }
  };

  const getAchievementColor = (category) => {
    switch (category?.toLowerCase()) {
      case 'completion': return 'text-green-600 bg-green-100';
      case 'performance': return 'text-blue-600 bg-blue-100';
      case 'streak': return 'text-orange-600 bg-orange-100';
      case 'social': return 'text-purple-600 bg-purple-100';
      case 'milestone': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const AchievementCard = ({ achievement, isEarned = false, progress = null }) => {
    const achievementData = achievement.achievement || achievement;
    const Icon = getCategoryIcon(achievementData.category);
    const colorClass = getAchievementColor(achievementData.category);

    return (
      <Card className={`transition-all duration-200 hover:shadow-md ${isEarned ? 'border-green-200' : 'border-gray-200'}`}>
        <CardContent className=\"p-4\">
          <div className=\"flex items-start space-x-3\">
            <div className={`p-2 rounded-lg ${colorClass}`}>
              <Icon className=\"h-5 w-5\" />
            </div>
            
            <div className=\"flex-1 min-w-0\">
              <div className=\"flex items-center justify-between mb-2\">
                <h3 className=\"font-semibold text-lg truncate\">{achievementData.name}</h3>
                {isEarned && (
                  <Badge variant=\"outline\" className=\"bg-green-50 text-green-700 border-green-200\">
                    Earned
                  </Badge>
                )}
              </div>
              
              <p className=\"text-gray-600 text-sm mb-3\">{achievementData.description}</p>
              
              <div className=\"space-y-2\">
                <div className=\"flex justify-between items-center text-sm\">
                  <span className=\"text-gray-500\">Category:</span>
                  <Badge variant=\"secondary\" className=\"capitalize\">
                    {achievementData.category}
                  </Badge>
                </div>
                
                <div className=\"flex justify-between items-center text-sm\">
                  <span className=\"text-gray-500\">Points:</span>
                  <span className=\"font-semibold text-blue-600\">
                    {achievementData.points || 0} XP
                  </span>
                </div>
                
                {achievement.earned_at && (
                  <div className=\"flex justify-between items-center text-sm\">
                    <span className=\"text-gray-500\">Earned:</span>
                    <span className=\"text-green-600\">
                      {new Date(achievement.earned_at).toLocaleDateString()}
                    </span>
                  </div>
                )}
                
                {progress && !isEarned && (
                  <div className=\"space-y-1\">
                    <div className=\"flex justify-between items-center text-sm\">
                      <span className=\"text-gray-500\">Progress:</span>
                      <span className=\"font-medium\">{Math.round(progress.percentage)}%</span>
                    </div>
                    <Progress value={progress.percentage} className=\"h-2\" />
                    {progress.description && (
                      <p className=\"text-xs text-gray-500\">{progress.description}</p>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  const categories = ['all', 'completion', 'performance', 'streak', 'social', 'milestone'];

  const filterAchievementsByCategory = (achievementsList) => {
    if (selectedCategory === 'all') return achievementsList;
    return achievementsList.filter(achievement => 
      (achievement.achievement?.category || achievement.category) === selectedCategory
    );
  };

  return (
    <div className=\"space-y-6\">
      {/* Header Stats */}
      <div className=\"grid grid-cols-1 md:grid-cols-3 gap-4\">
        <Card>
          <CardContent className=\"p-4 text-center\">
            <Trophy className=\"h-8 w-8 mx-auto text-yellow-600 mb-2\" />
            <div className=\"text-2xl font-bold text-yellow-600\">{totalEarned}</div>
            <div className=\"text-sm text-gray-600\">Total Earned</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className=\"p-4 text-center\">
            <Target className=\"h-8 w-8 mx-auto text-blue-600 mb-2\" />
            <div className=\"text-2xl font-bold text-blue-600\">{recommendations.length}</div>
            <div className=\"text-sm text-gray-600\">Available</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className=\"p-4 text-center\">
            <Clock className=\"h-8 w-8 mx-auto text-green-600 mb-2\" />
            <div className=\"text-2xl font-bold text-green-600\">
              {earnedAchievements.filter(a => {
                const earnedDate = new Date(a.earned_at);
                const weekAgo = new Date();
                weekAgo.setDate(weekAgo.getDate() - 7);
                return earnedDate >= weekAgo;
              }).length}
            </div>
            <div className=\"text-sm text-gray-600\">This Week</div>
          </CardContent>
        </Card>
      </div>

      {/* Category Filter */}
      <div className=\"flex flex-wrap gap-2\">
        {categories.map(category => (
          <Button
            key={category}
            variant={selectedCategory === category ? 'default' : 'outline'}
            size=\"sm\"
            onClick={() => setSelectedCategory(category)}
            className=\"capitalize\"
          >
            {category}
          </Button>
        ))}
      </div>

      {/* Achievements Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className=\"grid w-full grid-cols-2\">
          <TabsTrigger value=\"earned\" className=\"flex items-center space-x-2\">
            <CheckCircle className=\"h-4 w-4\" />
            <span>Earned ({totalEarned})</span>
          </TabsTrigger>
          <TabsTrigger value=\"available\" className=\"flex items-center space-x-2\">
            <Lock className=\"h-4 w-4\" />
            <span>Available ({recommendations.length})</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value=\"earned\" className=\"mt-6\">
          <div className=\"space-y-4\">
            {filterAchievementsByCategory(earnedAchievements).length > 0 ? (
              filterAchievementsByCategory(earnedAchievements).map((achievement, index) => (
                <AchievementCard 
                  key={index} 
                  achievement={achievement} 
                  isEarned={true}
                />
              ))
            ) : (
              <Card>
                <CardContent className=\"p-8 text-center\">
                  <Trophy className=\"h-12 w-12 mx-auto text-gray-400 mb-4\" />
                  <h3 className=\"text-lg font-semibold text-gray-600 mb-2\">
                    No achievements earned yet
                  </h3>
                  <p className=\"text-gray-500 mb-4\">
                    Complete activities and reach milestones to earn your first achievement!
                  </p>
                  <Button onClick={() => setActiveTab('available')}>
                    View Available Achievements
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value=\"available\" className=\"mt-6\">
          <div className=\"space-y-4\">
            {filterAchievementsByCategory(recommendations).length > 0 ? (
              filterAchievementsByCategory(recommendations).map((achievement, index) => (
                <AchievementCard 
                  key={index} 
                  achievement={achievement} 
                  isEarned={false}
                  progress={achievement.progress}
                />
              ))
            ) : (
              <Card>
                <CardContent className=\"p-8 text-center\">
                  <Target className=\"h-12 w-12 mx-auto text-gray-400 mb-4\" />
                  <h3 className=\"text-lg font-semibold text-gray-600 mb-2\">
                    No available achievements
                  </h3>
                  <p className=\"text-gray-500 mb-4\">
                    {selectedCategory === 'all' 
                      ? \"You've earned all available achievements in this category!\"
                      : `No achievements available in the ${selectedCategory} category.`
                    }
                  </p>
                  {selectedCategory !== 'all' && (
                    <Button onClick={() => setSelectedCategory('all')}>
                      View All Categories
                    </Button>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>
      </Tabs>

      {/* Achievement Progress Summary */}
      {recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className=\"flex items-center space-x-2\">
              <Target className=\"h-5 w-5\" />
              <span>Next Achievements</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className=\"space-y-3\">
              {recommendations.slice(0, 3).map((achievement, index) => (
                <div key={index} className=\"flex items-center space-x-3 p-3 bg-gray-50 rounded-lg\">
                  <div className={`p-2 rounded ${getAchievementColor(achievement.category)}`}>
                    {getCategoryIcon(achievement.category)({ className: \"h-4 w-4\" })}
                  </div>
                  <div className=\"flex-1\">
                    <p className=\"font-medium text-sm\">{achievement.name}</p>
                    <div className=\"flex items-center space-x-2 mt-1\">
                      <Progress 
                        value={achievement.progress?.percentage || 0} 
                        className=\"h-2 flex-1\" 
                      />
                      <span className=\"text-xs text-gray-600\">
                        {Math.round(achievement.progress?.percentage || 0)}%
                      </span>
                    </div>
                  </div>
                  <Badge variant=\"outline\" className=\"text-xs\">
                    {achievement.points || 0} XP
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AchievementsList;
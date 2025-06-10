import React from 'react';
import { Progress } from '../../components/ui/progress';
import { Card, CardContent } from '../../components/ui/card';
import { Zap, Calendar, Clock } from 'lucide-react';

const XPProgressBar = ({ currentXP, weeklyXP, todayXP }) => {
  const formatXP = (xp) => {
    if (xp >= 1000000) {
      return `${(xp / 1000000).toFixed(1)}M`;
    } else if (xp >= 1000) {
      return `${(xp / 1000).toFixed(1)}K`;
    }
    return xp.toString();
  };

  const getXPColor = (xp) => {
    if (xp >= 1000) return 'text-purple-600';
    if (xp >= 500) return 'text-blue-600';
    if (xp >= 100) return 'text-green-600';
    return 'text-gray-600';
  };

  const getProgressColor = (xp) => {
    if (xp >= 1000) return 'bg-purple-600';
    if (xp >= 500) return 'bg-blue-600';
    if (xp >= 100) return 'bg-green-600';
    return 'bg-gray-400';
  };

  return (
    <div className=\"space-y-4\">
      {/* Main XP Display */}
      <div className=\"text-center\">
        <div className=\"flex items-center justify-center space-x-2 mb-2\">
          <Zap className={`h-6 w-6 ${getXPColor(currentXP)}`} />
          <span className={`text-3xl font-bold ${getXPColor(currentXP)}`}>
            {formatXP(currentXP)}
          </span>
          <span className=\"text-lg text-gray-500\">XP</span>
        </div>
        <p className=\"text-sm text-gray-600\">Total Experience Points</p>
      </div>

      {/* XP Breakdown */}
      <div className=\"grid grid-cols-2 gap-4\">
        <Card className=\"border-l-4 border-l-blue-500\">
          <CardContent className=\"p-4\">
            <div className=\"flex items-center space-x-2\">
              <Calendar className=\"h-4 w-4 text-blue-600\" />
              <div>
                <p className=\"text-sm text-gray-600\">This Week</p>
                <p className=\"text-xl font-bold text-blue-600\">{formatXP(weeklyXP)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className=\"border-l-4 border-l-green-500\">
          <CardContent className=\"p-4\">
            <div className=\"flex items-center space-x-2\">
              <Clock className=\"h-4 w-4 text-green-600\" />
              <div>
                <p className=\"text-sm text-gray-600\">Today</p>
                <p className=\"text-xl font-bold text-green-600\">{formatXP(todayXP)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Weekly Progress Visualization */}
      <div className=\"space-y-2\">
        <div className=\"flex justify-between items-center\">
          <span className=\"text-sm font-medium\">Weekly Progress</span>
          <span className=\"text-sm text-gray-600\">{formatXP(weeklyXP)} / 2000 XP</span>
        </div>
        <div className=\"relative\">
          <Progress 
            value={Math.min((weeklyXP / 2000) * 100, 100)} 
            className=\"h-3\"
          />
          <div className=\"absolute inset-0 flex items-center justify-center\">
            <span className=\"text-xs font-medium text-white drop-shadow-lg\">
              {Math.round((weeklyXP / 2000) * 100)}%
            </span>
          </div>
        </div>
      </div>

      {/* XP Milestones */}
      <div className=\"flex justify-between text-xs text-gray-500\">
        <div className=\"text-center\">
          <div className={`w-2 h-2 rounded-full ${currentXP >= 100 ? 'bg-green-500' : 'bg-gray-300'} mx-auto mb-1`}></div>
          <span>100</span>
        </div>
        <div className=\"text-center\">
          <div className={`w-2 h-2 rounded-full ${currentXP >= 500 ? 'bg-blue-500' : 'bg-gray-300'} mx-auto mb-1`}></div>
          <span>500</span>
        </div>
        <div className=\"text-center\">
          <div className={`w-2 h-2 rounded-full ${currentXP >= 1000 ? 'bg-purple-500' : 'bg-gray-300'} mx-auto mb-1`}></div>
          <span>1K</span>
        </div>
        <div className=\"text-center\">
          <div className={`w-2 h-2 rounded-full ${currentXP >= 5000 ? 'bg-yellow-500' : 'bg-gray-300'} mx-auto mb-1`}></div>
          <span>5K</span>
        </div>
        <div className=\"text-center\">
          <div className={`w-2 h-2 rounded-full ${currentXP >= 10000 ? 'bg-red-500' : 'bg-gray-300'} mx-auto mb-1`}></div>
          <span>10K</span>
        </div>
      </div>
    </div>
  );
};

export default XPProgressBar;
import React from 'react';
import { Progress } from '../../components/ui/progress';
import { Badge } from '../../components/ui/badge';
import { Crown, Star, ArrowUp } from 'lucide-react';

const LevelDisplay = ({ level = {} }) => {
  const {
    current = 1,
    progress_percentage = 0,
    title = { title: 'Beginner', description: 'Just starting out' },
    next_title = { title: 'Novice', description: 'Learning the basics' },
    xp_needed_for_next = 0
  } = level;

  const getLevelColor = (lvl) => {
    if (lvl >= 50) return 'from-purple-500 to-pink-500';
    if (lvl >= 30) return 'from-blue-500 to-purple-500';
    if (lvl >= 20) return 'from-green-500 to-blue-500';
    if (lvl >= 10) return 'from-yellow-500 to-green-500';
    return 'from-gray-400 to-gray-500';
  };

  const getLevelIcon = (lvl) => {
    if (lvl >= 50) return Crown;
    if (lvl >= 20) return Star;
    return ArrowUp;
  };

  const Icon = getLevelIcon(current);

  return (
    <div className=\"space-y-4\">
      {/* Level Display */}
      <div className=\"text-center\">
        <div className={`inline-flex items-center justify-center w-24 h-24 rounded-full bg-gradient-to-br ${getLevelColor(current)} text-white mb-4 shadow-lg`}>
          <div className=\"text-center\">
            <Icon className=\"h-6 w-6 mx-auto mb-1\" />
            <div className=\"text-xl font-bold\">{current}</div>
          </div>
        </div>
        
        <div className=\"space-y-1\">
          <h3 className=\"text-xl font-bold\">{title.title}</h3>
          <p className=\"text-sm text-gray-600\">{title.description}</p>
        </div>
      </div>

      {/* Progress to Next Level */}
      <div className=\"space-y-3\">
        <div className=\"flex justify-between items-center\">
          <span className=\"text-sm font-medium\">Progress to Level {current + 1}</span>
          <Badge variant=\"outline\">{Math.round(progress_percentage)}%</Badge>
        </div>
        
        <div className=\"relative\">
          <Progress value={progress_percentage} className=\"h-4\" />
          <div className=\"absolute inset-0 flex items-center justify-center\">
            <span className=\"text-xs font-medium text-white drop-shadow-lg\">
              {Math.round(progress_percentage)}%
            </span>
          </div>
        </div>
        
        <div className=\"flex justify-between text-xs text-gray-500\">
          <span>Current: {title.title}</span>
          <span>Next: {next_title?.title || 'Max Level'}</span>
        </div>
        
        {xp_needed_for_next > 0 && (
          <p className=\"text-center text-sm text-gray-600\">
            {xp_needed_for_next.toLocaleString()} XP needed for next level
          </p>
        )}
      </div>

      {/* Level Milestones */}
      <div className=\"grid grid-cols-5 gap-2 pt-4\">
        {[1, 5, 10, 25, 50].map((milestone) => (
          <div key={milestone} className=\"text-center\">
            <div 
              className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold mb-1 ${
                current >= milestone 
                  ? 'bg-gradient-to-br from-green-400 to-green-600 text-white shadow-lg' 
                  : 'bg-gray-200 text-gray-500'
              }`}
            >
              {milestone}
            </div>
            <div className={`text-xs ${current >= milestone ? 'text-green-600' : 'text-gray-400'}`}>
              {milestone === 1 && 'Start'}
              {milestone === 5 && 'Novice'}
              {milestone === 10 && 'Student'}
              {milestone === 25 && 'Expert'}
              {milestone === 50 && 'Master'}
            </div>
          </div>
        ))}
      </div>

      {/* Next Level Rewards Preview */}
      {next_title && (
        <div className=\"bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg border\">
          <div className=\"flex items-center space-x-3\">
            <div className=\"flex-shrink-0\">
              <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${getLevelColor(current + 1)} flex items-center justify-center text-white`}>
                <Crown className=\"h-5 w-5\" />
              </div>
            </div>
            <div className=\"flex-1\">
              <h4 className=\"font-semibold text-gray-900\">Level {current + 1}: {next_title.title}</h4>
              <p className=\"text-sm text-gray-600\">{next_title.description}</p>
            </div>
            <Badge variant=\"secondary\">Next</Badge>
          </div>
        </div>
      )}
    </div>
  );
};

export default LevelDisplay;
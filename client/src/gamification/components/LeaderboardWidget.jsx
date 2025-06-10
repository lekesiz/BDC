import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Avatar } from '../../components/ui/avatar';
import { Trophy, Medal, Award, Crown } from 'lucide-react';

const LeaderboardWidget = ({ title, data = [], userRank = null }) => {
  const getRankIcon = (rank) => {
    switch (rank) {
      case 1: return <Crown className=\"h-5 w-5 text-yellow-500\" />;
      case 2: return <Medal className=\"h-5 w-5 text-gray-400\" />;
      case 3: return <Award className=\"h-5 w-5 text-amber-600\" />;
      default: return <Trophy className=\"h-4 w-4 text-gray-500\" />;
    }
  };

  const getRankColor = (rank) => {
    switch (rank) {
      case 1: return 'bg-gradient-to-r from-yellow-100 to-yellow-200 border-yellow-300';
      case 2: return 'bg-gradient-to-r from-gray-100 to-gray-200 border-gray-300';
      case 3: return 'bg-gradient-to-r from-amber-100 to-amber-200 border-amber-300';
      default: return 'bg-gray-50 border-gray-200';
    }
  };

  const formatScore = (score) => {
    if (typeof score !== 'number') return score;
    
    if (score >= 1000000) {
      return `${(score / 1000000).toFixed(1)}M`;
    } else if (score >= 1000) {
      return `${(score / 1000).toFixed(1)}K`;
    }
    return score.toLocaleString();
  };

  return (
    <Card>
      <CardHeader className=\"pb-3\">
        <CardTitle className=\"text-lg flex items-center space-x-2\">
          <Trophy className=\"h-5 w-5 text-yellow-600\" />
          <span>{title}</span>
        </CardTitle>
      </CardHeader>
      <CardContent className=\"space-y-2\">
        {data.length === 0 ? (
          <div className=\"text-center py-8\">
            <Trophy className=\"h-8 w-8 mx-auto text-gray-400 mb-2\" />
            <p className=\"text-gray-500 text-sm\">No leaderboard data available</p>
          </div>
        ) : (
          <>
            {data.map((entry, index) => (
              <div 
                key={entry.user_id || index}
                className={`
                  flex items-center space-x-3 p-3 rounded-lg border transition-all duration-200
                  ${getRankColor(entry.rank)}
                  ${userRank === entry.rank ? 'ring-2 ring-blue-500 ring-opacity-50' : ''}
                  hover:shadow-md
                `}
              >
                <div className=\"flex items-center space-x-2\">
                  {getRankIcon(entry.rank)}
                  <span className={`
                    font-bold text-sm
                    ${entry.rank <= 3 ? 'text-gray-800' : 'text-gray-600'}
                  `}>
                    #{entry.rank}
                  </span>
                </div>

                <div className=\"flex-1 min-w-0\">
                  <div className=\"flex items-center space-x-2\">
                    {entry.avatar_url ? (
                      <img 
                        src={entry.avatar_url} 
                        alt={entry.display_name}
                        className=\"w-6 h-6 rounded-full\"
                      />
                    ) : (
                      <div className=\"w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center text-white text-xs font-bold\">
                        {(entry.display_name || entry.username || 'U').charAt(0).toUpperCase()}
                      </div>
                    )}
                    <span className=\"font-medium text-sm truncate\">
                      {entry.display_name || entry.username || 'Unknown User'}
                    </span>
                  </div>
                </div>

                <div className=\"text-right\">
                  <div className={`
                    font-bold
                    ${entry.rank === 1 ? 'text-yellow-600' : 
                      entry.rank === 2 ? 'text-gray-600' :
                      entry.rank === 3 ? 'text-amber-600' : 'text-gray-700'}
                  `}>
                    {formatScore(entry.score || entry.xp)}
                  </div>
                  {entry.title && (
                    <Badge variant=\"outline\" className=\"text-xs mt-1\">
                      {entry.title.title || entry.title}
                    </Badge>
                  )}
                </div>
              </div>
            ))}

            {userRank && userRank > data.length && (
              <div className=\"border-t pt-3 mt-4\">
                <div className=\"flex items-center justify-between p-3 bg-blue-50 border border-blue-200 rounded-lg\">
                  <div className=\"flex items-center space-x-2\">
                    <Trophy className=\"h-4 w-4 text-blue-600\" />
                    <span className=\"font-medium text-blue-800\">Your Rank</span>
                  </div>
                  <Badge variant=\"outline\" className=\"bg-blue-100 text-blue-800 border-blue-300\">
                    #{userRank}
                  </Badge>
                </div>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default LeaderboardWidget;
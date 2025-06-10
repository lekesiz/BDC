import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Button } from '../../components/ui/button';
import { Heart, MessageCircle, Share, Trophy, Star, Target, Users } from 'lucide-react';

const SocialFeed = ({ feed = [] }) => {
  const [reactions, setReactions] = useState({});

  const getShareIcon = (shareType) => {
    switch (shareType?.toLowerCase()) {
      case 'achievement': return Trophy;
      case 'badge': return Star;
      case 'milestone': return Target;
      case 'level_up': return Star;
      case 'evaluation_result': return Star;
      case 'progress': return Target;
      default: return Users;
    }
  };

  const getShareColor = (shareType) => {
    switch (shareType?.toLowerCase()) {
      case 'achievement': return 'text-yellow-600 bg-yellow-100';
      case 'badge': return 'text-purple-600 bg-purple-100';
      case 'milestone': return 'text-green-600 bg-green-100';
      case 'level_up': return 'text-blue-600 bg-blue-100';
      case 'evaluation_result': return 'text-orange-600 bg-orange-100';
      case 'progress': return 'text-indigo-600 bg-indigo-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const handleReaction = (shareId, reactionType) => {
    setReactions(prev => ({
      ...prev,
      [shareId]: {
        ...prev[shareId],
        [reactionType]: (prev[shareId]?.[reactionType] || 0) + 1,
        userReacted: reactionType
      }
    }));

    // Here you would typically make an API call to record the reaction
    // fetch(`/api/gamification/social/shares/${shareId}/react`, { ... })
  };

  const renderShareContent = (share) => {
    const Icon = getShareIcon(share.type);
    const colorClass = getShareColor(share.type);

    switch (share.type) {
      case 'achievement':
        return (
          <div className=\"flex items-center space-x-3\">
            <div className={`p-2 rounded-lg ${colorClass}`}>
              <Icon className=\"h-5 w-5\" />
            </div>
            <div>
              <p className=\"font-medium\">Unlocked Achievement!</p>
              <p className=\"text-sm text-gray-600\">{share.content}</p>
            </div>
          </div>
        );

      case 'badge':
        return (
          <div className=\"flex items-center space-x-3\">
            <div className={`p-2 rounded-lg ${colorClass}`}>
              <Icon className=\"h-5 w-5\" />
            </div>
            <div>
              <p className=\"font-medium\">Earned a Badge!</p>
              <p className=\"text-sm text-gray-600\">{share.content}</p>
              {share.metadata?.badge_rarity && (
                <Badge variant=\"outline\" className=\"mt-1\">
                  {share.metadata.badge_rarity}
                </Badge>
              )}
            </div>
          </div>
        );

      case 'level_up':
        return (
          <div className=\"flex items-center space-x-3\">
            <div className={`p-2 rounded-lg ${colorClass}`}>
              <Icon className=\"h-5 w-5\" />
            </div>
            <div>
              <p className=\"font-medium\">Level Up!</p>
              <p className=\"text-sm text-gray-600\">
                Reached Level {share.metadata?.new_level}
              </p>
              {share.metadata?.title && (
                <Badge variant=\"outline\" className=\"mt-1\">
                  {share.metadata.title}
                </Badge>
              )}
            </div>
          </div>
        );

      case 'evaluation_result':
        return (
          <div className=\"flex items-center space-x-3\">
            <div className={`p-2 rounded-lg ${colorClass}`}>
              <Icon className=\"h-5 w-5\" />
            </div>
            <div>
              <p className=\"font-medium\">Evaluation Completed!</p>
              <p className=\"text-sm text-gray-600\">{share.content}</p>
              {share.metadata?.score && (
                <div className=\"flex items-center space-x-2 mt-1\">
                  <Badge 
                    variant=\"outline\" 
                    className={share.metadata.score >= 90 ? 'bg-green-100 text-green-700' : 
                              share.metadata.score >= 70 ? 'bg-yellow-100 text-yellow-700' : 
                              'bg-gray-100 text-gray-700'}
                  >
                    {share.metadata.score}%
                  </Badge>
                </div>
              )}
            </div>
          </div>
        );

      default:
        return (
          <div className=\"flex items-center space-x-3\">
            <div className={`p-2 rounded-lg ${colorClass}`}>
              <Icon className=\"h-5 w-5\" />
            </div>
            <div>
              <p className=\"text-sm text-gray-600\">{share.content}</p>
            </div>
          </div>
        );
    }
  };

  if (feed.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className=\"flex items-center space-x-2\">
            <Users className=\"h-5 w-5\" />
            <span>Social Feed</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className=\"text-center py-8\">
            <Users className=\"h-12 w-12 mx-auto text-gray-400 mb-4\" />
            <p className=\"text-gray-500\">No activity to show</p>
            <p className=\"text-sm text-gray-400\">Complete achievements and join teams to see activity!</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className=\"flex items-center space-x-2\">
          <Users className=\"h-5 w-5\" />
          <span>Social Feed</span>
        </CardTitle>
      </CardHeader>
      <CardContent className=\"space-y-4\">
        {feed.map((share, index) => (
          <div key={share.id || index} className=\"border rounded-lg p-4 hover:bg-gray-50 transition-colors\">
            {/* User Info */}
            <div className=\"flex items-center space-x-3 mb-3\">
              {share.user.avatar_url ? (
                <img 
                  src={share.user.avatar_url} 
                  alt={share.user.display_name}
                  className=\"w-8 h-8 rounded-full\"
                />
              ) : (
                <div className=\"w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm font-bold\">
                  {share.user.display_name.charAt(0).toUpperCase()}
                </div>
              )}
              <div className=\"flex-1\">
                <p className=\"font-medium text-sm\">{share.user.display_name}</p>
                <p className=\"text-xs text-gray-500\">{formatTimeAgo(share.created_at)}</p>
              </div>
              <Badge variant=\"outline\" className=\"text-xs capitalize\">
                {share.type.replace('_', ' ')}
              </Badge>
            </div>

            {/* Share Content */}
            <div className=\"mb-3\">
              {renderShareContent(share)}
            </div>

            {/* Reactions */}
            <div className=\"flex items-center justify-between pt-3 border-t\">
              <div className=\"flex items-center space-x-4\">
                <Button
                  variant=\"ghost\"
                  size=\"sm\"
                  onClick={() => handleReaction(share.id, 'like')}
                  className=\"text-gray-500 hover:text-red-500 transition-colors\"
                >
                  <Heart className={`h-4 w-4 mr-1 ${reactions[share.id]?.userReacted === 'like' ? 'fill-red-500 text-red-500' : ''}`} />
                  {(share.reactions?.likes || 0) + (reactions[share.id]?.likes || 0)}
                </Button>

                <Button
                  variant=\"ghost\"
                  size=\"sm\"
                  className=\"text-gray-500 hover:text-blue-500 transition-colors\"
                >
                  <MessageCircle className=\"h-4 w-4 mr-1\" />
                  {share.reactions?.comments || 0}
                </Button>

                <Button
                  variant=\"ghost\"
                  size=\"sm\"
                  className=\"text-gray-500 hover:text-green-500 transition-colors\"
                >
                  <Share className=\"h-4 w-4 mr-1\" />
                  Share
                </Button>
              </div>

              {share.is_public && (
                <Badge variant=\"outline\" className=\"text-xs\">
                  Public
                </Badge>
              )}
            </div>
          </div>
        ))}

        {/* Load More Button */}
        <div className=\"text-center pt-4\">
          <Button variant=\"outline\" size=\"sm\">
            Load More
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default SocialFeed;
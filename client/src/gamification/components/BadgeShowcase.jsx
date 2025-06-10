import React, { useState } from 'react';
import { Badge } from '../../components/ui/badge';
import { Card, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Modal } from '../../components/ui/modal';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../../components/ui/tooltip';
import { Award, Calendar, Info } from 'lucide-react';

const BadgeShowcase = ({ badges = [] }) => {
  const [selectedBadge, setSelectedBadge] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const getRarityColor = (rarity) => {
    switch (rarity?.toLowerCase()) {
      case 'legendary': return 'from-yellow-400 via-orange-500 to-red-500';
      case 'epic': return 'from-purple-400 via-purple-500 to-purple-600';
      case 'rare': return 'from-blue-400 via-blue-500 to-blue-600';
      case 'uncommon': return 'from-green-400 via-green-500 to-green-600';
      default: return 'from-gray-400 via-gray-500 to-gray-600';
    }
  };

  const getRarityBorder = (rarity) => {
    switch (rarity?.toLowerCase()) {
      case 'legendary': return 'border-yellow-400 shadow-yellow-200';
      case 'epic': return 'border-purple-400 shadow-purple-200';
      case 'rare': return 'border-blue-400 shadow-blue-200';
      case 'uncommon': return 'border-green-400 shadow-green-200';
      default: return 'border-gray-400 shadow-gray-200';
    }
  };

  const getBadgeAnimation = (rarity) => {
    switch (rarity?.toLowerCase()) {
      case 'legendary': return 'animate-pulse';
      case 'epic': return 'hover:animate-bounce';
      default: return '';
    }
  };

  const BadgeItem = ({ badge, size = 'md', showDetails = false }) => {
    const sizeClasses = {
      sm: 'w-12 h-12 text-lg',
      md: 'w-16 h-16 text-xl',
      lg: 'w-20 h-20 text-2xl',
      xl: 'w-24 h-24 text-3xl'
    };

    const badgeData = badge.badge || badge;

    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger>
            <div 
              className={`
                ${sizeClasses[size]} 
                rounded-full 
                bg-gradient-to-br ${getRarityColor(badgeData.rarity)}
                border-2 ${getRarityBorder(badgeData.rarity)}
                flex items-center justify-center 
                cursor-pointer 
                transition-all duration-300 
                hover:scale-110 hover:shadow-lg
                ${getBadgeAnimation(badgeData.rarity)}
              `}
              onClick={() => {
                setSelectedBadge(badge);
                setShowModal(true);
              }}
            >
              <span className=\"text-white font-bold drop-shadow-lg\">
                {badgeData.icon || '🏆'}
              </span>
            </div>
          </TooltipTrigger>
          <TooltipContent>
            <div className=\"text-center\">
              <p className=\"font-semibold\">{badgeData.name}</p>
              <p className=\"text-sm text-gray-600\">{badgeData.description}</p>
              <Badge variant=\"outline\" className=\"mt-1\">
                {badgeData.rarity}
              </Badge>
            </div>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  };

  const BadgeModal = () => {
    if (!selectedBadge) return null;

    const badgeData = selectedBadge.badge || selectedBadge;

    return (
      <Modal isOpen={showModal} onClose={() => setShowModal(false)}>
        <div className=\"p-6 max-w-md mx-auto\">
          <div className=\"text-center mb-6\">
            <div className={`w-32 h-32 mx-auto rounded-full bg-gradient-to-br ${getRarityColor(badgeData.rarity)} border-4 ${getRarityBorder(badgeData.rarity)} flex items-center justify-center mb-4 shadow-2xl`}>
              <span className=\"text-6xl\">{badgeData.icon || '🏆'}</span>
            </div>
            <h2 className=\"text-2xl font-bold mb-2\">{badgeData.name}</h2>
            <Badge variant=\"outline\" className=\"mb-4\">
              {badgeData.rarity}
            </Badge>
          </div>

          <div className=\"space-y-4\">
            <div>
              <h3 className=\"font-semibold mb-2\">Description</h3>
              <p className=\"text-gray-600\">{badgeData.description}</p>
            </div>

            <div className=\"grid grid-cols-2 gap-4\">
              <div>
                <h4 className=\"font-medium text-sm text-gray-700\">Points</h4>
                <p className=\"text-lg font-bold text-blue-600\">{badgeData.points || 0}</p>
              </div>
              <div>
                <h4 className=\"font-medium text-sm text-gray-700\">Category</h4>
                <p className=\"text-lg capitalize\">{badgeData.category || 'General'}</p>
              </div>
            </div>

            {selectedBadge.earned_at && (
              <div className=\"flex items-center space-x-2 text-sm text-gray-600\">
                <Calendar className=\"h-4 w-4\" />
                <span>Earned on {new Date(selectedBadge.earned_at).toLocaleDateString()}</span>
              </div>
            )}

            {selectedBadge.metadata && Object.keys(selectedBadge.metadata).length > 0 && (
              <div>
                <h4 className=\"font-medium text-sm text-gray-700 mb-2\">Achievement Details</h4>
                <div className=\"bg-gray-50 p-3 rounded-lg\">
                  {Object.entries(selectedBadge.metadata).map(([key, value]) => (
                    <div key={key} className=\"flex justify-between text-sm\">
                      <span className=\"capitalize\">{key.replace('_', ' ')}:</span>
                      <span className=\"font-medium\">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <Button 
            onClick={() => setShowModal(false)} 
            className=\"w-full mt-6\"
          >
            Close
          </Button>
        </div>
      </Modal>
    );
  };

  if (!badges || badges.length === 0) {
    return (
      <div className=\"text-center py-8\">
        <Award className=\"h-12 w-12 mx-auto text-gray-400 mb-4\" />
        <p className=\"text-gray-500\">No badges earned yet</p>
        <p className=\"text-sm text-gray-400\">Complete activities to earn your first badge!</p>
      </div>
    );
  }

  // Group badges by rarity for better display
  const badgesByRarity = badges.reduce((acc, badge) => {
    const rarity = badge.badge?.rarity || badge.rarity || 'common';
    if (!acc[rarity]) acc[rarity] = [];
    acc[rarity].push(badge);
    return acc;
  }, {});

  const rarityOrder = ['legendary', 'epic', 'rare', 'uncommon', 'common'];

  return (
    <div className=\"space-y-6\">
      {/* Featured Badges (Top 3) */}
      <div>
        <h3 className=\"text-lg font-semibold mb-4 flex items-center space-x-2\">
          <Award className=\"h-5 w-5\" />
          <span>Featured Badges</span>
        </h3>
        <div className=\"flex justify-center space-x-4\">
          {badges.slice(0, 3).map((badge, index) => (
            <div key={index} className=\"text-center\">
              <BadgeItem badge={badge} size=\"lg\" />
              <p className=\"text-sm font-medium mt-2\">
                {badge.badge?.name || badge.name}
              </p>
              <Badge variant=\"outline\" className=\"text-xs\">
                {badge.badge?.rarity || badge.rarity}
              </Badge>
            </div>
          ))}
        </div>
      </div>

      {/* All Badges by Rarity */}
      <div>
        <h3 className=\"text-lg font-semibold mb-4\">All Badges</h3>
        <div className=\"space-y-4\">
          {rarityOrder.map(rarity => {
            const rarityBadges = badgesByRarity[rarity];
            if (!rarityBadges || rarityBadges.length === 0) return null;

            return (
              <div key={rarity}>
                <div className=\"flex items-center space-x-2 mb-3\">
                  <Badge variant=\"outline\" className={`${getRarityColor(rarity)} text-white border-0`}>
                    {rarity.charAt(0).toUpperCase() + rarity.slice(1)}
                  </Badge>
                  <span className=\"text-sm text-gray-600\">({rarityBadges.length})</span>
                </div>
                <div className=\"grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-3\">
                  {rarityBadges.map((badge, index) => (
                    <div key={index} className=\"text-center\">
                      <BadgeItem badge={badge} size=\"md\" />
                      <p className=\"text-xs mt-1 truncate\">
                        {badge.badge?.name || badge.name}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Badge Statistics */}
      <Card>
        <CardContent className=\"p-4\">
          <h4 className=\"font-semibold mb-3\">Badge Statistics</h4>
          <div className=\"grid grid-cols-2 gap-4 text-sm\">
            <div>
              <span className=\"text-gray-600\">Total Badges:</span>
              <span className=\"font-bold ml-2\">{badges.length}</span>
            </div>
            <div>
              <span className=\"text-gray-600\">Rarest Badge:</span>
              <span className=\"font-bold ml-2 capitalize\">
                {badges.find(b => (b.badge?.rarity || b.rarity) === 'legendary') ? 'Legendary' :
                 badges.find(b => (b.badge?.rarity || b.rarity) === 'epic') ? 'Epic' :
                 badges.find(b => (b.badge?.rarity || b.rarity) === 'rare') ? 'Rare' : 'Common'}
              </span>
            </div>
            <div>
              <span className=\"text-gray-600\">Most Recent:</span>
              <span className=\"font-bold ml-2\">
                {badges[0]?.earned_at ? 
                  new Date(badges[0].earned_at).toLocaleDateString() : 
                  'N/A'
                }
              </span>
            </div>
            <div>
              <span className=\"text-gray-600\">Total Points:</span>
              <span className=\"font-bold ml-2\">
                {badges.reduce((sum, badge) => sum + (badge.badge?.points || badge.points || 0), 0)}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      <BadgeModal />
    </div>
  );
};

export default BadgeShowcase;
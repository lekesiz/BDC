// TODO: i18n - processed
import { useState, useEffect } from 'react';
import {
  Award,
  Medal,
  Star,
  CheckCircle,
  Clock,
  Calendar,
  TrendingUp,
  Filter,
  Loader,
  BookOpen,
  Target,
  Crown,
  Zap } from
'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/toast';
/**
 * PortalAchievementsPage displays the student's achievements, badges, 
 * certificates and progress milestones
 */import { useTranslation } from "react-i18next";
const PortalAchievementsPage = () => {const { t } = useTranslation();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [achievements, setAchievements] = useState({
    highlights: [],
    badges: [],
    certificates: [],
    recentAchievements: []
  });
  const [filter, setFilter] = useState('all');
  // Fetch achievements data
  useEffect(() => {
    const fetchAchievements = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/api/portal/achievements');
        setAchievements(response.data);
      } catch (error) {
        console.error('Error fetching achievements:', error);
        toast({
          title: 'Error',
          description: 'Failed to load achievements',
          type: 'error'
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchAchievements();
  }, []); // Remove toast dependency to prevent infinite loop
  // Format date
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };
  // Get icon based on achievement type
  const getAchievementIcon = (type, className = "h-6 w-6") => {
    switch (type) {
      case 'badge':
        return <Medal className={className} />;
      case 'certificate':
        return <Award className={className} />;
      case 'completion':
        return <CheckCircle className={className} />;
      case 'milestone':
        return <Target className={className} />;
      case 'skill':
        return <Zap className={className} />;
      case 'excellence':
        return <Crown className={className} />;
      default:
        return <Star className={className} />;
    }
  };
  // Get color class based on achievement type
  const getAchievementColorClass = (type) => {
    switch (type) {
      case 'badge':
        return 'bg-purple-50 text-purple-500';
      case 'certificate':
        return 'bg-green-50 text-green-500';
      case 'completion':
        return 'bg-blue-50 text-blue-500';
      case 'milestone':
        return 'bg-yellow-50 text-yellow-500';
      case 'skill':
        return 'bg-orange-50 text-orange-500';
      case 'excellence':
        return 'bg-red-50 text-red-500';
      default:
        return 'bg-gray-50 text-gray-500';
    }
  };
  // Filter achievements based on selected filter
  const getFilteredAchievements = () => {
    if (filter === 'all') {
      return {
        badges: achievements.badges || [],
        certificates: achievements.certificates || []
      };
    } else if (filter === 'badges') {
      return {
        badges: achievements.badges || [],
        certificates: []
      };
    } else if (filter === 'certificates') {
      return {
        badges: [],
        certificates: achievements.certificates || []
      };
    }
    return {
      badges: [],
      certificates: []
    };
  };
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader className="w-10 h-10 text-primary animate-spin" />
      </div>);

  }
  // Get filtered achievements
  const filteredAchievements = getFilteredAchievements();
  return (
    <div className="container mx-auto py-6">
      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-2">{t("components.my_achievements")}</h1>
        <p className="text-gray-600">{t("pages.track_your_learning_milestones_earned_badges_and_c")}

        </p>
      </div>
      {/* Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {(achievements.highlights || []).map((highlight) =>
        <Card
          key={highlight.id}
          className="p-4 text-center flex flex-col items-center">

            <div className={`p-3 rounded-full mb-3 ${getAchievementColorClass(highlight.type)}`}>
              {getAchievementIcon(highlight.type, "h-7 w-7")}
            </div>
            <h3 className="text-xl font-bold">{highlight.value}</h3>
            <p className="text-gray-500">{highlight.label}</p>
          </Card>
        )}
      </div>
      {/* Recently earned achievements */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">{t("components.recently_earned")}</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {(achievements.recentAchievements || []).map((achievement) =>
          <Card key={achievement.id} className="overflow-hidden">
              <div className={`h-2 ${achievement.type === 'badge' ? 'bg-purple-500' : achievement.type === 'certificate' ? 'bg-green-500' : 'bg-blue-500'}`}></div>
              <div className="p-6">
                <div className="flex items-center mb-4">
                  <div className={`p-3 rounded-full mr-3 ${getAchievementColorClass(achievement.type)}`}>
                    {getAchievementIcon(achievement.type)}
                  </div>
                  <div>
                    <h3 className="font-medium">{achievement.name}</h3>
                    <p className="text-sm text-gray-500">{t("components.earned_on")}
                    {formatDate(achievement.dateEarned)}
                    </p>
                  </div>
                </div>
                <p className="text-gray-600 mb-4">{achievement.description}</p>
                {achievement.type === 'certificate' &&
              <Button
                size="sm"
                variant="outline"
                className="w-full"
                onClick={() => window.open(`/api/portal/certificates/${achievement.id}/download`, '_blank')}>{t("pages.view_certificate")}


              </Button>
              }
              </div>
            </Card>
          )}
        </div>
      </div>
      {/* All achievements section */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">{t("pages.all_achievements")}</h2>
          <div className="flex space-x-2">
            <Button
              variant={filter === 'all' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('all')}>{t("components.all")}


            </Button>
            <Button
              variant={filter === 'badges' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('badges')}>{t("pages.badges")}


            </Button>
            <Button
              variant={filter === 'certificates' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('certificates')}>{t("components.certificates")}


            </Button>
          </div>
        </div>
        {/* Badges section */}
        {filteredAchievements.badges.length > 0 &&
        <div className="mb-8">
            <h3 className="text-lg font-medium mb-4">{t("pages.badges")}</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {filteredAchievements.badges.map((badge) =>
            <Card key={badge.id} className={`p-4 text-center ${!badge.isEarned ? 'opacity-50' : ''}`}>
                  <div className="flex flex-col items-center">
                    <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-3 ${badge.isEarned ? getAchievementColorClass(badge.type) : 'bg-gray-100 text-gray-400'}`}>
                      {getAchievementIcon(badge.type, "h-8 w-8")}
                    </div>
                    <h3 className="font-medium mb-1">{badge.name}</h3>
                    <p className="text-sm text-gray-500 mb-2">{badge.description}</p>
                    {badge.isEarned ?
                <span className="text-xs bg-green-100 text-green-600 px-2 py-1 rounded-full">{t("components.earned_on")}
                  {formatDate(badge.dateEarned)}
                      </span> :

                <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">{t("pages.not_earned_yet")}

                </span>
                }
                  </div>
                </Card>
            )}
            </div>
          </div>
        }
        {/* Certificates section */}
        {filteredAchievements.certificates.length > 0 &&
        <div>
            <h3 className="text-lg font-medium mb-4">{t("components.certificates")}</h3>
            <div className="space-y-4">
              {filteredAchievements.certificates.map((certificate) =>
            <Card key={certificate.id} className={`overflow-hidden ${!certificate.isEarned ? 'opacity-50' : ''}`}>
                  <div className="p-6 md:flex md:items-center md:justify-between">
                    <div className="flex items-center mb-4 md:mb-0">
                      <div className={`p-3 rounded-full mr-4 ${certificate.isEarned ? 'bg-green-50 text-green-500' : 'bg-gray-100 text-gray-400'}`}>
                        <Award className="h-6 w-6" />
                      </div>
                      <div>
                        <h3 className="font-medium">{certificate.name}</h3>
                        <p className="text-sm text-gray-500 mb-1">{certificate.description}</p>
                        {certificate.isEarned ?
                    <div className="flex items-center text-sm text-green-600">
                            <CheckCircle className="h-4 w-4 mr-1" />
                            <span>{t("components.earned_on")}{formatDate(certificate.dateEarned)}</span>
                          </div> :

                    <div className="flex items-center text-sm text-gray-500">
                            <Clock className="h-4 w-4 mr-1" />
                            <span>Progress: {certificate.progress}%</span>
                          </div>
                    }
                      </div>
                    </div>
                    {certificate.isEarned &&
                <Button
                  variant="outline"
                  onClick={() => window.open(`/api/portal/certificates/${certificate.id}/download`, '_blank')}>

                        <Award className="h-4 w-4 mr-2" />{t("pages.view_certificate")}

                </Button>
                }
                  </div>
                </Card>
            )}
            </div>
          </div>
        }
      </div>
    </div>);

};
export default PortalAchievementsPage;
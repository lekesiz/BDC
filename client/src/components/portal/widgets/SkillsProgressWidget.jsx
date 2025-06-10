// TODO: i18n - processed
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap, TrendingUp, CheckCircle, Loader } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
/**
 * Displays the student's skill development progress
 */import { useTranslation } from "react-i18next";
const SkillsProgressWidget = ({ data, isLoading, error }) => {const { t } = useTranslation();
  const navigate = useNavigate();
  // Get skill level label
  const getSkillLevelLabel = (level) => {
    switch (level) {
      case 1:return 'Beginner';
      case 2:return 'Basic';
      case 3:return 'Intermediate';
      case 4:return 'Advanced';
      case 5:return 'Expert';
      default:return 'Not Started';
    }
  };
  // Get skill level color
  const getSkillLevelColor = (level, maxLevel) => {
    const ratio = level / maxLevel;
    if (ratio < 0.2) return 'bg-red-500';
    if (ratio < 0.4) return 'bg-orange-500';
    if (ratio < 0.6) return 'bg-yellow-500';
    if (ratio < 0.8) return 'bg-blue-500';
    return 'bg-green-500';
  };
  if (isLoading) {
    return (
      <Card className="overflow-hidden h-full">
        <div className="p-6 flex justify-between items-center border-b">
          <h2 className="text-lg font-medium">{t("archive-components.skills_development")}</h2>
        </div>
        <div className="flex justify-center items-center p-12">
          <Loader className="h-8 w-8 text-primary animate-spin" />
        </div>
      </Card>);

  }
  if (error) {
    return (
      <Card className="overflow-hidden h-full">
        <div className="p-6 flex justify-between items-center border-b">
          <h2 className="text-lg font-medium">{t("archive-components.skills_development")}</h2>
        </div>
        <div className="p-6 text-center text-red-500">{t("components.failed_to_load_skills_data")}

        </div>
      </Card>);

  }
  // Get top skills to display (limit to 4)
  const topSkills = data?.skills?.slice(0, 4) || [];
  // Get recently improved skills
  const recentlyImproved = data?.skillGrowth?.slice(0, 3) || [];
  return (
    <Card className="overflow-hidden h-full">
      <div className="p-6 flex justify-between items-center border-b">
        <h2 className="text-lg font-medium">{t("archive-components.skills_development")}</h2>
        <Button
          variant="outline"
          size="sm"
          onClick={() => navigate('/portal/skills')}>{t("components.view_all_skills")}


        </Button>
      </div>
      <div className="p-6 space-y-5">
        {/* Current skill levels */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium text-gray-500 mb-2">{t("components.top_skills")}</h3>
          {topSkills.map((skill) =>
          <div key={skill.id} className="space-y-2">
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <div className="p-1.5 rounded-full bg-blue-50 mr-2">
                    <Zap className="h-3.5 w-3.5 text-blue-500" />
                  </div>
                  <h4 className="font-medium">{skill.name}</h4>
                </div>
                <span className="text-xs px-2 py-0.5 bg-gray-100 rounded-full">
                  {getSkillLevelLabel(skill.currentLevel)}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                className={`h-2 rounded-full ${getSkillLevelColor(skill.currentLevel, skill.maxLevel)}`}
                style={{ width: `${skill.currentLevel / skill.maxLevel * 100}%` }}>
              </div>
              </div>
            </div>
          )}
        </div>
        {/* Recently improved skills */}
        {recentlyImproved.length > 0 &&
        <div>
            <h3 className="text-sm font-medium text-gray-500 mb-3">{t("components.recent_improvements")}</h3>
            <div className="space-y-3">
              {recentlyImproved.map((item) =>
            <div key={item.id} className="bg-gray-50 rounded-lg p-3">
                  <div className="flex justify-between items-center mb-1">
                    <div className="flex items-center">
                      <TrendingUp className="h-4 w-4 text-green-500 mr-2" />
                      <h4 className="font-medium text-sm">{item.name}</h4>
                    </div>
                    <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded">
                      +{item.growthPercentage}%
                    </span>
                  </div>
                  <div className="flex items-center">
                    <div className="relative flex-grow h-2 bg-gray-100 rounded-full">
                      <div
                    className="absolute left-0 top-0 h-2 bg-gray-300 rounded-full"
                    style={{ width: `${item.previousLevel / item.maxLevel * 100}%` }}>
                  </div>
                      <div
                    className="absolute left-0 top-0 h-2 bg-green-500 rounded-full"
                    style={{ width: `${item.currentLevel / item.maxLevel * 100}%` }}>
                  </div>
                    </div>
                    <div className="ml-2 flex space-x-2 text-xs">
                      <span className="text-gray-500">{t("components.level")}{item.previousLevel} → {item.currentLevel}</span>
                    </div>
                  </div>
                </div>
            )}
            </div>
          </div>
        }
      </div>
    </Card>);

};
export default SkillsProgressWidget;
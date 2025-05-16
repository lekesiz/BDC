import { useState, useEffect } from 'react';
import { 
  Zap, 
  TrendingUp, 
  Award, 
  CheckCircle, 
  AlertCircle, 
  BarChart2,
  Filter,
  Search,
  ChevronDown,
  ChevronUp,
  BarChart,
  PieChart,
  ArrowUp,
  AlertTriangle,
  BookOpen,
  Clock,
  Loader
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/toast';

/**
 * PortalSkillsPage displays the student's skills, development areas,
 * and progress in various competencies
 */
const PortalSkillsPage = () => {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [skillsData, setSkillsData] = useState({
    highlightMetrics: [],
    technicalSkills: [],
    softSkills: [],
    skillGrowth: [],
    recommendedFocus: []
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('all');
  const [selectedSkill, setSelectedSkill] = useState(null);
  
  // Fetch skills data
  useEffect(() => {
    const fetchSkillsData = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/api/portal/skills');
        setSkillsData(response.data);
      } catch (error) {
        console.error('Error fetching skills data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load skills data',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchSkillsData();
  }, [toast]);
  
  // Filter skills based on search term and filter
  const getFilteredSkills = () => {
    // First apply category filter
    let filtered = [];
    if (filter === 'all') {
      filtered = [...skillsData.technicalSkills, ...skillsData.softSkills];
    } else if (filter === 'technical') {
      filtered = [...skillsData.technicalSkills];
    } else if (filter === 'soft') {
      filtered = [...skillsData.softSkills];
    } else if (filter === 'focus') {
      filtered = skillsData.recommendedFocus.map(focus => {
        // Find the referenced skill
        const skill = [...skillsData.technicalSkills, ...skillsData.softSkills]
          .find(s => s.id === focus.skillId);
        return skill ? { ...skill, focusReason: focus.reason } : null;
      }).filter(Boolean);
    }
    
    // Then apply search filter if there's a search term
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(skill => 
        skill.name.toLowerCase().includes(term) || 
        skill.description.toLowerCase().includes(term) || 
        skill.category.toLowerCase().includes(term)
      );
    }
    
    return filtered;
  };
  
  // Get skill level label
  const getSkillLevelLabel = (level) => {
    switch (level) {
      case 1: return 'Beginner';
      case 2: return 'Basic';
      case 3: return 'Intermediate';
      case 4: return 'Advanced';
      case 5: return 'Expert';
      default: return 'Not Started';
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
  
  // Format date
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };
  
  // Handle skill selection
  const handleSkillSelect = (skill) => {
    setSelectedSkill(selectedSkill?.id === skill.id ? null : skill);
  };
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader className="w-10 h-10 text-primary animate-spin" />
      </div>
    );
  }
  
  const filteredSkills = getFilteredSkills();
  
  return (
    <div className="container mx-auto py-6">
      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-2">Skills Development</h1>
        <p className="text-gray-600">
          Track your progress in technical and soft skills across your learning journey
        </p>
      </div>
      
      {/* Skills metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {skillsData.highlightMetrics.map(metric => (
          <Card 
            key={metric.id} 
            className="p-4 text-center flex flex-col items-center"
          >
            <div className={`p-3 rounded-full mb-3 ${
              metric.type === 'average' 
                ? 'bg-blue-50 text-blue-500' 
                : metric.type === 'mastered'
                ? 'bg-green-50 text-green-500'
                : metric.type === 'improved'
                ? 'bg-purple-50 text-purple-500'
                : 'bg-yellow-50 text-yellow-500'
            }`}>
              {metric.type === 'average' && <BarChart className="h-6 w-6" />}
              {metric.type === 'mastered' && <CheckCircle className="h-6 w-6" />}
              {metric.type === 'improved' && <TrendingUp className="h-6 w-6" />}
              {metric.type === 'focus' && <AlertCircle className="h-6 w-6" />}
            </div>
            <h3 className="text-xl font-bold">{metric.value}</h3>
            <p className="text-gray-500">{metric.label}</p>
          </Card>
        ))}
      </div>
      
      {/* Search and filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Input
            type="text"
            placeholder="Search skills..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        </div>
        
        <div className="flex space-x-2">
          <Button
            variant={filter === 'all' ? 'default' : 'outline'}
            onClick={() => setFilter('all')}
          >
            All Skills
          </Button>
          <Button
            variant={filter === 'technical' ? 'default' : 'outline'}
            onClick={() => setFilter('technical')}
          >
            Technical
          </Button>
          <Button
            variant={filter === 'soft' ? 'default' : 'outline'}
            onClick={() => setFilter('soft')}
          >
            Soft Skills
          </Button>
          <Button
            variant={filter === 'focus' ? 'default' : 'outline'}
            onClick={() => setFilter('focus')}
          >
            Focus Areas
          </Button>
        </div>
      </div>
      
      {/* Recent skill growth chart */}
      {filter === 'all' && !searchTerm && (
        <Card className="p-6 mb-8">
          <h2 className="text-lg font-medium mb-4">Recent Skill Growth</h2>
          <div className="space-y-4">
            {skillsData.skillGrowth.map(item => (
              <div key={item.id}>
                <div className="flex justify-between items-center mb-2">
                  <h3 className="font-medium">{item.name}</h3>
                  <div className="flex items-center">
                    <span className="text-sm text-gray-600 mr-2">{item.growthPercentage}%</span>
                    <TrendingUp className="h-4 w-4 text-green-500" />
                  </div>
                </div>
                <div className="flex items-center">
                  <div className="relative flex-grow h-4 bg-gray-100 rounded-full">
                    <div 
                      className="absolute left-0 top-0 h-4 bg-gray-300 rounded-full"
                      style={{ width: `${item.previousLevel / item.maxLevel * 100}%` }}
                    ></div>
                    <div 
                      className="absolute left-0 top-0 h-4 bg-green-500 rounded-full"
                      style={{ width: `${item.currentLevel / item.maxLevel * 100}%` }}
                    ></div>
                  </div>
                  <div className="ml-4 flex space-x-2">
                    <span className="text-xs px-2 py-1 bg-gray-100 rounded">Before: {item.previousLevel}</span>
                    <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded">Now: {item.currentLevel}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
      
      {/* Skills list */}
      {filteredSkills.length === 0 ? (
        <Card className="p-8 text-center">
          <Zap className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-1">No skills found</h3>
          <p className="text-gray-500">
            Try adjusting your search or filter to find what you're looking for
          </p>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredSkills.map(skill => (
            <Card 
              key={skill.id} 
              className="overflow-hidden"
            >
              <div className="p-6 cursor-pointer" onClick={() => handleSkillSelect(skill)}>
                <div className="flex justify-between items-start">
                  <div className="flex items-start">
                    <div className={`p-2 rounded-full mr-4 ${
                      skill.type === 'technical' 
                        ? 'bg-blue-50 text-blue-500' 
                        : 'bg-purple-50 text-purple-500'
                    }`}>
                      {skill.type === 'technical' ? (
                        <Zap className="h-5 w-5" />
                      ) : (
                        <Users className="h-5 w-5" />
                      )}
                    </div>
                    <div>
                      <div className="flex items-center mb-1">
                        <h3 className="font-medium">{skill.name}</h3>
                        {skill.focusReason && (
                          <span className="ml-2 px-2 py-0.5 bg-yellow-100 text-yellow-700 text-xs rounded-full">
                            Focus Area
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-500 mb-2">{skill.description}</p>
                      <div className="flex space-x-2">
                        <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100">
                          {skill.category}
                        </span>
                        {skill.lastImproved && (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100">
                            Updated {formatDate(skill.lastImproved)}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col items-end">
                    <div className="flex items-center mb-1">
                      <span className="text-sm font-medium mr-2">
                        Level {skill.currentLevel}/{skill.maxLevel}
                      </span>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100">
                        {getSkillLevelLabel(skill.currentLevel)}
                      </span>
                    </div>
                    <div className="w-32 bg-gray-200 rounded-full h-2.5 mb-2">
                      <div 
                        className={`h-2.5 rounded-full ${getSkillLevelColor(skill.currentLevel, skill.maxLevel)}`}
                        style={{ width: `${(skill.currentLevel / skill.maxLevel) * 100}%` }}
                      ></div>
                    </div>
                    {selectedSkill?.id === skill.id ? (
                      <ChevronUp className="h-5 w-5 text-gray-400" />
                    ) : (
                      <ChevronDown className="h-5 w-5 text-gray-400" />
                    )}
                  </div>
                </div>
              </div>
              
              {/* Expanded skill details */}
              {selectedSkill?.id === skill.id && (
                <div className="p-6 pt-0 border-t mt-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium mb-3">Skill Breakdown</h4>
                      <div className="space-y-3">
                        {skill.subskills && skill.subskills.map(subskill => (
                          <div key={subskill.id}>
                            <div className="flex justify-between items-center mb-1">
                              <span className="text-sm">{subskill.name}</span>
                              <span className="text-xs">{subskill.level}/{skill.maxLevel}</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className={`h-2 rounded-full ${getSkillLevelColor(subskill.level, skill.maxLevel)}`}
                                style={{ width: `${(subskill.level / skill.maxLevel) * 100}%` }}
                              ></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium mb-3">Learning Path</h4>
                      {skill.learningPath && (
                        <div className="space-y-4">
                          {skill.learningPath.map((item, index) => (
                            <div 
                              key={index} 
                              className={`flex ${item.completed ? 'text-gray-400' : 'text-gray-700'}`}
                            >
                              <div className="mr-3 mt-0.5">
                                {item.completed ? (
                                  <CheckCircle className="h-5 w-5 text-green-500" />
                                ) : (
                                  <Circle className="h-5 w-5 text-gray-300" />
                                )}
                              </div>
                              <div>
                                <h5 className={`text-sm font-medium ${item.completed ? 'line-through' : ''}`}>
                                  {item.title}
                                </h5>
                                <p className="text-xs text-gray-500">{item.description}</p>
                                {item.resource && (
                                  <a 
                                    href="#" 
                                    className="text-xs text-primary inline-flex items-center mt-1"
                                    onClick={(e) => {
                                      e.preventDefault();
                                      e.stopPropagation();
                                      // Handle resource link
                                    }}
                                  >
                                    <BookOpen className="h-3 w-3 mr-1" />
                                    View Resource
                                  </a>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {skill.focusReason && (
                        <div className="mt-4 p-3 bg-yellow-50 rounded-md border border-yellow-200">
                          <div className="flex">
                            <AlertTriangle className="h-5 w-5 text-yellow-500 mr-2 mt-0.5 flex-shrink-0" />
                            <div>
                              <h5 className="text-sm font-medium text-yellow-700">Focus area recommendation</h5>
                              <p className="text-sm text-yellow-600">{skill.focusReason}</p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

// Fix missing component error
const Circle = (props) => (
  <div 
    className={`rounded-full border-2 border-current ${props.className || ''}`}
    style={{width: '1.25em', height: '1.25em'}}
  />
);

const Users = (props) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={props.className || ''}
  >
    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
    <circle cx="9" cy="7" r="4" />
    <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
    <path d="M16 3.13a4 4 0 0 1 0 7.75" />
  </svg>
);

export default PortalSkillsPage;
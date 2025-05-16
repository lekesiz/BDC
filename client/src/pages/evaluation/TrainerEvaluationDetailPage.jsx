import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Download, User, Clock, Calendar, CheckCircle, AlertTriangle, Award, BarChart2, Send } from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/toast';

/**
 * TrainerEvaluationDetailPage displays a detailed view of a trainer evaluation
 */
const TrainerEvaluationDetailPage = () => {
  const { id } = useParams(); // evaluation ID
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [evaluation, setEvaluation] = useState(null);
  const [beneficiary, setBeneficiary] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  
  // Fetch evaluation and beneficiary data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        
        // Fetch evaluation data
        const evaluationResponse = await api.get(`/api/trainer-evaluations/${id}`);
        setEvaluation(evaluationResponse.data);
        
        // Fetch beneficiary data
        const beneficiaryResponse = await api.get(`/api/beneficiaries/${evaluationResponse.data.beneficiary_id}`);
        setBeneficiary(beneficiaryResponse.data);
      } catch (error) {
        console.error('Error fetching data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load evaluation data',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [id, toast]);
  
  // Handle downloading the evaluation as PDF
  const handleDownloadPDF = async () => {
    try {
      const response = await api.get(`/api/trainer-evaluations/${id}/pdf`, {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `evaluation-${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading PDF:', error);
      toast({
        title: 'Error',
        description: 'Failed to download evaluation PDF',
        type: 'error',
      });
    }
  };
  
  // Handle sharing the evaluation with the beneficiary
  const handleShareWithBeneficiary = async () => {
    try {
      await api.post(`/api/trainer-evaluations/${id}/share`);
      
      toast({
        title: 'Success',
        description: 'Evaluation has been shared with the beneficiary',
        type: 'success',
      });
    } catch (error) {
      console.error('Error sharing evaluation:', error);
      toast({
        title: 'Error',
        description: 'Failed to share evaluation',
        type: 'error',
      });
    }
  };

  // Render loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Render empty state if no evaluation data
  if (!evaluation || !beneficiary) {
    return (
      <div className="container mx-auto py-6">
        <Card className="p-6 text-center">
          <AlertTriangle className="w-12 h-12 text-amber-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Evaluation Not Found</h2>
          <p className="text-gray-600 mb-4">The requested evaluation could not be found.</p>
          <Button onClick={() => navigate('/beneficiaries')}>Back to Beneficiaries</Button>
        </Card>
      </div>
    );
  }

  // Calculate average competency score
  const averageScore = 
    evaluation.competencies.reduce((sum, comp) => sum + comp.score, 0) / 
    evaluation.competencies.length;

  return (
    <div className="container mx-auto py-6 max-w-5xl">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            onClick={() => navigate(`/beneficiaries/${beneficiary.id}`)}
            className="flex items-center"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Beneficiary
          </Button>
          <h1 className="text-2xl font-bold">Evaluation Details</h1>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            onClick={handleDownloadPDF}
            className="flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            Download PDF
          </Button>
          
          <Button
            onClick={handleShareWithBeneficiary}
            className="flex items-center"
          >
            <Send className="w-4 h-4 mr-2" />
            Share with Beneficiary
          </Button>
        </div>
      </div>
      
      {/* Evaluation header card */}
      <Card className="mb-6 p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h2 className="text-xl font-semibold mb-2">{evaluation.title}</h2>
            <p className="text-gray-700 mb-4">{evaluation.description}</p>
            
            <div className="flex items-center text-gray-600 mb-2">
              <User className="w-4 h-4 mr-2" />
              <span>Beneficiary: {beneficiary.first_name} {beneficiary.last_name}</span>
            </div>
            
            <div className="flex items-center text-gray-600 mb-2">
              <Calendar className="w-4 h-4 mr-2" />
              <span>Date: {new Date(evaluation.evaluation_date).toLocaleDateString()}</span>
            </div>
            
            <div className="flex items-center text-gray-600">
              <User className="w-4 h-4 mr-2" />
              <span>Evaluator: {evaluation.trainer_name || 'Unknown Trainer'}</span>
            </div>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg flex flex-col items-center justify-center">
            <div className="text-center mb-2">
              <h3 className="text-sm font-medium text-gray-500">Average Competency Score</h3>
              <div className="flex items-center justify-center">
                <div className="text-5xl font-bold text-primary">{averageScore.toFixed(1)}</div>
                <div className="text-xl text-gray-400 ml-1">/5</div>
              </div>
            </div>
            
            <div className="w-full bg-gray-200 h-1.5 rounded-full mt-2">
              <div
                className={`h-1.5 rounded-full ${
                  averageScore >= 4.5 ? 'bg-green-600' :
                  averageScore >= 3.5 ? 'bg-blue-500' :
                  averageScore >= 2.5 ? 'bg-amber-500' :
                  'bg-red-500'
                }`}
                style={{ width: `${(averageScore / 5) * 100}%` }}
              ></div>
            </div>
            
            <div className="flex justify-between w-full px-1 mt-1 text-xs text-gray-500">
              <span>Needs Improvement</span>
              <span>Outstanding</span>
            </div>
          </div>
        </div>
      </Card>
      
      {/* Evaluation content tabs */}
      <Tabs 
        value={activeTab} 
        onValueChange={setActiveTab}
        className="mb-6"
      >
        <Tabs.TabsList>
          <Tabs.TabTrigger value="overview">
            <BarChart2 className="w-4 h-4 mr-2" />
            Overview
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="competencies">
            <Award className="w-4 h-4 mr-2" />
            Competencies
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="development">
            <CheckCircle className="w-4 h-4 mr-2" />
            Development Plan
          </Tabs.TabTrigger>
        </Tabs.TabsList>
        
        {/* Overview tab */}
        <Tabs.TabContent value="overview">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Strengths */}
            <Card className="p-6">
              <h3 className="font-medium text-lg mb-3 flex items-center text-green-700">
                <CheckCircle className="w-5 h-5 mr-2" />
                Strengths
              </h3>
              <ul className="space-y-2">
                {evaluation.strengths.map((strength, index) => (
                  <li key={index} className="flex items-start">
                    <div className="flex-shrink-0 w-6 h-6 rounded-full bg-green-100 flex items-center justify-center text-green-500 mr-2">
                      <CheckCircle className="w-4 h-4" />
                    </div>
                    <span>{strength}</span>
                  </li>
                ))}
              </ul>
            </Card>
            
            {/* Areas for Improvement */}
            <Card className="p-6">
              <h3 className="font-medium text-lg mb-3 flex items-center text-amber-700">
                <AlertTriangle className="w-5 h-5 mr-2" />
                Areas for Improvement
              </h3>
              <ul className="space-y-2">
                {evaluation.areas_for_improvement.map((area, index) => (
                  <li key={index} className="flex items-start">
                    <div className="flex-shrink-0 w-6 h-6 rounded-full bg-amber-100 flex items-center justify-center text-amber-500 mr-2">
                      <AlertTriangle className="w-4 h-4" />
                    </div>
                    <span>{area}</span>
                  </li>
                ))}
              </ul>
            </Card>
          </div>
          
          {/* Overall Feedback */}
          <Card className="p-6 mb-6">
            <h3 className="font-medium text-lg mb-3">Overall Feedback</h3>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-gray-700 whitespace-pre-line">{evaluation.overall_feedback}</p>
            </div>
          </Card>
        </Tabs.TabContent>
        
        {/* Competencies tab */}
        <Tabs.TabContent value="competencies">
          <Card className="p-6 mb-6">
            <h3 className="font-medium text-lg mb-4">Competency Assessment</h3>
            
            <div className="space-y-6">
              {evaluation.competencies.map((competency, index) => (
                <div key={index} className="border-b border-gray-200 pb-6 last:border-0 last:pb-0">
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-2">
                    <h4 className="font-medium text-gray-900">{competency.name}</h4>
                    <div className="flex items-center mt-2 md:mt-0">
                      <div className="flex">
                        {[1, 2, 3, 4, 5].map((rating) => (
                          <div
                            key={rating}
                            className={`w-8 h-8 rounded-full flex items-center justify-center mr-1 ${
                              rating <= competency.score
                                ? 'bg-primary text-white'
                                : 'bg-gray-100 text-gray-400'
                            }`}
                          >
                            {rating}
                          </div>
                        ))}
                      </div>
                      <div className="ml-3 text-gray-700">
                        {competency.score === 1 && 'Needs Significant Improvement'}
                        {competency.score === 2 && 'Developing'}
                        {competency.score === 3 && 'Meets Expectations'}
                        {competency.score === 4 && 'Exceeds Expectations'}
                        {competency.score === 5 && 'Outstanding'}
                      </div>
                    </div>
                  </div>
                  
                  {competency.notes && (
                    <div className="bg-gray-50 p-3 rounded-lg mt-2">
                      <p className="text-gray-700 text-sm">{competency.notes}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>
          
          {/* Competency visualization */}
          <Card className="p-6">
            <h3 className="font-medium text-lg mb-4">Competency Radar</h3>
            
            <div className="aspect-square max-w-md mx-auto">
              {/* This would be a radar chart in a real implementation */}
              <div className="h-full rounded-full border border-gray-200 relative">
                {/* Radar circles */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-[20%] h-[20%] rounded-full border border-gray-200"></div>
                  <div className="w-[40%] h-[40%] rounded-full border border-gray-200"></div>
                  <div className="w-[60%] h-[60%] rounded-full border border-gray-200"></div>
                  <div className="w-[80%] h-[80%] rounded-full border border-gray-200"></div>
                  <div className="w-full h-full rounded-full border border-gray-200"></div>
                </div>
                
                {/* Radar lines */}
                {evaluation.competencies.map((_, index) => {
                  const angle = (index / evaluation.competencies.length) * 2 * Math.PI;
                  const x2 = 50 + 50 * Math.sin(angle);
                  const y2 = 50 - 50 * Math.cos(angle);
                  
                  return (
                    <div 
                      key={index}
                      className="absolute top-1/2 left-1/2 w-0 h-0 border-t border-gray-200"
                      style={{
                        transform: `rotate(${angle}rad)`,
                        width: '50%',
                        transformOrigin: '0 0',
                      }}
                    ></div>
                  );
                })}
                
                {/* Radar points */}
                {evaluation.competencies.map((competency, index) => {
                  const angle = (index / evaluation.competencies.length) * 2 * Math.PI;
                  const radius = (competency.score / 5) * 50;
                  const x = 50 + radius * Math.sin(angle);
                  const y = 50 - radius * Math.cos(angle);
                  
                  return (
                    <div 
                      key={index}
                      className="absolute w-3 h-3 rounded-full bg-primary border-2 border-white"
                      style={{
                        left: `${x}%`,
                        top: `${y}%`,
                        transform: 'translate(-50%, -50%)',
                      }}
                    ></div>
                  );
                })}
                
                {/* Labels */}
                {evaluation.competencies.map((competency, index) => {
                  const angle = (index / evaluation.competencies.length) * 2 * Math.PI;
                  const x = 50 + 60 * Math.sin(angle);
                  const y = 50 - 60 * Math.cos(angle);
                  
                  return (
                    <div 
                      key={index}
                      className="absolute text-xs text-center font-medium text-gray-700 p-1 bg-white rounded shadow-sm"
                      style={{
                        left: `${x}%`,
                        top: `${y}%`,
                        transform: 'translate(-50%, -50%)',
                        maxWidth: '100px',
                      }}
                    >
                      {competency.name}
                    </div>
                  );
                })}
              </div>
            </div>
          </Card>
        </Tabs.TabContent>
        
        {/* Development Plan tab */}
        <Tabs.TabContent value="development">
          {/* Action Plan */}
          <Card className="p-6 mb-6">
            <h3 className="font-medium text-lg mb-3">Action Plan</h3>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-gray-700 whitespace-pre-line">{evaluation.action_plan}</p>
            </div>
          </Card>
          
          {/* Development Goals */}
          <Card className="p-6">
            <h3 className="font-medium text-lg mb-4">Development Goals</h3>
            
            <div className="space-y-4">
              {evaluation.goals.map((goal, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 mr-3">
                      {index + 1}
                    </div>
                    <h4 className="font-medium text-gray-900">{goal.description}</h4>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 ml-11">
                    <div>
                      <p className="text-sm text-gray-500 mb-1">Timeline</p>
                      <p className="text-gray-700 flex items-center">
                        <Clock className="w-4 h-4 text-gray-400 mr-1" />
                        {goal.timeline}
                      </p>
                    </div>
                    
                    <div>
                      <p className="text-sm text-gray-500 mb-1">Success Criteria</p>
                      <p className="text-gray-700 flex items-center">
                        <CheckCircle className="w-4 h-4 text-gray-400 mr-1" />
                        {goal.success_criteria}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </Tabs.TabContent>
      </Tabs>
    </div>
  );
};

export default TrainerEvaluationDetailPage;
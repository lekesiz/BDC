// TODO: i18n - processed
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { Label } from '../ui/label';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription, AlertTitle } from '../ui/alert';
import { Shield, Search, AlertTriangle, CheckCircle, XCircle, FileText, Link2, Brain } from 'lucide-react';
import { useToast } from '../../hooks/useToast';
import LoadingSpinner from '../ui/LoadingSpinner';
import { Badge } from '../ui/badge';
import api from '../../lib/api';import { useTranslation } from "react-i18next";
const PlagiarismDetector = ({ submissionId, initialText }) => {const { t } = useTranslation();
  const [text, setText] = useState(initialText || '');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [selectedSource, setSelectedSource] = useState(null);
  const { toast } = useToast();
  const handleCheckPlagiarism = async () => {
    if (!text.trim()) {
      toast({
        title: "Error",
        description: "Please enter text to check for plagiarism",
        variant: "destructive"
      });
      return;
    }
    setLoading(true);
    try {
      const response = await api.post('/ai/check-plagiarism', {
        text: text.trim(),
        submission_id: submissionId,
        check_type: 'comprehensive',
        include_ai_detection: true
      });
      setResults(response.data);
      if (response.data.plagiarism_percentage > 20) {
        toast({
          title: "Plagiarism Detected",
          description: `${response.data.plagiarism_percentage}% similarity found`,
          variant: "destructive"
        });
      } else {
        toast({
          title: "Check Complete",
          description: "Text appears to be original"
        });
      }
    } catch (error) {
      console.error('Error checking plagiarism:', error);
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to check plagiarism",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };
  const getPlagiarismSeverity = (percentage) => {
    if (percentage >= 50) return { color: 'red', label: 'High', icon: XCircle };
    if (percentage >= 20) return { color: 'yellow', label: 'Medium', icon: AlertTriangle };
    return { color: 'green', label: 'Low', icon: CheckCircle };
  };
  const getAIDetectionSeverity = (score) => {
    if (score >= 0.8) return { color: 'red', label: 'Very Likely AI', icon: Brain };
    if (score >= 0.5) return { color: 'yellow', label: 'Possibly AI', icon: Brain };
    return { color: 'green', label: 'Likely Human', icon: CheckCircle };
  };
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-blue-600" />{t("components.plagiarism_ai_detection")}

          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="text-input">{t("components.text_to_check")}</Label>
            <Textarea
              id="text-input"
              placeholder="Paste or type the text you want to check for plagiarism and AI generation..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={10}
              className="font-mono text-sm" />

            <p className="text-sm text-gray-500">
              {text.split(' ').filter((word) => word.length > 0).length}{t("components.words_")}
              {text.length} characters
            </p>
          </div>
          <Button
            onClick={handleCheckPlagiarism}
            disabled={loading || !text.trim()}
            className="w-full">

            {loading ?
            <>
                <LoadingSpinner size="sm" className="mr-2" />{t("components.checking")}

            </> :

            <>
                <Search className="h-4 w-4 mr-2" />{t("components.check_for_plagiarism_ai")}

            </>
            }
          </Button>
        </CardContent>
      </Card>
      {results &&
      <div className="space-y-4">
          {/* Overall Results */}
          <Card>
            <CardHeader>
              <CardTitle>{t("components.detection_results")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Plagiarism Results */}
              <div className="space-y-3">
                <h4 className="font-medium flex items-center gap-2">
                  <FileText className="h-4 w-4" />{t("components.plagiarism_check")}

              </h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">{t("components.similarity_score")}</span>
                    <Badge
                    variant={results.plagiarism_percentage > 20 ? "destructive" : "default"}
                    className="flex items-center gap-1">

                      {getPlagiarismSeverity(results.plagiarism_percentage).icon &&
                    React.createElement(getPlagiarismSeverity(results.plagiarism_percentage).icon, { className: "h-3 w-3" })
                    }
                      {results.plagiarism_percentage}%
                    </Badge>
                  </div>
                  <Progress
                  value={results.plagiarism_percentage}
                  className="h-2"
                  indicatorClassName={`bg-${getPlagiarismSeverity(results.plagiarism_percentage).color}-500`} />

                  <p className="text-sm text-gray-600">
                    {getPlagiarismSeverity(results.plagiarism_percentage).label}{t("components.similarity_detected")}
                </p>
                </div>
              </div>
              {/* AI Detection Results */}
              {results.ai_detection &&
            <div className="space-y-3">
                  <h4 className="font-medium flex items-center gap-2">
                    <Brain className="h-4 w-4" />{t("components.ai_detection")}

              </h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">{t("components.ai_probability")}</span>
                      <Badge
                    variant={results.ai_detection.score > 0.5 ? "destructive" : "default"}
                    className="flex items-center gap-1">

                        {getAIDetectionSeverity(results.ai_detection.score).icon &&
                    React.createElement(getAIDetectionSeverity(results.ai_detection.score).icon, { className: "h-3 w-3" })
                    }
                        {(results.ai_detection.score * 100).toFixed(1)}%
                      </Badge>
                    </div>
                    <Progress
                  value={results.ai_detection.score * 100}
                  className="h-2"
                  indicatorClassName={`bg-${getAIDetectionSeverity(results.ai_detection.score).color}-500`} />

                    <p className="text-sm text-gray-600">
                      {getAIDetectionSeverity(results.ai_detection.score).label}
                    </p>
                  </div>
                </div>
            }
              {/* Summary */}
              <Alert className={results.plagiarism_percentage > 20 || results.ai_detection?.score > 0.5 ? "border-red-200 bg-red-50" : "border-green-200 bg-green-50"}>
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>{t("components.summary")}</AlertTitle>
                <AlertDescription>
                  {results.plagiarism_percentage > 20 || results.ai_detection?.score > 0.5 ?
                <>{t("components.this_submission_requires_review")}

                  {results.plagiarism_percentage > 20 && `${results.plagiarism_percentage}% similarity detected. `}
                      {results.ai_detection?.score > 0.5 && `AI-generated content likely (${(results.ai_detection.score * 100).toFixed(1)}% probability).`}
                    </> :

                "This submission appears to be original and human-written."
                }
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
          {/* Matched Sources */}
          {results.sources && results.sources.length > 0 &&
        <Card>
              <CardHeader>
                <CardTitle>{t("components.matched_sources_")}{results.sources.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {results.sources.map((source, index) =>
              <div
                key={index}
                className="p-3 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => setSelectedSource(selectedSource === index ? null : index)}>

                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <Link2 className="h-4 w-4 text-gray-400" />
                            <h5 className="font-medium text-sm">{source.title || `Source ${index + 1}`}</h5>
                            <Badge variant="outline" className="text-xs">
                              {source.similarity_percentage}{t("components._match")}
                      </Badge>
                          </div>
                          <p className="text-xs text-gray-600">
                            {source.url || source.type || 'Unknown source'}
                          </p>
                        </div>
                      </div>
                      {selectedSource === index && source.matched_text &&
                <div className="mt-3 p-3 bg-gray-50 rounded text-sm">
                          <p className="font-medium text-xs text-gray-600 mb-1">{t("components.matched_text")}</p>
                          <p className="text-gray-700 italic">"{source.matched_text}"</p>
                        </div>
                }
                    </div>
              )}
                </div>
              </CardContent>
            </Card>
        }
          {/* AI Detection Details */}
          {results.ai_detection?.details &&
        <Card>
              <CardHeader>
                <CardTitle>{t("components.ai_detection_details")}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(results.ai_detection.details).map(([key, value]) =>
              <div key={key} className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 capitalize">
                        {key.replace(/_/g, ' ')}
                      </span>
                      <span className="text-sm font-medium">
                        {typeof value === 'number' ? `${(value * 100).toFixed(1)}%` : value}
                      </span>
                    </div>
              )}
                </div>
              </CardContent>
            </Card>
        }
        </div>
      }
    </div>);

};
export default PlagiarismDetector;
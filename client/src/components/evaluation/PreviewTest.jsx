import { useState } from 'react';
import { Clock, ChevronLeft, ChevronRight } from 'lucide-react';
import { QUESTION_TYPES } from '@/lib/constants';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
/**
 * PreviewTest component that shows how the test will appear to users
 */
const PreviewTest = ({ test }) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const { questions, title, description, instructions, time_limit } = test;
  const hasPrevious = currentQuestionIndex > 0;
  const hasNext = currentQuestionIndex < questions.length - 1;
  const goToPrevious = () => {
    if (hasPrevious) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };
  const goToNext = () => {
    if (hasNext) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };
  const currentQuestion = questions[currentQuestionIndex];
  return (
    <div className="container mx-auto">
      <Card className="mb-4 p-6">
        <div className="mb-4">
          <h1 className="text-2xl font-bold">{title || 'Untitled Test'}</h1>
          <p className="text-gray-700 mt-2">{description || 'No description provided'}</p>
        </div>
        {instructions && (
          <div className="mb-4 bg-gray-50 p-4 rounded-lg">
            <h2 className="text-lg font-semibold mb-2">Instructions</h2>
            <p className="text-gray-700">{instructions}</p>
          </div>
        )}
        <div className="flex items-center justify-between">
          <div className="flex items-center text-sm text-gray-600">
            <span>Total Questions: <strong>{questions.length}</strong></span>
          </div>
          {time_limit > 0 && (
            <div className="flex items-center text-sm text-gray-600">
              <Clock className="w-4 h-4 mr-1" />
              <span>Time Limit: <strong>{time_limit} minutes</strong></span>
            </div>
          )}
        </div>
      </Card>
      <div className="mb-4 bg-white p-3 rounded-lg shadow flex items-center justify-between sticky top-0 z-10">
        <Button
          variant="outline"
          size="sm"
          onClick={goToPrevious}
          disabled={!hasPrevious}
          className="flex items-center"
        >
          <ChevronLeft className="w-4 h-4 mr-1" />
          Previous
        </Button>
        <span className="text-sm font-medium">
          Question {currentQuestionIndex + 1} of {questions.length}
        </span>
        <Button
          variant="outline"
          size="sm"
          onClick={goToNext}
          disabled={!hasNext}
          className="flex items-center"
        >
          Next
          <ChevronRight className="w-4 h-4 ml-1" />
        </Button>
      </div>
      <Card className="p-6">
        {currentQuestion ? (
          <div>
            <div className="mb-6">
              <h3 className="text-lg font-medium mb-1">
                Question {currentQuestionIndex + 1} 
                <span className="text-sm font-normal text-gray-500 ml-2">
                  ({currentQuestion.points} {currentQuestion.points === 1 ? 'point' : 'points'})
                </span>
              </h3>
              <p className="text-gray-800">{currentQuestion.question_text || 'No question text provided'}</p>
            </div>
            <div className="space-y-4">
              {currentQuestion.question_type === QUESTION_TYPES.MULTIPLE_CHOICE && (
                <div className="space-y-2">
                  {currentQuestion.options?.map((option, i) => (
                    <label key={i} className="flex items-start p-3 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer">
                      <input
                        type="radio"
                        name={`preview-q-${currentQuestionIndex}`}
                        className="mt-0.5 h-4 w-4 text-primary border-gray-300 focus:ring-primary"
                      />
                      <span className="ml-3">{option.text || `Option ${i + 1}`}</span>
                    </label>
                  ))}
                </div>
              )}
              {currentQuestion.question_type === QUESTION_TYPES.TEXT && (
                <div>
                  <textarea
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-primary focus:border-primary"
                    rows="4"
                    placeholder="Enter your answer here..."
                  ></textarea>
                </div>
              )}
              {currentQuestion.question_type === QUESTION_TYPES.TRUE_FALSE && (
                <div className="space-y-2">
                  <label className="flex items-start p-3 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer">
                    <input
                      type="radio"
                      name={`preview-q-${currentQuestionIndex}`}
                      className="mt-0.5 h-4 w-4 text-primary border-gray-300 focus:ring-primary"
                    />
                    <span className="ml-3">True</span>
                  </label>
                  <label className="flex items-start p-3 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer">
                    <input
                      type="radio"
                      name={`preview-q-${currentQuestionIndex}`}
                      className="mt-0.5 h-4 w-4 text-primary border-gray-300 focus:ring-primary"
                    />
                    <span className="ml-3">False</span>
                  </label>
                </div>
              )}
              {currentQuestion.question_type === QUESTION_TYPES.MATCHING && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <h4 className="font-medium">Left Items</h4>
                    {currentQuestion.matches?.map((match, i) => (
                      <div key={i} className="p-3 rounded-lg border border-gray-200 bg-white">
                        {match.left || `Left Item ${i + 1}`}
                      </div>
                    ))}
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-medium">Right Items</h4>
                    {currentQuestion.matches?.map((match, i) => (
                      <div key={i} className="p-3 rounded-lg border border-gray-200 bg-white">
                        <select className="w-full bg-transparent focus:ring-0 border-0 p-0 focus:outline-none">
                          <option value="">Select a match</option>
                          {currentQuestion.matches?.map((m, j) => (
                            <option key={j} value={j}>
                              {m.right || `Right Item ${j + 1}`}
                            </option>
                          ))}
                        </select>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {currentQuestion.question_type === QUESTION_TYPES.ORDERING && (
                <div className="space-y-2">
                  <h4 className="font-medium">Arrange items in the correct order:</h4>
                  {currentQuestion.order_items?.map((item, i) => (
                    <div key={i} className="flex items-center p-3 rounded-lg border border-gray-200 bg-white">
                      <span className="mr-3 text-gray-500">{i + 1}</span>
                      <select className="w-full bg-transparent focus:ring-0 border-0 p-0 focus:outline-none">
                        <option value="">Select an item</option>
                        {currentQuestion.order_items?.map((orderItem, j) => (
                          <option key={j} value={j}>
                            {orderItem.text || `Item ${j + 1}`}
                          </option>
                        ))}
                      </select>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="text-center p-8 text-gray-500">
            No questions available for preview. Please add at least one question.
          </div>
        )}
      </Card>
      <div className="mt-4 flex justify-between">
        <Button
          variant="outline"
          onClick={goToPrevious}
          disabled={!hasPrevious}
          className="flex items-center"
        >
          <ChevronLeft className="w-4 h-4 mr-1" />
          Previous
        </Button>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">
            Question {currentQuestionIndex + 1} of {questions.length}
          </span>
        </div>
        <Button
          variant="outline"
          onClick={goToNext}
          disabled={!hasNext}
          className="flex items-center"
        >
          Next
          <ChevronRight className="w-4 h-4 ml-1" />
        </Button>
      </div>
    </div>
  );
};
export default PreviewTest;
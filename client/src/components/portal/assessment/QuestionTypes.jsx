import { useState } from 'react';
import { CheckCircle, XCircle, AlertCircle, Info } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
/**
 * Multiple Choice Question Component
 */
export const MultipleChoiceQuestion = ({ 
  question, 
  options, 
  correctAnswer, 
  onAnswer,
  userAnswer,
  showFeedback,
  questionIndex
}) => {
  const isCorrect = userAnswer === correctAnswer;
  return (
    <div className="mb-8">
      <div className="flex items-start mb-4">
        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-medium mr-3 flex-shrink-0">
          {questionIndex + 1}
        </div>
        <div>
          <h3 className="text-lg font-medium mb-1">{question}</h3>
          {showFeedback && (
            <div className={`text-sm ${isCorrect ? 'text-green-600' : 'text-red-600'} flex items-center mb-2`}>
              {isCorrect ? (
                <>
                  <CheckCircle className="h-4 w-4 mr-1" />
                  <span>Correct</span>
                </>
              ) : (
                <>
                  <XCircle className="h-4 w-4 mr-1" />
                  <span>Incorrect</span>
                </>
              )}
            </div>
          )}
        </div>
      </div>
      <div className="space-y-3 pl-11">
        {options.map((option, index) => (
          <div key={index}>
            <button
              className={`w-full text-left p-3 border rounded-md transition-colors flex items-start ${
                userAnswer === index 
                  ? userAnswer === correctAnswer
                    ? 'bg-green-50 border-green-200'
                    : showFeedback
                      ? 'bg-red-50 border-red-200' 
                      : 'bg-primary/10 border-primary/30'
                  : correctAnswer === index && showFeedback
                    ? 'bg-green-50 border-green-200'
                    : 'hover:bg-gray-50'
              }`}
              onClick={() => onAnswer(index)}
              disabled={showFeedback}
            >
              <div className={`w-5 h-5 rounded-full border flex-shrink-0 flex items-center justify-center mr-3 mt-0.5 ${
                userAnswer === index
                  ? userAnswer === correctAnswer 
                    ? 'bg-green-500 border-green-500 text-white'
                    : showFeedback
                      ? 'bg-red-500 border-red-500 text-white'
                      : 'bg-primary border-primary text-white'
                  : correctAnswer === index && showFeedback
                    ? 'bg-green-500 border-green-500 text-white'
                    : 'border-gray-300'
              }`}>
                {userAnswer === index && userAnswer === correctAnswer && showFeedback && <CheckCircle className="h-3 w-3" />}
                {userAnswer === index && userAnswer !== correctAnswer && showFeedback && <XCircle className="h-3 w-3" />}
                {correctAnswer === index && showFeedback && userAnswer !== index && <CheckCircle className="h-3 w-3" />}
              </div>
              <span>{option}</span>
            </button>
          </div>
        ))}
      </div>
      {showFeedback && !isCorrect && (
        <div className="mt-4 pl-11">
          <Card className="p-4 bg-blue-50 border-blue-200">
            <div className="flex">
              <Info className="h-5 w-5 text-blue-500 mr-2 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-blue-700 mb-1">Explanation</p>
                <p className="text-sm text-blue-700">
                  The correct answer is: {options[correctAnswer]}
                </p>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};
/**
 * True/False Question Component
 */
export const TrueFalseQuestion = ({
  question,
  correctAnswer,
  onAnswer,
  userAnswer,
  showFeedback,
  explanation,
  questionIndex
}) => {
  const isCorrect = userAnswer === correctAnswer;
  return (
    <div className="mb-8">
      <div className="flex items-start mb-4">
        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-medium mr-3 flex-shrink-0">
          {questionIndex + 1}
        </div>
        <div>
          <h3 className="text-lg font-medium mb-1">{question}</h3>
          {showFeedback && (
            <div className={`text-sm ${isCorrect ? 'text-green-600' : 'text-red-600'} flex items-center mb-2`}>
              {isCorrect ? (
                <>
                  <CheckCircle className="h-4 w-4 mr-1" />
                  <span>Correct</span>
                </>
              ) : (
                <>
                  <XCircle className="h-4 w-4 mr-1" />
                  <span>Incorrect</span>
                </>
              )}
            </div>
          )}
        </div>
      </div>
      <div className="flex space-x-4 pl-11">
        <button
          className={`flex-1 p-3 border rounded-md transition-colors ${
            userAnswer === true 
              ? userAnswer === correctAnswer
                ? 'bg-green-50 border-green-200'
                : showFeedback
                  ? 'bg-red-50 border-red-200' 
                  : 'bg-primary/10 border-primary/30'
              : correctAnswer === true && showFeedback
                ? 'bg-green-50 border-green-200'
                : 'hover:bg-gray-50'
          }`}
          onClick={() => onAnswer(true)}
          disabled={showFeedback}
        >
          <div className="flex items-center justify-center">
            <div className={`w-5 h-5 rounded-full border flex items-center justify-center mr-2 ${
              userAnswer === true
                ? userAnswer === correctAnswer 
                  ? 'bg-green-500 border-green-500 text-white'
                  : showFeedback
                    ? 'bg-red-500 border-red-500 text-white'
                    : 'bg-primary border-primary text-white'
                : correctAnswer === true && showFeedback
                  ? 'bg-green-500 border-green-500 text-white'
                  : 'border-gray-300'
            }`}>
              {userAnswer === true && userAnswer === correctAnswer && showFeedback && <CheckCircle className="h-3 w-3" />}
              {userAnswer === true && userAnswer !== correctAnswer && showFeedback && <XCircle className="h-3 w-3" />}
              {correctAnswer === true && showFeedback && userAnswer !== true && <CheckCircle className="h-3 w-3" />}
            </div>
            <span>True</span>
          </div>
        </button>
        <button
          className={`flex-1 p-3 border rounded-md transition-colors ${
            userAnswer === false 
              ? userAnswer === correctAnswer
                ? 'bg-green-50 border-green-200'
                : showFeedback
                  ? 'bg-red-50 border-red-200' 
                  : 'bg-primary/10 border-primary/30'
              : correctAnswer === false && showFeedback
                ? 'bg-green-50 border-green-200'
                : 'hover:bg-gray-50'
          }`}
          onClick={() => onAnswer(false)}
          disabled={showFeedback}
        >
          <div className="flex items-center justify-center">
            <div className={`w-5 h-5 rounded-full border flex items-center justify-center mr-2 ${
              userAnswer === false
                ? userAnswer === correctAnswer 
                  ? 'bg-green-500 border-green-500 text-white'
                  : showFeedback
                    ? 'bg-red-500 border-red-500 text-white'
                    : 'bg-primary border-primary text-white'
                : correctAnswer === false && showFeedback
                  ? 'bg-green-500 border-green-500 text-white'
                  : 'border-gray-300'
            }`}>
              {userAnswer === false && userAnswer === correctAnswer && showFeedback && <CheckCircle className="h-3 w-3" />}
              {userAnswer === false && userAnswer !== correctAnswer && showFeedback && <XCircle className="h-3 w-3" />}
              {correctAnswer === false && showFeedback && userAnswer !== false && <CheckCircle className="h-3 w-3" />}
            </div>
            <span>False</span>
          </div>
        </button>
      </div>
      {showFeedback && !isCorrect && explanation && (
        <div className="mt-4 pl-11">
          <Card className="p-4 bg-blue-50 border-blue-200">
            <div className="flex">
              <Info className="h-5 w-5 text-blue-500 mr-2 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-blue-700 mb-1">Explanation</p>
                <p className="text-sm text-blue-700">{explanation}</p>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};
/**
 * Short Answer Question Component
 */
export const ShortAnswerQuestion = ({
  question,
  correctAnswer,
  onAnswer,
  userAnswer = '',
  showFeedback,
  explanation,
  questionIndex
}) => {
  const [inputValue, setInputValue] = useState(userAnswer);
  // Check if the answer is correct
  // This is a simple exact match, but could be extended to handle partial matches
  const isCorrect = () => {
    if (!userAnswer) return false;
    if (Array.isArray(correctAnswer)) {
      return correctAnswer.some(ans => 
        userAnswer.toLowerCase().trim() === ans.toLowerCase().trim()
      );
    }
    return userAnswer.toLowerCase().trim() === correctAnswer.toLowerCase().trim();
  };
  // Handle input change
  const handleChange = (e) => {
    setInputValue(e.target.value);
  };
  // Handle submit
  const handleSubmit = () => {
    onAnswer(inputValue);
  };
  // Handle key press (submit on Enter)
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };
  return (
    <div className="mb-8">
      <div className="flex items-start mb-4">
        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-medium mr-3 flex-shrink-0">
          {questionIndex + 1}
        </div>
        <div>
          <h3 className="text-lg font-medium mb-1">{question}</h3>
          {showFeedback && (
            <div className={`text-sm ${isCorrect() ? 'text-green-600' : 'text-red-600'} flex items-center mb-2`}>
              {isCorrect() ? (
                <>
                  <CheckCircle className="h-4 w-4 mr-1" />
                  <span>Correct</span>
                </>
              ) : (
                <>
                  <XCircle className="h-4 w-4 mr-1" />
                  <span>Incorrect</span>
                </>
              )}
            </div>
          )}
        </div>
      </div>
      <div className="pl-11">
        <div className="mb-3">
          <input
            type="text"
            className={`w-full border rounded-md p-3 ${
              showFeedback
                ? isCorrect()
                  ? 'border-green-300 bg-green-50'
                  : 'border-red-300 bg-red-50'
                : 'border-gray-300 focus:border-primary focus:ring focus:ring-primary/20'
            }`}
            placeholder="Type your answer here..."
            value={inputValue}
            onChange={handleChange}
            onKeyPress={handleKeyPress}
            disabled={showFeedback}
          />
        </div>
        {!showFeedback && (
          <Button onClick={handleSubmit}>
            Submit Answer
          </Button>
        )}
        {showFeedback && (
          <div className="mt-2">
            <Card className="p-4 bg-blue-50 border-blue-200">
              <div className="flex">
                <Info className="h-5 w-5 text-blue-500 mr-2 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-blue-700 mb-1">
                    {isCorrect() ? 'Correct!' : 'Answer'}
                  </p>
                  <p className="text-sm text-blue-700">
                    {Array.isArray(correctAnswer) 
                      ? `Accepted answers: ${correctAnswer.join(', ')}`
                      : `Correct answer: ${correctAnswer}`
                    }
                  </p>
                  {explanation && (
                    <p className="text-sm text-blue-700 mt-2 pt-2 border-t border-blue-200">
                      {explanation}
                    </p>
                  )}
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};
/**
 * Matching Question Component
 */
export const MatchingQuestion = ({
  question,
  items,
  correctMatches,
  onAnswer,
  userMatches = {},
  showFeedback,
  questionIndex
}) => {
  // Calculate if each match is correct
  const getMatchStatus = (itemId) => {
    if (!showFeedback) return null;
    if (!userMatches[itemId]) return 'unmatched';
    return userMatches[itemId] === correctMatches[itemId] ? 'correct' : 'incorrect';
  };
  // Calculate overall correctness
  const isAllCorrect = () => {
    if (!userMatches) return false;
    return Object.keys(correctMatches).every(
      itemId => userMatches[itemId] === correctMatches[itemId]
    );
  };
  // Handle selection of an option
  const [selectedItem, setSelectedItem] = useState(null);
  const [selectedOption, setSelectedOption] = useState(null);
  const handleSelectItem = (itemId) => {
    if (showFeedback) return;
    if (selectedItem === itemId) {
      setSelectedItem(null);
    } else if (selectedOption) {
      // If an option is already selected, make the match
      const newMatches = { ...userMatches, [itemId]: selectedOption };
      onAnswer(newMatches);
      setSelectedItem(null);
      setSelectedOption(null);
    } else {
      setSelectedItem(itemId);
      setSelectedOption(null);
    }
  };
  const handleSelectOption = (optionId) => {
    if (showFeedback) return;
    if (selectedOption === optionId) {
      setSelectedOption(null);
    } else if (selectedItem) {
      // If an item is already selected, make the match
      const newMatches = { ...userMatches, [selectedItem]: optionId };
      onAnswer(newMatches);
      setSelectedItem(null);
      setSelectedOption(null);
    } else {
      setSelectedOption(optionId);
      setSelectedItem(null);
    }
  };
  // Get all options (right column)
  const options = items.map(item => item.match);
  return (
    <div className="mb-8">
      <div className="flex items-start mb-4">
        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-medium mr-3 flex-shrink-0">
          {questionIndex + 1}
        </div>
        <div>
          <h3 className="text-lg font-medium mb-1">{question}</h3>
          {showFeedback && (
            <div className={`text-sm ${isAllCorrect() ? 'text-green-600' : 'text-red-600'} flex items-center mb-2`}>
              {isAllCorrect() ? (
                <>
                  <CheckCircle className="h-4 w-4 mr-1" />
                  <span>All matches correct!</span>
                </>
              ) : (
                <>
                  <XCircle className="h-4 w-4 mr-1" />
                  <span>Some matches are incorrect</span>
                </>
              )}
            </div>
          )}
        </div>
      </div>
      <div className="pl-11">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Left column: Items */}
          <div className="space-y-3">
            <h4 className="font-medium mb-3">Items</h4>
            {items.map((item) => (
              <button
                key={item.id}
                className={`w-full text-left p-3 border rounded-md transition-colors ${
                  selectedItem === item.id
                    ? 'bg-primary/10 border-primary/30'
                    : getMatchStatus(item.id) === 'correct'
                    ? 'bg-green-50 border-green-200'
                    : getMatchStatus(item.id) === 'incorrect'
                    ? 'bg-red-50 border-red-200'
                    : 'hover:bg-gray-50'
                }`}
                onClick={() => handleSelectItem(item.id)}
                disabled={showFeedback}
              >
                <div className="flex justify-between items-center">
                  <span>{item.text}</span>
                  {showFeedback && (
                    <span>
                      {getMatchStatus(item.id) === 'correct' && <CheckCircle className="h-4 w-4 text-green-600" />}
                      {getMatchStatus(item.id) === 'incorrect' && <XCircle className="h-4 w-4 text-red-600" />}
                      {getMatchStatus(item.id) === 'unmatched' && <AlertCircle className="h-4 w-4 text-yellow-600" />}
                    </span>
                  )}
                </div>
                {userMatches[item.id] && (
                  <div className={`text-sm mt-1 ${
                    getMatchStatus(item.id) === 'correct'
                      ? 'text-green-600'
                      : getMatchStatus(item.id) === 'incorrect'
                      ? 'text-red-600'
                      : 'text-gray-500'
                  }`}>
                    Matched with: {options[userMatches[item.id]]}
                  </div>
                )}
              </button>
            ))}
          </div>
          {/* Right column: Options */}
          <div className="space-y-3">
            <h4 className="font-medium mb-3">Matches</h4>
            {options.map((option, index) => (
              <button
                key={index}
                className={`w-full text-left p-3 border rounded-md transition-colors ${
                  selectedOption === index
                    ? 'bg-primary/10 border-primary/30'
                    : 'hover:bg-gray-50'
                }`}
                onClick={() => handleSelectOption(index)}
                disabled={showFeedback}
              >
                {option}
              </button>
            ))}
          </div>
        </div>
        {showFeedback && !isAllCorrect() && (
          <div className="mt-4">
            <Card className="p-4 bg-blue-50 border-blue-200">
              <div className="flex">
                <Info className="h-5 w-5 text-blue-500 mr-2 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-blue-700 mb-2">Correct Matches</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {items.map(item => (
                      <div key={item.id} className="text-sm text-blue-700">
                        <span className="font-medium">{item.text}</span> → {item.match}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};
/**
 * Multiple Answer Question Component (Checkboxes)
 */
export const MultipleAnswerQuestion = ({
  question,
  options,
  correctAnswers,
  onAnswer,
  userAnswers = [],
  showFeedback,
  explanation,
  questionIndex
}) => {
  const isCorrect = () => {
    if (!userAnswers || userAnswers.length === 0) return false;
    if (userAnswers.length !== correctAnswers.length) return false;
    return correctAnswers.every(ans => userAnswers.includes(ans)) &&
           userAnswers.every(ans => correctAnswers.includes(ans));
  };
  // Handle toggle of option
  const toggleOption = (index) => {
    if (showFeedback) return;
    const newAnswers = [...userAnswers];
    const answerIndex = newAnswers.indexOf(index);
    if (answerIndex === -1) {
      newAnswers.push(index);
    } else {
      newAnswers.splice(answerIndex, 1);
    }
    onAnswer(newAnswers);
  };
  return (
    <div className="mb-8">
      <div className="flex items-start mb-4">
        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-medium mr-3 flex-shrink-0">
          {questionIndex + 1}
        </div>
        <div>
          <h3 className="text-lg font-medium mb-1">{question}</h3>
          <p className="text-sm text-gray-500 mb-2">Select all that apply</p>
          {showFeedback && (
            <div className={`text-sm ${isCorrect() ? 'text-green-600' : 'text-red-600'} flex items-center mb-2`}>
              {isCorrect() ? (
                <>
                  <CheckCircle className="h-4 w-4 mr-1" />
                  <span>Correct</span>
                </>
              ) : (
                <>
                  <XCircle className="h-4 w-4 mr-1" />
                  <span>Incorrect</span>
                </>
              )}
            </div>
          )}
        </div>
      </div>
      <div className="space-y-3 pl-11">
        {options.map((option, index) => (
          <div key={index}>
            <button
              className={`w-full text-left p-3 border rounded-md transition-colors flex items-start ${
                userAnswers.includes(index)
                  ? correctAnswers.includes(index) && showFeedback
                    ? 'bg-green-50 border-green-200'
                    : !correctAnswers.includes(index) && showFeedback
                    ? 'bg-red-50 border-red-200' 
                    : 'bg-primary/10 border-primary/30'
                  : correctAnswers.includes(index) && showFeedback
                    ? 'bg-green-50 border-green-200'
                    : 'hover:bg-gray-50'
              }`}
              onClick={() => toggleOption(index)}
              disabled={showFeedback}
            >
              <div className={`w-5 h-5 rounded border flex-shrink-0 flex items-center justify-center mr-3 mt-0.5 ${
                userAnswers.includes(index)
                  ? correctAnswers.includes(index) && showFeedback
                    ? 'bg-green-500 border-green-500 text-white'
                    : !correctAnswers.includes(index) && showFeedback
                    ? 'bg-red-500 border-red-500 text-white'
                    : 'bg-primary border-primary text-white'
                  : correctAnswers.includes(index) && showFeedback
                    ? 'border-green-500'
                    : 'border-gray-300'
              }`}>
                {userAnswers.includes(index) && (
                  <CheckCircle className="h-3 w-3" />
                )}
                {correctAnswers.includes(index) && showFeedback && !userAnswers.includes(index) && (
                  <CheckCircle className="h-3 w-3 text-green-500" />
                )}
              </div>
              <span>{option}</span>
            </button>
          </div>
        ))}
      </div>
      {showFeedback && !isCorrect() && (
        <div className="mt-4 pl-11">
          <Card className="p-4 bg-blue-50 border-blue-200">
            <div className="flex">
              <Info className="h-5 w-5 text-blue-500 mr-2 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-blue-700 mb-1">Correct Answers</p>
                <ul className="list-disc pl-5 text-sm text-blue-700">
                  {correctAnswers.map(ans => (
                    <li key={ans}>{options[ans]}</li>
                  ))}
                </ul>
                {explanation && (
                  <p className="text-sm text-blue-700 mt-2 pt-2 border-t border-blue-200">
                    {explanation}
                  </p>
                )}
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};
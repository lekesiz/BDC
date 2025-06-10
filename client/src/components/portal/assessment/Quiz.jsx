// TODO: i18n - processed
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
  Award,
  Timer } from
'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import {
  MultipleChoiceQuestion,
  TrueFalseQuestion,
  ShortAnswerQuestion,
  MatchingQuestion,
  MultipleAnswerQuestion } from
'./QuestionTypes';
/**
 * Quiz Component
 * Handles quiz flow, timer, scoring, and results
 */import { useTranslation } from "react-i18next";
const Quiz = ({
  quizData,
  onComplete,
  onExit,
  timedMode = false
}) => {const { t } = useTranslation();
  const navigate = useNavigate();
  const [activeQuestion, setActiveQuestion] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [remainingTime, setRemainingTime] = useState(quizData.timeLimit || 0);
  const [reviewMode, setReviewMode] = useState(false);
  // Timer functionality
  useEffect(() => {
    if (!timedMode || quizCompleted || !quizData.timeLimit) return;
    // Start the timer
    const timer = setInterval(() => {
      setRemainingTime((prevTime) => {
        // If time is up, automatically submit the quiz
        if (prevTime <= 1) {
          clearInterval(timer);
          handleCompleteQuiz();
          return 0;
        }
        return prevTime - 1;
      });
    }, 1000);
    // Cleanup on unmount
    return () => clearInterval(timer);
  }, [timedMode, quizCompleted]);
  // Format time remaining
  const formatTimeRemaining = () => {
    const minutes = Math.floor(remainingTime / 60);
    const seconds = remainingTime % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };
  // Handle answering a question
  const handleAnswer = (answer) => {
    setUserAnswers((prev) => ({
      ...prev,
      [activeQuestion]: answer
    }));
  };
  // Navigate to the next question
  const handleNextQuestion = () => {
    if (activeQuestion < quizData.questions.length - 1) {
      setActiveQuestion(activeQuestion + 1);
    } else {
      // If this is the last question
      if (Object.keys(userAnswers).length < quizData.questions.length) {
        // There are unanswered questions
        const confirmedSubmit = window.confirm("You haven't answered all questions. Submit anyway?");
        if (confirmedSubmit) {
          handleCompleteQuiz();
        }
      } else {
        handleCompleteQuiz();
      }
    }
  };
  // Navigate to the previous question
  const handlePreviousQuestion = () => {
    if (activeQuestion > 0) {
      setActiveQuestion(activeQuestion - 1);
    }
  };
  // Complete the quiz
  const handleCompleteQuiz = () => {
    setQuizCompleted(true);
    // Calculate the score
    const score = calculateScore();
    // Provide results to parent component
    onComplete({
      answers: userAnswers,
      score: score.percentage,
      correctCount: score.correct,
      totalQuestions: quizData.questions.length,
      completedAt: new Date(),
      timeSpent: quizData.timeLimit ? quizData.timeLimit - remainingTime : null
    });
    // Show the results screen
    setShowResults(true);
  };
  // Calculate the quiz score
  const calculateScore = () => {
    let correct = 0;
    let total = quizData.questions.length;
    quizData.questions.forEach((question, index) => {
      if (isAnswerCorrect(question, userAnswers[index])) {
        correct++;
      }
    });
    return {
      correct,
      total,
      percentage: Math.round(correct / total * 100)
    };
  };
  // Check if an answer is correct
  const isAnswerCorrect = (question, answer) => {
    if (answer === undefined) return false;
    switch (question.type) {
      case 'multipleChoice':
        return answer === question.correctAnswer;
      case 'trueFalse':
        return answer === question.correctAnswer;
      case 'shortAnswer':
        if (Array.isArray(question.correctAnswer)) {
          return question.correctAnswer.some((ans) =>
          answer.toLowerCase().trim() === ans.toLowerCase().trim()
          );
        }
        return answer.toLowerCase().trim() === question.correctAnswer.toLowerCase().trim();
      case 'matching':
        return Object.keys(question.correctMatches).every(
          (itemId) => answer[itemId] === question.correctMatches[itemId]
        );
      case 'multipleAnswer':
        if (!answer || answer.length === 0) return false;
        if (answer.length !== question.correctAnswers.length) return false;
        return question.correctAnswers.every((ans) => answer.includes(ans)) &&
        answer.every((ans) => question.correctAnswers.includes(ans));
      default:
        return false;
    }
  };
  // Restart the quiz
  const handleRestartQuiz = () => {
    setUserAnswers({});
    setActiveQuestion(0);
    setQuizCompleted(false);
    setShowResults(false);
    setRemainingTime(quizData.timeLimit || 0);
    setReviewMode(false);
  };
  // Enter review mode
  const handleReviewQuiz = () => {
    setReviewMode(true);
    setShowResults(false);
    setActiveQuestion(0);
  };
  // Get the current question
  const currentQuestion = quizData.questions[activeQuestion];
  // Render the results screen
  if (showResults) {
    const score = calculateScore();
    const passingScore = quizData.passingScore || 70;
    const passed = score.percentage >= passingScore;
    return (
      <Card className="p-6">
        <div className="text-center mb-8">
          <div className={`w-24 h-24 mx-auto rounded-full flex items-center justify-center mb-4 ${
          passed ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`
          }>
            {passed ?
            <Award className="h-12 w-12" /> :

            <XCircle className="h-12 w-12" />
            }
          </div>
          <h2 className="text-2xl font-bold mb-2">
            {passed ? 'Congratulations!' : 'Quiz Completed'}
          </h2>
          <p className="text-lg">{t("components.you_scored")}
            <span className="font-semibold">{score.percentage}%</span>
          </p>
          <p className="text-gray-500 mt-1">
            {score.correct}{t("components.out_of")}{score.total}{t("components.questions_correct")}
          </p>
          {timedMode && quizData.timeLimit &&
          <p className="text-gray-500 mt-2">{t("components.time_spent")}
            {Math.floor((quizData.timeLimit - remainingTime) / 60)}m {(quizData.timeLimit - remainingTime) % 60}s
            </p>
          }
        </div>
        <div className="flex flex-col sm:flex-row gap-2 justify-center">
          <Button variant="outline" onClick={handleRestartQuiz}>
            <RotateCcw className="h-4 w-4 mr-2" />{t("components.restart_quiz")}

          </Button>
          <Button variant="outline" onClick={handleReviewQuiz}>
            <CheckCircle className="h-4 w-4 mr-2" />{t("components.review_answers")}

          </Button>
          <Button onClick={onExit}>{t("components.exit")}

          </Button>
        </div>
      </Card>);

  }
  // Render the current question
  return (
    <Card className="p-6">
      {/* Quiz header */}
      <div className="flex justify-between items-center mb-8">
        <h2 className="text-xl font-semibold">{quizData.title}</h2>
        {timedMode && remainingTime > 0 &&
        <div className="flex items-center bg-gray-100 rounded-full px-3 py-1">
            <Timer className="h-4 w-4 mr-2 text-gray-500" />
            <span className="font-medium">{formatTimeRemaining()}</span>
          </div>
        }
      </div>
      {/* Progress indicator */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-500 mb-2">
          <span>{t("components.question")}{activeQuestion + 1} of {quizData.questions.length}</span>
          <span>
            {Object.keys(userAnswers).length} of {quizData.questions.length} answered
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div
            className="bg-primary h-2.5 rounded-full"
            style={{ width: `${Object.keys(userAnswers).length / quizData.questions.length * 100}%` }}>
          </div>
        </div>
      </div>
      {/* Question */}
      <div className="mb-8">
        {currentQuestion.type === 'multipleChoice' &&
        <MultipleChoiceQuestion
          question={currentQuestion.question}
          options={currentQuestion.options}
          correctAnswer={currentQuestion.correctAnswer}
          onAnswer={handleAnswer}
          userAnswer={userAnswers[activeQuestion]}
          showFeedback={reviewMode}
          questionIndex={activeQuestion} />

        }
        {currentQuestion.type === 'trueFalse' &&
        <TrueFalseQuestion
          question={currentQuestion.question}
          correctAnswer={currentQuestion.correctAnswer}
          onAnswer={handleAnswer}
          userAnswer={userAnswers[activeQuestion]}
          showFeedback={reviewMode}
          explanation={currentQuestion.explanation}
          questionIndex={activeQuestion} />

        }
        {currentQuestion.type === 'shortAnswer' &&
        <ShortAnswerQuestion
          question={currentQuestion.question}
          correctAnswer={currentQuestion.correctAnswer}
          onAnswer={handleAnswer}
          userAnswer={userAnswers[activeQuestion]}
          showFeedback={reviewMode}
          explanation={currentQuestion.explanation}
          questionIndex={activeQuestion} />

        }
        {currentQuestion.type === 'matching' &&
        <MatchingQuestion
          question={currentQuestion.question}
          items={currentQuestion.items}
          correctMatches={currentQuestion.correctMatches}
          onAnswer={handleAnswer}
          userMatches={userAnswers[activeQuestion]}
          showFeedback={reviewMode}
          questionIndex={activeQuestion} />

        }
        {currentQuestion.type === 'multipleAnswer' &&
        <MultipleAnswerQuestion
          question={currentQuestion.question}
          options={currentQuestion.options}
          correctAnswers={currentQuestion.correctAnswers}
          onAnswer={handleAnswer}
          userAnswers={userAnswers[activeQuestion]}
          showFeedback={reviewMode}
          explanation={currentQuestion.explanation}
          questionIndex={activeQuestion} />

        }
      </div>
      {/* Navigation buttons */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={handlePreviousQuestion}
          disabled={activeQuestion === 0}>

          <ChevronLeft className="h-4 w-4 mr-2" />{t("components.previous")}

        </Button>
        <div className="flex gap-2">
          {reviewMode &&
          <Button variant="outline" onClick={() => setShowResults(true)}>{t("components.back_to_results")}

          </Button>
          }
          {activeQuestion === quizData.questions.length - 1 && !reviewMode ?
          <Button onClick={handleCompleteQuiz}>{t("components.submit_quiz")}

          </Button> :

          <Button onClick={handleNextQuestion}>{t("components.next")}

            <ChevronRight className="h-4 w-4 ml-2" />
            </Button>
          }
        </div>
      </div>
    </Card>);

};
export default Quiz;
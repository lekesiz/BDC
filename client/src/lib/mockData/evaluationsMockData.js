/**
 * Evaluations Mock Data for Demo and Testing
 */

// Evaluation types
export const EVALUATION_TYPES = {
  QUIZ: 'quiz',
  EXAM: 'exam',
  ASSIGNMENT: 'assignment',
  PROJECT: 'project',
  PRESENTATION: 'presentation',
  PRACTICAL: 'practical'
};

// Evaluation status
export const EVALUATION_STATUS = {
  DRAFT: 'draft',
  PUBLISHED: 'published',
  ACTIVE: 'active',
  COMPLETED: 'completed',
  ARCHIVED: 'archived'
};

// Difficulty levels
export const DIFFICULTY_LEVELS = {
  BEGINNER: 'beginner',
  INTERMEDIATE: 'intermediate',
  ADVANCED: 'advanced',
  EXPERT: 'expert'
};

// Question types
export const QUESTION_TYPES = {
  MULTIPLE_CHOICE: 'multiple_choice',
  TRUE_FALSE: 'true_false',
  SHORT_ANSWER: 'short_answer',
  ESSAY: 'essay',
  MATCHING: 'matching',
  FILL_BLANK: 'fill_blank'
};

// Sample evaluation topics
const evaluationTopics = [
  'Genel Yetenek', 'Matematik', 'Türkçe', 'İngilizce', 'Bilgisayar Bilimleri',
  'Mesleki Bilgi', 'İş Güvenliği', 'İletişim Becerileri', 'Problem Çözme',
  'Yaratıcı Düşünce', 'Liderlik', 'Takım Çalışması', 'Proje Yönetimi',
  'Dijital Okuryazarlık', 'Finansal Okuryazarlık', 'Girişimcilik'
];

// Generate sample questions
const generateQuestions = (count, type = null) => {
  const questions = [];
  const questionTexts = [
    'Aşağıdakilerden hangisi doğrudur?',
    'Bu konuyla ilgili en uygun yaklaşım nedir?',
    'Verilen durumda nasıl davranılmalıdır?',
    'Bu problemin çözümü için hangi adımlar izlenmelidir?',
    'Aşağıdaki kavramlardan hangisi tanımla eşleşir?'
  ];
  
  const options = [
    ['Seçenek A', 'Seçenek B', 'Seçenek C', 'Seçenek D'],
    ['Doğru planlamak', 'Hızlı hareket etmek', 'Beklemek', 'Vazgeçmek'],
    ['Sakin kalmak', 'Acele etmek', 'Panik yapmak', 'Görmezden gelmek'],
    ['Analiz → Plan → Uygulama → Değerlendirme', 'Uygulama → Plan → Analiz', 'Plan → Analiz → Uygulama', 'Değerlendirme → Plan → Uygulama']
  ];

  for (let i = 1; i <= count; i++) {
    const questionType = type || Object.values(QUESTION_TYPES)[Math.floor(Math.random() * Object.values(QUESTION_TYPES).length)];
    const questionText = questionTexts[Math.floor(Math.random() * questionTexts.length)];
    
    let question = {
      id: i,
      type: questionType,
      question: `${i}. ${questionText}`,
      points: Math.floor(Math.random() * 10) + 5, // 5-15 points
      difficulty: Object.values(DIFFICULTY_LEVELS)[Math.floor(Math.random() * Object.values(DIFFICULTY_LEVELS).length)]
    };

    switch (questionType) {
      case QUESTION_TYPES.MULTIPLE_CHOICE:
        question.options = options[Math.floor(Math.random() * options.length)];
        question.correctAnswer = Math.floor(Math.random() * question.options.length);
        break;
      case QUESTION_TYPES.TRUE_FALSE:
        question.options = ['Doğru', 'Yanlış'];
        question.correctAnswer = Math.floor(Math.random() * 2);
        break;
      case QUESTION_TYPES.SHORT_ANSWER:
        question.correctAnswer = 'Örnek kısa cevap';
        question.maxLength = 100;
        break;
      case QUESTION_TYPES.ESSAY:
        question.correctAnswer = 'Örnek essay cevabı...';
        question.maxLength = 1000;
        break;
      case QUESTION_TYPES.FILL_BLANK:
        question.question = `${i}. Bu _____ bir örnek _____ sorusudur.`;
        question.correctAnswer = ['blank1', 'blank2'];
        break;
    }

    questions.push(question);
  }

  return questions;
};

// Generate evaluations
const generateEvaluation = (id) => {
  const topic = evaluationTopics[Math.floor(Math.random() * evaluationTopics.length)];
  const type = Object.values(EVALUATION_TYPES)[Math.floor(Math.random() * Object.values(EVALUATION_TYPES).length)];
  const status = Object.values(EVALUATION_STATUS)[Math.floor(Math.random() * Object.values(EVALUATION_STATUS).length)];
  const difficulty = Object.values(DIFFICULTY_LEVELS)[Math.floor(Math.random() * Object.values(DIFFICULTY_LEVELS).length)];
  
  const createdDate = new Date(2024, Math.floor(Math.random() * 6), Math.floor(Math.random() * 28));
  const questionCount = Math.floor(Math.random() * 20) + 10; // 10-30 questions
  const duration = Math.floor(Math.random() * 90) + 30; // 30-120 minutes
  
  return {
    id,
    title: `${topic} ${type === 'exam' ? 'Sınavı' : type === 'quiz' ? 'Quiz' : 'Değerlendirmesi'}`,
    description: `${topic} alanında ${difficulty} seviyesinde hazırlanmış ${type} değerlendirmesi.`,
    type,
    status,
    difficulty,
    category: topic,
    
    // Basic info
    duration, // minutes
    totalQuestions: questionCount,
    totalPoints: questionCount * 10, // assuming average 10 points per question
    passingScore: 60, // percentage
    maxAttempts: type === 'exam' ? 1 : 3,
    
    // Scheduling
    startDate: createdDate.toISOString(),
    endDate: new Date(createdDate.getTime() + 30 * 24 * 60 * 60 * 1000).toISOString(), // 30 days later
    isActive: status === 'active',
    
    // Visibility and access
    isPublic: Math.random() > 0.3,
    allowRetake: type !== 'exam',
    showResults: Math.random() > 0.2,
    showCorrectAnswers: Math.random() > 0.5,
    
    // Questions
    questions: generateQuestions(questionCount),
    
    // Statistics
    stats: {
      totalAttempts: Math.floor(Math.random() * 100) + 10,
      averageScore: Math.floor(Math.random() * 40) + 60, // 60-100
      passRate: Math.floor(Math.random() * 30) + 70, // 70-100%
      averageTimeSpent: Math.floor(Math.random() * 30) + duration - 15 // near duration
    },
    
    // Settings
    settings: {
      randomizeQuestions: Math.random() > 0.5,
      randomizeOptions: Math.random() > 0.5,
      preventBacktrack: type === 'exam',
      timeLimit: duration,
      showTimer: Math.random() > 0.3,
      fullscreen: type === 'exam',
      preventCopy: type === 'exam'
    },
    
    // Metadata
    createdBy: {
      id: Math.floor(Math.random() * 5) + 1,
      name: 'Ahmet Yılmaz',
      email: 'trainer@bdc.com'
    },
    createdAt: createdDate.toISOString(),
    updatedAt: new Date(createdDate.getTime() + Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
    
    // Tags and categories
    tags: [topic, difficulty, type].filter(Boolean),
    learningOutcomes: [
      `${topic} alanında temel kavramları anlama`,
      'Problem çözme becerileri geliştirme',
      'Analitik düşünce becerileri kazanma'
    ]
  };
};

// Generate evaluation results/attempts
const generateEvaluationResult = (evaluationId, userId) => {
  const startTime = new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000);
  const duration = Math.floor(Math.random() * 90) + 30; // 30-120 minutes
  const endTime = new Date(startTime.getTime() + duration * 60 * 1000);
  
  const totalQuestions = Math.floor(Math.random() * 20) + 10;
  const correctAnswers = Math.floor(Math.random() * totalQuestions);
  const score = Math.round((correctAnswers / totalQuestions) * 100);
  
  return {
    id: Math.floor(Math.random() * 10000),
    evaluationId,
    userId,
    attemptNumber: Math.floor(Math.random() * 3) + 1,
    
    // Timing
    startedAt: startTime.toISOString(),
    completedAt: endTime.toISOString(),
    timeSpent: duration, // minutes
    
    // Scoring
    totalQuestions,
    correctAnswers,
    wrongAnswers: totalQuestions - correctAnswers,
    skippedAnswers: Math.floor(Math.random() * 3),
    score, // percentage
    grade: score >= 90 ? 'A' : score >= 80 ? 'B' : score >= 70 ? 'C' : score >= 60 ? 'D' : 'F',
    passed: score >= 60,
    
    // Detailed results
    questionResults: Array.from({ length: totalQuestions }, (_, i) => ({
      questionId: i + 1,
      userAnswer: Math.floor(Math.random() * 4),
      correctAnswer: Math.floor(Math.random() * 4),
      isCorrect: Math.random() > 0.3,
      points: Math.floor(Math.random() * 10) + 5,
      timeSpent: Math.floor(Math.random() * 3) + 1 // minutes per question
    })),
    
    // Analysis
    categoryScores: {
      'Temel Bilgiler': Math.floor(Math.random() * 40) + 60,
      'Uygulama': Math.floor(Math.random() * 40) + 60,
      'Analiz': Math.floor(Math.random() * 40) + 60,
      'Sentez': Math.floor(Math.random() * 40) + 60
    },
    
    difficultyScores: {
      beginner: Math.floor(Math.random() * 20) + 80,
      intermediate: Math.floor(Math.random() * 30) + 70,
      advanced: Math.floor(Math.random() * 40) + 60
    },
    
    feedback: score >= 90 ? 'Mükemmel performans!' : 
             score >= 80 ? 'Çok iyi çalışma!' :
             score >= 70 ? 'İyi bir performans.' :
             score >= 60 ? 'Geçer not, geliştirilmeli.' : 'Başarısız, tekrar çalışılmalı.',
    
    recommendations: [
      score < 70 ? 'Temel konuları tekrar edin' : 'İleri düzey konulara geçebilirsiniz',
      'Pratik sorular çözün',
      'Zaman yönetiminizi geliştirin'
    ].filter(Boolean)
  };
};

// Generate mock data
export const mockEvaluations = Array.from({ length: 25 }, (_, i) => generateEvaluation(i + 1));

// Generate evaluation results
export const mockEvaluationResults = [];
for (let evalId = 1; evalId <= 25; evalId++) {
  const resultCount = Math.floor(Math.random() * 10) + 5; // 5-15 results per evaluation
  for (let i = 0; i < resultCount; i++) {
    const userId = Math.floor(Math.random() * 30) + 1; // random user
    mockEvaluationResults.push(generateEvaluationResult(evalId, userId));
  }
}

// Evaluation statistics
export const evaluationStats = {
  total: mockEvaluations.length,
  active: mockEvaluations.filter(e => e.status === 'active').length,
  draft: mockEvaluations.filter(e => e.status === 'draft').length,
  completed: mockEvaluations.filter(e => e.status === 'completed').length,
  totalAttempts: mockEvaluationResults.length,
  averageScore: Math.round(mockEvaluationResults.reduce((sum, r) => sum + r.score, 0) / mockEvaluationResults.length),
  passRate: Math.round((mockEvaluationResults.filter(r => r.passed).length / mockEvaluationResults.length) * 100),
  
  byType: Object.values(EVALUATION_TYPES).reduce((acc, type) => {
    acc[type] = mockEvaluations.filter(e => e.type === type).length;
    return acc;
  }, {}),
  
  byDifficulty: Object.values(DIFFICULTY_LEVELS).reduce((acc, level) => {
    acc[level] = mockEvaluations.filter(e => e.difficulty === level).length;
    return acc;
  }, {}),
  
  categoryDistribution: evaluationTopics.reduce((acc, topic) => {
    acc[topic] = mockEvaluations.filter(e => e.category === topic).length;
    return acc;
  }, {})
};

export default mockEvaluations;
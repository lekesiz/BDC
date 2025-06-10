// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // Mock trainer evaluations data for development
export const mockTrainerEvaluations = [
{
  id: 1,
  beneficiary_id: 1,
  trainer_id: 1,
  trainer_name: "Sarah Johnson",
  title: "Q2 Performance Evaluation",
  description: "Comprehensive evaluation of progress over the past quarter, focusing on technical and soft skills development.",
  evaluation_date: "2023-06-15T10:30:00Z",
  competencies: [
  {
    name: "Technical Skills",
    score: 4,
    notes: "Shows excellent progress in technical fundamentals. Has mastered core concepts and is beginning to apply them to more complex scenarios."
  },
  {
    name: "Communication",
    score: 3,
    notes: "Communicates clearly in one-on-one settings. Could benefit from more practice in group presentations and technical documentation."
  },
  {
    name: "Problem Solving",
    score: 4,
    notes: "Demonstrates strong analytical thinking and methodical approach to problem-solving. Successfully tackles complex problems with minimal guidance."
  },
  {
    name: "Teamwork",
    score: 3,
    notes: "Works well with others and contributes effectively to team projects. Could take more initiative in collaborative settings."
  },
  {
    name: "Leadership",
    score: 2,
    notes: "Shows potential but needs more confidence and experience in leading others. Has begun to mentor newer beneficiaries occasionally."
  }],

  strengths: [
  "Excellent analytical thinking and problem decomposition",
  "Quick to master new technical concepts",
  "Reliable and consistent in meeting commitments",
  "Receptive to feedback and implements suggestions effectively"],

  areas_for_improvement: [
  "Public speaking and group presentations",
  "Taking initiative in team settings",
  "Technical documentation and written communication",
  "Mentoring and leadership skills"],

  action_plan: "Over the next quarter, we will focus on developing leadership and communication skills through targeted exercises and opportunities. The beneficiary will be assigned to lead a small project team, with regular coaching and feedback sessions to support growth in this area. Additionally, they will attend our technical writing workshop to improve documentation skills.\n\nWe will continue to build on technical strengths by introducing more advanced concepts and real-world applications, while providing opportunities to mentor newer beneficiaries to develop leadership capabilities.",
  goals: [
  {
    description: "Lead a small project team to completion",
    timeline: "Next 3 months",
    success_criteria: "Successfully deliver project outcomes and receive positive feedback from team members"
  },
  {
    description: "Improve technical documentation skills",
    timeline: "6 weeks",
    success_criteria: "Create comprehensive documentation for at least two projects that meets our quality standards"
  },
  {
    description: "Develop public speaking confidence",
    timeline: "2 months",
    success_criteria: "Deliver three technical presentations to the group with increasing complexity"
  }],

  overall_feedback: "Overall, the beneficiary has shown excellent progress this quarter, particularly in technical skills and problem-solving abilities. They consistently demonstrate a strong work ethic and eagerness to learn, absorbing new concepts quickly and applying them effectively.\n\nWhile technical capabilities are developing well, there are opportunities for growth in leadership and communication areas. With targeted development in these areas, they have excellent potential to advance to more senior roles.\n\nThe beneficiary should be proud of their achievements this quarter and I'm confident they will continue to make significant strides in the coming months, especially if they focus on the identified development areas."
},
{
  id: 2,
  beneficiary_id: 1,
  trainer_id: 2,
  trainer_name: "Michael Chen",
  title: "Technical Assessment: Programming Fundamentals",
  description: "Focused evaluation of programming skills and technical capabilities following the completion of the intermediate programming module.",
  evaluation_date: "2023-04-10T14:15:00Z",
  competencies: [
  {
    name: "Programming Syntax",
    score: 5,
    notes: "Excellent command of language syntax and conventions. Code is clean and follows best practices consistently."
  },
  {
    name: "Algorithmic Thinking",
    score: 4,
    notes: "Strong ability to develop efficient algorithms. Occasionally overlooks edge cases but responds well to hints."
  },
  {
    name: "Debugging Skills",
    score: 3,
    notes: "Competent at identifying and fixing bugs. Would benefit from learning more systematic debugging approaches."
  },
  {
    name: "Code Organization",
    score: 4,
    notes: "Well-structured code with good modularity. Demonstrates understanding of software design principles."
  },
  {
    name: "Technical Communication",
    score: 3,
    notes: "Can explain technical concepts adequately. Documentation could be more comprehensive and clear."
  }],

  strengths: [
  "Exceptional mastery of programming syntax and conventions",
  "Strong algorithm development capabilities",
  "Writes clean, well-organized code",
  "Quick to grasp new programming concepts"],

  areas_for_improvement: [
  "Edge case handling in complex algorithms",
  "Systematic debugging approach",
  "Technical documentation clarity",
  "Testing thoroughness"],

  action_plan: "Based on this technical assessment, we'll focus on advancing the beneficiary's programming skills to the next level. The primary focus will be on developing more robust code through improved testing and debugging practices.\n\nSpecific actions include:\n1. Assigning increasingly complex programming challenges that require thorough edge case handling\n2. Introducing formal testing methodologies and requiring test coverage for all assignments\n3. Providing focused workshops on technical documentation and code commenting\n4. Pairing with a senior developer for regular code reviews and mentorship\n\nProgress will be measured through weekly code reviews and a follow-up assessment in 2 months.",
  goals: [
  {
    description: "Develop and implement a comprehensive testing strategy for a project",
    timeline: "1 month",
    success_criteria: "Achieve 80%+ test coverage with effective test cases that identify potential issues"
  },
  {
    description: "Create well-documented code with clear technical explanations",
    timeline: "Ongoing",
    success_criteria: "Documentation that allows other developers to understand and contribute to the code without additional explanation"
  },
  {
    description: "Build a complex application that handles all edge cases robustly",
    timeline: "2 months",
    success_criteria: "Application that functions correctly under all test conditions without unexpected behavior"
  }],

  overall_feedback: "The beneficiary has demonstrated excellent programming fundamentals and is progressing well through our technical curriculum. Their code is consistently well-structured and they show a natural aptitude for algorithmic thinking.\n\nParticularly impressive is their ability to quickly master new syntax and programming concepts, applying them appropriately in their projects. Their code is clean and readable, showing good adherence to best practices.\n\nTo progress to the advanced level, focus should be placed on developing more robust code through careful consideration of edge cases, comprehensive testing, and clearer documentation. With these improvements, they have the potential to become an exceptional developer capable of handling complex systems and mentoring others."
}];

// Mock API responses for trainer evaluations
export const fetchMockTrainerEvaluations = (beneficiaryId) => {
  return {
    status: 200,
    data: mockTrainerEvaluations.filter((evaluation) =>
    evaluation.beneficiary_id.toString() === beneficiaryId.toString()
    )
  };
};
export const fetchMockTrainerEvaluation = (id) => {
  const evaluation = mockTrainerEvaluations.find((evaluation) => evaluation.id.toString() === id.toString());
  if (evaluation) {
    return {
      status: 200,
      data: evaluation
    };
  }
  return {
    status: 404,
    data: { message: 'Evaluation not found' }
  };
};
export const createMockTrainerEvaluation = (data) => {
  return {
    status: 201,
    data: {
      id: mockTrainerEvaluations.length + 1,
      ...data,
      created_at: new Date().toISOString()
    }
  };
};
export const shareMockTrainerEvaluation = (id) => {
  return {
    status: 200,
    data: { message: 'Evaluation shared successfully' }
  };
};
export const downloadMockTrainerEvaluationPDF = () => {
  return {
    status: 200,
    data: new Blob(['Mock Evaluation PDF content'], { type: 'application/pdf' })
  };
};
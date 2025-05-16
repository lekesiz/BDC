// Mock AI analysis data for session results
export const mockAnalysisData = {
  // Basic info
  session_id: 1,
  test_id: 1,
  user_id: 1,
  created_at: '2023-06-15T16:30:00Z',
  status: 'draft', // 'draft', 'approved', 'rejected'
  trainer_feedback: '',
  
  // Overview information
  summary: "The student demonstrated good overall understanding of core communication concepts, with particular strength in active listening principles. Performance was above the class average for non-verbal communication but showed some gaps in complex communication scenarios. Response patterns indicate a methodical approach with careful consideration of options before selection.",
  
  key_observations: [
    "Consistently strong performance on active listening questions (100% accuracy)",
    "Demonstrated understanding of non-verbal communication importance",
    "Took more time on complex scenario questions, indicating careful analysis",
    "Showed confidence in answering fundamental principles questions",
    "Applied theoretical knowledge effectively to practical scenarios"
  ],
  
  strengths: [
    "Strong grasp of active listening principles and techniques",
    "Good understanding of non-verbal communication importance",
    "Ability to identify effective communication strategies in basic scenarios",
    "Recognition of communication barriers and how to overcome them"
  ],
  
  areas_for_improvement: [
    "Understanding complex multi-stakeholder communication scenarios",
    "Applying communication strategies in high-pressure situations",
    "Identifying subtle non-verbal cues in challenging contexts",
    "Adapting communication style for different audiences"
  ],
  
  learning_style_analysis: "Based on response patterns, the student appears to have a reflective learning style, taking time to analyze information before making decisions. They perform better on questions that allow thoughtful consideration rather than requiring quick responses. This suggests they would benefit from learning materials that provide opportunities for reflection and application, such as case studies and scenarios with guidance.",
  
  peer_comparison: "The student's performance places them in the 75th percentile compared to peers taking the same assessment. They scored significantly above the average in questions related to active listening (92nd percentile) but closer to the median for questions about communication adaptation (58th percentile).",
  
  // Skills analysis
  skills_analysis: {
    "Communication": {
      proficiency: 85,
      analysis: "Strong foundational understanding of communication principles with particular strength in active listening concepts. Can identify effective communication strategies in standard scenarios but shows some uncertainty in complex or ambiguous situations.",
      strengths: [
        "Identifying effective listening techniques",
        "Understanding communication barriers",
        "Recognizing importance of feedback loops"
      ],
      areas_to_work_on: [
        "Adapting communication for different contexts",
        "Handling communication in conflict situations",
        "Identifying subtle non-verbal cues"
      ]
    },
    
    "Leadership": {
      proficiency: 72,
      analysis: "Good understanding of basic leadership communication with room for growth in more advanced concepts. Can recognize effective leadership communication styles but has some gaps in applying them to challenging scenarios.",
      strengths: [
        "Understanding different leadership communication styles",
        "Recognizing the importance of clear messaging",
        "Identifying when to use formal vs. informal communication"
      ],
      areas_to_work_on: [
        "Communicating vision effectively",
        "Adapting leadership style to different team dynamics",
        "Handling difficult conversations as a leader"
      ]
    },
    
    "Critical Thinking": {
      proficiency: 68,
      analysis: "Developing critical thinking skills applied to communication contexts. Shows good analytical ability when given time to process but occasionally misses connections between communication concepts.",
      strengths: [
        "Analyzing straightforward communication scenarios",
        "Recognizing cause-effect relationships in communication",
        "Evaluating effectiveness of communication methods"
      ],
      areas_to_work_on: [
        "Quickly identifying key factors in complex scenarios",
        "Developing more systematic analysis approaches",
        "Making connections between multiple communication concepts"
      ]
    }
  },
  
  // Response patterns
  response_patterns: {
    answer_strategy: "The student shows a methodical approach to answering questions, spending more time on complex scenarios and less on factual recall questions. There's evidence of careful consideration before selecting answers, particularly on multiple-choice questions where similar options are presented.",
    
    key_patterns: [
      "Consistently selects 'active listening' as an important factor across different scenarios",
      "Takes significantly more time on questions involving conflict resolution",
      "Sometimes changes answers before final submission, indicating reflective thinking",
      "More confident (faster response time) on questions about verbal versus non-verbal communication",
      "Performs better on questions with practical examples rather than theoretical concepts"
    ],
    
    question_types: {
      "Multiple Choice": {
        accuracy: 82,
        analysis: "Good performance on multiple choice questions, with careful consideration of options. Occasionally tripped up by similar-sounding distractors."
      },
      "True/False": {
        accuracy: 90,
        analysis: "Strong performance on true/false questions, indicating solid grasp of core concepts and ability to distinguish correct statements from plausible-sounding falsehoods."
      },
      "Matching": {
        accuracy: 75,
        analysis: "Some difficulty with matching questions, particularly when concepts are closely related. Shows good understanding of main concepts but sometimes confuses nuanced distinctions."
      }
    },
    
    time_management: {
      analysis: "Good overall time management with appropriate allocation of time to different question types. Spends more time on complex questions and less on straightforward factual recall, showing good prioritization.",
      avg_time_per_question: 42,
      fastest_question_type: "True/False (24 seconds average)",
      slowest_question_type: "Matching (68 seconds average)"
    }
  },
  
  // Growth trends (comparing to previous assessments)
  growth_trends: {
    longitudinal_analysis: "Comparing to the previous two communication assessments, the student has shown steady improvement in active listening concepts (+15% over 3 months) but progress has plateaued somewhat in adapting communication styles (+5% over the same period). Overall, their growth trajectory is positive but could benefit from targeted intervention in specific areas.",
    
    skill_progress: {
      "Communication": {
        previous: 70,
        current: 85,
        change: 15
      },
      "Leadership": {
        previous: 65,
        current: 72,
        change: 7
      },
      "Critical Thinking": {
        previous: 62,
        current: 68,
        change: 6
      }
    },
    
    mastery_path: {
      description: "Based on current performance and growth rate, the student is on track to achieve mastery in core communication concepts within 3-4 months, but may require additional support to reach advanced proficiency in leadership communication.",
      milestones: [
        {
          title: "Foundation Concepts",
          description: "Understanding basic communication principles and active listening techniques",
          achieved: true
        },
        {
          title: "Practical Application",
          description: "Applying communication concepts to standard workplace scenarios",
          achieved: true
        },
        {
          title: "Complex Scenarios",
          description: "Navigating multi-stakeholder communication challenges and conflicts",
          achieved: false
        },
        {
          title: "Leadership Communication",
          description: "Developing and implementing strategic communication as a leader",
          achieved: false
        },
        {
          title: "Advanced Mastery",
          description: "Adapting communication approaches for specialized contexts and challenges",
          achieved: false
        }
      ]
    },
    
    learning_velocity: {
      analysis: "The student is learning at an above-average pace compared to peers, particularly in fundamental concepts. Their learning velocity has increased 15% since the previous assessment cycle, suggesting effective engagement with materials and practice.",
      current_velocity: 8.5,
      projected_timeline: 4,
      peer_comparison: 72
    }
  },
  
  // Recommendations
  recommendations: {
    next_steps: [
      {
        title: "Focus on Complex Communication Scenarios",
        description: "Practice with multi-stakeholder case studies that require adapting communication approaches for different audiences simultaneously."
      },
      {
        title: "Develop Conflict Resolution Skills",
        description: "Work through communication scenarios involving differing viewpoints and emotional components to strengthen adaptive communication."
      },
      {
        title: "Practice Leadership Communication",
        description: "Engage in role-playing exercises as a team leader to practice articulating vision and providing constructive feedback."
      },
      {
        title: "Strengthen Critical Analysis",
        description: "Analyze real-world communication breakdowns to identify what went wrong and how to improve outcomes."
      }
    ],
    
    resources: [
      {
        title: "Navigating Difficult Conversations",
        description: "Video course on handling challenging communication scenarios with practical techniques",
        type: "video",
        duration: "45 min",
        skill: "Communication"
      },
      {
        title: "Leadership Communication Case Studies",
        description: "Collection of real-world examples with guided analysis questions",
        type: "article",
        duration: "60 min",
        skill: "Leadership"
      },
      {
        title: "Communication Styles Assessment",
        description: "Interactive exercise to identify personal communication patterns and areas for development",
        type: "exercise",
        duration: "30 min",
        skill: "Self-awareness"
      },
      {
        title: "Advanced Communication Strategies",
        description: "Comprehensive course covering complex communication contexts and techniques",
        type: "course",
        duration: "4 hours",
        skill: "Communication"
      }
    ],
    
    learning_plan: {
      description: "The following 4-week plan is designed to address key development areas while building on existing strengths in active listening and basic communication concepts.",
      weekly_focus: [
        {
          week: 1,
          focus: "Complex Communication Scenarios",
          description: "Practice analyzing and responding to multi-stakeholder communication challenges, focusing on identifying key stakeholders and their needs.",
          skills: ["Critical Thinking", "Communication"],
          hours: 4
        },
        {
          week: 2,
          focus: "Conflict Resolution Communication",
          description: "Learn techniques for de-escalation, neutral language, and effective questioning in conflict situations.",
          skills: ["Conflict Resolution", "Active Listening"],
          hours: 5
        },
        {
          week: 3,
          focus: "Leadership Communication",
          description: "Develop skills for clear vision communication, delegating effectively, and providing constructive feedback.",
          skills: ["Leadership", "Coaching"],
          hours: 4
        },
        {
          week: 4,
          focus: "Communication Adaptation",
          description: "Practice adapting communication style for different audiences and contexts, including cultural considerations.",
          skills: ["Adaptability", "Cultural Intelligence"],
          hours: 3
        }
      ]
    }
  }
};

// Mock API response for analysis
export const getMockAnalysis = (id) => {
  return {
    status: 200,
    data: mockAnalysisData
  };
};

// Mock API response for generating analysis
export const generateMockAnalysis = () => {
  return {
    status: 200,
    data: {
      ...mockAnalysisData,
      created_at: new Date().toISOString()
    }
  };
};

// Mock API response for updating analysis status
export const updateMockAnalysisStatus = (id, data) => {
  return {
    status: 200,
    data: {
      ...mockAnalysisData,
      status: data.status,
      trainer_feedback: data.trainer_feedback,
      updated_at: new Date().toISOString()
    }
  };
};

// Mock API response for updating trainer feedback
export const updateMockTrainerFeedback = (id, data) => {
  return {
    status: 200,
    data: {
      ...mockAnalysisData,
      trainer_feedback: data.trainer_feedback,
      updated_at: new Date().toISOString()
    }
  };
};
export const reportTemplates = [
  {
    id: 'executive-summary',
    name: 'Executive Summary',
    description: 'High-level overview with key metrics and insights',
    category: 'Management',
    sections: [
      {
        id: 'section-exec-1',
        title: 'Key Performance Indicators',
        layout: 'grid',
        widgets: [
          {
            id: 'widget-1',
            type: 'kpi',
            config: {
              title: 'Total Beneficiaries',
              value: 1250,
              unit: '',
              trend: 'up',
              trendValue: 12.5,
              color: '#3b82f6',
              icon: 'users'
            }
          },
          {
            id: 'widget-2',
            type: 'kpi',
            config: {
              title: 'Completion Rate',
              value: 87,
              unit: '%',
              trend: 'up',
              trendValue: 5.2,
              color: '#10b981',
              showProgress: true
            }
          },
          {
            id: 'widget-3',
            type: 'kpi',
            config: {
              title: 'Active Programs',
              value: 24,
              unit: '',
              trend: 'neutral',
              trendValue: 0,
              color: '#f59e0b',
              icon: 'book'
            }
          }
        ]
      },
      {
        id: 'section-exec-2',
        title: 'Performance Trends',
        layout: 'single',
        widgets: [
          {
            id: 'widget-4',
            type: 'chart',
            config: {
              title: 'Monthly Progress Overview',
              chartType: 'line',
              showLegend: true,
              showGrid: true,
              colors: ['#3b82f6', '#10b981', '#f59e0b']
            }
          }
        ]
      },
      {
        id: 'section-exec-3',
        title: 'Program Distribution',
        layout: 'two-column',
        widgets: [
          {
            id: 'widget-5',
            type: 'chart',
            config: {
              title: 'Beneficiaries by Program',
              chartType: 'pie',
              showLegend: true,
              colors: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
            }
          },
          {
            id: 'widget-6',
            type: 'chart',
            config: {
              title: 'Completion Rates by Program',
              chartType: 'bar',
              showLegend: false,
              showGrid: true,
              colors: ['#10b981']
            }
          }
        ]
      },
      {
        id: 'section-exec-4',
        title: 'Executive Notes',
        layout: 'single',
        widgets: [
          {
            id: 'widget-7',
            type: 'text',
            config: {
              content: '<h3>Summary</h3><p>This report provides a comprehensive overview of our training programs and beneficiary progress for the current period.</p><h3>Key Highlights</h3><ul><li>12.5% increase in total beneficiaries</li><li>87% average completion rate across all programs</li><li>Strong performance in technical skills training</li></ul>',
              fontSize: 'base',
              alignment: 'left'
            }
          }
        ]
      }
    ],
    dataSources: ['beneficiaries', 'programs', 'analytics'],
    layout: 'single'
  },
  {
    id: 'detailed-analysis',
    name: 'Detailed Analysis',
    description: 'In-depth analysis with comprehensive data tables and charts',
    category: 'Analytics',
    sections: [
      {
        id: 'section-detail-1',
        title: 'Overview Metrics',
        layout: 'grid',
        widgets: [
          {
            id: 'widget-d1',
            type: 'kpi',
            config: {
              title: 'Total Enrollment',
              value: 3456,
              trend: 'up',
              trendValue: 8.7,
              color: '#3b82f6'
            }
          },
          {
            id: 'widget-d2',
            type: 'kpi',
            config: {
              title: 'Average Score',
              value: 78.5,
              unit: '%',
              trend: 'up',
              trendValue: 3.2,
              color: '#10b981',
              showProgress: true
            }
          },
          {
            id: 'widget-d3',
            type: 'kpi',
            config: {
              title: 'Dropout Rate',
              value: 4.2,
              unit: '%',
              trend: 'down',
              trendValue: -1.5,
              color: '#ef4444'
            }
          }
        ]
      },
      {
        id: 'section-detail-2',
        title: 'Beneficiary Performance Data',
        layout: 'single',
        widgets: [
          {
            id: 'widget-d4',
            type: 'table',
            config: {
              title: 'Detailed Beneficiary Progress',
              pageSize: 15,
              sortable: true,
              filterable: true,
              exportable: true
            }
          }
        ]
      },
      {
        id: 'section-detail-3',
        title: 'Comparative Analysis',
        layout: 'two-column',
        widgets: [
          {
            id: 'widget-d5',
            type: 'chart',
            config: {
              title: 'Program Comparison',
              chartType: 'radar',
              showLegend: true
            }
          },
          {
            id: 'widget-d6',
            type: 'chart',
            config: {
              title: 'Year-over-Year Growth',
              chartType: 'area',
              showLegend: true,
              showGrid: true
            }
          }
        ]
      },
      {
        id: 'section-detail-4',
        title: 'Skill Assessment Matrix',
        layout: 'single',
        widgets: [
          {
            id: 'widget-d7',
            type: 'table',
            config: {
              title: 'Skills Progress by Category',
              variant: 'pivot',
              sortable: true
            }
          }
        ]
      }
    ],
    dataSources: ['beneficiaries', 'evaluations', 'analytics', 'performance'],
    layout: 'single'
  },
  {
    id: 'progress-report',
    name: 'Progress Report',
    description: 'Track progress and milestones for beneficiaries and programs',
    category: 'Tracking',
    sections: [
      {
        id: 'section-prog-1',
        title: 'Progress Summary',
        layout: 'grid',
        widgets: [
          {
            id: 'widget-p1',
            type: 'kpi',
            config: {
              title: 'On Track',
              value: 72,
              unit: '%',
              trend: 'up',
              trendValue: 5,
              color: '#10b981',
              showProgress: true
            }
          },
          {
            id: 'widget-p2',
            type: 'kpi',
            config: {
              title: 'At Risk',
              value: 18,
              unit: '%',
              trend: 'down',
              trendValue: -3,
              color: '#f59e0b',
              showProgress: true
            }
          },
          {
            id: 'widget-p3',
            type: 'kpi',
            config: {
              title: 'Behind Schedule',
              value: 10,
              unit: '%',
              trend: 'down',
              trendValue: -2,
              color: '#ef4444',
              showProgress: true
            }
          }
        ]
      },
      {
        id: 'section-prog-2',
        title: 'Progress Timeline',
        layout: 'single',
        widgets: [
          {
            id: 'widget-p4',
            type: 'chart',
            config: {
              title: 'Monthly Progress Trend',
              chartType: 'line',
              showLegend: true,
              showGrid: true
            }
          }
        ]
      },
      {
        id: 'section-prog-3',
        title: 'Individual Progress Tracking',
        layout: 'single',
        widgets: [
          {
            id: 'widget-p5',
            type: 'table',
            config: {
              title: 'Beneficiary Progress Details',
              pageSize: 20,
              sortable: true,
              filterable: true
            }
          }
        ]
      }
    ],
    dataSources: ['beneficiaries', 'programs', 'analytics'],
    layout: 'single'
  },
  {
    id: 'trainer-evaluation',
    name: 'Trainer Evaluation',
    description: 'Comprehensive trainer performance and feedback analysis',
    category: 'HR',
    sections: [
      {
        id: 'section-trainer-1',
        title: 'Trainer Performance Overview',
        layout: 'grid',
        widgets: [
          {
            id: 'widget-t1',
            type: 'kpi',
            config: {
              title: 'Average Rating',
              value: 4.5,
              unit: '/5',
              trend: 'up',
              trendValue: 0.3,
              color: '#10b981',
              icon: 'star'
            }
          },
          {
            id: 'widget-t2',
            type: 'kpi',
            config: {
              title: 'Sessions Conducted',
              value: 324,
              trend: 'up',
              trendValue: 12,
              color: '#3b82f6'
            }
          },
          {
            id: 'widget-t3',
            type: 'kpi',
            config: {
              title: 'Student Success Rate',
              value: 89,
              unit: '%',
              trend: 'up',
              trendValue: 4,
              color: '#8b5cf6',
              showProgress: true
            }
          }
        ]
      },
      {
        id: 'section-trainer-2',
        title: 'Rating Distribution',
        layout: 'two-column',
        widgets: [
          {
            id: 'widget-t4',
            type: 'chart',
            config: {
              title: 'Trainer Ratings by Category',
              chartType: 'radar',
              showLegend: true
            }
          },
          {
            id: 'widget-t5',
            type: 'chart',
            config: {
              title: 'Rating Trends',
              chartType: 'line',
              showLegend: true,
              showGrid: true
            }
          }
        ]
      },
      {
        id: 'section-trainer-3',
        title: 'Detailed Evaluations',
        layout: 'single',
        widgets: [
          {
            id: 'widget-t6',
            type: 'table',
            config: {
              title: 'Trainer Performance Details',
              sortable: true,
              filterable: true
            }
          }
        ]
      }
    ],
    dataSources: ['trainers', 'evaluations', 'analytics'],
    layout: 'single'
  },
  {
    id: 'financial-summary',
    name: 'Financial Summary',
    description: 'Budget utilization and financial metrics',
    category: 'Finance',
    sections: [
      {
        id: 'section-fin-1',
        title: 'Financial Overview',
        layout: 'grid',
        widgets: [
          {
            id: 'widget-f1',
            type: 'kpi',
            config: {
              title: 'Total Budget',
              value: 250000,
              unit: '$',
              color: '#3b82f6',
              icon: 'dollar'
            }
          },
          {
            id: 'widget-f2',
            type: 'kpi',
            config: {
              title: 'Utilized',
              value: 187500,
              unit: '$',
              trend: 'up',
              trendValue: 75,
              color: '#10b981'
            }
          },
          {
            id: 'widget-f3',
            type: 'kpi',
            config: {
              title: 'Remaining',
              value: 62500,
              unit: '$',
              color: '#f59e0b'
            }
          }
        ]
      },
      {
        id: 'section-fin-2',
        title: 'Budget Distribution',
        layout: 'two-column',
        widgets: [
          {
            id: 'widget-f4',
            type: 'chart',
            config: {
              title: 'Budget by Category',
              chartType: 'donut',
              showLegend: true
            }
          },
          {
            id: 'widget-f5',
            type: 'chart',
            config: {
              title: 'Monthly Expenditure',
              chartType: 'bar',
              showGrid: true
            }
          }
        ]
      }
    ],
    dataSources: ['performance', 'analytics'],
    layout: 'single'
  },
  {
    id: 'attendance-report',
    name: 'Attendance Report',
    description: 'Track attendance patterns and participation rates',
    category: 'Operations',
    sections: [
      {
        id: 'section-att-1',
        title: 'Attendance Overview',
        layout: 'grid',
        widgets: [
          {
            id: 'widget-a1',
            type: 'kpi',
            config: {
              title: 'Average Attendance',
              value: 92,
              unit: '%',
              trend: 'up',
              trendValue: 3,
              color: '#10b981',
              showProgress: true
            }
          },
          {
            id: 'widget-a2',
            type: 'kpi',
            config: {
              title: 'Sessions This Month',
              value: 156,
              trend: 'up',
              trendValue: 12,
              color: '#3b82f6'
            }
          },
          {
            id: 'widget-a3',
            type: 'kpi',
            config: {
              title: 'Perfect Attendance',
              value: 234,
              unit: ' students',
              color: '#8b5cf6'
            }
          }
        ]
      },
      {
        id: 'section-att-2',
        title: 'Attendance Trends',
        layout: 'single',
        widgets: [
          {
            id: 'widget-a4',
            type: 'chart',
            config: {
              title: 'Daily Attendance Pattern',
              chartType: 'area',
              showLegend: true,
              showGrid: true
            }
          }
        ]
      },
      {
        id: 'section-att-3',
        title: 'Program-wise Attendance',
        layout: 'single',
        widgets: [
          {
            id: 'widget-a5',
            type: 'table',
            config: {
              title: 'Attendance by Program',
              sortable: true,
              pageSize: 10
            }
          }
        ]
      }
    ],
    dataSources: ['analytics', 'programs', 'beneficiaries'],
    layout: 'single'
  },
  {
    id: 'custom-blank',
    name: 'Blank Report',
    description: 'Start with a blank canvas',
    category: 'Custom',
    sections: [],
    dataSources: [],
    layout: 'single'
  }
];
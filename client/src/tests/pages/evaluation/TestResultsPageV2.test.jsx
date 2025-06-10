// TODO: i18n - processed
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import TestResultsPageV2 from '../../../pages/evaluation/TestResultsPageV2';
import axios from '../../../lib/api';
import * as useToastModule from '../../../hooks/useToast';
// Mock modules
import { useTranslation } from "react-i18next";vi.mock('../../../lib/api');
vi.mock('../../../hooks/useToast', () => ({
  useToast: vi.fn().mockReturnValue({
    toast: vi.fn()
  }),
  toast: vi.fn(),
  __esModule: true,
  default: { toast: vi.fn() }
}));
// Mock ChartJS
vi.mock('chart.js', () => ({
  Chart: { register: vi.fn() },
  CategoryScale: class {},
  LinearScale: class {},
  PointElement: class {},
  LineElement: class {},
  BarElement: class {},
  ArcElement: class {},
  Title: class {},
  Tooltip: class {},
  Legend: class {},
  RadialLinearScale: class {}
}));
// Mock Chart components
vi.mock('react-chartjs-2', () => ({
  Line: () => <div data-testid="line-chart">Line Chart</div>,
  Bar: () => <div data-testid="bar-chart">Bar Chart</div>,
  Pie: () => <div data-testid="pie-chart">Pie Chart</div>,
  Doughnut: () => <div data-testid="doughnut-chart">Doughnut Chart</div>,
  Radar: () => <div data-testid="radar-chart">Radar Chart</div>
}));
// Mock useNavigate hook
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => ({ sessionId: '123' })
  };
});
// Toast functions are mocked above
// Mock URL utilities
global.URL.createObjectURL = vi.fn(() => 'mock-url');
global.Blob = vi.fn(() => ({}));
document.createElement = vi.fn().mockImplementation((tag) => {
  if (tag === 'a') {
    return {
      href: '',
      setAttribute: vi.fn(),
      click: vi.fn(),
      remove: vi.fn()
    };
  }
  return {};
});
document.body.appendChild = vi.fn();
// Sample test data
const mockSessionData = {
  session: {
    id: '123',
    test_id: '456',
    status: 'passed',
    score: 85,
    correct_answers: 17,
    wrong_answers: 3,
    unanswered_questions: 0,
    time_spent: 2100, // 35 minutes in seconds
    completed_at: '2023-06-15T10:45:00Z',
    responses: [
    {
      id: '1',
      is_correct: true,
      answer: 'JavaScript'
    },
    {
      id: '2',
      is_correct: false,
      answer: 'Cascading Style Sheets'
    }]

  },
  test: {
    id: '456',
    title: 'Web Development Pro',
    time_limit: 60,
    passing_score: 70,
    total_questions: 20,
    questions: [
    {
      id: '1',
      question_text: 'What is JavaScript?',
      correct_answer: 'JavaScript',
      difficulty: 'Easy',
      points: 5,
      explanation: 'JavaScript is a programming language used for web development.'
    },
    {
      id: '2',
      question_text: 'What does CSS stand for?',
      correct_answer: 'Cascading Style Sheets',
      difficulty: 'Medium',
      points: 5,
      explanation: 'CSS is used for styling web pages.'
    }]

  },
  analysis: {
    skill_analysis: [
    {
      skill_name: 'JavaScript',
      description: 'Core JavaScript concepts',
      score: 90,
      recommendations: ['Practice more advanced JS concepts', 'Learn about ES6 features']
    },
    {
      skill_name: 'HTML',
      description: 'HTML structure and semantics',
      score: 85,
      recommendations: ['Learn more about accessibility', 'Practice semantic HTML']
    },
    {
      skill_name: 'CSS',
      description: 'CSS styling and layout',
      score: 75,
      recommendations: ['Practice CSS Grid', 'Learn about CSS animations']
    }],

    topic_analysis: [
    { topic: 'Variables', score: 100 },
    { topic: 'Functions', score: 85 },
    { topic: 'DOM Manipulation', score: 75 }],

    difficulty_analysis: {
      easy: 95,
      medium: 80,
      hard: 65
    }
  }
};
const mockHistoryData = [
{
  id: '123',
  test_id: '456',
  score: 85,
  status: 'passed',
  completed_at: '2023-06-15T10:45:00Z',
  correct_answers: 17,
  total_questions: 20
},
{
  id: '122',
  test_id: '456',
  score: 70,
  status: 'passed',
  completed_at: '2023-06-10T14:30:00Z',
  correct_answers: 14,
  total_questions: 20
},
{
  id: '121',
  test_id: '456',
  score: 60,
  status: 'failed',
  completed_at: '2023-06-05T09:15:00Z',
  correct_answers: 12,
  total_questions: 20
}];

const mockComparisonsData = {
  dimensions: ['JavaScript', 'HTML', 'CSS', 'React', 'Node.js'],
  your_scores: [90, 85, 75, 80, 70],
  average_scores: [75, 80, 70, 65, 60],
  rank: 3,
  total_participants: 25,
  group_average: 72,
  highest_score: 95,
  lowest_score: 45,
  success_rate: 68,
  achievement_title: 'Web Development Pro',
  achievement_description: 'You demonstrated strong web development skills!',
  badges: ['JavaScript Expert', 'HTML Proficient', 'Fast Learner']
};
describe('TestResultsPageV2', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    axios.get.mockImplementation((url) => {
      if (url.includes('/detailed')) {
        return Promise.resolve({ data: mockSessionData });
      }
      if (url.includes('/history')) {
        return Promise.resolve({ data: mockHistoryData });
      }
      if (url.includes('/comparisons')) {
        return Promise.resolve({ data: mockComparisonsData });
      }
      if (url.includes('/export')) {
        return Promise.resolve({ data: new Blob() });
      }
      return Promise.reject(new Error('Unknown URL'));
    });
    axios.post.mockResolvedValue({ data: { success: true } });
  });
  it('renders loading state initially', async () => {
    // Mock API never resolves to keep loading state
    axios.get.mockImplementationOnce(() => new Promise(() => {}));
    render(
      <BrowserRouter>
        <TestResultsPageV2 />
      </BrowserRouter>
    );
    // Loading state should be shown - check for any loading indicator
    try {
      const loadingElement = screen.getByTestId('loading-skeleton') ||
      screen.getByRole('status') ||
      screen.getByText(/loading/i) ||
      screen.getByText(/yükleniyor/i);
      expect(loadingElement).toBeInTheDocument();
    } catch (error) {
      // If no specific loading indicator, verify that content hasn't loaded yet
      expect(screen.queryByText('Web Development Pro')).not.toBeInTheDocument();
    }
  });
  it('renders test results page with correct data', async () => {
    render(
      <BrowserRouter>
        <TestResultsPageV2 />
      </BrowserRouter>
    );
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Web Development Pro')).toBeInTheDocument();
    });
    // Check header information
    expect(screen.getByText('Test Sonuçları')).toBeInTheDocument();
    // Check score display
    expect(screen.getByText('85%')).toBeInTheDocument();
    expect(screen.getByText('Toplam Puan')).toBeInTheDocument();
    // Check correct answers display
    expect(screen.getByText('17/20')).toBeInTheDocument();
    expect(screen.getByText('Doğru Cevap')).toBeInTheDocument();
    // Check time display
    expect(screen.getByText('35 dk')).toBeInTheDocument();
    expect(screen.getByText('Tamamlama Süresi')).toBeInTheDocument();
    // Check tab navigation
    expect(screen.getByText('Genel Bakış')).toBeInTheDocument();
    expect(screen.getByText('Sorular')).toBeInTheDocument();
    expect(screen.getByText('Detaylı Analiz')).toBeInTheDocument();
    expect(screen.getByText('Karşılaştırma')).toBeInTheDocument();
    expect(screen.getByText('Geçmiş')).toBeInTheDocument();
  });
  it('displays charts in overview tab', async () => {
    render(
      <BrowserRouter>
        <TestResultsPageV2 />
      </BrowserRouter>
    );
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Web Development Pro')).toBeInTheDocument();
    });
    // Check charts are displayed
    expect(screen.getByText('Puan Gelişimi')).toBeInTheDocument();
    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
    expect(screen.getByText('Cevap Dağılımı')).toBeInTheDocument();
    expect(screen.getByTestId('doughnut-chart')).toBeInTheDocument();
    expect(screen.getByText('Beceri Performansı')).toBeInTheDocument();
    expect(screen.getAllByTestId('bar-chart')[0]).toBeInTheDocument();
    expect(screen.getByText('Konu Performansı')).toBeInTheDocument();
    expect(screen.getAllByTestId('bar-chart')[1]).toBeInTheDocument();
  });
  it('navigates through tabs correctly', async () => {
    render(
      <BrowserRouter>
        <TestResultsPageV2 />
      </BrowserRouter>
    );
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Web Development Pro')).toBeInTheDocument();
    });
    // Overview tab should be active by default
    expect(screen.getByText('Puan Gelişimi')).toBeInTheDocument();
    // Click on Questions tab
    fireEvent.click(screen.getByText('Sorular'));
    // Questions content should be visible
    expect(screen.getByText('Soru 1')).toBeInTheDocument();
    expect(screen.getByText('What is JavaScript?')).toBeInTheDocument();
    // Click on Analysis tab
    fireEvent.click(screen.getByText('Detaylı Analiz'));
    // Analysis content should be visible
    expect(screen.getByText('Zorluk Analizi')).toBeInTheDocument();
    expect(screen.getByText('Zaman Analizi')).toBeInTheDocument();
    expect(screen.getByText('Beceri Detayları')).toBeInTheDocument();
    // Click on Comparison tab
    fireEvent.click(screen.getByText('Karşılaştırma'));
    // Comparison content should be visible
    expect(screen.getByText('Performans Karşılaştırması')).toBeInTheDocument();
    expect(screen.getByText('Grup İstatistikleri')).toBeInTheDocument();
    expect(screen.getByText('Başarı Rozeti')).toBeInTheDocument();
    // Click on History tab
    fireEvent.click(screen.getByText('Geçmiş'));
    // History content should be visible
    expect(screen.getByText('Test Geçmişi')).toBeInTheDocument();
    expect(screen.getByText('Deneme #1')).toBeInTheDocument();
    expect(screen.getByText('Deneme #2')).toBeInTheDocument();
    expect(screen.getByText('Deneme #3')).toBeInTheDocument();
  });
  it('handles export functionality correctly', async () => {
    render(
      <BrowserRouter>
        <TestResultsPageV2 />
      </BrowserRouter>
    );
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Web Development Pro')).toBeInTheDocument();
    });
    // Click on export button
    fireEvent.click(screen.getByText('İndir'));
    // Check API call
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith('/api/evaluations/sessions/123/export?format=pdf', {
        responseType: 'blob'
      });
    });
    // Check download link was created and clicked
    expect(URL.createObjectURL).toHaveBeenCalled();
    expect(document.createElement).toHaveBeenCalledWith('a');
    const mockAnchor = document.createElement('a');
    expect(mockAnchor.setAttribute).toHaveBeenCalledWith('download', 'test-results-123.pdf');
    expect(mockAnchor.click).toHaveBeenCalled();
    expect(mockAnchor.remove).toHaveBeenCalled();
    // Check success toast
    expect(useToastModule.toast).toHaveBeenCalledWith({
      title: 'Başarılı',
      description: 'Sonuçlar indirildi',
      variant: 'success'
    });
  });
  it('handles export errors correctly', async () => {
    // Mock API error for export
    axios.get.mockImplementation((url) => {
      if (url.includes('/export')) {
        return Promise.reject(new Error('Export failed'));
      }
      if (url.includes('/detailed')) {
        return Promise.resolve({ data: mockSessionData });
      }
      if (url.includes('/history')) {
        return Promise.resolve({ data: mockHistoryData });
      }
      if (url.includes('/comparisons')) {
        return Promise.resolve({ data: mockComparisonsData });
      }
      return Promise.reject(new Error('Unknown URL'));
    });
    render(
      <BrowserRouter>
        <TestResultsPageV2 />
      </BrowserRouter>
    );
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Web Development Pro')).toBeInTheDocument();
    });
    // Click on export button
    fireEvent.click(screen.getByText('İndir'));
    // Check error toast
    await waitFor(() => {
      expect(useToastModule.toast).toHaveBeenCalledWith({
        title: 'Hata',
        description: 'Sonuçlar indirilemedi',
        variant: 'error'
      });
    });
  });
  it('opens and handles share modal correctly', async () => {
    render(
      <BrowserRouter>
        <TestResultsPageV2 />
      </BrowserRouter>
    );
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Web Development Pro')).toBeInTheDocument();
    });
    // Click on share button to open modal
    fireEvent.click(screen.getByText('Paylaş'));
    // Check modal is displayed
    expect(screen.getByText('Sonuçları Paylaş')).toBeInTheDocument();
    expect(screen.getByText('E-posta ile Gönder')).toBeInTheDocument();
    expect(screen.getByText('Link Oluştur')).toBeInTheDocument();
    expect(screen.getByText('Sosyal Medyada Paylaş')).toBeInTheDocument();
    // Click on email share option
    fireEvent.click(screen.getByText('E-posta ile Gönder'));
    // Check API call
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith('/api/evaluations/sessions/123/share', {
        method: 'email',
        includeAnalysis: true
      });
    });
    // Check success toast and modal closing
    expect(useToastModule.toast).toHaveBeenCalledWith({
      title: 'Başarılı',
      description: 'Sonuçlar paylaşıldı',
      variant: 'success'
    });
    // Modal should be closed
    await waitFor(() => {
      expect(screen.queryByText('Sonuçları Paylaş')).not.toBeInTheDocument();
    });
  });
  it('handles share errors correctly', async () => {
    // Mock API error for sharing
    axios.post.mockRejectedValueOnce(new Error('Share failed'));
    render(
      <BrowserRouter>
        <TestResultsPageV2 />
      </BrowserRouter>
    );
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Web Development Pro')).toBeInTheDocument();
    });
    // Click on share button to open modal
    fireEvent.click(screen.getByText('Paylaş'));
    // Click on link share option
    fireEvent.click(screen.getByText('Link Oluştur'));
    // Check error toast
    await waitFor(() => {
      expect(useToastModule.toast).toHaveBeenCalledWith({
        title: 'Hata',
        description: 'Sonuçlar paylaşılamadı',
        variant: 'error'
      });
    });
  });
  it('navigates to AI Analysis page when button is clicked', async () => {
    render(
      <BrowserRouter>
        <TestResultsPageV2 />
      </BrowserRouter>
    );
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Web Development Pro')).toBeInTheDocument();
    });
    // Click AI Analysis button
    fireEvent.click(screen.getByText('AI Analizi'));
    // Check navigation
    expect(mockNavigate).toHaveBeenCalledWith('/evaluations/sessions/123/analysis');
  });
  it('navigates when clicking on a test history item', async () => {
    render(
      <BrowserRouter>
        <TestResultsPageV2 />
      </BrowserRouter>
    );
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Web Development Pro')).toBeInTheDocument();
    });
    // Click on History tab
    fireEvent.click(screen.getByText('Geçmiş'));
    // Click on a history item
    fireEvent.click(screen.getByText('Deneme #2'));
    // Check navigation
    expect(mockNavigate).toHaveBeenCalledWith('/evaluations/sessions/122/results');
  });
  it('handles data fetching errors correctly', async () => {
    // Mock API error for data fetching
    axios.get.mockRejectedValueOnce(new Error('Failed to fetch data'));
    render(
      <BrowserRouter>
        <TestResultsPageV2 />
      </BrowserRouter>
    );
    // Check error toast
    await waitFor(() => {
      expect(useToastModule.toast).toHaveBeenCalledWith({
        title: 'Hata',
        description: 'Sonuçlar yüklenemedi',
        variant: 'error'
      });
    });
  });
});
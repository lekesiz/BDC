// TODO: i18n - processed
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import TestCreationPageV2 from '../../../pages/evaluation/TestCreationPageV2';
import axios from '../../../lib/api';
// Import using the correct path structure
import * as useToastModule from '../../../hooks/useToast';
import { EVALUATION_STATUS, QUESTION_TYPES } from '../../../lib/constants';
// Mock modules
import { useTranslation } from "react-i18next";vi.mock('@/lib/api');
vi.mock('@/hooks/useToast');
// Mock DragDropContext
vi.mock('@hello-pangea/dnd', () => ({
  DragDropContext: ({ children, onDragEnd }) => {
    return <div data-testid="drag-drop-context">{children}</div>;
  },
  Droppable: ({ children }) => children({ droppableProps: {}, innerRef: vi.fn() }),
  Draggable: ({ children }) => children({ innerRef: vi.fn(), draggableProps: {}, dragHandleProps: {} }, { isDragging: false })
}));
// Mock useNavigate hook
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => ({ id: undefined }) // Default to create mode
  };
});
// Mock toast functions properly
vi.mock('../../../hooks/useToast', () => ({
  useToast: vi.fn().mockReturnValue({
    toast: vi.fn()
  }),
  toast: vi.fn(),
  __esModule: true,
  default: { toast: vi.fn() }
}));
// Sample response data for API calls
const mockCategories = [
{ id: 'cat1', name: 'Programming' },
{ id: 'cat2', name: 'Web Development' },
{ id: 'cat3', name: 'Data Science' }];

const mockTemplates = [
{
  id: 'temp1',
  title: { tr: 'Programlama Temelleri', en: 'Programming Basics' },
  description: { tr: 'Temel programlama konseptlerini test edin', en: 'Test basic programming concepts' },
  questions: [
  {
    id: '1',
    question_text: { tr: 'JavaScript nedir?', en: 'What is JavaScript?' },
    question_type: QUESTION_TYPES.MULTIPLE_CHOICE,
    options: [
    { text: { tr: 'Programlama dili', en: 'Programming language' }, is_correct: true },
    { text: { tr: 'Veritabanı', en: 'Database' }, is_correct: false }]

  }]

}];

const mockQuestionBank = [
{
  id: 'bank1',
  question_text: { tr: 'HTML nedir?', en: 'What is HTML?' },
  question_type: QUESTION_TYPES.MULTIPLE_CHOICE,
  points: 5,
  options: [
  { text: { tr: 'İşaretleme dili', en: 'Markup language' }, is_correct: true },
  { text: { tr: 'Programlama dili', en: 'Programming language' }, is_correct: false }]

}];

const mockAiSuggestions = [
{
  question_text: { tr: 'CSS seçicileri nelerdir?', en: 'What are CSS selectors?' },
  question_type: QUESTION_TYPES.TEXT,
  points: 5,
  difficulty: 'medium'
}];

describe('TestCreationPageV2', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock API responses
    axios.get.mockImplementation((url) => {
      if (url.includes('/categories')) {
        return Promise.resolve({ data: mockCategories });
      }
      if (url.includes('/templates')) {
        return Promise.resolve({ data: mockTemplates });
      }
      if (url.includes('/bank')) {
        return Promise.resolve({ data: mockQuestionBank });
      }
      return Promise.reject(new Error('Unknown URL'));
    });
    axios.post.mockImplementation((url) => {
      if (url.includes('/ai/suggestions')) {
        return Promise.resolve({ data: mockAiSuggestions });
      }
      if (url.includes('/evaluations')) {
        return Promise.resolve({ data: { id: 'new-test-id' } });
      }
      if (url.includes('/upload')) {
        return Promise.resolve({ data: { url: 'https://example.com/uploaded-file.jpg' } });
      }
      return Promise.reject(new Error('Unknown URL'));
    });
  });
  it('renders the test creation page with correct title', async () => {
    render(
      <BrowserRouter>
        <TestCreationPageV2 />
      </BrowserRouter>
    );
    // Wait for initial data to load
    await waitFor(() => {
      expect(screen.getByText('Yeni Test Oluştur')).toBeInTheDocument();
    });
    // Check basic elements
    expect(screen.getByText('Öğrenenlerin becerilerini değerlendirmek için kapsamlı testler oluşturun')).toBeInTheDocument();
    expect(screen.getByText('Temel Bilgiler')).toBeInTheDocument();
    expect(screen.getByText('Sorular')).toBeInTheDocument();
    expect(screen.getByText('Ayarlar')).toBeInTheDocument();
    expect(screen.getByText('Önizleme')).toBeInTheDocument();
  });
  it('fetches initial data correctly', async () => {
    render(
      <BrowserRouter>
        <TestCreationPageV2 />
      </BrowserRouter>
    );
    // Wait for initial data to load
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith('/api/evaluations/categories');
      expect(axios.get).toHaveBeenCalledWith('/api/evaluations/templates');
      expect(axios.get).toHaveBeenCalledWith('/api/evaluations/questions/bank');
    });
    // Check if categories are loaded
    const categorySelect = screen.getByText('Kategori Seçin');
    fireEvent.click(categorySelect);
    await waitFor(() => {
      expect(screen.getByText('Programming')).toBeInTheDocument();
      expect(screen.getByText('Web Development')).toBeInTheDocument();
      expect(screen.getByText('Data Science')).toBeInTheDocument();
    });
    // Check if templates are loaded
    expect(screen.getByText('Programlama Temelleri')).toBeInTheDocument();
    expect(screen.getByText('Temel programlama konseptlerini test edin')).toBeInTheDocument();
  });
  it('navigates between tabs correctly', async () => {
    render(
      <BrowserRouter>
        <TestCreationPageV2 />
      </BrowserRouter>
    );
    // Wait for initial data to load
    await waitFor(() => {
      expect(screen.getByText('Test Bilgileri')).toBeInTheDocument();
    });
    // Initial tab should be 'basic'
    expect(screen.getByText('Başlık (Türkçe) *')).toBeInTheDocument();
    // Click on Questions tab
    fireEvent.click(screen.getByText('Sorular'));
    // Should show questions tab content
    expect(screen.getByText('Yeni Soru')).toBeInTheDocument();
    // Click on Settings tab
    fireEvent.click(screen.getByText('Ayarlar'));
    // Should show settings tab content
    expect(screen.getByText('Test Ayarları')).toBeInTheDocument();
    expect(screen.getByText('Soruları Karıştır')).toBeInTheDocument();
    // Click on Preview tab
    fireEvent.click(screen.getByText('Önizleme'));
    // Should show preview tab content
    expect(screen.getByText('Test Önizleme')).toBeInTheDocument();
  });
  it('switches between languages correctly', async () => {
    render(
      <BrowserRouter>
        <TestCreationPageV2 />
      </BrowserRouter>
    );
    // Wait for initial data to load
    await waitFor(() => {
      expect(screen.getByText('Test Bilgileri')).toBeInTheDocument();
    });
    // Default language is TR
    expect(screen.getByText('Başlık (Türkçe) *')).toBeInTheDocument();
    expect(screen.queryByText('Title (English)')).not.toBeInTheDocument();
    // Switch to English
    fireEvent.click(screen.getByText('TR'));
    fireEvent.click(screen.getByText('EN'));
    // Should show English fields
    expect(screen.getByText('Başlık (Türkçe) *')).toBeInTheDocument();
    expect(screen.getByText('Title (English)')).toBeInTheDocument();
  });
  it('adds a new question correctly', async () => {
    render(
      <BrowserRouter>
        <TestCreationPageV2 />
      </BrowserRouter>
    );
    // Wait for initial data to load
    await waitFor(() => {
      expect(screen.getByText('Test Bilgileri')).toBeInTheDocument();
    });
    // Go to questions tab
    fireEvent.click(screen.getByText('Sorular'));
    // Initially no questions
    expect(screen.getByText('0 soru, toplam 0 puan')).toBeInTheDocument();
    // Click add new question button
    fireEvent.click(screen.getByText('Yeni Soru'));
    // Should have added a question
    await waitFor(() => {
      expect(screen.getByText('Soru 1')).toBeInTheDocument();
      expect(screen.getByText('Soru Metni (Türkçe) *')).toBeInTheDocument();
    });
  });
  it('opens and uses question bank correctly', async () => {
    render(
      <BrowserRouter>
        <TestCreationPageV2 />
      </BrowserRouter>
    );
    // Wait for initial data to load
    await waitFor(() => {
      expect(screen.getByText('Test Bilgileri')).toBeInTheDocument();
    });
    // Go to questions tab
    fireEvent.click(screen.getByText('Sorular'));
    // Open question bank
    fireEvent.click(screen.getByText('Soru Bankası'));
    // Should show question bank
    await waitFor(() => {
      expect(screen.getByText('HTML nedir?')).toBeInTheDocument();
    });
    // Add question from bank
    fireEvent.click(screen.getAllByText('Ekle')[0]);
    // Should add the question and show success toast
    expect(useToastModule.toast).toHaveBeenCalledWith({
      title: 'Başarılı',
      description: 'Soru eklendi',
      variant: 'success'
    });
  });
  it('generates AI suggestions correctly', async () => {
    render(
      <BrowserRouter>
        <TestCreationPageV2 />
      </BrowserRouter>
    );
    // Wait for initial data to load
    await waitFor(() => {
      expect(screen.getByText('Test Bilgileri')).toBeInTheDocument();
    });
    // Click on AI suggestion button
    fireEvent.click(screen.getByText('Öner'));
    // Should call AI suggestions API
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith('/api/evaluations/ai/suggestions', expect.any(Object));
    });
    // Should show AI suggestions
    await waitFor(() => {
      expect(screen.getByText('CSS seçicileri nelerdir?')).toBeInTheDocument();
    });
    // Should show success toast
    expect(useToastModule.toast).toHaveBeenCalledWith({
      title: 'AI Önerileri',
      description: '5 soru önerisi oluşturuldu',
      variant: 'success'
    });
  });
  it('applies a template correctly', async () => {
    render(
      <BrowserRouter>
        <TestCreationPageV2 />
      </BrowserRouter>
    );
    // Wait for initial data to load
    await waitFor(() => {
      expect(screen.getByText('Test Bilgileri')).toBeInTheDocument();
    });
    // Click on template to apply
    fireEvent.click(screen.getByText('Programlama Temelleri'));
    // Should show success toast
    expect(useToastModule.toast).toHaveBeenCalledWith({
      title: 'Şablon Uygulandı',
      description: 'Programlama Temelleri',
      variant: 'success'
    });
  });
  it('submits the form correctly in create mode', async () => {
    render(
      <BrowserRouter>
        <TestCreationPageV2 />
      </BrowserRouter>
    );
    // Wait for initial data to load
    await waitFor(() => {
      expect(screen.getByText('Test Bilgileri')).toBeInTheDocument();
    });
    // Fill basic information
    fireEvent.change(screen.getByLabelText('Başlık (Türkçe) *'), {
      target: { value: 'Test Başlığı' }
    });
    fireEvent.change(screen.getByLabelText('Açıklama (Türkçe) *'), {
      target: { value: 'Test açıklaması burada yer alır' }
    });
    // Submit the form
    fireEvent.click(screen.getByText('Kaydet'));
    // Should call API with form data
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith('/api/evaluations', expect.any(Object));
    });
    // Should show success toast
    expect(useToastModule.toast).toHaveBeenCalledWith({
      title: 'Başarılı',
      description: 'Test oluşturuldu',
      variant: 'success'
    });
    // Should navigate to new test page
    expect(mockNavigate).toHaveBeenCalledWith('/evaluations/new-test-id');
  });
  it('handles validation errors correctly', async () => {
    render(
      <BrowserRouter>
        <TestCreationPageV2 />
      </BrowserRouter>
    );
    // Wait for initial data to load
    await waitFor(() => {
      expect(screen.getByText('Test Bilgileri')).toBeInTheDocument();
    });
    // Submit without required fields
    fireEvent.click(screen.getByText('Kaydet'));
    // Should show validation errors
    await waitFor(() => {
      expect(screen.getByText('Başlık en az 3 karakter olmalı')).toBeInTheDocument();
      expect(screen.getByText('Açıklama en az 10 karakter olmalı')).toBeInTheDocument();
    });
  });
  it('handles file upload correctly', async () => {
    render(
      <BrowserRouter>
        <TestCreationPageV2 />
      </BrowserRouter>
    );
    // Wait for initial data to load
    await waitFor(() => {
      expect(screen.getByText('Test Bilgileri')).toBeInTheDocument();
    });
    // Go to questions tab
    fireEvent.click(screen.getByText('Sorular'));
    // Add new question
    fireEvent.click(screen.getByText('Yeni Soru'));
    // Mock file upload
    const file = new File(['dummy content'], 'test-image.png', { type: 'image/png' });
    const fileInput = screen.getByLabelText('Yükle');
    Object.defineProperty(fileInput, 'files', {
      value: [file]
    });
    fireEvent.change(fileInput);
    // Should call upload API
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith('/api/upload', expect.any(Object), {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    });
    // Should show success toast
    expect(useToastModule.toast).toHaveBeenCalledWith({
      title: 'Başarılı',
      description: 'Medya yüklendi',
      variant: 'success'
    });
    // Should show media uploaded message
    await waitFor(() => {
      expect(screen.getByText('Medya yüklendi')).toBeInTheDocument();
    });
  });
  it('renders in edit mode correctly when id is provided', async () => {
    // Mock useParams to return an id
    vi.mock('react-router-dom', async () => {
      const actual = await vi.importActual('react-router-dom');
      return {
        ...actual,
        useNavigate: () => mockNavigate,
        useParams: () => ({ id: 'existing-test-id' })
      };
    });
    // Mock fetch test data response
    axios.get.mockImplementation((url) => {
      if (url.includes('/evaluations/existing-test-id')) {
        return Promise.resolve({
          data: {
            id: 'existing-test-id',
            title: { tr: 'Mevcut Test', en: '' },
            description: { tr: 'Mevcut test açıklaması', en: '' },
            category: 'cat1',
            status: EVALUATION_STATUS.ACTIVE,
            questions: []
          }
        });
      }
      if (url.includes('/categories')) {
        return Promise.resolve({ data: mockCategories });
      }
      if (url.includes('/templates')) {
        return Promise.resolve({ data: mockTemplates });
      }
      if (url.includes('/bank')) {
        return Promise.resolve({ data: mockQuestionBank });
      }
      return Promise.reject(new Error('Unknown URL'));
    });
    render(
      <BrowserRouter>
        <TestCreationPageV2 />
      </BrowserRouter>
    );
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Testi Düzenle')).toBeInTheDocument();
    });
    // Should have called API to fetch test data
    expect(axios.get).toHaveBeenCalledWith('/api/evaluations/existing-test-id');
    // Should show existing test data
    await waitFor(() => {
      expect(screen.getByDisplayValue('Mevcut Test')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Mevcut test açıklaması')).toBeInTheDocument();
    });
    // Button should say "Güncelle" instead of "Kaydet"
    expect(screen.getByText('Güncelle')).toBeInTheDocument();
  });
  it('shows preview mode correctly', async () => {
    render(
      <BrowserRouter>
        <TestCreationPageV2 />
      </BrowserRouter>
    );
    // Wait for initial data to load
    await waitFor(() => {
      expect(screen.getByText('Test Bilgileri')).toBeInTheDocument();
    });
    // Enter test title and description
    fireEvent.change(screen.getByLabelText('Başlık (Türkçe) *'), {
      target: { value: 'Test Başlığı' }
    });
    fireEvent.change(screen.getByLabelText('Açıklama (Türkçe) *'), {
      target: { value: 'Test açıklaması burada yer alır' }
    });
    // Click preview button
    fireEvent.click(screen.getByText('Önizle'));
    // Should change to preview mode
    await waitFor(() => {
      expect(screen.getByText('Düzenle')).toBeInTheDocument();
    });
    // Should show test data in preview mode
    expect(screen.getByText('Test Başlığı')).toBeInTheDocument();
    expect(screen.getByText('Test açıklaması burada yer alır')).toBeInTheDocument();
  });
});
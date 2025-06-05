import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { 
  PlusCircle, X, Save, ArrowLeft, Play, Trash2, Upload, 
  Image, FileText, AudioLines, Video, Link, Copy, Library,
  Settings, Languages, Eye, ChevronLeft, ChevronRight,
  Sparkles, Timer, Award, Target, GripVertical
} from 'lucide-react';
import axios from '../../lib/api';
import { toast } from '../../hooks/useToast';
import { EVALUATION_STATUS, QUESTION_TYPES } from '../../lib/constants';
import { Button } from '../../components/ui/button';
import { Card } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Tabs } from '../../components/ui/tabs';
import { Label, Textarea } from '../../components/ui';
import { Select } from '../../components/ui/select';
import { Badge } from '../../components/ui/badge';
import { Alert } from '../../components/ui/alert';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
// Enhanced validation schema with media support and multi-language
const testSchema = z.object({
  title: z.object({
    tr: z.string().min(3, { message: 'Başlık en az 3 karakter olmalı' }),
    en: z.string().optional()
  }),
  description: z.object({
    tr: z.string().min(10, { message: 'Açıklama en az 10 karakter olmalı' }),
    en: z.string().optional()
  }),
  instructions: z.object({
    tr: z.string().optional(),
    en: z.string().optional()
  }),
  category: z.string().min(1, { message: 'Kategori seçiniz' }),
  tags: z.array(z.string()).optional(),
  difficulty: z.enum(['beginner', 'intermediate', 'advanced']),
  time_limit: z.number().min(0).optional(),
  passing_score: z.number().min(0).max(100).default(70),
  attempts_allowed: z.number().min(1).default(1),
  skills: z.array(z.string()).min(1, { message: 'En az bir beceri seçiniz' }),
  status: z.enum([EVALUATION_STATUS.DRAFT, EVALUATION_STATUS.ACTIVE, EVALUATION_STATUS.ARCHIVED]).default(EVALUATION_STATUS.DRAFT),
  settings: z.object({
    randomize_questions: z.boolean().default(false),
    randomize_options: z.boolean().default(false),
    show_feedback: z.boolean().default(true),
    show_correct_answers: z.boolean().default(true),
    enable_calculator: z.boolean().default(false),
    enable_spell_check: z.boolean().default(false),
    partial_credit: z.boolean().default(false)
  }),
  questions: z.array(
    z.object({
      id: z.string(),
      question_text: z.object({
        tr: z.string().min(3, { message: 'Soru metni zorunludur' }),
        en: z.string().optional()
      }),
      question_type: z.enum(Object.values(QUESTION_TYPES)),
      points: z.number().min(1).default(1),
      media: z.object({
        type: z.enum(['none', 'image', 'audio', 'video']).default('none'),
        url: z.string().optional(),
        caption: z.string().optional()
      }).optional(),
      explanation: z.string().optional(),
      hint: z.string().optional(),
      difficulty: z.enum(['easy', 'medium', 'hard']).default('medium'),
      options: z.array(
        z.object({
          text: z.object({
            tr: z.string().min(1, { message: 'Seçenek metni zorunludur' }),
            en: z.string().optional()
          }),
          is_correct: z.boolean().default(false),
          feedback: z.string().optional()
        })
      ).optional(),
      correct_answer: z.string().optional()
    })
  )
});
const TestCreationPageV2 = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditMode = !!id;
  const [activeTab, setActiveTab] = useState('basic');
  const [language, setLanguage] = useState('tr');
  const [previewMode, setPreviewMode] = useState(false);
  const [questionBank, setQuestionBank] = useState([]);
  const [categories, setCategories] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [showQuestionBank, setShowQuestionBank] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const {
    control,
    register,
    handleSubmit,
    watch,
    formState: { errors },
    setValue,
    reset
  } = useForm({
    resolver: zodResolver(testSchema),
    defaultValues: {
      title: { tr: '', en: '' },
      description: { tr: '', en: '' },
      instructions: { tr: '', en: '' },
      category: '',
      tags: [],
      difficulty: 'intermediate',
      time_limit: 60,
      passing_score: 70,
      attempts_allowed: 1,
      skills: [],
      status: EVALUATION_STATUS.DRAFT,
      settings: {
        randomize_questions: false,
        randomize_options: false,
        show_feedback: true,
        show_correct_answers: true,
        enable_calculator: false,
        enable_spell_check: false,
        partial_credit: false
      },
      questions: []
    }
  });
  const { fields: questions, append: addQuestion, remove: removeQuestion, move: moveQuestion } = useFieldArray({
    control,
    name: 'questions'
  });
  useEffect(() => {
    fetchInitialData();
    if (isEditMode) fetchTestData();
  }, [id]);
  const fetchInitialData = async () => {
    try {
      const [categoriesRes, templatesRes, bankRes] = await Promise.all([
        axios.get('/api/evaluations/categories'),
        axios.get('/api/evaluations/templates'),
        axios.get('/api/evaluations/questions/bank')
      ]);
      setCategories(categoriesRes.data);
      setTemplates(templatesRes.data);
      setQuestionBank(bankRes.data);
    } catch (error) {
      console.error('Error fetching initial data:', error);
    }
  };
  const fetchTestData = async () => {
    try {
      const response = await axios.get(`/api/evaluations/${id}`);
      reset(response.data);
    } catch (error) {
      toast({
        title: 'Hata',
        description: 'Test bilgileri yüklenemedi',
        variant: 'error'
      });
    }
  };
  const handleDragEnd = (result) => {
    if (!result.destination) return;
    moveQuestion(result.source.index, result.destination.index);
  };
  const addQuestionFromBank = (bankQuestion) => {
    const newQuestion = {
      ...bankQuestion,
      id: Date.now().toString()
    };
    addQuestion(newQuestion);
    setShowQuestionBank(false);
    toast({
      title: 'Başarılı',
      description: 'Soru eklendi',
      variant: 'success'
    });
  };
  const addNewQuestion = (type = QUESTION_TYPES.MULTIPLE_CHOICE) => {
    const newQuestion = {
      id: Date.now().toString(),
      question_text: { tr: '', en: '' },
      question_type: type,
      points: 1,
      difficulty: 'medium',
      media: { type: 'none' },
      options: type === QUESTION_TYPES.MULTIPLE_CHOICE || type === QUESTION_TYPES.TRUE_FALSE
        ? [
            { text: { tr: '', en: '' }, is_correct: false },
            { text: { tr: '', en: '' }, is_correct: false },
            { text: { tr: '', en: '' }, is_correct: false },
            { text: { tr: '', en: '' }, is_correct: false }
          ]
        : []
    };
    addQuestion(newQuestion);
  };
  const generateAISuggestions = async () => {
    try {
      setLoading(true);
      const skills = watch('skills');
      const category = watch('category');
      const difficulty = watch('difficulty');
      const response = await axios.post('/api/evaluations/ai/suggestions', {
        skills,
        category,
        difficulty,
        count: 5
      });
      setAiSuggestions(response.data);
      toast({
        title: 'AI Önerileri',
        description: '5 soru önerisi oluşturuldu',
        variant: 'success'
      });
    } catch (error) {
      toast({
        title: 'Hata',
        description: 'AI önerileri alınamadı',
        variant: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  const handleMediaUpload = async (questionIndex, file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await axios.post('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setValue(`questions.${questionIndex}.media`, {
        type: file.type.startsWith('image/') ? 'image' : 
              file.type.startsWith('audio/') ? 'audio' : 
              file.type.startsWith('video/') ? 'video' : 'none',
        url: response.data.url,
        caption: ''
      });
      toast({
        title: 'Başarılı',
        description: 'Medya yüklendi',
        variant: 'success'
      });
    } catch (error) {
      toast({
        title: 'Hata',
        description: 'Medya yüklenemedi',
        variant: 'error'
      });
    }
  };
  const applyTemplate = (template) => {
    reset(template);
    toast({
      title: 'Şablon Uygulandı',
      description: template.title.tr,
      variant: 'success'
    });
  };
  const onSubmit = async (data) => {
    try {
      setLoading(true);
      if (isEditMode) {
        await axios.put(`/api/evaluations/${id}`, data);
        toast({
          title: 'Başarılı',
          description: 'Test güncellendi',
          variant: 'success'
        });
      } else {
        const response = await axios.post('/api/evaluations', data);
        toast({
          title: 'Başarılı',
          description: 'Test oluşturuldu',
          variant: 'success'
        });
        navigate(`/evaluations/${response.data.id}`);
      }
    } catch (error) {
      toast({
        title: 'Hata',
        description: error.message,
        variant: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  const steps = [
    { id: 'basic', title: 'Temel Bilgiler', icon: <FileText className="h-4 w-4" /> },
    { id: 'questions', title: 'Sorular', icon: <Library className="h-4 w-4" /> },
    { id: 'settings', title: 'Ayarlar', icon: <Settings className="h-4 w-4" /> },
    { id: 'preview', title: 'Önizleme', icon: <Eye className="h-4 w-4" /> }
  ];
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-30">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                onClick={() => navigate('/evaluations')}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Değerlendirmeler
              </Button>
              <div>
                <h1 className="text-xl font-semibold">
                  {isEditMode ? 'Testi Düzenle' : 'Yeni Test Oluştur'}
                </h1>
                <p className="text-sm text-gray-600">
                  Öğrenenlerin becerilerini değerlendirmek için kapsamlı testler oluşturun
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Select
                value={language}
                onValueChange={setLanguage}
                className="w-24"
              >
                <Select.Option value="tr">TR</Select.Option>
                <Select.Option value="en">EN</Select.Option>
              </Select>
              <Button
                variant="outline"
                onClick={() => setPreviewMode(!previewMode)}
              >
                <Eye className="h-4 w-4 mr-2" />
                {previewMode ? 'Düzenle' : 'Önizle'}
              </Button>
              <Button
                onClick={handleSubmit(onSubmit)}
                disabled={loading}
              >
                <Save className="h-4 w-4 mr-2" />
                {isEditMode ? 'Güncelle' : 'Kaydet'}
              </Button>
            </div>
          </div>
        </div>
        {/* Steps */}
        <div className="px-6 pb-4">
          <div className="flex items-center gap-8">
            {steps.map((step, index) => (
              <button
                key={step.id}
                onClick={() => {
                  setActiveTab(step.id);
                  setCurrentStep(index);
                }}
                className={`flex items-center gap-2 pb-2 border-b-2 transition-colors ${
                  activeTab === step.id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                {step.icon}
                <span className="font-medium">{step.title}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
      {/* Content */}
      <div className="p-6 max-w-6xl mx-auto">
        {/* Basic Information Tab */}
        {activeTab === 'basic' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Test Bilgileri</h3>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="title.tr">Başlık (Türkçe) *</Label>
                    <Input
                      id="title.tr"
                      {...register('title.tr')}
                      placeholder="Test başlığını girin"
                      className={errors.title?.tr ? 'border-red-500' : ''}
                    />
                    {errors.title?.tr && (
                      <p className="text-sm text-red-500 mt-1">{errors.title.tr.message}</p>
                    )}
                  </div>
                  {language === 'en' && (
                    <div>
                      <Label htmlFor="title.en">Title (English)</Label>
                      <Input
                        id="title.en"
                        {...register('title.en')}
                        placeholder="Enter test title"
                      />
                    </div>
                  )}
                  <div>
                    <Label htmlFor="description.tr">Açıklama (Türkçe) *</Label>
                    <Textarea
                      id="description.tr"
                      {...register('description.tr')}
                      placeholder="Test açıklamasını girin"
                      rows={3}
                      className={errors.description?.tr ? 'border-red-500' : ''}
                    />
                    {errors.description?.tr && (
                      <p className="text-sm text-red-500 mt-1">{errors.description.tr.message}</p>
                    )}
                  </div>
                  {language === 'en' && (
                    <div>
                      <Label htmlFor="description.en">Description (English)</Label>
                      <Textarea
                        id="description.en"
                        {...register('description.en')}
                        placeholder="Enter test description"
                        rows={3}
                      />
                    </div>
                  )}
                  <div>
                    <Label htmlFor="instructions.tr">Talimatlar (Türkçe)</Label>
                    <Textarea
                      id="instructions.tr"
                      {...register('instructions.tr')}
                      placeholder="Test talimatlarını girin"
                      rows={3}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="category">Kategori *</Label>
                      <Select
                        id="category"
                        value={watch('category')}
                        onValueChange={(value) => setValue('category', value)}
                      >
                        <Select.Option value="">Kategori Seçin</Select.Option>
                        {categories.map(cat => (
                          <Select.Option key={cat.id} value={cat.id}>
                            {cat.name}
                          </Select.Option>
                        ))}
                      </Select>
                      {errors.category && (
                        <p className="text-sm text-red-500 mt-1">{errors.category.message}</p>
                      )}
                    </div>
                    <div>
                      <Label htmlFor="difficulty">Zorluk Seviyesi</Label>
                      <Select
                        id="difficulty"
                        value={watch('difficulty')}
                        onValueChange={(value) => setValue('difficulty', value)}
                      >
                        <Select.Option value="beginner">Başlangıç</Select.Option>
                        <Select.Option value="intermediate">Orta</Select.Option>
                        <Select.Option value="advanced">İleri</Select.Option>
                      </Select>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <Label htmlFor="time_limit">Süre (dk)</Label>
                      <Input
                        id="time_limit"
                        type="number"
                        {...register('time_limit', { valueAsNumber: true })}
                        placeholder="60"
                      />
                    </div>
                    <div>
                      <Label htmlFor="passing_score">Geçme Notu (%)</Label>
                      <Input
                        id="passing_score"
                        type="number"
                        {...register('passing_score', { valueAsNumber: true })}
                        placeholder="70"
                      />
                    </div>
                    <div>
                      <Label htmlFor="attempts_allowed">Deneme Hakkı</Label>
                      <Input
                        id="attempts_allowed"
                        type="number"
                        {...register('attempts_allowed', { valueAsNumber: true })}
                        placeholder="1"
                      />
                    </div>
                  </div>
                </div>
              </Card>
            </div>
            <div className="space-y-6">
              {/* Templates */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Şablonlar</h3>
                <div className="space-y-2">
                  {templates.map(template => (
                    <button
                      key={template.id}
                      onClick={() => applyTemplate(template)}
                      className="w-full text-left p-3 rounded-lg border hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium">{template.title.tr}</p>
                          <p className="text-sm text-gray-600">{template.description.tr}</p>
                        </div>
                        <Copy className="h-4 w-4 text-gray-400" />
                      </div>
                    </button>
                  ))}
                </div>
              </Card>
              {/* AI Suggestions */}
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">AI Önerileri</h3>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={generateAISuggestions}
                    disabled={loading || !watch('skills').length}
                  >
                    <Sparkles className="h-4 w-4 mr-2" />
                    Öner
                  </Button>
                </div>
                {aiSuggestions && (
                  <div className="space-y-2">
                    {aiSuggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => addQuestion(suggestion)}
                        className="w-full text-left p-3 rounded-lg border hover:bg-gray-50 transition-colors"
                      >
                        <p className="font-medium text-sm">{suggestion.question_text.tr}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="secondary" size="sm">
                            {suggestion.points} puan
                          </Badge>
                          <Badge variant="secondary" size="sm">
                            {suggestion.difficulty}
                          </Badge>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </Card>
            </div>
          </div>
        )}
        {/* Questions Tab */}
        {activeTab === 'questions' && (
          <div className="space-y-6">
            <Card className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-lg font-semibold">Sorular</h3>
                  <p className="text-sm text-gray-600">
                    {questions.length} soru, toplam {questions.reduce((sum, q) => sum + q.points, 0)} puan
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setShowQuestionBank(!showQuestionBank)}
                  >
                    <Library className="h-4 w-4 mr-2" />
                    Soru Bankası
                  </Button>
                  <div className="relative">
                    <Button>
                      <PlusCircle className="h-4 w-4 mr-2" />
                      Yeni Soru
                    </Button>
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border p-2 hidden group-hover:block">
                      {Object.entries(QUESTION_TYPES).map(([key, value]) => (
                        <button
                          key={key}
                          onClick={() => addNewQuestion(value)}
                          className="w-full text-left px-3 py-2 rounded hover:bg-gray-100"
                        >
                          {value}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
              {/* Question Bank Modal */}
              {showQuestionBank && (
                <div className="mb-6 p-4 border rounded-lg bg-gray-50">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-semibold">Soru Bankası</h4>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowQuestionBank(false)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {questionBank.map(question => (
                      <Card key={question.id} className="p-4">
                        <p className="font-medium mb-2">{question.question_text.tr}</p>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge variant="secondary" size="sm">
                              {question.type}
                            </Badge>
                            <Badge variant="secondary" size="sm">
                              {question.points} puan
                            </Badge>
                          </div>
                          <Button
                            size="sm"
                            onClick={() => addQuestionFromBank(question)}
                          >
                            Ekle
                          </Button>
                        </div>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
              {/* Questions List */}
              <DragDropContext onDragEnd={handleDragEnd}>
                <Droppable droppableId="questions">
                  {(provided) => (
                    <div
                      {...provided.droppableProps}
                      ref={provided.innerRef}
                      className="space-y-4"
                    >
                      {questions.map((question, index) => (
                        <Draggable
                          key={question.id}
                          draggableId={question.id}
                          index={index}
                        >
                          {(provided, snapshot) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              className={`${
                                snapshot.isDragging ? 'opacity-50' : ''
                              }`}
                            >
                              <Card className="p-6">
                                <div className="flex items-start gap-4">
                                  <div
                                    {...provided.dragHandleProps}
                                    className="cursor-move mt-1"
                                  >
                                    <GripVertical className="h-5 w-5 text-gray-400" />
                                  </div>
                                  <div className="flex-1">
                                    <div className="flex items-start justify-between mb-4">
                                      <div className="flex items-center gap-3">
                                        <span className="font-semibold">
                                          Soru {index + 1}
                                        </span>
                                        <Badge variant="secondary">
                                          {question.question_type}
                                        </Badge>
                                        <Badge variant="secondary">
                                          {question.points} puan
                                        </Badge>
                                        <Badge variant="secondary">
                                          {question.difficulty}
                                        </Badge>
                                      </div>
                                      <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => removeQuestion(index)}
                                      >
                                        <Trash2 className="h-4 w-4" />
                                      </Button>
                                    </div>
                                    <div className="space-y-4">
                                      <div>
                                        <Label>Soru Metni (Türkçe) *</Label>
                                        <Textarea
                                          {...register(`questions.${index}.question_text.tr`)}
                                          placeholder="Soru metnini girin"
                                          rows={2}
                                        />
                                      </div>
                                      {language === 'en' && (
                                        <div>
                                          <Label>Question Text (English)</Label>
                                          <Textarea
                                            {...register(`questions.${index}.question_text.en`)}
                                            placeholder="Enter question text"
                                            rows={2}
                                          />
                                        </div>
                                      )}
                                      {/* Media Upload */}
                                      <div>
                                        <Label>Medya</Label>
                                        <div className="flex items-center gap-2">
                                          <label className="cursor-pointer">
                                            <Button variant="outline" as="div">
                                              <Upload className="h-4 w-4 mr-2" />
                                              Yükle
                                            </Button>
                                            <input
                                              type="file"
                                              className="hidden"
                                              accept="image/*,audio/*,video/*"
                                              onChange={(e) => {
                                                if (e.target.files[0]) {
                                                  handleMediaUpload(index, e.target.files[0]);
                                                }
                                              }}
                                            />
                                          </label>
                                          {question.media?.url && (
                                            <div className="flex items-center gap-2">
                                              {question.media.type === 'image' && <Image className="h-4 w-4" />}
                                              {question.media.type === 'audio' && <AudioLines className="h-4 w-4" />}
                                              {question.media.type === 'video' && <Video className="h-4 w-4" />}
                                              <span className="text-sm text-gray-600">
                                                Medya yüklendi
                                              </span>
                                              <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => 
                                                  setValue(`questions.${index}.media`, { type: 'none' })
                                                }
                                              >
                                                <X className="h-4 w-4" />
                                              </Button>
                                            </div>
                                          )}
                                        </div>
                                      </div>
                                      {/* Question Type Specific Fields */}
                                      {(question.question_type === QUESTION_TYPES.MULTIPLE_CHOICE || 
                                        question.question_type === QUESTION_TYPES.TRUE_FALSE) && (
                                        <div>
                                          <Label>Seçenekler</Label>
                                          <div className="space-y-2">
                                            {question.options?.map((option, optionIndex) => (
                                              <div key={optionIndex} className="flex items-center gap-2">
                                                <input
                                                  type={question.question_type === QUESTION_TYPES.MULTIPLE_CHOICE ? 'checkbox' : 'radio'}
                                                  name={`question-${index}-correct`}
                                                  checked={option.is_correct}
                                                  onChange={(e) => {
                                                    if (question.question_type === QUESTION_TYPES.TRUE_FALSE) {
                                                      question.options.forEach((opt, idx) => {
                                                        setValue(
                                                          `questions.${index}.options.${idx}.is_correct`,
                                                          idx === optionIndex
                                                        );
                                                      });
                                                    } else {
                                                      setValue(
                                                        `questions.${index}.options.${optionIndex}.is_correct`,
                                                        e.target.checked
                                                      );
                                                    }
                                                  }}
                                                />
                                                <Input
                                                  {...register(
                                                    `questions.${index}.options.${optionIndex}.text.tr`
                                                  )}
                                                  placeholder={`Seçenek ${optionIndex + 1}`}
                                                />
                                                {question.options.length > 2 && (
                                                  <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() => {
                                                      const newOptions = [...question.options];
                                                      newOptions.splice(optionIndex, 1);
                                                      setValue(`questions.${index}.options`, newOptions);
                                                    }}
                                                  >
                                                    <X className="h-4 w-4" />
                                                  </Button>
                                                )}
                                              </div>
                                            ))}
                                          </div>
                                          {question.question_type === QUESTION_TYPES.MULTIPLE_CHOICE && (
                                            <Button
                                              variant="outline"
                                              size="sm"
                                              className="mt-2"
                                              onClick={() => {
                                                const newOptions = [...question.options];
                                                newOptions.push({
                                                  text: { tr: '', en: '' },
                                                  is_correct: false
                                                });
                                                setValue(`questions.${index}.options`, newOptions);
                                              }}
                                            >
                                              <PlusCircle className="h-4 w-4 mr-2" />
                                              Seçenek Ekle
                                            </Button>
                                          )}
                                        </div>
                                      )}
                                      {question.question_type === QUESTION_TYPES.TEXT && (
                                        <div>
                                          <Label>Doğru Cevap</Label>
                                          <Textarea
                                            {...register(`questions.${index}.correct_answer`)}
                                            placeholder="Doğru cevabı girin"
                                            rows={2}
                                          />
                                        </div>
                                      )}
                                      <div className="grid grid-cols-2 gap-4">
                                        <div>
                                          <Label>İpucu</Label>
                                          <Input
                                            {...register(`questions.${index}.hint`)}
                                            placeholder="İpucu (opsiyonel)"
                                          />
                                        </div>
                                        <div>
                                          <Label>Açıklama</Label>
                                          <Input
                                            {...register(`questions.${index}.explanation`)}
                                            placeholder="Cevap açıklaması (opsiyonel)"
                                          />
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </Card>
                            </div>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              </DragDropContext>
            </Card>
          </div>
        )}
        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Test Ayarları</h3>
              <div className="space-y-4">
                <label className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Soruları Karıştır</p>
                    <p className="text-sm text-gray-600">
                      Her öğrenci için soruları farklı sırada göster
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    {...register('settings.randomize_questions')}
                    className="h-5 w-5"
                  />
                </label>
                <label className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Seçenekleri Karıştır</p>
                    <p className="text-sm text-gray-600">
                      Çoktan seçmeli sorularda seçenekleri karıştır
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    {...register('settings.randomize_options')}
                    className="h-5 w-5"
                  />
                </label>
                <label className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Geri Bildirim Göster</p>
                    <p className="text-sm text-gray-600">
                      Test sonunda geri bildirim ve açıklamaları göster
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    {...register('settings.show_feedback')}
                    className="h-5 w-5"
                  />
                </label>
                <label className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Doğru Cevapları Göster</p>
                    <p className="text-sm text-gray-600">
                      Test sonunda doğru cevapları göster
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    {...register('settings.show_correct_answers')}
                    className="h-5 w-5"
                  />
                </label>
              </div>
            </Card>
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">İleri Düzey Ayarlar</h3>
              <div className="space-y-4">
                <label className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Hesap Makinesi</p>
                    <p className="text-sm text-gray-600">
                      Test sırasında hesap makinesine izin ver
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    {...register('settings.enable_calculator')}
                    className="h-5 w-5"
                  />
                </label>
                <label className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Yazım Denetimi</p>
                    <p className="text-sm text-gray-600">
                      Metin cevaplarında yazım denetimini aktif et
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    {...register('settings.enable_spell_check')}
                    className="h-5 w-5"
                  />
                </label>
                <label className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Kısmi Puan</p>
                    <p className="text-sm text-gray-600">
                      Çoktan seçmeli sorularda kısmi puan vermeyi aktif et
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    {...register('settings.partial_credit')}
                    className="h-5 w-5"
                  />
                </label>
                <div>
                  <Label htmlFor="status">Test Durumu</Label>
                  <Select
                    id="status"
                    value={watch('status')}
                    onValueChange={(value) => setValue('status', value)}
                  >
                    <Select.Option value={EVALUATION_STATUS.DRAFT}>Taslak</Select.Option>
                    <Select.Option value={EVALUATION_STATUS.ACTIVE}>Aktif</Select.Option>
                    <Select.Option value={EVALUATION_STATUS.ARCHIVED}>Arşivlenmiş</Select.Option>
                  </Select>
                </div>
              </div>
            </Card>
          </div>
        )}
        {/* Preview Tab */}
        {activeTab === 'preview' && (
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-6">Test Önizleme</h3>
            <div className="max-w-3xl mx-auto">
              <div className="space-y-6">
                {/* Test Header */}
                <div className="text-center mb-8">
                  <h1 className="text-2xl font-bold">{watch('title.tr')}</h1>
                  <p className="text-gray-600 mt-2">{watch('description.tr')}</p>
                  <div className="flex items-center justify-center gap-4 mt-4">
                    <Badge variant="secondary">
                      <Timer className="h-4 w-4 mr-1" />
                      {watch('time_limit')} dakika
                    </Badge>
                    <Badge variant="secondary">
                      <Target className="h-4 w-4 mr-1" />
                      {watch('passing_score')}% geçme notu
                    </Badge>
                    <Badge variant="secondary">
                      <Award className="h-4 w-4 mr-1" />
                      {questions.reduce((sum, q) => sum + q.points, 0)} puan
                    </Badge>
                  </div>
                </div>
                {/* Instructions */}
                {watch('instructions.tr') && (
                  <Alert>
                    <p className="font-medium">Talimatlar</p>
                    <p className="mt-1">{watch('instructions.tr')}</p>
                  </Alert>
                )}
                {/* Questions */}
                {questions.map((question, index) => (
                  <Card key={question.id} className="p-6">
                    <div className="mb-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-semibold">Soru {index + 1}</h3>
                        <Badge variant="secondary">{question.points} puan</Badge>
                      </div>
                      <p className="text-gray-900">{question.question_text.tr}</p>
                      {question.media?.url && (
                        <div className="mt-4">
                          {question.media.type === 'image' && (
                            <img 
                              src={question.media.url} 
                              alt="Soru görseli"
                              className="max-w-full h-auto rounded-lg"
                            />
                          )}
                          {question.media.type === 'audio' && (
                            <audio controls className="w-full">
                              <source src={question.media.url} />
                            </audio>
                          )}
                          {question.media.type === 'video' && (
                            <video controls className="w-full rounded-lg">
                              <source src={question.media.url} />
                            </video>
                          )}
                        </div>
                      )}
                    </div>
                    {/* Answer Options */}
                    {question.question_type === QUESTION_TYPES.MULTIPLE_CHOICE && (
                      <div className="space-y-2">
                        {question.options?.map((option, optIndex) => (
                          <label key={optIndex} className="flex items-center gap-3 p-3 rounded-lg border hover:bg-gray-50 cursor-pointer">
                            <input
                              type="checkbox"
                              disabled
                              className="h-4 w-4"
                            />
                            <span>{option.text.tr}</span>
                          </label>
                        ))}
                      </div>
                    )}
                    {question.question_type === QUESTION_TYPES.TRUE_FALSE && (
                      <div className="space-y-2">
                        <label className="flex items-center gap-3 p-3 rounded-lg border hover:bg-gray-50 cursor-pointer">
                          <input
                            type="radio"
                            name={`preview-q-${index}`}
                            disabled
                            className="h-4 w-4"
                          />
                          <span>Doğru</span>
                        </label>
                        <label className="flex items-center gap-3 p-3 rounded-lg border hover:bg-gray-50 cursor-pointer">
                          <input
                            type="radio"
                            name={`preview-q-${index}`}
                            disabled
                            className="h-4 w-4"
                          />
                          <span>Yanlış</span>
                        </label>
                      </div>
                    )}
                    {question.question_type === QUESTION_TYPES.TEXT && (
                      <Textarea
                        placeholder="Cevabınızı buraya yazın..."
                        disabled
                        rows={3}
                      />
                    )}
                  </Card>
                ))}
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};
export default TestCreationPageV2;
import React, { useState, useEffect } from 'react';
import { format, addMinutes, parseISO, differenceInMinutes } from 'date-fns';
import { tr } from 'date-fns/locale';
import { 
  X, Calendar, Clock, MapPin, Users, Bell, Video, Tag, 
  FileText, Repeat, AlertCircle, CheckCircle, Link, 
  Plus, Trash2, Edit, Save, ChevronDown, ChevronUp
} from 'lucide-react';
import axios from '../../lib/api';
import { toast } from '../../hooks/useToast';
import { Button } from '../ui/button';
import { Card } from '../ui/card';
import { Input } from '../ui/input';
import { Textarea } from '../ui';
import { Select } from '../ui/select';
import { Badge } from '../ui/badge';
import { Alert } from '../ui/alert';
import { Tabs } from '../ui/tabs';
import { useAuth } from '../../hooks/useAuth';
/**
 * Enhanced AppointmentModal with advanced features
 */
const AppointmentModalV2 = ({ appointment, timeSlot, onClose, onSave }) => {
  const { user } = useAuth();
  const isEditMode = !!appointment;
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    type: 'session',
    start_time: null,
    end_time: null,
    location: '',
    is_online: false,
    meeting_url: '',
    beneficiaries: [],
    trainer_id: user?.role === 'trainer' ? user.id : '',
    status: 'pending',
    reminder_enabled: true,
    reminder_time: 15,
    recurrence_type: 'none',
    recurrence_end_date: null,
    recurrence_days: [],
    google_event_id: '',
    tags: [],
    attachments: [],
    notes: '',
    color: '#3B82F6',
    notification_settings: {
      email: true,
      sms: false,
      push: true
    },
    custom_fields: {}
  });
  const [beneficiaries, setBeneficiaries] = useState([]);
  const [trainers, setTrainers] = useState([]);
  const [conflicts, setConflicts] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('details');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [validateForm, setValidateForm] = useState(false);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [templates, setTemplates] = useState([]);
  useEffect(() => {
    if (appointment) {
      setFormData({
        ...appointment,
        start_time: parseISO(appointment.start_time),
        end_time: parseISO(appointment.end_time),
        beneficiaries: appointment.beneficiary_ids || []
      });
    } else if (timeSlot) {
      setFormData({
        ...formData,
        start_time: timeSlot.start,
        end_time: timeSlot.end
      });
    }
    fetchInitialData();
  }, [appointment, timeSlot]);
  useEffect(() => {
    if (formData.start_time && formData.end_time) {
      checkConflicts();
    }
  }, [formData.start_time, formData.end_time, formData.beneficiaries, formData.trainer_id]);
  const fetchInitialData = async () => {
    try {
      const [beneficiariesRes, trainersRes, templatesRes] = await Promise.all([
        axios.get('/api/beneficiaries'),
        axios.get('/api/users?role=trainer'),
        axios.get('/api/appointments/templates')
      ]);
      setBeneficiaries(beneficiariesRes.data);
      setTrainers(trainersRes.data);
      setTemplates(templatesRes.data);
    } catch (error) {
      console.error('Error fetching initial data:', error);
    }
  };
  const checkConflicts = async () => {
    if (!formData.start_time || !formData.end_time) return;
    try {
      const response = await axios.post('/api/appointments/check-conflicts', {
        start_time: formData.start_time.toISOString(),
        end_time: formData.end_time.toISOString(),
        trainer_id: formData.trainer_id,
        beneficiary_ids: formData.beneficiaries,
        exclude_id: appointment?.id
      });
      setConflicts(response.data.conflicts);
      setSuggestions(response.data.suggestions);
    } catch (error) {
      console.error('Error checking conflicts:', error);
    }
  };
  const fetchAvailableSlots = async () => {
    if (!formData.trainer_id || !formData.beneficiaries.length) return;
    try {
      const response = await axios.post('/api/appointments/available-slots', {
        trainer_id: formData.trainer_id,
        beneficiary_ids: formData.beneficiaries,
        date: format(formData.start_time || new Date(), 'yyyy-MM-dd'),
        duration: differenceInMinutes(formData.end_time, formData.start_time)
      });
      setAvailableSlots(response.data);
    } catch (error) {
      console.error('Error fetching available slots:', error);
    }
  };
  const applyTemplate = (template) => {
    setFormData({
      ...formData,
      ...template,
      start_time: formData.start_time,
      end_time: formData.end_time
    });
    toast({
      title: 'Şablon Uygulandı',
      description: template.title,
      variant: 'success'
    });
  };
  const handleSubmit = async (e) => {
    e.preventDefault();
    setValidateForm(true);
    if (!formData.title || !formData.start_time || !formData.end_time) {
      toast({
        title: 'Hata',
        description: 'Lütfen zorunlu alanları doldurun',
        variant: 'error'
      });
      return;
    }
    if (conflicts.length > 0 && !window.confirm('Çakışmalar var. Devam etmek istiyor musunuz?')) {
      return;
    }
    setLoading(true);
    try {
      const data = {
        ...formData,
        start_time: formData.start_time.toISOString(),
        end_time: formData.end_time.toISOString(),
        beneficiary_ids: formData.beneficiaries
      };
      if (isEditMode) {
        await axios.put(`/api/appointments/${appointment.id}`, data);
        toast({
          title: 'Başarılı',
          description: 'Randevu güncellendi',
          variant: 'success'
        });
      } else {
        await axios.post('/api/appointments', data);
        toast({
          title: 'Başarılı',
          description: 'Randevu oluşturuldu',
          variant: 'success'
        });
      }
      onSave();
    } catch (error) {
      toast({
        title: 'Hata',
        description: error.response?.data?.message || 'İşlem başarısız',
        variant: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  const handleDelete = async () => {
    if (!window.confirm('Bu randevuyu silmek istediğinizden emin misiniz?')) {
      return;
    }
    setLoading(true);
    try {
      await axios.delete(`/api/appointments/${appointment.id}`);
      toast({
        title: 'Başarılı',
        description: 'Randevu silindi',
        variant: 'success'
      });
      onSave();
    } catch (error) {
      toast({
        title: 'Hata',
        description: 'Randevu silinemedi',
        variant: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  const handleGoogleSync = async () => {
    try {
      const response = await axios.post(`/api/appointments/${appointment.id}/sync-google`);
      setFormData({
        ...formData,
        google_event_id: response.data.google_event_id
      });
      toast({
        title: 'Başarılı',
        description: 'Google Takvim ile senkronize edildi',
        variant: 'success'
      });
    } catch (error) {
      toast({
        title: 'Hata',
        description: 'Senkronizasyon başarısız',
        variant: 'error'
      });
    }
  };
  const handleDurationChange = (duration) => {
    if (formData.start_time) {
      setFormData({
        ...formData,
        end_time: addMinutes(formData.start_time, duration)
      });
    }
  };
  const getStatusBadge = (status) => {
    const statusMap = {
      confirmed: { label: 'Onaylandı', variant: 'success' },
      pending: { label: 'Beklemede', variant: 'warning' },
      cancelled: { label: 'İptal', variant: 'error' }
    };
    const { label, variant } = statusMap[status] || statusMap.pending;
    return <Badge variant={variant}>{label}</Badge>;
  };
  const getTypeIcon = (type) => {
    const icons = {
      session: <Users className="h-4 w-4" />,
      evaluation: <FileText className="h-4 w-4" />,
      meeting: <Calendar className="h-4 w-4" />
    };
    return icons[type] || <Calendar className="h-4 w-4" />;
  };
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 border-b flex items-center justify-between">
          <div className="flex items-center gap-3">
            {getTypeIcon(formData.type)}
            <h2 className="text-xl font-semibold">
              {isEditMode ? 'Randevuyu Düzenle' : 'Yeni Randevu'}
            </h2>
            {isEditMode && getStatusBadge(formData.status)}
          </div>
          <div className="flex items-center gap-2">
            {isEditMode && formData.google_event_id && (
              <Badge variant="secondary">
                <Link className="h-3 w-3 mr-1" />
                Google Takvim
              </Badge>
            )}
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          <form onSubmit={handleSubmit}>
            {/* Conflicts Alert */}
            {conflicts.length > 0 && (
              <Alert variant="warning" className="m-6 mb-0">
                <AlertCircle className="h-4 w-4" />
                <div>
                  <h4 className="font-semibold">Çakışmalar Bulundu</h4>
                  <ul className="text-sm mt-1">
                    {conflicts.map((conflict, index) => (
                      <li key={index}>
                        {conflict.title} - {format(parseISO(conflict.start_time), 'HH:mm')}
                      </li>
                    ))}
                  </ul>
                </div>
              </Alert>
            )}
            {/* Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab} className="p-6">
              <Tabs.TabsList>
                <Tabs.TabTrigger value="details">Detaylar</Tabs.TabTrigger>
                <Tabs.TabTrigger value="participants">Katılımcılar</Tabs.TabTrigger>
                <Tabs.TabTrigger value="schedule">Zamanlama</Tabs.TabTrigger>
                {isEditMode && <Tabs.TabTrigger value="history">Geçmiş</Tabs.TabTrigger>}
              </Tabs.TabsList>
              {/* Details Tab */}
              <Tabs.TabContent value="details" className="space-y-4">
                {/* Templates */}
                {!isEditMode && templates.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Şablon Kullan
                    </label>
                    <div className="flex gap-2">
                      {templates.map(template => (
                        <Button
                          key={template.id}
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => applyTemplate(template)}
                        >
                          {template.title}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}
                {/* Basic Fields */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Başlık *
                    </label>
                    <Input
                      value={formData.title}
                      onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      placeholder="Randevu başlığı"
                      className={validateForm && !formData.title ? 'border-red-500' : ''}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tür
                    </label>
                    <Select
                      value={formData.type}
                      onValueChange={(value) => setFormData({ ...formData, type: value })}
                    >
                      <Select.Option value="session">Oturum</Select.Option>
                      <Select.Option value="evaluation">Değerlendirme</Select.Option>
                      <Select.Option value="meeting">Toplantı</Select.Option>
                    </Select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Açıklama
                  </label>
                  <Textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Randevu açıklaması (opsiyonel)"
                    rows={3}
                  />
                </div>
                {/* Location */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Konum
                  </label>
                  <div className="flex gap-2">
                    <div className="flex-1">
                      <Input
                        value={formData.location}
                        onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                        placeholder="Randevu konumu"
                        disabled={formData.is_online}
                      />
                    </div>
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={formData.is_online}
                        onChange={(e) => setFormData({ 
                          ...formData, 
                          is_online: e.target.checked,
                          location: e.target.checked ? '' : formData.location
                        })}
                      />
                      <Video className="h-4 w-4" />
                      <span>Online</span>
                    </label>
                  </div>
                  {formData.is_online && (
                    <Input
                      value={formData.meeting_url}
                      onChange={(e) => setFormData({ ...formData, meeting_url: e.target.value })}
                      placeholder="Toplantı linki"
                      className="mt-2"
                    />
                  )}
                </div>
                {/* Tags */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Etiketler
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {['Önemli', 'Acil', 'Rutin', 'İlk Görüşme', 'Takip'].map(tag => (
                      <label key={tag} className="flex items-center gap-1">
                        <input
                          type="checkbox"
                          checked={formData.tags.includes(tag)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setFormData({ ...formData, tags: [...formData.tags, tag] });
                            } else {
                              setFormData({ 
                                ...formData, 
                                tags: formData.tags.filter(t => t !== tag) 
                              });
                            }
                          }}
                        />
                        <Badge variant="secondary">{tag}</Badge>
                      </label>
                    ))}
                  </div>
                </div>
                {/* Advanced Options */}
                <div className="pt-4">
                  <button
                    type="button"
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
                  >
                    {showAdvanced ? <ChevronUp /> : <ChevronDown />}
                    Gelişmiş Seçenekler
                  </button>
                  {showAdvanced && (
                    <div className="mt-4 space-y-4 p-4 border rounded-lg">
                      {/* Color */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Renk
                        </label>
                        <div className="flex gap-2">
                          {['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444'].map(color => (
                            <button
                              key={color}
                              type="button"
                              className={`w-8 h-8 rounded-full ${
                                formData.color === color ? 'ring-2 ring-offset-2 ring-gray-900' : ''
                              }`}
                              style={{ backgroundColor: color }}
                              onClick={() => setFormData({ ...formData, color })}
                            />
                          ))}
                        </div>
                      </div>
                      {/* Notifications */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Bildirim Ayarları
                        </label>
                        <div className="space-y-2">
                          <label className="flex items-center gap-2">
                            <input
                              type="checkbox"
                              checked={formData.notification_settings.email}
                              onChange={(e) => setFormData({
                                ...formData,
                                notification_settings: {
                                  ...formData.notification_settings,
                                  email: e.target.checked
                                }
                              })}
                            />
                            <span className="text-sm">E-posta bildirimi</span>
                          </label>
                          <label className="flex items-center gap-2">
                            <input
                              type="checkbox"
                              checked={formData.notification_settings.sms}
                              onChange={(e) => setFormData({
                                ...formData,
                                notification_settings: {
                                  ...formData.notification_settings,
                                  sms: e.target.checked
                                }
                              })}
                            />
                            <span className="text-sm">SMS bildirimi</span>
                          </label>
                          <label className="flex items-center gap-2">
                            <input
                              type="checkbox"
                              checked={formData.notification_settings.push}
                              onChange={(e) => setFormData({
                                ...formData,
                                notification_settings: {
                                  ...formData.notification_settings,
                                  push: e.target.checked
                                }
                              })}
                            />
                            <span className="text-sm">Push bildirimi</span>
                          </label>
                        </div>
                      </div>
                      {/* Notes */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Özel Notlar
                        </label>
                        <Textarea
                          value={formData.notes}
                          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                          placeholder="Özel notlar (sadece siz görebilirsiniz)"
                          rows={2}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </Tabs.TabContent>
              {/* Participants Tab */}
              <Tabs.TabContent value="participants" className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Eğitmen
                  </label>
                  <Select
                    value={formData.trainer_id}
                    onValueChange={(value) => setFormData({ ...formData, trainer_id: value })}
                  >
                    <Select.Option value="">Eğitmen Seçin</Select.Option>
                    {trainers.map(trainer => (
                      <Select.Option key={trainer.id} value={trainer.id}>
                        {trainer.name}
                      </Select.Option>
                    ))}
                  </Select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Katılımcılar
                  </label>
                  <div className="space-y-2">
                    {beneficiaries.map(beneficiary => (
                      <label key={beneficiary.id} className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={formData.beneficiaries.includes(beneficiary.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setFormData({
                                ...formData,
                                beneficiaries: [...formData.beneficiaries, beneficiary.id]
                              });
                            } else {
                              setFormData({
                                ...formData,
                                beneficiaries: formData.beneficiaries.filter(id => id !== beneficiary.id)
                              });
                            }
                          }}
                        />
                        <span>{beneficiary.name}</span>
                        <Badge variant="secondary" size="sm">
                          {beneficiary.program_name}
                        </Badge>
                      </label>
                    ))}
                  </div>
                </div>
                {/* Participant Conflicts */}
                {conflicts.length > 0 && (
                  <Alert variant="warning">
                    <AlertCircle className="h-4 w-4" />
                    <div>
                      <h4 className="font-semibold">Katılımcı Çakışmaları</h4>
                      <p className="text-sm mt-1">
                        Seçilen katılımcıların bu zaman diliminde başka randevuları var.
                      </p>
                    </div>
                  </Alert>
                )}
              </Tabs.TabContent>
              {/* Schedule Tab */}
              <Tabs.TabContent value="schedule" className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Başlangıç *
                    </label>
                    <Input
                      type="datetime-local"
                      value={formData.start_time ? format(formData.start_time, "yyyy-MM-dd'T'HH:mm") : ''}
                      onChange={(e) => setFormData({ 
                        ...formData, 
                        start_time: e.target.value ? new Date(e.target.value) : null 
                      })}
                      className={validateForm && !formData.start_time ? 'border-red-500' : ''}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Bitiş *
                    </label>
                    <Input
                      type="datetime-local"
                      value={formData.end_time ? format(formData.end_time, "yyyy-MM-dd'T'HH:mm") : ''}
                      onChange={(e) => setFormData({ 
                        ...formData, 
                        end_time: e.target.value ? new Date(e.target.value) : null 
                      })}
                      className={validateForm && !formData.end_time ? 'border-red-500' : ''}
                    />
                  </div>
                </div>
                {/* Quick Duration Buttons */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Hızlı Süre Seçimi
                  </label>
                  <div className="flex gap-2">
                    {[30, 45, 60, 90, 120].map(duration => (
                      <Button
                        key={duration}
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => handleDurationChange(duration)}
                        disabled={!formData.start_time}
                      >
                        {duration} dk
                      </Button>
                    ))}
                  </div>
                </div>
                {/* Reminder */}
                <div>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={formData.reminder_enabled}
                      onChange={(e) => setFormData({ 
                        ...formData, 
                        reminder_enabled: e.target.checked 
                      })}
                    />
                    <Bell className="h-4 w-4" />
                    <span>Hatırlatıcı</span>
                  </label>
                  {formData.reminder_enabled && (
                    <Select
                      value={formData.reminder_time}
                      onValueChange={(value) => setFormData({ 
                        ...formData, 
                        reminder_time: parseInt(value) 
                      })}
                      className="mt-2"
                    >
                      <Select.Option value="5">5 dakika önce</Select.Option>
                      <Select.Option value="15">15 dakika önce</Select.Option>
                      <Select.Option value="30">30 dakika önce</Select.Option>
                      <Select.Option value="60">1 saat önce</Select.Option>
                      <Select.Option value="1440">1 gün önce</Select.Option>
                    </Select>
                  )}
                </div>
                {/* Recurrence */}
                <div>
                  <label className="flex items-center gap-2">
                    <Repeat className="h-4 w-4" />
                    <span>Tekrarlayan Randevu</span>
                  </label>
                  <Select
                    value={formData.recurrence_type}
                    onValueChange={(value) => setFormData({ 
                      ...formData, 
                      recurrence_type: value 
                    })}
                    className="mt-2"
                  >
                    <Select.Option value="none">Tekrar Yok</Select.Option>
                    <Select.Option value="daily">Günlük</Select.Option>
                    <Select.Option value="weekly">Haftalık</Select.Option>
                    <Select.Option value="monthly">Aylık</Select.Option>
                    <Select.Option value="custom">Özel</Select.Option>
                  </Select>
                  {formData.recurrence_type !== 'none' && (
                    <div className="mt-2 space-y-2">
                      <Input
                        type="date"
                        value={formData.recurrence_end_date || ''}
                        onChange={(e) => setFormData({ 
                          ...formData, 
                          recurrence_end_date: e.target.value 
                        })}
                        placeholder="Bitiş tarihi"
                      />
                      {formData.recurrence_type === 'weekly' && (
                        <div className="flex gap-2">
                          {['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'].map((day, index) => (
                            <label key={day} className="flex items-center gap-1">
                              <input
                                type="checkbox"
                                checked={formData.recurrence_days.includes(index)}
                                onChange={(e) => {
                                  if (e.target.checked) {
                                    setFormData({
                                      ...formData,
                                      recurrence_days: [...formData.recurrence_days, index]
                                    });
                                  } else {
                                    setFormData({
                                      ...formData,
                                      recurrence_days: formData.recurrence_days.filter(d => d !== index)
                                    });
                                  }
                                }}
                              />
                              <span className="text-sm">{day}</span>
                            </label>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
                {/* Available Slots */}
                {availableSlots.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Önerilen Zamanlar
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      {availableSlots.map((slot, index) => (
                        <Button
                          key={index}
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setFormData({
                              ...formData,
                              start_time: parseISO(slot.start),
                              end_time: parseISO(slot.end)
                            });
                          }}
                        >
                          {format(parseISO(slot.start), 'HH:mm')} - {format(parseISO(slot.end), 'HH:mm')}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}
              </Tabs.TabContent>
              {/* History Tab */}
              {isEditMode && (
                <Tabs.TabContent value="history" className="space-y-4">
                  <div>
                    <h4 className="font-medium mb-3">Randevu Geçmişi</h4>
                    <div className="space-y-3">
                      {appointment.history?.map((entry, index) => (
                        <div key={index} className="flex items-start gap-3 text-sm">
                          <div className="w-2 h-2 bg-gray-400 rounded-full mt-1.5"></div>
                          <div>
                            <p className="font-medium">{entry.action}</p>
                            <p className="text-gray-600">
                              {entry.user_name} - {format(parseISO(entry.created_at), 'dd MMM yyyy HH:mm', { locale: tr })}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  {appointment.google_event_id && (
                    <div>
                      <h4 className="font-medium mb-3">Google Takvim</h4>
                      <div className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-3">
                          <Link className="h-5 w-5 text-blue-600" />
                          <div>
                            <p className="font-medium">Google Takvim'de</p>
                            <p className="text-sm text-gray-600">
                              Son senkronizasyon: {format(new Date(), 'dd MMM yyyy HH:mm', { locale: tr })}
                            </p>
                          </div>
                        </div>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={handleGoogleSync}
                        >
                          <RefreshCw className="h-4 w-4 mr-2" />
                          Yenile
                        </Button>
                      </div>
                    </div>
                  )}
                </Tabs.TabContent>
              )}
            </Tabs>
          </form>
        </div>
        {/* Footer */}
        <div className="p-6 border-t flex items-center justify-between">
          <div>
            {isEditMode && (
              <Button
                type="button"
                variant="destructive"
                onClick={handleDelete}
                disabled={loading}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Sil
              </Button>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={loading}
            >
              İptal
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={loading}
            >
              <Save className="h-4 w-4 mr-2" />
              {isEditMode ? 'Güncelle' : 'Oluştur'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
export default AppointmentModalV2;
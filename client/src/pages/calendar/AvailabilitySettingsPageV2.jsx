import React, { useState, useEffect } from 'react';
import { format, setHours, setMinutes, addDays, startOfWeek, endOfWeek } from 'date-fns';
import { tr } from 'date-fns/locale';
import { 
  Clock, Calendar, Plus, X, Save, Copy, AlertCircle, 
  CheckCircle, Settings, Coffee, Ban, Moon, Sun,
  ChevronDown, ChevronUp, Trash2, Edit, RefreshCw
} from 'lucide-react';
import axios from '../../lib/api';
import { toast } from '../../hooks/useToast';
import { Button } from '../../components/ui/button';
import { Card } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Select } from '../../components/ui/select';
import { Badge } from '../../components/ui/badge';
import { Alert } from '../../components/ui/alert';
import { Tabs } from '../../components/ui/tabs';
import { Textarea, Label } from '../../components/ui';
import { useAuth } from '../../hooks/useAuth';

/**
 * Enhanced AvailabilitySettingsPage with advanced scheduling features
 */
const AvailabilitySettingsPageV2 = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('schedule');
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  
  // Weekly Schedule State
  const [weeklySchedule, setWeeklySchedule] = useState({
    monday: { enabled: true, slots: [] },
    tuesday: { enabled: true, slots: [] },
    wednesday: { enabled: true, slots: [] },
    thursday: { enabled: true, slots: [] },
    friday: { enabled: true, slots: [] },
    saturday: { enabled: false, slots: [] },
    sunday: { enabled: false, slots: [] }
  });
  
  // Settings State
  const [settings, setSettings] = useState({
    timezone: 'Europe/Istanbul',
    defaultDuration: 60,
    bufferTime: 15,
    minAdvanceNotice: 24,
    maxAdvanceBooking: 30,
    slotIncrement: 30,
    allowOverlapping: false,
    autoAcceptAppointments: false,
    sendConfirmationEmail: true,
    sendReminderEmail: true,
    maxDailyAppointments: 8,
    maxWeeklyAppointments: 40,
    breakBetweenAppointments: 5,
    lunchBreak: {
      enabled: true,
      startTime: '12:00',
      endTime: '13:00'
    }
  });
  
  // Special Days State
  const [specialDays, setSpecialDays] = useState([]);
  const [holidays, setHolidays] = useState([]);
  const [workingHours, setWorkingHours] = useState({
    start: '09:00',
    end: '18:00'
  });
  
  // Templates
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  
  // Blocked Times
  const [blockedTimes, setBlockedTimes] = useState([]);
  const [recurringBlocks, setRecurringBlocks] = useState([]);
  
  // Override Rules
  const [overrideRules, setOverrideRules] = useState([]);
  
  // View State
  const [expandedDays, setExpandedDays] = useState({});
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  const [previewDate, setPreviewDate] = useState(new Date());

  useEffect(() => {
    fetchAvailabilityData();
  }, []);

  const fetchAvailabilityData = async () => {
    try {
      setLoading(true);
      const [scheduleRes, settingsRes, specialRes, templatesRes, blockedRes] = await Promise.all([
        axios.get('/api/availability/schedule'),
        axios.get('/api/availability/settings'),
        axios.get('/api/availability/special-days'),
        axios.get('/api/availability/templates'),
        axios.get('/api/availability/blocked-times')
      ]);
      
      setWeeklySchedule(scheduleRes.data.schedule || weeklySchedule);
      setSettings(settingsRes.data.settings || settings);
      setSpecialDays(specialRes.data.specialDays || []);
      setHolidays(specialRes.data.holidays || []);
      setTemplates(templatesRes.data || []);
      setBlockedTimes(blockedRes.data.blockedTimes || []);
      setRecurringBlocks(blockedRes.data.recurringBlocks || []);
    } catch (error) {
      console.error('Error fetching availability data:', error);
      toast({
        title: 'Hata',
        description: 'Uygunluk verileri yüklenemedi',
        variant: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const addTimeSlot = (day) => {
    const newSlot = {
      id: Date.now().toString(),
      startTime: '09:00',
      endTime: '10:00',
      maxAppointments: 1,
      appointmentTypes: ['all']
    };
    
    setWeeklySchedule({
      ...weeklySchedule,
      [day]: {
        ...weeklySchedule[day],
        slots: [...weeklySchedule[day].slots, newSlot]
      }
    });
  };

  const updateTimeSlot = (day, slotId, updates) => {
    setWeeklySchedule({
      ...weeklySchedule,
      [day]: {
        ...weeklySchedule[day],
        slots: weeklySchedule[day].slots.map(slot => 
          slot.id === slotId ? { ...slot, ...updates } : slot
        )
      }
    });
  };

  const removeTimeSlot = (day, slotId) => {
    setWeeklySchedule({
      ...weeklySchedule,
      [day]: {
        ...weeklySchedule[day],
        slots: weeklySchedule[day].slots.filter(slot => slot.id !== slotId)
      }
    });
  };

  const copyDaySchedule = (fromDay, toDay) => {
    setWeeklySchedule({
      ...weeklySchedule,
      [toDay]: {
        ...weeklySchedule[fromDay],
        slots: weeklySchedule[fromDay].slots.map(slot => ({
          ...slot,
          id: Date.now().toString() + Math.random()
        }))
      }
    });
    
    toast({
      title: 'Başarılı',
      description: 'Program kopyalandı',
      variant: 'success'
    });
  };

  const applyTemplate = (template) => {
    setWeeklySchedule(template.schedule);
    setSettings({ ...settings, ...template.settings });
    
    toast({
      title: 'Başarılı',
      description: 'Şablon uygulandı',
      variant: 'success'
    });
  };

  const saveAsTemplate = async () => {
    const templateName = prompt('Şablon adı:');
    if (!templateName) return;
    
    try {
      await axios.post('/api/availability/templates', {
        name: templateName,
        schedule: weeklySchedule,
        settings: settings
      });
      
      toast({
        title: 'Başarılı',
        description: 'Şablon kaydedildi',
        variant: 'success'
      });
      
      fetchAvailabilityData();
    } catch (error) {
      toast({
        title: 'Hata',
        description: 'Şablon kaydedilemedi',
        variant: 'error'
      });
    }
  };

  const addSpecialDay = () => {
    const newSpecialDay = {
      id: Date.now().toString(),
      date: format(new Date(), 'yyyy-MM-dd'),
      type: 'custom',
      slots: [],
      reason: ''
    };
    
    setSpecialDays([...specialDays, newSpecialDay]);
  };

  const addBlockedTime = () => {
    const newBlock = {
      id: Date.now().toString(),
      startDate: format(new Date(), 'yyyy-MM-dd'),
      endDate: format(new Date(), 'yyyy-MM-dd'),
      startTime: '09:00',
      endTime: '10:00',
      reason: '',
      recurring: false,
      recurrencePattern: 'weekly'
    };
    
    setBlockedTimes([...blockedTimes, newBlock]);
  };

  const saveAvailability = async () => {
    setSaving(true);
    
    try {
      await Promise.all([
        axios.put('/api/availability/schedule', { schedule: weeklySchedule }),
        axios.put('/api/availability/settings', { settings }),
        axios.put('/api/availability/special-days', { specialDays, holidays }),
        axios.put('/api/availability/blocked-times', { blockedTimes, recurringBlocks })
      ]);
      
      toast({
        title: 'Başarılı',
        description: 'Uygunluk ayarları kaydedildi',
        variant: 'success'
      });
    } catch (error) {
      toast({
        title: 'Hata',
        description: 'Ayarlar kaydedilemedi',
        variant: 'error'
      });
    } finally {
      setSaving(false);
    }
  };

  const generateTimeOptions = () => {
    const options = [];
    for (let hour = 0; hour < 24; hour++) {
      for (let minute = 0; minute < 60; minute += settings.slotIncrement) {
        const time = format(setMinutes(setHours(new Date(), hour), minute), 'HH:mm');
        options.push(time);
      }
    }
    return options;
  };

  const getDayName = (day) => {
    const names = {
      monday: 'Pazartesi',
      tuesday: 'Salı',
      wednesday: 'Çarşamba',
      thursday: 'Perşembe',
      friday: 'Cuma',
      saturday: 'Cumartesi',
      sunday: 'Pazar'
    };
    return names[day];
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Uygunluk Ayarları</h1>
            <p className="text-gray-600 mt-1">Randevu alınabilir zamanlarınızı yönetin</p>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={saveAsTemplate}
            >
              <Save className="h-4 w-4 mr-2" />
              Şablon Olarak Kaydet
            </Button>
            
            <Button
              onClick={saveAvailability}
              disabled={saving}
            >
              <Save className="h-4 w-4 mr-2" />
              Kaydet
            </Button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <Tabs.TabsList>
          <Tabs.TabTrigger value="schedule">Haftalık Program</Tabs.TabTrigger>
          <Tabs.TabTrigger value="settings">Genel Ayarlar</Tabs.TabTrigger>
          <Tabs.TabTrigger value="special">Özel Günler</Tabs.TabTrigger>
          <Tabs.TabTrigger value="blocked">Bloklu Zamanlar</Tabs.TabTrigger>
          <Tabs.TabTrigger value="preview">Önizleme</Tabs.TabTrigger>
        </Tabs.TabsList>

        {/* Weekly Schedule Tab */}
        <Tabs.TabContent value="schedule">
          <Card className="p-6">
            {/* Templates */}
            {templates.length > 0 && (
              <div className="mb-6">
                <Label>Şablonlar</Label>
                <div className="flex gap-2 mt-2">
                  {templates.map(template => (
                    <Button
                      key={template.id}
                      variant="outline"
                      size="sm"
                      onClick={() => applyTemplate(template)}
                    >
                      {template.name}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {/* Working Hours */}
            <div className="mb-6">
              <Label>Genel Çalışma Saatleri</Label>
              <div className="flex items-center gap-4 mt-2">
                <div className="flex items-center gap-2">
                  <Sun className="h-4 w-4 text-yellow-600" />
                  <Select
                    value={workingHours.start}
                    onValueChange={(value) => setWorkingHours({ ...workingHours, start: value })}
                  >
                    {generateTimeOptions().map(time => (
                      <Select.Option key={time} value={time}>{time}</Select.Option>
                    ))}
                  </Select>
                </div>
                <span>-</span>
                <div className="flex items-center gap-2">
                  <Moon className="h-4 w-4 text-blue-600" />
                  <Select
                    value={workingHours.end}
                    onValueChange={(value) => setWorkingHours({ ...workingHours, end: value })}
                  >
                    {generateTimeOptions().map(time => (
                      <Select.Option key={time} value={time}>{time}</Select.Option>
                    ))}
                  </Select>
                </div>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    Object.keys(weeklySchedule).forEach(day => {
                      if (weeklySchedule[day].enabled) {
                        setWeeklySchedule({
                          ...weeklySchedule,
                          [day]: {
                            ...weeklySchedule[day],
                            slots: [{
                              id: Date.now().toString(),
                              startTime: workingHours.start,
                              endTime: workingHours.end,
                              maxAppointments: 1,
                              appointmentTypes: ['all']
                            }]
                          }
                        });
                      }
                    });
                  }}
                >
                  Tüm Günlere Uygula
                </Button>
              </div>
            </div>

            {/* Days */}
            <div className="space-y-4">
              {Object.entries(weeklySchedule).map(([day, daySchedule]) => (
                <div key={day} className="border rounded-lg">
                  <div
                    className="p-4 flex items-center justify-between cursor-pointer"
                    onClick={() => setExpandedDays({ ...expandedDays, [day]: !expandedDays[day] })}
                  >
                    <div className="flex items-center gap-3">
                      {expandedDays[day] ? <ChevronUp /> : <ChevronDown />}
                      <h3 className="font-medium">{getDayName(day)}</h3>
                      <label className="flex items-center gap-2" onClick={e => e.stopPropagation()}>
                        <input
                          type="checkbox"
                          checked={daySchedule.enabled}
                          onChange={(e) => setWeeklySchedule({
                            ...weeklySchedule,
                            [day]: { ...daySchedule, enabled: e.target.checked }
                          })}
                        />
                        <span className="text-sm">Aktif</span>
                      </label>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {daySchedule.slots.length > 0 && (
                        <Badge variant="secondary">
                          {daySchedule.slots.length} zaman aralığı
                        </Badge>
                      )}
                      <div className="relative">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                          }}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                        <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border p-2 hidden group-hover:block z-10">
                          <p className="text-sm font-medium mb-2">Kopyala:</p>
                          {Object.keys(weeklySchedule).filter(d => d !== day).map(targetDay => (
                            <button
                              key={targetDay}
                              onClick={() => copyDaySchedule(day, targetDay)}
                              className="w-full text-left px-3 py-1 rounded hover:bg-gray-100 text-sm"
                            >
                              {getDayName(targetDay)}'ye
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {expandedDays[day] && daySchedule.enabled && (
                    <div className="p-4 pt-0 space-y-3">
                      {daySchedule.slots.map(slot => (
                        <div key={slot.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                          <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4 text-gray-600" />
                            <Select
                              value={slot.startTime}
                              onValueChange={(value) => updateTimeSlot(day, slot.id, { startTime: value })}
                            >
                              {generateTimeOptions().map(time => (
                                <Select.Option key={time} value={time}>{time}</Select.Option>
                              ))}
                            </Select>
                            <span>-</span>
                            <Select
                              value={slot.endTime}
                              onValueChange={(value) => updateTimeSlot(day, slot.id, { endTime: value })}
                            >
                              {generateTimeOptions().map(time => (
                                <Select.Option key={time} value={time}>{time}</Select.Option>
                              ))}
                            </Select>
                          </div>
                          
                          <div className="flex items-center gap-2">
                            <Users className="h-4 w-4 text-gray-600" />
                            <Input
                              type="number"
                              value={slot.maxAppointments}
                              onChange={(e) => updateTimeSlot(day, slot.id, { 
                                maxAppointments: parseInt(e.target.value) || 1 
                              })}
                              className="w-16"
                              min="1"
                            />
                            <span className="text-sm text-gray-600">randevu</span>
                          </div>
                          
                          <div className="flex items-center gap-2">
                            <Select
                              value={slot.appointmentTypes.includes('all') ? 'all' : 'specific'}
                              onValueChange={(value) => {
                                if (value === 'all') {
                                  updateTimeSlot(day, slot.id, { appointmentTypes: ['all'] });
                                } else {
                                  updateTimeSlot(day, slot.id, { appointmentTypes: ['session'] });
                                }
                              }}
                            >
                              <Select.Option value="all">Tüm Türler</Select.Option>
                              <Select.Option value="specific">Belirli Türler</Select.Option>
                            </Select>
                            
                            {!slot.appointmentTypes.includes('all') && (
                              <div className="flex gap-1">
                                {['session', 'evaluation', 'meeting'].map(type => (
                                  <label key={type} className="flex items-center gap-1">
                                    <input
                                      type="checkbox"
                                      checked={slot.appointmentTypes.includes(type)}
                                      onChange={(e) => {
                                        if (e.target.checked) {
                                          updateTimeSlot(day, slot.id, {
                                            appointmentTypes: [...slot.appointmentTypes, type]
                                          });
                                        } else {
                                          updateTimeSlot(day, slot.id, {
                                            appointmentTypes: slot.appointmentTypes.filter(t => t !== type)
                                          });
                                        }
                                      }}
                                    />
                                    <span className="text-sm">{type}</span>
                                  </label>
                                ))}
                              </div>
                            )}
                          </div>
                          
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeTimeSlot(day, slot.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => addTimeSlot(day)}
                      >
                        <Plus className="h-4 w-4 mr-2" />
                        Zaman Aralığı Ekle
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>
        </Tabs.TabContent>

        {/* Settings Tab */}
        <Tabs.TabContent value="settings">
          <Card className="p-6">
            <div className="grid grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold mb-4">Randevu Ayarları</h3>
                
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="defaultDuration">Varsayılan Süre (dk)</Label>
                    <Input
                      id="defaultDuration"
                      type="number"
                      value={settings.defaultDuration}
                      onChange={(e) => setSettings({ 
                        ...settings, 
                        defaultDuration: parseInt(e.target.value) || 60 
                      })}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="bufferTime">Randevular Arası Boşluk (dk)</Label>
                    <Input
                      id="bufferTime"
                      type="number"
                      value={settings.bufferTime}
                      onChange={(e) => setSettings({ 
                        ...settings, 
                        bufferTime: parseInt(e.target.value) || 0 
                      })}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="minAdvanceNotice">Minimum Ön Bildirim (saat)</Label>
                    <Input
                      id="minAdvanceNotice"
                      type="number"
                      value={settings.minAdvanceNotice}
                      onChange={(e) => setSettings({ 
                        ...settings, 
                        minAdvanceNotice: parseInt(e.target.value) || 24 
                      })}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="maxAdvanceBooking">Maksimum İleri Tarih (gün)</Label>
                    <Input
                      id="maxAdvanceBooking"
                      type="number"
                      value={settings.maxAdvanceBooking}
                      onChange={(e) => setSettings({ 
                        ...settings, 
                        maxAdvanceBooking: parseInt(e.target.value) || 30 
                      })}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="slotIncrement">Zaman Aralığı (dk)</Label>
                    <Select
                      id="slotIncrement"
                      value={settings.slotIncrement}
                      onValueChange={(value) => setSettings({ 
                        ...settings, 
                        slotIncrement: parseInt(value) 
                      })}
                    >
                      <Select.Option value="15">15 dakika</Select.Option>
                      <Select.Option value="30">30 dakika</Select.Option>
                      <Select.Option value="45">45 dakika</Select.Option>
                      <Select.Option value="60">60 dakika</Select.Option>
                    </Select>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold mb-4">Sistem Ayarları</h3>
                
                <div className="space-y-4">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={settings.autoAcceptAppointments}
                      onChange={(e) => setSettings({ 
                        ...settings, 
                        autoAcceptAppointments: e.target.checked 
                      })}
                    />
                    <span>Randevuları Otomatik Onayla</span>
                  </label>
                  
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={settings.sendConfirmationEmail}
                      onChange={(e) => setSettings({ 
                        ...settings, 
                        sendConfirmationEmail: e.target.checked 
                      })}
                    />
                    <span>Onay E-postası Gönder</span>
                  </label>
                  
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={settings.sendReminderEmail}
                      onChange={(e) => setSettings({ 
                        ...settings, 
                        sendReminderEmail: e.target.checked 
                      })}
                    />
                    <span>Hatırlatma E-postası Gönder</span>
                  </label>
                  
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={settings.allowOverlapping}
                      onChange={(e) => setSettings({ 
                        ...settings, 
                        allowOverlapping: e.target.checked 
                      })}
                    />
                    <span>Çakışan Randevulara İzin Ver</span>
                  </label>
                </div>
                
                <div className="mt-6">
                  <label className="flex items-center gap-2 mb-3">
                    <Coffee className="h-4 w-4" />
                    <span>Öğle Arası</span>
                    <input
                      type="checkbox"
                      checked={settings.lunchBreak.enabled}
                      onChange={(e) => setSettings({ 
                        ...settings, 
                        lunchBreak: { 
                          ...settings.lunchBreak, 
                          enabled: e.target.checked 
                        }
                      })}
                    />
                  </label>
                  
                  {settings.lunchBreak.enabled && (
                    <div className="flex items-center gap-2">
                      <Select
                        value={settings.lunchBreak.startTime}
                        onValueChange={(value) => setSettings({ 
                          ...settings, 
                          lunchBreak: { 
                            ...settings.lunchBreak, 
                            startTime: value 
                          }
                        })}
                      >
                        {generateTimeOptions().map(time => (
                          <Select.Option key={time} value={time}>{time}</Select.Option>
                        ))}
                      </Select>
                      <span>-</span>
                      <Select
                        value={settings.lunchBreak.endTime}
                        onValueChange={(value) => setSettings({ 
                          ...settings, 
                          lunchBreak: { 
                            ...settings.lunchBreak, 
                            endTime: value 
                          }
                        })}
                      >
                        {generateTimeOptions().map(time => (
                          <Select.Option key={time} value={time}>{time}</Select.Option>
                        ))}
                      </Select>
                    </div>
                  )}
                </div>
              </div>
            </div>
            
            {/* Advanced Settings */}
            <div className="mt-6 pt-6 border-t">
              <button
                type="button"
                onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
                className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
              >
                {showAdvancedSettings ? <ChevronUp /> : <ChevronDown />}
                Gelişmiş Ayarlar
              </button>
              
              {showAdvancedSettings && (
                <div className="mt-4 grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="maxDailyAppointments">Günlük Maksimum Randevu</Label>
                    <Input
                      id="maxDailyAppointments"
                      type="number"
                      value={settings.maxDailyAppointments}
                      onChange={(e) => setSettings({ 
                        ...settings, 
                        maxDailyAppointments: parseInt(e.target.value) || 0 
                      })}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="maxWeeklyAppointments">Haftalık Maksimum Randevu</Label>
                    <Input
                      id="maxWeeklyAppointments"
                      type="number"
                      value={settings.maxWeeklyAppointments}
                      onChange={(e) => setSettings({ 
                        ...settings, 
                        maxWeeklyAppointments: parseInt(e.target.value) || 0 
                      })}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="breakBetweenAppointments">Randevular Arası Mola (dk)</Label>
                    <Input
                      id="breakBetweenAppointments"
                      type="number"
                      value={settings.breakBetweenAppointments}
                      onChange={(e) => setSettings({ 
                        ...settings, 
                        breakBetweenAppointments: parseInt(e.target.value) || 0 
                      })}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="timezone">Zaman Dilimi</Label>
                    <Select
                      id="timezone"
                      value={settings.timezone}
                      onValueChange={(value) => setSettings({ 
                        ...settings, 
                        timezone: value 
                      })}
                    >
                      <Select.Option value="Europe/Istanbul">Türkiye (İstanbul)</Select.Option>
                      <Select.Option value="UTC">UTC</Select.Option>
                      <Select.Option value="Europe/London">London</Select.Option>
                      <Select.Option value="America/New_York">New York</Select.Option>
                    </Select>
                  </div>
                </div>
              )}
            </div>
          </Card>
        </Tabs.TabContent>

        {/* Special Days Tab */}
        <Tabs.TabContent value="special">
          <Card className="p-6">
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Özel Günler</h3>
                <Button size="sm" onClick={addSpecialDay}>
                  <Plus className="h-4 w-4 mr-2" />
                  Özel Gün Ekle
                </Button>
              </div>
              
              <div className="space-y-3">
                {specialDays.map(day => (
                  <div key={day.id} className="p-4 border rounded-lg">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 space-y-3">
                        <div className="grid grid-cols-3 gap-3">
                          <Input
                            type="date"
                            value={day.date}
                            onChange={(e) => setSpecialDays(specialDays.map(d => 
                              d.id === day.id ? { ...d, date: e.target.value } : d
                            ))}
                          />
                          
                          <Select
                            value={day.type}
                            onValueChange={(value) => setSpecialDays(specialDays.map(d => 
                              d.id === day.id ? { ...d, type: value } : d
                            ))}
                          >
                            <Select.Option value="custom">Özel</Select.Option>
                            <Select.Option value="holiday">Tatil</Select.Option>
                            <Select.Option value="halfday">Yarım Gün</Select.Option>
                          </Select>
                          
                          <Input
                            placeholder="Açıklama"
                            value={day.reason}
                            onChange={(e) => setSpecialDays(specialDays.map(d => 
                              d.id === day.id ? { ...d, reason: e.target.value } : d
                            ))}
                          />
                        </div>
                        
                        {day.type === 'custom' && (
                          <div className="space-y-2">
                            {day.slots.map((slot, index) => (
                              <div key={index} className="flex items-center gap-2">
                                <Select
                                  value={slot.startTime}
                                  onValueChange={(value) => {
                                    const newSlots = [...day.slots];
                                    newSlots[index] = { ...slot, startTime: value };
                                    setSpecialDays(specialDays.map(d => 
                                      d.id === day.id ? { ...d, slots: newSlots } : d
                                    ));
                                  }}
                                >
                                  {generateTimeOptions().map(time => (
                                    <Select.Option key={time} value={time}>{time}</Select.Option>
                                  ))}
                                </Select>
                                <span>-</span>
                                <Select
                                  value={slot.endTime}
                                  onValueChange={(value) => {
                                    const newSlots = [...day.slots];
                                    newSlots[index] = { ...slot, endTime: value };
                                    setSpecialDays(specialDays.map(d => 
                                      d.id === day.id ? { ...d, slots: newSlots } : d
                                    ));
                                  }}
                                >
                                  {generateTimeOptions().map(time => (
                                    <Select.Option key={time} value={time}>{time}</Select.Option>
                                  ))}
                                </Select>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => {
                                    const newSlots = day.slots.filter((_, i) => i !== index);
                                    setSpecialDays(specialDays.map(d => 
                                      d.id === day.id ? { ...d, slots: newSlots } : d
                                    ));
                                  }}
                                >
                                  <X className="h-4 w-4" />
                                </Button>
                              </div>
                            ))}
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                const newSlots = [...day.slots, { startTime: '09:00', endTime: '10:00' }];
                                setSpecialDays(specialDays.map(d => 
                                  d.id === day.id ? { ...d, slots: newSlots } : d
                                ));
                              }}
                            >
                              <Plus className="h-4 w-4 mr-2" />
                              Zaman Ekle
                            </Button>
                          </div>
                        )}
                      </div>
                      
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSpecialDays(specialDays.filter(d => d.id !== day.id))}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Holidays */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Resmi Tatiller</h3>
              <div className="space-y-2">
                {[
                  { date: '2024-01-01', name: "Yılbaşı" },
                  { date: '2024-04-23', name: "23 Nisan Ulusal Egemenlik ve Çocuk Bayramı" },
                  { date: '2024-05-01', name: "1 Mayıs İşçi Bayramı" },
                  { date: '2024-05-19', name: "19 Mayıs Atatürk'ü Anma, Gençlik ve Spor Bayramı" },
                  { date: '2024-08-30', name: "30 Ağustos Zafer Bayramı" },
                  { date: '2024-10-29', name: "29 Ekim Cumhuriyet Bayramı" }
                ].map(holiday => (
                  <label key={holiday.date} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={holidays.some(h => h.date === holiday.date)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setHolidays([...holidays, holiday]);
                        } else {
                          setHolidays(holidays.filter(h => h.date !== holiday.date));
                        }
                      }}
                    />
                    <span>{holiday.name} - {format(parseISO(holiday.date), 'dd MMMM yyyy', { locale: tr })}</span>
                  </label>
                ))}
              </div>
            </div>
          </Card>
        </Tabs.TabContent>

        {/* Blocked Times Tab */}
        <Tabs.TabContent value="blocked">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Bloklu Zamanlar</h3>
              <Button size="sm" onClick={addBlockedTime}>
                <Plus className="h-4 w-4 mr-2" />
                Bloklu Zaman Ekle
              </Button>
            </div>
            
            <div className="space-y-3">
              {blockedTimes.map(block => (
                <div key={block.id} className="p-4 border rounded-lg">
                  <div className="grid grid-cols-5 gap-3">
                    <Input
                      type="date"
                      value={block.startDate}
                      onChange={(e) => setBlockedTimes(blockedTimes.map(b => 
                        b.id === block.id ? { ...b, startDate: e.target.value } : b
                      ))}
                    />
                    
                    <Input
                      type="date"
                      value={block.endDate}
                      onChange={(e) => setBlockedTimes(blockedTimes.map(b => 
                        b.id === block.id ? { ...b, endDate: e.target.value } : b
                      ))}
                    />
                    
                    <Select
                      value={block.startTime}
                      onValueChange={(value) => setBlockedTimes(blockedTimes.map(b => 
                        b.id === block.id ? { ...b, startTime: value } : b
                      ))}
                    >
                      {generateTimeOptions().map(time => (
                        <Select.Option key={time} value={time}>{time}</Select.Option>
                      ))}
                    </Select>
                    
                    <Select
                      value={block.endTime}
                      onValueChange={(value) => setBlockedTimes(blockedTimes.map(b => 
                        b.id === block.id ? { ...b, endTime: value } : b
                      ))}
                    >
                      {generateTimeOptions().map(time => (
                        <Select.Option key={time} value={time}>{time}</Select.Option>
                      ))}
                    </Select>
                    
                    <Input
                      placeholder="Sebep"
                      value={block.reason}
                      onChange={(e) => setBlockedTimes(blockedTimes.map(b => 
                        b.id === block.id ? { ...b, reason: e.target.value } : b
                      ))}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between mt-3">
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={block.recurring}
                        onChange={(e) => setBlockedTimes(blockedTimes.map(b => 
                          b.id === block.id ? { ...b, recurring: e.target.checked } : b
                        ))}
                      />
                      <Repeat className="h-4 w-4" />
                      <span>Tekrarlayan</span>
                    </label>
                    
                    {block.recurring && (
                      <Select
                        value={block.recurrencePattern}
                        onValueChange={(value) => setBlockedTimes(blockedTimes.map(b => 
                          b.id === block.id ? { ...b, recurrencePattern: value } : b
                        ))}
                      >
                        <Select.Option value="daily">Günlük</Select.Option>
                        <Select.Option value="weekly">Haftalık</Select.Option>
                        <Select.Option value="monthly">Aylık</Select.Option>
                      </Select>
                    )}
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setBlockedTimes(blockedTimes.filter(b => b.id !== block.id))}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </Tabs.TabContent>

        {/* Preview Tab */}
        <Tabs.TabContent value="preview">
          <Card className="p-6">
            <div className="mb-4">
              <Label>Önizleme Tarihi</Label>
              <Input
                type="date"
                value={format(previewDate, 'yyyy-MM-dd')}
                onChange={(e) => setPreviewDate(new Date(e.target.value))}
              />
            </div>
            
            <div className="border rounded-lg p-4">
              <h4 className="font-semibold mb-3">
                {format(previewDate, 'dd MMMM yyyy EEEE', { locale: tr })}
              </h4>
              
              <div className="space-y-2">
                {/* Preview logic would show available slots for the selected date */}
                <div className="p-3 bg-green-50 text-green-800 rounded">
                  Uygun: 09:00 - 10:00
                </div>
                <div className="p-3 bg-green-50 text-green-800 rounded">
                  Uygun: 10:30 - 11:30
                </div>
                <div className="p-3 bg-red-50 text-red-800 rounded">
                  Dolu: 11:30 - 12:30
                </div>
                <div className="p-3 bg-gray-50 text-gray-800 rounded">
                  Öğle Arası: 12:30 - 13:30
                </div>
                <div className="p-3 bg-green-50 text-green-800 rounded">
                  Uygun: 14:00 - 15:00
                </div>
              </div>
            </div>
          </Card>
        </Tabs.TabContent>
      </Tabs>
    </div>
  );
};

export default AvailabilitySettingsPageV2;
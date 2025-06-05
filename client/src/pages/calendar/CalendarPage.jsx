import React, { useState, useEffect, useMemo } from 'react';
import { 
  format, startOfWeek, endOfWeek, startOfMonth, endOfMonth, eachDayOfInterval,
  isSameMonth, isSameDay, addDays, parseISO, isToday, getDay, addMonths, subMonths,
  addWeeks, subWeeks, startOfDay, endOfDay, isWithinInterval, differenceInMinutes,
  addMinutes, setHours, setMinutes
} from 'date-fns';
import { tr, enUS } from 'date-fns/locale';
import { 
  CalendarDays, ChevronLeft, ChevronRight, Plus, Filter, Users, Clock, 
  Calendar, List, LayoutGrid, Search, MapPin, Bell, Video, Settings,
  Palette, Download, Upload, RefreshCw, MoreHorizontal, Tag
} from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from '../../lib/api';
import { toast } from '../../hooks/useToast';
import { Button } from '../../components/ui/button';
import { Card } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Select } from '../../components/ui/select';
import { Badge } from '../../components/ui/badge';
import { Tabs } from '../../components/ui/tabs';
import { Label } from '../../components/ui';
import AppointmentCard from '../../components/appointment/AppointmentCard';
import AppointmentModal from '../../components/appointment/AppointmentModal';
import { useAuth } from '../../hooks/useAuth';
/**
 * Enhanced CalendarPage with advanced features and improved UI/UX
 */
const CalendarPageV2 = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  // State management
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [viewMode, setViewMode] = useState('month'); // 'month', 'week', 'day', 'agenda', 'year'
  const [appointments, setAppointments] = useState([]);
  const [filteredAppointments, setFilteredAppointments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [selectedTimeSlot, setSelectedTimeSlot] = useState(null);
  const [hoveredDate, setHoveredDate] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [draggedAppointment, setDraggedAppointment] = useState(null);
  const [language, setLanguage] = useState('tr');
  const [theme, setTheme] = useState('light');
  const [calendarSettings, setCalendarSettings] = useState({
    weekStartsOn: 1, // Monday
    workingHours: { start: 9, end: 18 },
    timeSlotDuration: 30, // minutes
    defaultAppointmentDuration: 60, // minutes
    showWeekNumbers: true,
    enableDragDrop: true,
    enableDoubleClick: true,
    showWeekends: true
  });
  const [filters, setFilters] = useState({
    searchTerm: '',
    beneficiaryId: '',
    trainerId: '',
    status: 'all',
    type: 'all',
    tags: [],
    dateRange: 'all'
  });
  const [quickFilters, setQuickFilters] = useState({
    myAppointments: false,
    upcomingOnly: false,
    needsConfirmation: false,
    conflicts: false
  });
  // Computed values
  const daysToDisplay = useMemo(() => {
    if (viewMode === 'month') {
      const monthStart = startOfMonth(currentDate);
      const monthEnd = endOfMonth(currentDate);
      const startDate = startOfWeek(monthStart, { weekStartsOn: calendarSettings.weekStartsOn });
      const endDate = endOfWeek(monthEnd, { weekStartsOn: calendarSettings.weekStartsOn });
      return eachDayOfInterval({ start: startDate, end: endDate });
    } else if (viewMode === 'week') {
      const weekStart = startOfWeek(currentDate, { weekStartsOn: calendarSettings.weekStartsOn });
      const weekEnd = endOfWeek(currentDate, { weekStartsOn: calendarSettings.weekStartsOn });
      return eachDayOfInterval({ start: weekStart, end: weekEnd });
    } else if (viewMode === 'day') {
      return [currentDate];
    }
    return [];
  }, [currentDate, viewMode, calendarSettings.weekStartsOn]);
  const timeSlots = useMemo(() => {
    const slots = [];
    const startHour = calendarSettings.workingHours.start;
    const endHour = calendarSettings.workingHours.end;
    const slotDuration = calendarSettings.timeSlotDuration;
    for (let hour = startHour; hour < endHour; hour++) {
      for (let minute = 0; minute < 60; minute += slotDuration) {
        slots.push({ hour, minute });
      }
    }
    return slots;
  }, [calendarSettings]);
  // Data fetching
  useEffect(() => {
    fetchAppointments();
  }, [currentDate, viewMode]);
  useEffect(() => {
    applyFilters();
  }, [appointments, filters, quickFilters]);
  const fetchAppointments = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get('/api/appointments', {
        params: {
          start_date: format(startOfMonth(currentDate), 'yyyy-MM-dd'),
          end_date: format(endOfMonth(currentDate), 'yyyy-MM-dd'),
          view_mode: viewMode
        }
      });
      setAppointments(response.data);
    } catch (error) {
      console.error('Error fetching appointments:', error);
      toast({
        title: 'Hata',
        description: 'Randevular yüklenemedi',
        variant: 'error'
      });
    } finally {
      setIsLoading(false);
    }
  };
  const applyFilters = () => {
    let filtered = [...appointments];
    // Apply search filter
    if (filters.searchTerm) {
      filtered = filtered.filter(apt => 
        apt.title.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
        apt.beneficiary_name?.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
        apt.trainer_name?.toLowerCase().includes(filters.searchTerm.toLowerCase())
      );
    }
    // Apply quick filters
    if (quickFilters.myAppointments) {
      filtered = filtered.filter(apt => 
        apt.trainer_id === user?.id || apt.beneficiary_id === user?.id
      );
    }
    if (quickFilters.upcomingOnly) {
      filtered = filtered.filter(apt => 
        new Date(apt.start_time) > new Date()
      );
    }
    if (quickFilters.needsConfirmation) {
      filtered = filtered.filter(apt => apt.status === 'pending');
    }
    // Apply other filters
    if (filters.status !== 'all') {
      filtered = filtered.filter(apt => apt.status === filters.status);
    }
    if (filters.type !== 'all') {
      filtered = filtered.filter(apt => apt.type === filters.type);
    }
    if (filters.tags.length > 0) {
      filtered = filtered.filter(apt => 
        apt.tags?.some(tag => filters.tags.includes(tag))
      );
    }
    setFilteredAppointments(filtered);
  };
  // Event handlers
  const handleDateNavigation = (direction) => {
    if (viewMode === 'month') {
      setCurrentDate(direction === 'prev' ? 
        subMonths(currentDate, 1) : 
        addMonths(currentDate, 1)
      );
    } else if (viewMode === 'week') {
      setCurrentDate(direction === 'prev' ? 
        subWeeks(currentDate, 1) : 
        addWeeks(currentDate, 1)
      );
    } else if (viewMode === 'day') {
      setCurrentDate(direction === 'prev' ? 
        subDays(currentDate, 1) : 
        addDays(currentDate, 1)
      );
    }
  };
  const handleDateSelect = (date) => {
    setSelectedDate(date);
    if (viewMode === 'month') {
      setViewMode('day');
      setCurrentDate(date);
    }
  };
  const handleTimeSlotClick = (date, timeSlot) => {
    if (calendarSettings.enableDoubleClick) return;
    const slotStart = setMinutes(setHours(date, timeSlot.hour), timeSlot.minute);
    const slotEnd = addMinutes(slotStart, calendarSettings.defaultAppointmentDuration);
    setSelectedTimeSlot({ start: slotStart, end: slotEnd });
    setShowModal(true);
  };
  const handleTimeSlotDoubleClick = (date, timeSlot) => {
    if (!calendarSettings.enableDoubleClick) return;
    const slotStart = setMinutes(setHours(date, timeSlot.hour), timeSlot.minute);
    const slotEnd = addMinutes(slotStart, calendarSettings.defaultAppointmentDuration);
    setSelectedTimeSlot({ start: slotStart, end: slotEnd });
    setShowModal(true);
  };
  const handleAppointmentClick = (appointment) => {
    setSelectedAppointment(appointment);
    setShowModal(true);
  };
  const handleAppointmentDragStart = (appointment) => {
    if (!calendarSettings.enableDragDrop) return;
    setIsDragging(true);
    setDraggedAppointment(appointment);
  };
  const handleAppointmentDrop = async (date, timeSlot) => {
    if (!draggedAppointment || !calendarSettings.enableDragDrop) return;
    try {
      const newStart = setMinutes(setHours(date, timeSlot.hour), timeSlot.minute);
      const duration = differenceInMinutes(
        new Date(draggedAppointment.end_time),
        new Date(draggedAppointment.start_time)
      );
      const newEnd = addMinutes(newStart, duration);
      await axios.put(`/api/appointments/${draggedAppointment.id}`, {
        ...draggedAppointment,
        start_time: newStart.toISOString(),
        end_time: newEnd.toISOString()
      });
      toast({
        title: 'Başarılı',
        description: 'Randevu yeni zamana taşındı',
        variant: 'success'
      });
      fetchAppointments();
    } catch (error) {
      toast({
        title: 'Hata',
        description: 'Randevu taşınamadı',
        variant: 'error'
      });
    } finally {
      setIsDragging(false);
      setDraggedAppointment(null);
    }
  };
  const exportCalendar = async (format = 'ics') => {
    try {
      const response = await axios.get('/api/appointments/export', {
        params: { format },
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `calendar-${format(new Date(), 'yyyy-MM-dd')}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast({
        title: 'Başarılı',
        description: 'Takvim dışa aktarıldı',
        variant: 'success'
      });
    } catch (error) {
      toast({
        title: 'Hata',
        description: 'Takvim dışa aktarılamadı',
        variant: 'error'
      });
    }
  };
  const syncGoogleCalendar = async () => {
    try {
      await axios.post('/api/appointments/sync/google');
      toast({
        title: 'Başarılı',
        description: 'Google Takvim senkronize edildi',
        variant: 'success'
      });
      fetchAppointments();
    } catch (error) {
      toast({
        title: 'Hata',
        description: 'Senkronizasyon başarısız',
        variant: 'error'
      });
    }
  };
  // Helper functions
  const getAppointmentsForDate = (date) => {
    return filteredAppointments.filter(apt => 
      isSameDay(parseISO(apt.start_time), date)
    );
  };
  const getAppointmentsForTimeSlot = (date, timeSlot) => {
    const slotStart = setMinutes(setHours(date, timeSlot.hour), timeSlot.minute);
    const slotEnd = addMinutes(slotStart, calendarSettings.timeSlotDuration);
    return filteredAppointments.filter(apt => {
      const aptStart = parseISO(apt.start_time);
      const aptEnd = parseISO(apt.end_time);
      return isWithinInterval(aptStart, { start: slotStart, end: slotEnd }) ||
             isWithinInterval(slotStart, { start: aptStart, end: aptEnd });
    });
  };
  const getAppointmentPosition = (appointment, timeSlot) => {
    const aptStart = parseISO(appointment.start_time);
    const slotStart = setMinutes(setHours(aptStart, timeSlot.hour), timeSlot.minute);
    const minutesFromSlotStart = differenceInMinutes(aptStart, slotStart);
    const top = (minutesFromSlotStart / calendarSettings.timeSlotDuration) * 100;
    const duration = differenceInMinutes(
      parseISO(appointment.end_time),
      aptStart
    );
    const height = (duration / calendarSettings.timeSlotDuration) * 100;
    return { top: `${top}%`, height: `${height}%` };
  };
  const getDayClass = (date) => {
    const classes = [];
    if (!isSameMonth(date, currentDate)) {
      classes.push('text-gray-400');
    }
    if (isToday(date)) {
      classes.push('bg-blue-50 font-semibold');
    }
    if (isSameDay(date, selectedDate)) {
      classes.push('bg-blue-100 ring-2 ring-blue-600');
    }
    if (getDay(date) === 0 || getDay(date) === 6) {
      classes.push('bg-gray-50');
    }
    if (hoveredDate && isSameDay(date, hoveredDate)) {
      classes.push('bg-gray-100');
    }
    return classes.join(' ');
  };
  const getAppointmentColor = (appointment) => {
    const colors = {
      session: 'bg-blue-500',
      evaluation: 'bg-purple-500',
      meeting: 'bg-green-500',
      other: 'bg-gray-500'
    };
    return colors[appointment.type] || colors.other;
  };
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-30">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold">Takvim</h1>
              <p className="text-sm text-gray-600">Randevularınızı yönetin</p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                onClick={() => navigate('/calendar/availability')}
              >
                <Clock className="h-4 w-4 mr-2" />
                Uygunluk Ayarları
              </Button>
              <Button
                variant="outline"
                onClick={() => navigate('/calendar/google-sync')}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Google Sync
              </Button>
              <Button
                onClick={() => setShowModal(true)}
              >
                <Plus className="h-4 w-4 mr-2" />
                Yeni Randevu
              </Button>
            </div>
          </div>
        </div>
      </div>
      {/* Toolbar */}
      <div className="bg-white border-b px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* Date Navigation */}
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleDateNavigation('prev')}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setCurrentDate(new Date())}
              >
                Bugün
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleDateNavigation('next')}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
            {/* Current Date Display */}
            <h2 className="text-lg font-semibold">
              {format(currentDate, viewMode === 'month' ? 'MMMM yyyy' : 'dd MMMM yyyy', {
                locale: language === 'tr' ? tr : enUS
              })}
            </h2>
          </div>
          <div className="flex items-center gap-2">
            {/* View Mode Selector */}
            <div className="flex items-center border rounded-lg">
              <Button
                variant={viewMode === 'month' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('month')}
              >
                <LayoutGrid className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === 'week' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('week')}
              >
                <CalendarDays className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === 'day' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('day')}
              >
                <Calendar className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === 'agenda' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('agenda')}
              >
                <List className="h-4 w-4" />
              </Button>
            </div>
            {/* More Options */}
            <div className="relative">
              <Button variant="ghost" size="sm">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border p-2 hidden group-hover:block">
                <button
                  onClick={() => exportCalendar('ics')}
                  className="w-full text-left px-3 py-2 rounded hover:bg-gray-100"
                >
                  <Download className="h-4 w-4 mr-2 inline" />
                  Takvimi Dışa Aktar
                </button>
                <button
                  onClick={syncGoogleCalendar}
                  className="w-full text-left px-3 py-2 rounded hover:bg-gray-100"
                >
                  <RefreshCw className="h-4 w-4 mr-2 inline" />
                  Google Takvim Sync
                </button>
                <button
                  onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
                  className="w-full text-left px-3 py-2 rounded hover:bg-gray-100"
                >
                  <Palette className="h-4 w-4 mr-2 inline" />
                  Tema Değiştir
                </button>
                <button
                  onClick={() => navigate('/calendar/settings')}
                  className="w-full text-left px-3 py-2 rounded hover:bg-gray-100"
                >
                  <Settings className="h-4 w-4 mr-2 inline" />
                  Takvim Ayarları
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="flex">
        {/* Sidebar Filters */}
        <div className="w-64 bg-white border-r p-4 space-y-6">
          {/* Search */}
          <div>
            <Label>Ara</Label>
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Randevu ara..."
                value={filters.searchTerm}
                onChange={(e) => setFilters({ ...filters, searchTerm: e.target.value })}
                className="pl-10"
              />
            </div>
          </div>
          {/* Quick Filters */}
          <div>
            <Label>Hızlı Filtreler</Label>
            <div className="space-y-2 mt-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={quickFilters.myAppointments}
                  onChange={(e) => setQuickFilters({ ...quickFilters, myAppointments: e.target.checked })}
                  className="mr-2"
                />
                <span className="text-sm">Sadece Benim Randevularım</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={quickFilters.upcomingOnly}
                  onChange={(e) => setQuickFilters({ ...quickFilters, upcomingOnly: e.target.checked })}
                  className="mr-2"
                />
                <span className="text-sm">Yaklaşan Randevular</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={quickFilters.needsConfirmation}
                  onChange={(e) => setQuickFilters({ ...quickFilters, needsConfirmation: e.target.checked })}
                  className="mr-2"
                />
                <span className="text-sm">Onay Bekleyenler</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={quickFilters.conflicts}
                  onChange={(e) => setQuickFilters({ ...quickFilters, conflicts: e.target.checked })}
                  className="mr-2"
                />
                <span className="text-sm">Çakışan Randevular</span>
              </label>
            </div>
          </div>
          {/* Filters */}
          <div>
            <Label>Filtreler</Label>
            <div className="space-y-3 mt-2">
              <Select
                value={filters.type}
                onValueChange={(value) => setFilters({ ...filters, type: value })}
              >
                <Select.Option value="all">Tüm Türler</Select.Option>
                <Select.Option value="session">Oturum</Select.Option>
                <Select.Option value="evaluation">Değerlendirme</Select.Option>
                <Select.Option value="meeting">Toplantı</Select.Option>
              </Select>
              <Select
                value={filters.status}
                onValueChange={(value) => setFilters({ ...filters, status: value })}
              >
                <Select.Option value="all">Tüm Durumlar</Select.Option>
                <Select.Option value="confirmed">Onaylandı</Select.Option>
                <Select.Option value="pending">Beklemede</Select.Option>
                <Select.Option value="cancelled">İptal</Select.Option>
              </Select>
              <Select
                value={filters.dateRange}
                onValueChange={(value) => setFilters({ ...filters, dateRange: value })}
              >
                <Select.Option value="all">Tüm Tarihler</Select.Option>
                <Select.Option value="today">Bugün</Select.Option>
                <Select.Option value="week">Bu Hafta</Select.Option>
                <Select.Option value="month">Bu Ay</Select.Option>
              </Select>
            </div>
          </div>
          {/* Calendar Settings */}
          <div>
            <Label>Görünüm Ayarları</Label>
            <div className="space-y-2 mt-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={calendarSettings.showWeekNumbers}
                  onChange={(e) => setCalendarSettings({ 
                    ...calendarSettings, 
                    showWeekNumbers: e.target.checked 
                  })}
                  className="mr-2"
                />
                <span className="text-sm">Hafta Numaralarını Göster</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={calendarSettings.showWeekends}
                  onChange={(e) => setCalendarSettings({ 
                    ...calendarSettings, 
                    showWeekends: e.target.checked 
                  })}
                  className="mr-2"
                />
                <span className="text-sm">Hafta Sonlarını Göster</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={calendarSettings.enableDragDrop}
                  onChange={(e) => setCalendarSettings({ 
                    ...calendarSettings, 
                    enableDragDrop: e.target.checked 
                  })}
                  className="mr-2"
                />
                <span className="text-sm">Sürükle-Bırak</span>
              </label>
            </div>
          </div>
          {/* Legend */}
          <div>
            <Label>Renk Açıklamaları</Label>
            <div className="space-y-2 mt-2">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-blue-500 rounded"></div>
                <span className="text-sm">Oturum</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-purple-500 rounded"></div>
                <span className="text-sm">Değerlendirme</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-500 rounded"></div>
                <span className="text-sm">Toplantı</span>
              </div>
            </div>
          </div>
        </div>
        {/* Calendar Content */}
        <div className="flex-1 p-6">
          {isLoading ? (
            <div className="flex items-center justify-center h-96">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <>
              {viewMode === 'month' && (
                <div className="bg-white rounded-lg shadow">
                  {/* Month View Header */}
                  <div className="grid grid-cols-7 gap-0 border-b">
                    {calendarSettings.showWeekNumbers && (
                      <div className="p-3 text-sm font-medium text-gray-500 text-center border-r">
                        Hafta
                      </div>
                    )}
                    {['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'].map((day, index) => (
                      <div
                        key={day}
                        className={`p-3 text-sm font-medium text-gray-700 text-center ${
                          index < 5 ? '' : 'bg-gray-50'
                        }`}
                      >
                        {day}
                      </div>
                    ))}
                  </div>
                  {/* Month View Grid */}
                  <div className="grid grid-cols-7 gap-0">
                    {daysToDisplay.map((date, index) => {
                      const dayAppointments = getAppointmentsForDate(date);
                      const isWeekend = getDay(date) === 0 || getDay(date) === 6;
                      return (
                        <div
                          key={index}
                          className={`min-h-[120px] border-r border-b p-2 cursor-pointer transition-colors ${
                            getDayClass(date)
                          } ${!calendarSettings.showWeekends && isWeekend ? 'hidden' : ''}`}
                          onClick={() => handleDateSelect(date)}
                          onMouseEnter={() => setHoveredDate(date)}
                          onMouseLeave={() => setHoveredDate(null)}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <span className={`text-sm ${
                              !isSameMonth(date, currentDate) ? 'text-gray-400' : ''
                            }`}>
                              {format(date, 'd')}
                            </span>
                            {dayAppointments.length > 0 && (
                              <Badge variant="secondary" size="sm">
                                {dayAppointments.length}
                              </Badge>
                            )}
                          </div>
                          <div className="space-y-1">
                            {dayAppointments.slice(0, 3).map(appointment => (
                              <div
                                key={appointment.id}
                                className={`text-xs p-1 rounded cursor-pointer text-white ${
                                  getAppointmentColor(appointment)
                                }`}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleAppointmentClick(appointment);
                                }}
                                draggable={calendarSettings.enableDragDrop}
                                onDragStart={() => handleAppointmentDragStart(appointment)}
                              >
                                {format(parseISO(appointment.start_time), 'HH:mm')} {appointment.title}
                              </div>
                            ))}
                            {dayAppointments.length > 3 && (
                              <div className="text-xs text-gray-500 text-center">
                                +{dayAppointments.length - 3} daha
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
              {viewMode === 'week' && (
                <div className="bg-white rounded-lg shadow">
                  <div className="grid grid-cols-8 gap-0">
                    {/* Time Column */}
                    <div className="border-r">
                      <div className="h-12 border-b"></div>
                      {timeSlots.map((slot, index) => (
                        <div
                          key={index}
                          className="h-16 border-b px-2 py-1 text-xs text-gray-500"
                        >
                          {format(setMinutes(setHours(new Date(), slot.hour), slot.minute), 'HH:mm')}
                        </div>
                      ))}
                    </div>
                    {/* Days Columns */}
                    {daysToDisplay.map((date, dayIndex) => (
                      <div key={dayIndex} className="border-r relative">
                        <div className="h-12 border-b p-2 text-center">
                          <div className="font-medium">{format(date, 'EEE', { locale: tr })}</div>
                          <div className={`text-sm ${isToday(date) ? 'text-blue-600 font-bold' : ''}`}>
                            {format(date, 'd')}
                          </div>
                        </div>
                        {timeSlots.map((slot, slotIndex) => {
                          const slotAppointments = getAppointmentsForTimeSlot(date, slot);
                          return (
                            <div
                              key={slotIndex}
                              className="h-16 border-b relative hover:bg-gray-50 cursor-pointer"
                              onClick={() => handleTimeSlotClick(date, slot)}
                              onDoubleClick={() => handleTimeSlotDoubleClick(date, slot)}
                              onDrop={() => handleAppointmentDrop(date, slot)}
                              onDragOver={(e) => e.preventDefault()}
                            >
                              {slotAppointments.map(appointment => {
                                const position = getAppointmentPosition(appointment, slot);
                                return (
                                  <div
                                    key={appointment.id}
                                    className={`absolute left-0 right-0 mx-1 p-1 rounded text-xs text-white cursor-move ${
                                      getAppointmentColor(appointment)
                                    }`}
                                    style={{
                                      top: position.top,
                                      height: position.height,
                                      minHeight: '20px'
                                    }}
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleAppointmentClick(appointment);
                                    }}
                                    draggable={calendarSettings.enableDragDrop}
                                    onDragStart={() => handleAppointmentDragStart(appointment)}
                                  >
                                    <div className="font-medium">{appointment.title}</div>
                                    <div>{format(parseISO(appointment.start_time), 'HH:mm')}</div>
                                  </div>
                                );
                              })}
                            </div>
                          );
                        })}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {viewMode === 'day' && (
                <div className="bg-white rounded-lg shadow">
                  <div className="grid grid-cols-2 gap-0">
                    {/* Time Column */}
                    <div className="border-r">
                      <div className="h-12 border-b p-3 font-medium">
                        {format(currentDate, 'EEEE, dd MMMM yyyy', { locale: tr })}
                      </div>
                      {timeSlots.map((slot, index) => (
                        <div
                          key={index}
                          className="h-20 border-b px-3 py-2 text-sm text-gray-500"
                        >
                          {format(setMinutes(setHours(new Date(), slot.hour), slot.minute), 'HH:mm')}
                        </div>
                      ))}
                    </div>
                    {/* Appointments Column */}
                    <div className="relative">
                      <div className="h-12 border-b p-3">
                        <Badge variant="secondary">
                          {getAppointmentsForDate(currentDate).length} randevu
                        </Badge>
                      </div>
                      {timeSlots.map((slot, index) => {
                        const slotAppointments = getAppointmentsForTimeSlot(currentDate, slot);
                        return (
                          <div
                            key={index}
                            className="h-20 border-b relative hover:bg-gray-50 cursor-pointer"
                            onClick={() => handleTimeSlotClick(currentDate, slot)}
                            onDoubleClick={() => handleTimeSlotDoubleClick(currentDate, slot)}
                            onDrop={() => handleAppointmentDrop(currentDate, slot)}
                            onDragOver={(e) => e.preventDefault()}
                          >
                            {slotAppointments.map(appointment => (
                              <div
                                key={appointment.id}
                                className={`absolute left-2 right-2 p-2 rounded text-white cursor-move ${
                                  getAppointmentColor(appointment)
                                }`}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleAppointmentClick(appointment);
                                }}
                                draggable={calendarSettings.enableDragDrop}
                                onDragStart={() => handleAppointmentDragStart(appointment)}
                              >
                                <div className="font-medium">{appointment.title}</div>
                                <div className="text-sm">
                                  {format(parseISO(appointment.start_time), 'HH:mm')} - 
                                  {format(parseISO(appointment.end_time), 'HH:mm')}
                                </div>
                                {appointment.location && (
                                  <div className="text-sm flex items-center mt-1">
                                    <MapPin className="h-3 w-3 mr-1" />
                                    {appointment.location}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}
              {viewMode === 'agenda' && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold mb-4">Randevu Listesi</h3>
                  <div className="space-y-4">
                    {filteredAppointments.map(appointment => (
                      <Card
                        key={appointment.id}
                        className="p-4 cursor-pointer hover:shadow-md transition-shadow"
                        onClick={() => handleAppointmentClick(appointment)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <div className={`w-3 h-3 rounded-full ${getAppointmentColor(appointment)}`}></div>
                              <h4 className="font-medium">{appointment.title}</h4>
                              <Badge variant={appointment.status === 'confirmed' ? 'success' : 'warning'}>
                                {appointment.status}
                              </Badge>
                            </div>
                            <div className="flex items-center gap-4 text-sm text-gray-600">
                              <div className="flex items-center gap-1">
                                <Clock className="h-4 w-4" />
                                {format(parseISO(appointment.start_time), 'dd MMM HH:mm', { locale: tr })}
                              </div>
                              {appointment.location && (
                                <div className="flex items-center gap-1">
                                  <MapPin className="h-4 w-4" />
                                  {appointment.location}
                                </div>
                              )}
                              {appointment.beneficiary_name && (
                                <div className="flex items-center gap-1">
                                  <Users className="h-4 w-4" />
                                  {appointment.beneficiary_name}
                                </div>
                              )}
                            </div>
                            {appointment.description && (
                              <p className="text-sm text-gray-700 mt-2">{appointment.description}</p>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            {appointment.is_online && (
                              <Badge variant="secondary">
                                <Video className="h-3 w-3 mr-1" />
                                Online
                              </Badge>
                            )}
                            {appointment.has_reminder && (
                              <Badge variant="secondary">
                                <Bell className="h-3 w-3" />
                              </Badge>
                            )}
                          </div>
                        </div>
                      </Card>
                    ))}
                    {filteredAppointments.length === 0 && (
                      <div className="text-center py-8 text-gray-500">
                        Randevu bulunamadı
                      </div>
                    )}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
      {/* Appointment Modal */}
      {showModal && (
        <AppointmentModal
          appointment={selectedAppointment}
          timeSlot={selectedTimeSlot}
          onClose={() => {
            setShowModal(false);
            setSelectedAppointment(null);
            setSelectedTimeSlot(null);
          }}
          onSave={() => {
            fetchAppointments();
            setShowModal(false);
            setSelectedAppointment(null);
            setSelectedTimeSlot(null);
          }}
        />
      )}
    </div>
  );
};
export default CalendarPageV2;
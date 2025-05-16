import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Save, Clock, Plus, Minus, Calendar, AlertTriangle, CheckCircle, Loader, Info } from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/toast';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/hooks/useAuth';

/**
 * AvailabilitySettingsPage allows users to set their availability for appointments
 */
const AvailabilitySettingsPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [availabilitySettings, setAvailabilitySettings] = useState({
    regular_schedule: [
      { day: 0, is_available: false, time_slots: [] }, // Sunday
      { day: 1, is_available: true, time_slots: [{ start: '09:00', end: '17:00' }] }, // Monday
      { day: 2, is_available: true, time_slots: [{ start: '09:00', end: '17:00' }] }, // Tuesday
      { day: 3, is_available: true, time_slots: [{ start: '09:00', end: '17:00' }] }, // Wednesday
      { day: 4, is_available: true, time_slots: [{ start: '09:00', end: '17:00' }] }, // Thursday
      { day: 5, is_available: true, time_slots: [{ start: '09:00', end: '17:00' }] }, // Friday
      { day: 6, is_available: false, time_slots: [] }, // Saturday
    ],
    exceptions: [], // Date-specific exceptions
    buffer_time: 15, // Minutes between appointments
    appointment_duration: 60, // Default appointment duration in minutes
    advance_notice: 24, // Hours in advance for appointment booking
    max_appointments_per_day: 8,
    auto_confirm: true,
    working_hours: {
      start: '09:00',
      end: '17:00',
    },
    break_time: {
      enabled: true,
      start: '12:00',
      end: '13:00',
    },
    sync_with_google: false,
  });
  const [activeTab, setActiveTab] = useState('weekly');
  const [availableTimeRange, setAvailableTimeRange] = useState({
    start: '08:00',
    end: '20:00',
  });
  const [dateExceptions, setDateExceptions] = useState([]);
  const [newException, setNewException] = useState({
    date: '',
    is_available: false,
    time_slots: [],
  });

  const daysOfWeek = [
    'Sunday',
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
  ];

  // Fetch availability settings
  useEffect(() => {
    const fetchAvailabilitySettings = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/api/availability');
        
        if (response.data) {
          setAvailabilitySettings(response.data);
          
          // Process exceptions to format dates correctly
          const formattedExceptions = response.data.exceptions.map(exception => ({
            ...exception,
            date: new Date(exception.date).toISOString().split('T')[0],
          }));
          
          setDateExceptions(formattedExceptions);
        }
      } catch (error) {
        console.error('Error fetching availability settings:', error);
        toast({
          title: 'Error',
          description: 'Failed to load availability settings',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchAvailabilitySettings();
  }, [toast]);

  // Handle day availability toggle
  const handleDayAvailabilityToggle = (dayIndex) => {
    setAvailabilitySettings(prev => {
      const updatedSchedule = [...prev.regular_schedule];
      updatedSchedule[dayIndex] = {
        ...updatedSchedule[dayIndex],
        is_available: !updatedSchedule[dayIndex].is_available,
        time_slots: !updatedSchedule[dayIndex].is_available 
          ? [{ start: prev.working_hours.start, end: prev.working_hours.end }] 
          : [],
      };
      
      return {
        ...prev,
        regular_schedule: updatedSchedule,
      };
    });
  };

  // Handle time slot changes
  const handleTimeSlotChange = (dayIndex, slotIndex, field, value) => {
    setAvailabilitySettings(prev => {
      const updatedSchedule = [...prev.regular_schedule];
      const updatedTimeSlots = [...updatedSchedule[dayIndex].time_slots];
      
      updatedTimeSlots[slotIndex] = {
        ...updatedTimeSlots[slotIndex],
        [field]: value,
      };
      
      updatedSchedule[dayIndex] = {
        ...updatedSchedule[dayIndex],
        time_slots: updatedTimeSlots,
      };
      
      return {
        ...prev,
        regular_schedule: updatedSchedule,
      };
    });
  };

  // Add a new time slot to a day
  const handleAddTimeSlot = (dayIndex) => {
    setAvailabilitySettings(prev => {
      const updatedSchedule = [...prev.regular_schedule];
      const updatedTimeSlots = [...updatedSchedule[dayIndex].time_slots];
      
      // Calculate a reasonable default for the new time slot
      let newStart = '09:00';
      let newEnd = '17:00';
      
      if (updatedTimeSlots.length > 0) {
        const lastSlot = updatedTimeSlots[updatedTimeSlots.length - 1];
        const [lastEndHours, lastEndMinutes] = lastSlot.end.split(':').map(Number);
        
        // Add 1 hour to the end time of the last slot for the new start time
        let newStartHours = lastEndHours + 1;
        let newStartMinutes = lastEndMinutes;
        
        // If hours go beyond 23, cap at 23
        if (newStartHours > 23) {
          newStartHours = 23;
          newStartMinutes = 0;
        }
        
        // Calculate end time (start time + 1 hour)
        let newEndHours = newStartHours + 1;
        let newEndMinutes = newStartMinutes;
        
        // If end hours go beyond 23, cap at 23:59
        if (newEndHours > 23) {
          newEndHours = 23;
          newEndMinutes = 59;
        }
        
        newStart = `${newStartHours.toString().padStart(2, '0')}:${newStartMinutes.toString().padStart(2, '0')}`;
        newEnd = `${newEndHours.toString().padStart(2, '0')}:${newEndMinutes.toString().padStart(2, '0')}`;
      }
      
      updatedTimeSlots.push({ start: newStart, end: newEnd });
      
      updatedSchedule[dayIndex] = {
        ...updatedSchedule[dayIndex],
        time_slots: updatedTimeSlots,
      };
      
      return {
        ...prev,
        regular_schedule: updatedSchedule,
      };
    });
  };

  // Remove a time slot
  const handleRemoveTimeSlot = (dayIndex, slotIndex) => {
    setAvailabilitySettings(prev => {
      const updatedSchedule = [...prev.regular_schedule];
      const updatedTimeSlots = updatedSchedule[dayIndex].time_slots.filter((_, i) => i !== slotIndex);
      
      updatedSchedule[dayIndex] = {
        ...updatedSchedule[dayIndex],
        time_slots: updatedTimeSlots,
      };
      
      return {
        ...prev,
        regular_schedule: updatedSchedule,
      };
    });
  };

  // Handle general settings changes
  const handleSettingChange = (field, value) => {
    setAvailabilitySettings(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  // Handle working hours changes
  const handleWorkingHoursChange = (field, value) => {
    setAvailabilitySettings(prev => ({
      ...prev,
      working_hours: {
        ...prev.working_hours,
        [field]: value,
      },
    }));
  };

  // Handle break time changes
  const handleBreakTimeChange = (field, value) => {
    if (field === 'enabled') {
      setAvailabilitySettings(prev => ({
        ...prev,
        break_time: {
          ...prev.break_time,
          enabled: value,
        },
      }));
    } else {
      setAvailabilitySettings(prev => ({
        ...prev,
        break_time: {
          ...prev.break_time,
          [field]: value,
        },
      }));
    }
  };

  // Handle new exception changes
  const handleNewExceptionChange = (field, value) => {
    setNewException(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  // Handle adding a new exception
  const handleAddException = () => {
    // Validate the exception date
    if (!newException.date) {
      toast({
        title: 'Error',
        description: 'Please select a date for the exception',
        type: 'error',
      });
      return;
    }
    
    // Check if an exception already exists for this date
    const existingExceptionIndex = dateExceptions.findIndex(
      exception => exception.date === newException.date
    );
    
    if (existingExceptionIndex !== -1) {
      // Update existing exception
      const updatedExceptions = [...dateExceptions];
      updatedExceptions[existingExceptionIndex] = {
        ...newException,
        time_slots: newException.is_available 
          ? newException.time_slots.length > 0
            ? newException.time_slots
            : [{ start: availabilitySettings.working_hours.start, end: availabilitySettings.working_hours.end }]
          : [],
      };
      
      setDateExceptions(updatedExceptions);
    } else {
      // Add new exception
      setDateExceptions(prev => [
        ...prev,
        {
          ...newException,
          time_slots: newException.is_available 
            ? [{ start: availabilitySettings.working_hours.start, end: availabilitySettings.working_hours.end }]
            : [],
        },
      ]);
    }
    
    // Reset the new exception form
    setNewException({
      date: '',
      is_available: false,
      time_slots: [],
    });
  };

  // Handle removing an exception
  const handleRemoveException = (index) => {
    setDateExceptions(prev => prev.filter((_, i) => i !== index));
  };

  // Handle exception time slot changes
  const handleExceptionTimeSlotChange = (exceptionIndex, slotIndex, field, value) => {
    setDateExceptions(prev => {
      const updatedExceptions = [...prev];
      const updatedTimeSlots = [...updatedExceptions[exceptionIndex].time_slots];
      
      updatedTimeSlots[slotIndex] = {
        ...updatedTimeSlots[slotIndex],
        [field]: value,
      };
      
      updatedExceptions[exceptionIndex] = {
        ...updatedExceptions[exceptionIndex],
        time_slots: updatedTimeSlots,
      };
      
      return updatedExceptions;
    });
  };

  // Add a new time slot to an exception
  const handleAddExceptionTimeSlot = (exceptionIndex) => {
    setDateExceptions(prev => {
      const updatedExceptions = [...prev];
      const updatedTimeSlots = [...updatedExceptions[exceptionIndex].time_slots];
      
      // Calculate a reasonable default for the new time slot
      let newStart = '09:00';
      let newEnd = '17:00';
      
      if (updatedTimeSlots.length > 0) {
        const lastSlot = updatedTimeSlots[updatedTimeSlots.length - 1];
        const [lastEndHours, lastEndMinutes] = lastSlot.end.split(':').map(Number);
        
        // Add 1 hour to the end time of the last slot for the new start time
        let newStartHours = lastEndHours + 1;
        let newStartMinutes = lastEndMinutes;
        
        // If hours go beyond 23, cap at 23
        if (newStartHours > 23) {
          newStartHours = 23;
          newStartMinutes = 0;
        }
        
        // Calculate end time (start time + 1 hour)
        let newEndHours = newStartHours + 1;
        let newEndMinutes = newStartMinutes;
        
        // If end hours go beyond 23, cap at 23:59
        if (newEndHours > 23) {
          newEndHours = 23;
          newEndMinutes = 59;
        }
        
        newStart = `${newStartHours.toString().padStart(2, '0')}:${newStartMinutes.toString().padStart(2, '0')}`;
        newEnd = `${newEndHours.toString().padStart(2, '0')}:${newEndMinutes.toString().padStart(2, '0')}`;
      }
      
      updatedTimeSlots.push({ start: newStart, end: newEnd });
      
      updatedExceptions[exceptionIndex] = {
        ...updatedExceptions[exceptionIndex],
        time_slots: updatedTimeSlots,
      };
      
      return updatedExceptions;
    });
  };

  // Remove a time slot from an exception
  const handleRemoveExceptionTimeSlot = (exceptionIndex, slotIndex) => {
    setDateExceptions(prev => {
      const updatedExceptions = [...prev];
      const updatedTimeSlots = updatedExceptions[exceptionIndex].time_slots.filter((_, i) => i !== slotIndex);
      
      updatedExceptions[exceptionIndex] = {
        ...updatedExceptions[exceptionIndex],
        time_slots: updatedTimeSlots,
      };
      
      return updatedExceptions;
    });
  };

  // Handle saving the settings
  const handleSaveSettings = async () => {
    try {
      setIsSaving(true);
      
      // Prepare data for saving
      const dataToSave = {
        ...availabilitySettings,
        exceptions: dateExceptions,
      };
      
      await api.put('/api/availability', dataToSave);
      
      toast({
        title: 'Success',
        description: 'Availability settings saved successfully',
        type: 'success',
      });
    } catch (error) {
      console.error('Error saving availability settings:', error);
      toast({
        title: 'Error',
        description: 'Failed to save availability settings',
        type: 'error',
      });
    } finally {
      setIsSaving(false);
    }
  };

  // Generate time options (30 min intervals) for select dropdowns
  const generateTimeOptions = () => {
    const options = [];
    const [startHour, startMinute] = availableTimeRange.start.split(':').map(Number);
    const [endHour, endMinute] = availableTimeRange.end.split(':').map(Number);
    
    const startTime = new Date();
    startTime.setHours(startHour, startMinute, 0, 0);
    
    const endTime = new Date();
    endTime.setHours(endHour, endMinute, 0, 0);
    
    // Loop in 30 minute increments
    for (let time = startTime; time <= endTime; time.setMinutes(time.getMinutes() + 30)) {
      const hours = time.getHours().toString().padStart(2, '0');
      const minutes = time.getMinutes().toString().padStart(2, '0');
      const timeString = `${hours}:${minutes}`;
      
      options.push(
        <option key={timeString} value={timeString}>
          {timeString}
        </option>
      );
    }
    
    return options;
  };

  // Time options for dropdowns
  const timeOptions = generateTimeOptions();

  // Apply working hours to all available days
  const applyWorkingHoursToAll = () => {
    setAvailabilitySettings(prev => {
      const updatedSchedule = prev.regular_schedule.map(day => {
        if (day.is_available) {
          return {
            ...day,
            time_slots: [{ start: prev.working_hours.start, end: prev.working_hours.end }],
          };
        }
        return day;
      });
      
      return {
        ...prev,
        regular_schedule: updatedSchedule,
      };
    });
  };

  // Render loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader className="w-10 h-10 text-primary animate-spin" />
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Availability Settings</h1>
        <Button
          onClick={handleSaveSettings}
          disabled={isSaving}
          className="flex items-center"
        >
          {isSaving ? (
            <>
              <Loader className="w-4 h-4 mr-2 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="w-4 h-4 mr-2" />
              Save Settings
            </>
          )}
        </Button>
      </div>
      
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="mb-6"
      >
        <Tabs.TabsList>
          <Tabs.TabTrigger value="weekly">
            <Calendar className="w-4 h-4 mr-2" />
            Weekly Schedule
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="exceptions">
            <AlertTriangle className="w-4 h-4 mr-2" />
            Date Exceptions
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="settings">
            <Clock className="w-4 h-4 mr-2" />
            General Settings
          </Tabs.TabTrigger>
        </Tabs.TabsList>
        
        {/* Weekly Schedule Tab */}
        <Tabs.TabContent value="weekly">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Working Hours Card */}
            <Card className="p-6">
              <h2 className="text-lg font-medium mb-4">Default Working Hours</h2>
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Start Time
                  </label>
                  <select
                    value={availabilitySettings.working_hours.start}
                    onChange={(e) => handleWorkingHoursChange('start', e.target.value)}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                  >
                    {timeOptions}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    End Time
                  </label>
                  <select
                    value={availabilitySettings.working_hours.end}
                    onChange={(e) => handleWorkingHoursChange('end', e.target.value)}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                  >
                    {timeOptions}
                  </select>
                </div>
              </div>
              
              <div className="flex items-center mb-4">
                <input
                  id="break_time_enabled"
                  name="break_time_enabled"
                  type="checkbox"
                  checked={availabilitySettings.break_time.enabled}
                  onChange={(e) => handleBreakTimeChange('enabled', e.target.checked)}
                  className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                />
                <label htmlFor="break_time_enabled" className="ml-2 block text-sm text-gray-700">
                  Include Daily Break Time
                </label>
              </div>
              
              {availabilitySettings.break_time.enabled && (
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Break Start
                    </label>
                    <select
                      value={availabilitySettings.break_time.start}
                      onChange={(e) => handleBreakTimeChange('start', e.target.value)}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                    >
                      {timeOptions}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Break End
                    </label>
                    <select
                      value={availabilitySettings.break_time.end}
                      onChange={(e) => handleBreakTimeChange('end', e.target.value)}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                    >
                      {timeOptions}
                    </select>
                  </div>
                </div>
              )}
              
              <Button
                variant="outline"
                size="sm"
                onClick={applyWorkingHoursToAll}
                className="mt-2"
              >
                Apply To All Available Days
              </Button>
            </Card>
            
            {/* Schedule Overview Card */}
            <Card className="p-6">
              <h2 className="text-lg font-medium mb-4">Schedule Overview</h2>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="space-y-1">
                  <div className="font-medium">Available Days:</div>
                  <div>
                    {availabilitySettings.regular_schedule
                      .filter(day => day.is_available)
                      .map(day => daysOfWeek[day.day])
                      .join(', ') || 'None'}
                  </div>
                </div>
                
                <div className="space-y-1">
                  <div className="font-medium">Working Hours:</div>
                  <div>
                    {availabilitySettings.working_hours.start} - {availabilitySettings.working_hours.end}
                  </div>
                </div>
                
                <div className="space-y-1">
                  <div className="font-medium">Break Time:</div>
                  <div>
                    {availabilitySettings.break_time.enabled 
                      ? `${availabilitySettings.break_time.start} - ${availabilitySettings.break_time.end}` 
                      : 'No break time'}
                  </div>
                </div>
                
                <div className="space-y-1">
                  <div className="font-medium">Buffer Time:</div>
                  <div>{availabilitySettings.buffer_time} minutes</div>
                </div>
                
                <div className="space-y-1">
                  <div className="font-medium">Date Exceptions:</div>
                  <div>{dateExceptions.length} exceptions set</div>
                </div>
                
                <div className="space-y-1">
                  <div className="font-medium">Google Calendar:</div>
                  <div>
                    {availabilitySettings.sync_with_google 
                      ? 'Synced' 
                      : 'Not synced'}
                  </div>
                </div>
              </div>
            </Card>
          </div>
          
          {/* Daily Schedule Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            {availabilitySettings.regular_schedule.map((day, index) => (
              <Card key={index} className={`p-6 ${day.is_available ? 'border-primary' : 'border-gray-200'}`}>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium">{daysOfWeek[day.day]}</h3>
                  <div className="flex items-center">
                    <input
                      id={`day_${day.day}_available`}
                      name={`day_${day.day}_available`}
                      type="checkbox"
                      checked={day.is_available}
                      onChange={() => handleDayAvailabilityToggle(index)}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <label htmlFor={`day_${day.day}_available`} className="ml-2 block text-sm text-gray-700">
                      Available
                    </label>
                  </div>
                </div>
                
                {day.is_available && (
                  <div className="space-y-4">
                    {day.time_slots.map((slot, slotIndex) => (
                      <div key={slotIndex} className="flex items-center space-x-2">
                        <div className="grid grid-cols-2 gap-2 flex-1">
                          <select
                            value={slot.start}
                            onChange={(e) => handleTimeSlotChange(index, slotIndex, 'start', e.target.value)}
                            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                          >
                            {timeOptions}
                          </select>
                          <select
                            value={slot.end}
                            onChange={(e) => handleTimeSlotChange(index, slotIndex, 'end', e.target.value)}
                            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                          >
                            {timeOptions}
                          </select>
                        </div>
                        
                        {day.time_slots.length > 1 && (
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemoveTimeSlot(index, slotIndex)}
                            className="text-gray-500 hover:text-red-500"
                          >
                            <Minus className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    ))}
                    
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => handleAddTimeSlot(index)}
                      className="flex items-center w-full justify-center"
                    >
                      <Plus className="w-4 h-4 mr-1" />
                      Add Time Slot
                    </Button>
                  </div>
                )}
                
                {!day.is_available && (
                  <div className="text-gray-500 italic text-sm">
                    Not available on this day
                  </div>
                )}
              </Card>
            ))}
          </div>
        </Tabs.TabContent>
        
        {/* Date Exceptions Tab */}
        <Tabs.TabContent value="exceptions">
          <Card className="p-6 mb-6">
            <h2 className="text-lg font-medium mb-4">Add Date Exception</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date
                </label>
                <Input
                  type="date"
                  value={newException.date}
                  onChange={(e) => handleNewExceptionChange('date', e.target.value)}
                  min={new Date().toISOString().split('T')[0]} // Prevent past dates
                />
              </div>
              
              <div className="flex items-center space-x-2 h-[38px]">
                <input
                  id="exception_available"
                  name="exception_available"
                  type="checkbox"
                  checked={newException.is_available}
                  onChange={(e) => handleNewExceptionChange('is_available', e.target.checked)}
                  className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                />
                <label htmlFor="exception_available" className="block text-sm text-gray-700">
                  Available on this date
                </label>
              </div>
              
              <Button
                onClick={handleAddException}
                className="flex items-center"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Exception
              </Button>
            </div>
            
            <div className="flex items-center mt-4 bg-amber-50 p-4 rounded-lg">
              <Info className="w-5 h-5 text-amber-500 mr-2 flex-shrink-0" />
              <p className="text-sm text-amber-800">
                Date exceptions let you mark specific dates as unavailable (like holidays) or set special hours that differ from your regular weekly schedule.
              </p>
            </div>
          </Card>
          
          {/* Exception List */}
          {dateExceptions.length > 0 ? (
            <div className="space-y-4">
              {dateExceptions.map((exception, exIndex) => (
                <Card 
                  key={exIndex} 
                  className={`p-6 ${exception.is_available ? 'border-green-300' : 'border-red-300'}`}
                >
                  <div className="flex justify-between items-center mb-4">
                    <div className="flex items-center">
                      <h3 className="text-lg font-medium">
                        {new Date(exception.date).toLocaleDateString(undefined, { 
                          weekday: 'long', 
                          year: 'numeric', 
                          month: 'long', 
                          day: 'numeric' 
                        })}
                      </h3>
                      {exception.is_available ? (
                        <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Available
                        </span>
                      ) : (
                        <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          <AlertTriangle className="w-3 h-3 mr-1" />
                          Unavailable
                        </span>
                      )}
                    </div>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveException(exIndex)}
                      className="text-gray-500 hover:text-red-500"
                    >
                      <Minus className="w-4 h-4" />
                    </Button>
                  </div>
                  
                  {exception.is_available && (
                    <div className="space-y-4">
                      {exception.time_slots.map((slot, slotIndex) => (
                        <div key={slotIndex} className="flex items-center space-x-2">
                          <div className="grid grid-cols-2 gap-2 flex-1">
                            <select
                              value={slot.start}
                              onChange={(e) => handleExceptionTimeSlotChange(exIndex, slotIndex, 'start', e.target.value)}
                              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                            >
                              {timeOptions}
                            </select>
                            <select
                              value={slot.end}
                              onChange={(e) => handleExceptionTimeSlotChange(exIndex, slotIndex, 'end', e.target.value)}
                              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                            >
                              {timeOptions}
                            </select>
                          </div>
                          
                          {exception.time_slots.length > 1 && (
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => handleRemoveExceptionTimeSlot(exIndex, slotIndex)}
                              className="text-gray-500 hover:text-red-500"
                            >
                              <Minus className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      ))}
                      
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => handleAddExceptionTimeSlot(exIndex)}
                        className="flex items-center w-full justify-center"
                      >
                        <Plus className="w-4 h-4 mr-1" />
                        Add Time Slot
                      </Button>
                    </div>
                  )}
                  
                  {!exception.is_available && (
                    <div className="text-gray-500 italic text-sm">
                      You will not be available for appointments on this day
                    </div>
                  )}
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-6 text-center">
              <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <h3 className="text-lg font-medium text-gray-900 mb-1">No Exceptions Set</h3>
              <p className="text-gray-500 mb-4">
                You haven't added any date exceptions yet. Add exceptions for holidays, vacations, or special schedules.
              </p>
            </Card>
          )}
        </Tabs.TabContent>
        
        {/* General Settings Tab */}
        <Tabs.TabContent value="settings">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Appointment Settings */}
            <Card className="p-6">
              <h2 className="text-lg font-medium mb-4">Appointment Settings</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Default Appointment Duration (minutes)
                  </label>
                  <select
                    value={availabilitySettings.appointment_duration}
                    onChange={(e) => handleSettingChange('appointment_duration', parseInt(e.target.value))}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                  >
                    <option value={15}>15 minutes</option>
                    <option value={30}>30 minutes</option>
                    <option value={45}>45 minutes</option>
                    <option value={60}>60 minutes</option>
                    <option value={90}>90 minutes</option>
                    <option value={120}>2 hours</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Buffer Time Between Appointments (minutes)
                  </label>
                  <select
                    value={availabilitySettings.buffer_time}
                    onChange={(e) => handleSettingChange('buffer_time', parseInt(e.target.value))}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                  >
                    <option value={0}>No buffer</option>
                    <option value={5}>5 minutes</option>
                    <option value={10}>10 minutes</option>
                    <option value={15}>15 minutes</option>
                    <option value={30}>30 minutes</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Maximum Appointments Per Day
                  </label>
                  <Input
                    type="number"
                    min="1"
                    max="20"
                    value={availabilitySettings.max_appointments_per_day}
                    onChange={(e) => handleSettingChange('max_appointments_per_day', parseInt(e.target.value))}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Advance Notice Required (hours)
                  </label>
                  <select
                    value={availabilitySettings.advance_notice}
                    onChange={(e) => handleSettingChange('advance_notice', parseInt(e.target.value))}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                  >
                    <option value={0}>No advance notice</option>
                    <option value={1}>1 hour</option>
                    <option value={2}>2 hours</option>
                    <option value={6}>6 hours</option>
                    <option value={12}>12 hours</option>
                    <option value={24}>24 hours</option>
                    <option value={48}>2 days</option>
                    <option value={72}>3 days</option>
                  </select>
                </div>
                
                <div className="flex items-center">
                  <input
                    id="auto_confirm"
                    name="auto_confirm"
                    type="checkbox"
                    checked={availabilitySettings.auto_confirm}
                    onChange={(e) => handleSettingChange('auto_confirm', e.target.checked)}
                    className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                  />
                  <label htmlFor="auto_confirm" className="ml-2 block text-sm text-gray-700">
                    Automatically confirm appointments
                  </label>
                </div>
              </div>
            </Card>
            
            {/* Google Calendar Integration */}
            <Card className="p-6">
              <h2 className="text-lg font-medium mb-4">Google Calendar Integration</h2>
              
              <div className="flex items-center mb-4">
                <input
                  id="sync_with_google"
                  name="sync_with_google"
                  type="checkbox"
                  checked={availabilitySettings.sync_with_google}
                  onChange={(e) => handleSettingChange('sync_with_google', e.target.checked)}
                  className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                />
                <label htmlFor="sync_with_google" className="ml-2 block text-sm text-gray-700">
                  Sync availability with Google Calendar
                </label>
              </div>
              
              {availabilitySettings.sync_with_google ? (
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="flex">
                    <CheckCircle className="h-5 w-5 text-blue-400 mr-2" />
                    <h3 className="text-sm font-medium text-blue-800">Connected to Google Calendar</h3>
                  </div>
                  <p className="mt-2 text-sm text-blue-700">
                    Your availability is being synced with your Google Calendar. When you create appointments in either system, they will be reflected in both.
                  </p>
                  <div className="mt-3 flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        // Navigate to Google Calendar Sync page
                        navigate('/calendar/google-sync');
                      }}
                    >
                      Advanced Sync Settings
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        // In a real app, this would open Google Calendar
                        window.open('https://calendar.google.com/', '_blank');
                      }}
                    >
                      Open Google Calendar
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-700">
                    Connect your Google Calendar to automatically sync your availability and block times when you have other appointments.
                  </p>
                  <div className="mt-3 flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        // In a real app, this would initiate Google OAuth
                        handleSettingChange('sync_with_google', true);
                        toast({
                          title: 'Success',
                          description: 'Connected to Google Calendar (simulated)',
                          type: 'success',
                        });
                      }}
                    >
                      Connect to Google Calendar
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        // Navigate to Google Calendar Sync page
                        navigate('/calendar/google-sync');
                      }}
                    >
                      Sync Settings
                    </Button>
                  </div>
                </div>
              )}
              
              <div className="mt-6">
                <h3 className="text-md font-medium mb-2">Available time range</h3>
                <p className="text-sm text-gray-600 mb-3">
                  This setting controls the time options available in dropdowns throughout the application.
                </p>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Earliest Time
                    </label>
                    <select
                      value={availableTimeRange.start}
                      onChange={(e) => setAvailableTimeRange(prev => ({ ...prev, start: e.target.value }))}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                    >
                      {Array.from({ length: 13 }).map((_, i) => {
                        const hour = (i + 6).toString().padStart(2, '0'); // Start from 6 AM
                        return (
                          <option key={hour} value={`${hour}:00`}>
                            {`${hour}:00`}
                          </option>
                        );
                      })}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Latest Time
                    </label>
                    <select
                      value={availableTimeRange.end}
                      onChange={(e) => setAvailableTimeRange(prev => ({ ...prev, end: e.target.value }))}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                    >
                      {Array.from({ length: 13 }).map((_, i) => {
                        const hour = (i + 12).toString().padStart(2, '0'); // Start from 12 PM
                        return (
                          <option key={hour} value={`${hour}:00`}>
                            {`${hour}:00`}
                          </option>
                        );
                      })}
                    </select>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </Tabs.TabContent>
      </Tabs>
    </div>
  );
};

export default AvailabilitySettingsPage;
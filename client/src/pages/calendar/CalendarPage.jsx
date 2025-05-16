import { useState, useEffect, useMemo } from 'react';
import { format, startOfWeek, endOfWeek, startOfMonth, endOfMonth, eachDayOfInterval, 
  isSameMonth, isSameDay, addDays, parse, parseISO, isToday, getDay, addMonths, subMonths } from 'date-fns';
import { tr } from 'date-fns/locale';
import { CalendarDays, ChevronLeft, ChevronRight, Plus, Filter, Users, Clock, Calendar, List, LayoutGrid } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/toast';
import AppointmentCard from '@/components/appointment/AppointmentCard';
import AppointmentModal from '@/components/appointment/AppointmentModal';
import { useAuth } from '@/hooks/useAuth';

/**
 * CalendarPage displays a calendar view of appointments and allows scheduling new ones
 */
const CalendarPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const { user } = useAuth();

  // State management
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [viewMode, setViewMode] = useState('month'); // 'month', 'week', 'day', 'list'
  const [appointments, setAppointments] = useState([]);
  const [filteredAppointments, setFilteredAppointments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [filters, setFilters] = useState({
    searchTerm: '',
    beneficiaryId: '',
    trainerId: '',
    status: 'all', // 'all', 'upcoming', 'past', 'canceled'
    type: 'all', // 'all', 'session', 'evaluation', 'meeting'
  });

  // Calculate the days to display based on view mode
  const daysToDisplay = useMemo(() => {
    if (viewMode === 'month') {
      const monthStart = startOfMonth(currentDate);
      const monthEnd = endOfMonth(currentDate);
      const startDate = startOfWeek(monthStart);
      const endDate = endOfWeek(monthEnd);
      
      return eachDayOfInterval({ start: startDate, end: endDate });
    } else if (viewMode === 'week') {
      const weekStart = startOfWeek(currentDate);
      const weekEnd = endOfWeek(currentDate);
      
      return eachDayOfInterval({ start: weekStart, end: weekEnd });
    } else {
      // Day view - just return the current date in an array
      return [currentDate];
    }
  }, [currentDate, viewMode]);

  // Fetch appointments
  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        setIsLoading(true);
        
        // Define the date range for fetching appointments
        const startDate = viewMode === 'month' 
          ? startOfMonth(currentDate) 
          : viewMode === 'week'
            ? startOfWeek(currentDate)
            : currentDate;
            
        const endDate = viewMode === 'month'
          ? endOfMonth(currentDate)
          : viewMode === 'week'
            ? endOfWeek(currentDate)
            : currentDate;
        
        // Format dates for API
        const start = format(startDate, 'yyyy-MM-dd');
        const end = format(endDate, 'yyyy-MM-dd');
        
        // Get appointments from API
        const response = await api.get('/api/calendar/events', {
          params: { start, end }
        });
        setAppointments(response.data.events || []);
        applyFilters(response.data.events || []);
      } catch (error) {
        console.error('Error fetching appointments:', error);
        toast({
          title: 'Error',
          description: 'Failed to load appointments',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchAppointments();
  }, [currentDate, viewMode, toast]);

  // Apply filters to appointments
  const applyFilters = (appointmentsToFilter = appointments) => {
    let filtered = [...appointmentsToFilter];
    
    // Apply search term filter
    if (filters.searchTerm) {
      const searchLower = filters.searchTerm.toLowerCase();
      filtered = filtered.filter(appointment => 
        appointment.title.toLowerCase().includes(searchLower) || 
        appointment.description?.toLowerCase().includes(searchLower) ||
        appointment.beneficiary?.name.toLowerCase().includes(searchLower) ||
        appointment.trainer?.name.toLowerCase().includes(searchLower)
      );
    }
    
    // Apply beneficiary filter
    if (filters.beneficiaryId) {
      filtered = filtered.filter(appointment => 
        appointment.beneficiary_id === parseInt(filters.beneficiaryId)
      );
    }
    
    // Apply trainer filter
    if (filters.trainerId) {
      filtered = filtered.filter(appointment => 
        appointment.trainer_id === parseInt(filters.trainerId)
      );
    }
    
    // Apply status filter
    if (filters.status !== 'all') {
      const now = new Date();
      
      if (filters.status === 'upcoming') {
        filtered = filtered.filter(appointment => 
          new Date(appointment.start_time) > now && appointment.status !== 'canceled'
        );
      } else if (filters.status === 'past') {
        filtered = filtered.filter(appointment => 
          new Date(appointment.end_time) < now && appointment.status !== 'canceled'
        );
      } else if (filters.status === 'canceled') {
        filtered = filtered.filter(appointment => 
          appointment.status === 'canceled'
        );
      }
    }
    
    // Apply type filter
    if (filters.type !== 'all') {
      filtered = filtered.filter(appointment => 
        appointment.type === filters.type
      );
    }
    
    setFilteredAppointments(filtered);
  };

  // Handle filter changes
  const handleFilterChange = (key, value) => {
    setFilters(prev => {
      const newFilters = { ...prev, [key]: value };
      applyFilters(appointments);
      return newFilters;
    });
  };

  // Navigate to previous period
  const handlePrevious = () => {
    if (viewMode === 'month') {
      setCurrentDate(subMonths(currentDate, 1));
    } else if (viewMode === 'week') {
      setCurrentDate(addDays(currentDate, -7));
    } else {
      setCurrentDate(addDays(currentDate, -1));
    }
  };

  // Navigate to next period
  const handleNext = () => {
    if (viewMode === 'month') {
      setCurrentDate(addMonths(currentDate, 1));
    } else if (viewMode === 'week') {
      setCurrentDate(addDays(currentDate, 7));
    } else {
      setCurrentDate(addDays(currentDate, 1));
    }
  };

  // Set view to today
  const handleToday = () => {
    setCurrentDate(new Date());
    setSelectedDate(new Date());
  };

  // Change view mode
  const handleViewChange = (mode) => {
    setViewMode(mode);
  };

  // Open appointment modal for creating a new appointment
  const handleCreateAppointment = (date) => {
    setSelectedDate(date);
    setSelectedAppointment(null);
    setShowModal(true);
  };

  // Handle clicking on an appointment
  const handleAppointmentClick = (appointment) => {
    setSelectedAppointment(appointment);
    setShowModal(true);
  };

  // Get appointments for a specific day
  const getAppointmentsForDay = (day) => {
    return filteredAppointments.filter(appointment => {
      const appointmentDate = parseISO(appointment.start_time);
      return isSameDay(appointmentDate, day);
    });
  };

  // Format the header text based on view mode
  const getHeaderText = () => {
    if (viewMode === 'month') {
      return format(currentDate, 'MMMM yyyy', { locale: tr });
    } else if (viewMode === 'week') {
      const start = startOfWeek(currentDate);
      const end = endOfWeek(currentDate);
      const startMonth = format(start, 'MMM d', { locale: tr });
      const endMonth = format(end, 'MMM d, yyyy', { locale: tr });
      return `${startMonth} - ${endMonth}`;
    } else {
      return format(currentDate, 'EEEE, MMMM d, yyyy', { locale: tr });
    }
  };

  // Render day cell for the calendar
  const renderDay = (day, index) => {
    const dayAppointments = getAppointmentsForDay(day);
    const isCurrentMonth = isSameMonth(day, currentDate);
    const isSelected = isSameDay(day, selectedDate);
    
    return (
      <div
        key={index}
        className={`border border-gray-200 min-h-[120px] ${
          isCurrentMonth ? 'bg-white' : 'bg-gray-50 text-gray-400'
        } ${isToday(day) ? 'border-primary' : ''} ${
          isSelected ? 'bg-primary-50' : ''
        }`}
        onClick={() => setSelectedDate(day)}
      >
        <div className="flex justify-between items-center p-2 border-b border-gray-200">
          <span className={`text-sm font-medium ${isToday(day) ? 'text-primary' : ''}`}>
            {format(day, 'd')}
          </span>
          <button
            className="p-1 hover:bg-gray-100 rounded-full text-gray-600"
            onClick={(e) => {
              e.stopPropagation();
              handleCreateAppointment(day);
            }}
          >
            <Plus className="w-3 h-3" />
          </button>
        </div>
        <div className="p-1 max-h-[100px] overflow-y-auto">
          {dayAppointments.length > 0 ? (
            dayAppointments.map((appointment) => (
              <div
                key={appointment.id}
                className={`px-2 py-1 mb-1 text-xs rounded truncate ${
                  appointment.status === 'canceled' 
                    ? 'bg-gray-200 text-gray-600 line-through'
                    : `bg-${appointment.color || 'blue'}-100 text-${appointment.color || 'blue'}-800`
                }`}
                onClick={(e) => {
                  e.stopPropagation();
                  handleAppointmentClick(appointment);
                }}
              >
                {format(parseISO(appointment.start_time), 'HH:mm')} - {appointment.title}
              </div>
            ))
          ) : (
            <div className="text-xs text-gray-400 text-center mt-2">No appointments</div>
          )}
        </div>
      </div>
    );
  };

  // Render week view
  const renderWeekView = () => {
    const days = daysToDisplay;
    const hours = Array.from({ length: 12 }, (_, i) => i + 8); // 8 AM to 7 PM
    
    return (
      <div className="flex flex-col h-full">
        <div className="grid grid-cols-8 border-b border-gray-200">
          <div className="border-r border-gray-200 p-2 text-sm font-medium">
            Time
          </div>
          {days.map((day, idx) => (
            <div 
              key={idx} 
              className={`p-2 text-center text-sm font-medium ${
                isToday(day) ? 'text-primary' : ''
              }`}
            >
              <div>{format(day, 'E', { locale: tr })}</div>
              <div>{format(day, 'd')}</div>
            </div>
          ))}
        </div>
        
        <div className="flex-1 overflow-y-auto">
          {hours.map((hour) => (
            <div key={hour} className="grid grid-cols-8 border-b border-gray-200">
              <div className="border-r border-gray-200 p-2 text-xs text-gray-500 text-right">
                {hour}:00
              </div>
              
              {days.map((day, idx) => {
                const currentHourAppointments = filteredAppointments.filter(appointment => {
                  const startTime = parseISO(appointment.start_time);
                  return isSameDay(startTime, day) && startTime.getHours() === hour;
                });
                
                return (
                  <div 
                    key={idx} 
                    className={`border-r border-gray-200 p-1 min-h-[60px] ${
                      isToday(day) ? 'bg-primary-50' : ''
                    }`}
                    onClick={() => {
                      const date = new Date(day);
                      date.setHours(hour);
                      handleCreateAppointment(date);
                    }}
                  >
                    {currentHourAppointments.map((appointment) => (
                      <div
                        key={appointment.id}
                        className={`px-2 py-1 mb-1 text-xs rounded truncate cursor-pointer ${
                          appointment.status === 'canceled' 
                            ? 'bg-gray-200 text-gray-600 line-through'
                            : `bg-${appointment.color || 'blue'}-100 text-${appointment.color || 'blue'}-800`
                        }`}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleAppointmentClick(appointment);
                        }}
                      >
                        {format(parseISO(appointment.start_time), 'HH:mm')} - {appointment.title}
                      </div>
                    ))}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Render day view
  const renderDayView = () => {
    const hours = Array.from({ length: 14 }, (_, i) => i + 7); // 7 AM to 8 PM
    
    return (
      <div className="flex flex-col h-full">
        <div className="border-b border-gray-200 p-3 text-center">
          <div className={`font-medium ${isToday(currentDate) ? 'text-primary' : ''}`}>
            {format(currentDate, 'EEEE', { locale: tr })}
          </div>
          <div className="text-sm text-gray-600">
            {format(currentDate, 'd MMMM yyyy', { locale: tr })}
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          {hours.map((hour) => {
            const currentHourAppointments = filteredAppointments.filter(appointment => {
              const startTime = parseISO(appointment.start_time);
              return isSameDay(startTime, currentDate) && startTime.getHours() === hour;
            });
            
            return (
              <div key={hour} className="flex border-b border-gray-200">
                <div className="w-20 border-r border-gray-200 p-2 text-sm text-gray-500 text-right">
                  {hour}:00
                </div>
                
                <div 
                  className="flex-1 p-2 min-h-[80px]"
                  onClick={() => {
                    const date = new Date(currentDate);
                    date.setHours(hour);
                    handleCreateAppointment(date);
                  }}
                >
                  {currentHourAppointments.map((appointment) => (
                    <div
                      key={appointment.id}
                      className={`px-3 py-2 mb-2 text-sm rounded ${
                        appointment.status === 'canceled' 
                          ? 'bg-gray-200 text-gray-600 line-through'
                          : `bg-${appointment.color || 'blue'}-100 text-${appointment.color || 'blue'}-800`
                      }`}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleAppointmentClick(appointment);
                      }}
                    >
                      <div className="font-medium">
                        {format(parseISO(appointment.start_time), 'HH:mm')} - {format(parseISO(appointment.end_time), 'HH:mm')}
                      </div>
                      <div>{appointment.title}</div>
                      <div className="text-xs mt-1">
                        {appointment.beneficiary?.name && (
                          <span className="inline-flex items-center mr-2">
                            <Users className="w-3 h-3 mr-1" />
                            {appointment.beneficiary.name}
                          </span>
                        )}
                        {appointment.location && (
                          <span className="inline-flex items-center">
                            <Map className="w-3 h-3 mr-1" />
                            {appointment.location}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  // Render list view
  const renderListView = () => {
    // Group appointments by date
    const groupedAppointments = filteredAppointments.reduce((acc, appointment) => {
      const date = format(parseISO(appointment.start_time), 'yyyy-MM-dd');
      
      if (!acc[date]) {
        acc[date] = [];
      }
      
      acc[date].push(appointment);
      return acc;
    }, {});
    
    // Sort dates
    const sortedDates = Object.keys(groupedAppointments).sort();
    
    return (
      <div className="space-y-6">
        {sortedDates.length > 0 ? (
          sortedDates.map((date) => (
            <div key={date}>
              <h3 className="text-lg font-medium mb-2">
                {format(parseISO(date), 'EEEE, d MMMM yyyy', { locale: tr })}
              </h3>
              
              <div className="space-y-2">
                {groupedAppointments[date].map((appointment) => (
                  <AppointmentCard
                    key={appointment.id}
                    appointment={appointment}
                    onClick={() => handleAppointmentClick(appointment)}
                  />
                ))}
              </div>
            </div>
          ))
        ) : (
          <div className="text-center p-8">
            <CalendarDays className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <h3 className="text-lg font-medium text-gray-900 mb-1">No appointments found</h3>
            <p className="text-gray-500 mb-4">Try adjusting your filters or create a new appointment</p>
            <Button onClick={() => handleCreateAppointment(new Date())}>
              Create Appointment
            </Button>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Calendar</h1>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            onClick={() => navigate('/calendar/availability')}
            className="flex items-center"
          >
            <Clock className="w-4 h-4 mr-2" />
            Availability
          </Button>
          
          <Button
            variant="outline"
            onClick={() => navigate('/calendar/google-sync')}
            className="flex items-center"
          >
            <CalendarDays className="w-4 h-4 mr-2" />
            Google Sync
          </Button>
          
          <Button
            onClick={() => handleCreateAppointment(selectedDate)}
            className="flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create Appointment
          </Button>
        </div>
      </div>
      
      {/* Filters and controls */}
      <Card className="p-4 mb-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handlePrevious}
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleNext}
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleToday}
            >
              Today
            </Button>
            
            <h2 className="text-lg font-medium ml-2">
              {getHeaderText()}
            </h2>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="flex border border-gray-300 rounded-md overflow-hidden">
              <Button
                variant={viewMode === 'month' ? 'default' : 'ghost'}
                size="sm"
                className="rounded-none border-0"
                onClick={() => handleViewChange('month')}
              >
                <LayoutGrid className="w-4 h-4 mr-1" />
                Month
              </Button>
              
              <Button
                variant={viewMode === 'week' ? 'default' : 'ghost'}
                size="sm"
                className="rounded-none border-0"
                onClick={() => handleViewChange('week')}
              >
                <Calendar className="w-4 h-4 mr-1" />
                Week
              </Button>
              
              <Button
                variant={viewMode === 'day' ? 'default' : 'ghost'}
                size="sm"
                className="rounded-none border-0"
                onClick={() => handleViewChange('day')}
              >
                <Clock className="w-4 h-4 mr-1" />
                Day
              </Button>
              
              <Button
                variant={viewMode === 'list' ? 'default' : 'ghost'}
                size="sm"
                className="rounded-none border-0"
                onClick={() => handleViewChange('list')}
              >
                <List className="w-4 h-4 mr-1" />
                List
              </Button>
            </div>
            
            <div className="relative">
              <Input
                type="text"
                placeholder="Search..."
                value={filters.searchTerm}
                onChange={(e) => handleFilterChange('searchTerm', e.target.value)}
                className="pl-8"
              />
              <div className="absolute left-3 top-1/2 transform -translate-y-1/2">
                <Filter className="w-4 h-4 text-gray-400" />
              </div>
            </div>
          </div>
        </div>
        
        {/* Additional filters */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
            >
              <option value="all">All</option>
              <option value="upcoming">Upcoming</option>
              <option value="past">Past</option>
              <option value="canceled">Canceled</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Appointment Type
            </label>
            <select
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
              value={filters.type}
              onChange={(e) => handleFilterChange('type', e.target.value)}
            >
              <option value="all">All Types</option>
              <option value="session">Training Session</option>
              <option value="evaluation">Evaluation</option>
              <option value="meeting">Meeting</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Beneficiary
            </label>
            <select
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
              value={filters.beneficiaryId}
              onChange={(e) => handleFilterChange('beneficiaryId', e.target.value)}
            >
              <option value="">All Beneficiaries</option>
              {/* In a real app, this would be populated from an API */}
              <option value="1">John Doe</option>
              <option value="2">Jane Smith</option>
              <option value="3">Robert Johnson</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Trainer
            </label>
            <select
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
              value={filters.trainerId}
              onChange={(e) => handleFilterChange('trainerId', e.target.value)}
            >
              <option value="">All Trainers</option>
              {/* In a real app, this would be populated from an API */}
              <option value="1">Sarah Johnson</option>
              <option value="2">Michael Chen</option>
              <option value="3">Emily Davis</option>
            </select>
          </div>
        </div>
      </Card>
      
      {/* Calendar content */}
      <Card className="overflow-hidden h-[calc(100vh-16rem)]">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : (
          <div className="h-full">
            {viewMode === 'month' && (
              <div className="grid grid-cols-7 h-full">
                {/* Day headers */}
                {['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'].map((day, index) => (
                  <div key={index} className="border-b border-gray-200 p-2 text-center font-medium text-gray-700">
                    {day}
                  </div>
                ))}
                
                {/* Calendar days */}
                {daysToDisplay.map((day, index) => renderDay(day, index))}
              </div>
            )}
            
            {viewMode === 'week' && renderWeekView()}
            
            {viewMode === 'day' && renderDayView()}
            
            {viewMode === 'list' && renderListView()}
          </div>
        )}
      </Card>
      
      {/* Appointment Modal */}
      <AppointmentModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        selectedDate={selectedDate}
        appointment={selectedAppointment}
        onAppointmentUpdated={(updatedAppointment) => {
          if (selectedAppointment) {
            // Update existing appointment in the list
            setAppointments(prev => 
              prev.map(a => a.id === updatedAppointment.id ? updatedAppointment : a)
            );
          } else {
            // Add new appointment to the list
            setAppointments(prev => [...prev, updatedAppointment]);
          }
          
          // Re-apply filters
          setShowModal(false);
          applyFilters();
        }}
        onAppointmentDeleted={(id) => {
          setAppointments(prev => prev.filter(a => a.id !== id));
          setShowModal(false);
          applyFilters();
        }}
      />
    </div>
  );
};

// Map Component referenced in the calendar views
const Map = (props) => (
  <svg 
    xmlns="http://www.w3.org/2000/svg" 
    width="24" 
    height="24" 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round"
    {...props}
  >
    <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/>
    <line x1="9" x2="9" y1="3" y2="18"/>
    <line x1="15" x2="15" y1="6" y2="21"/>
  </svg>
);

export default CalendarPage;
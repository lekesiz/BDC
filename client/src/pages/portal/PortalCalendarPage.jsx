import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Calendar as CalendarIcon, 
  ChevronLeft, 
  ChevronRight, 
  List,
  LayoutGrid,
  Clock,
  Users,
  VideoIcon,
  BookOpen,
  Loader,
  MessageSquare,
  ArrowRight
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';
/**
 * PortalCalendarPage displays a calendar with all scheduled sessions for the student
 */
const PortalCalendarPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [calendarData, setCalendarData] = useState({
    sessions: [],
    currentMonth: new Date().getMonth(),
    currentYear: new Date().getFullYear()
  });
  const [view, setView] = useState('month'); // 'month' or 'list'
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [sessionsForSelectedDate, setSessionsForSelectedDate] = useState([]);
  // Month names
  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  // Weekday names
  const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  // Fetch calendar data
  useEffect(() => {
    const fetchCalendarData = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/api/portal/calendar', {
          params: {
            month: calendarData.currentMonth + 1, // API expects 1-12
            year: calendarData.currentYear
          }
        });
        const sessions = Array.isArray(response.data) 
          ? response.data 
          : response.data.sessions || response.data.events || [];
        setCalendarData(prevData => ({
          ...prevData,
          sessions: sessions
        }));
      } catch (error) {
        console.error('Error fetching calendar data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load calendar data',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchCalendarData();
  }, [calendarData.currentMonth, calendarData.currentYear, toast]);
  // Update sessions for selected date when date changes
  useEffect(() => {
    const sessions = calendarData.sessions.filter(session => {
      const sessionDate = new Date(session.date);
      return (
        sessionDate.getDate() === selectedDate.getDate() &&
        sessionDate.getMonth() === selectedDate.getMonth() &&
        sessionDate.getFullYear() === selectedDate.getFullYear()
      );
    });
    setSessionsForSelectedDate(sessions);
  }, [selectedDate, calendarData.sessions]);
  // Get days in month
  const getDaysInMonth = (month, year) => {
    return new Date(year, month + 1, 0).getDate();
  };
  // Get the first day of the month (0 = Sunday, 6 = Saturday)
  const getFirstDayOfMonth = (month, year) => {
    return new Date(year, month, 1).getDay();
  };
  // Generate the calendar days
  const generateCalendarDays = () => {
    const daysInMonth = getDaysInMonth(calendarData.currentMonth, calendarData.currentYear);
    const firstDay = getFirstDayOfMonth(calendarData.currentMonth, calendarData.currentYear);
    const days = [];
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < firstDay; i++) {
      days.push({ day: '', isEmpty: true });
    }
    // Add cells for each day of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(calendarData.currentYear, calendarData.currentMonth, day);
      const isToday = isSameDay(date, new Date());
      const isSelected = isSameDay(date, selectedDate);
      // Check if there are any sessions on this day
      const sessionsOnDay = calendarData.sessions.filter(session => {
        const sessionDate = new Date(session.date);
        return (
          sessionDate.getDate() === day &&
          sessionDate.getMonth() === calendarData.currentMonth &&
          sessionDate.getFullYear() === calendarData.currentYear
        );
      });
      days.push({ 
        day, 
        isEmpty: false, 
        isToday, 
        isSelected,
        hasSessions: sessionsOnDay.length > 0,
        sessionCount: sessionsOnDay.length,
        date
      });
    }
    return days;
  };
  // Check if two dates are the same day
  const isSameDay = (date1, date2) => {
    return (
      date1.getDate() === date2.getDate() &&
      date1.getMonth() === date2.getMonth() &&
      date1.getFullYear() === date2.getFullYear()
    );
  };
  // Navigate to previous month
  const goToPreviousMonth = () => {
    setCalendarData(prevData => {
      let newMonth = prevData.currentMonth - 1;
      let newYear = prevData.currentYear;
      if (newMonth < 0) {
        newMonth = 11;
        newYear -= 1;
      }
      return {
        ...prevData,
        currentMonth: newMonth,
        currentYear: newYear
      };
    });
  };
  // Navigate to next month
  const goToNextMonth = () => {
    setCalendarData(prevData => {
      let newMonth = prevData.currentMonth + 1;
      let newYear = prevData.currentYear;
      if (newMonth > 11) {
        newMonth = 0;
        newYear += 1;
      }
      return {
        ...prevData,
        currentMonth: newMonth,
        currentYear: newYear
      };
    });
  };
  // Handle day selection
  const handleDaySelect = (day) => {
    if (!day.isEmpty) {
      setSelectedDate(day.date);
    }
  };
  // Format time
  const formatTime = (dateString) => {
    const options = { hour: 'numeric', minute: '2-digit', hour12: true };
    return new Date(dateString).toLocaleTimeString(undefined, options);
  };
  // Determine session type icon
  const getSessionTypeIcon = (type) => {
    switch (type.toLowerCase()) {
      case 'video':
        return <VideoIcon className="w-4 h-4" />;
      case 'workshop':
        return <Users className="w-4 h-4" />;
      case 'lecture':
        return <BookOpen className="w-4 h-4" />;
      case 'discussion':
        return <MessageSquare className="w-4 h-4" />;
      default:
        return <CalendarIcon className="w-4 h-4" />;
    }
  };
  // List of all upcoming sessions for list view
  const getUpcomingSessions = () => {
    const today = new Date();
    return calendarData.sessions
      .filter(session => new Date(session.date) >= today)
      .sort((a, b) => new Date(a.date) - new Date(b.date));
  };
  // Format date
  const formatDate = (dateString) => {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader className="w-10 h-10 text-primary animate-spin" />
      </div>
    );
  }
  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Calendar</h1>
        <div className="flex space-x-2">
          <div className="bg-gray-100 p-1 rounded-md">
            <button
              className={`p-2 rounded-md ${view === 'month' ? 'bg-white shadow-sm' : 'text-gray-500'}`}
              onClick={() => setView('month')}
            >
              <LayoutGrid className="w-5 h-5" />
            </button>
            <button
              className={`p-2 rounded-md ${view === 'list' ? 'bg-white shadow-sm' : 'text-gray-500'}`}
              onClick={() => setView('list')}
            >
              <List className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
      {view === 'month' ? (
        <div className="space-y-6">
          {/* Calendar navigation */}
          <div className="flex justify-between items-center bg-white p-4 rounded-lg shadow-sm">
            <button
              onClick={goToPreviousMonth}
              className="p-2 rounded-full hover:bg-gray-100"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <h2 className="text-xl font-medium">
              {months[calendarData.currentMonth]} {calendarData.currentYear}
            </h2>
            <button
              onClick={goToNextMonth}
              className="p-2 rounded-full hover:bg-gray-100"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
          {/* Calendar grid */}
          <div className="grid grid-cols-7 gap-2">
            {/* Weekday headers */}
            {weekdays.map(day => (
              <div key={day} className="text-center py-2 font-medium text-gray-500">
                {day}
              </div>
            ))}
            {/* Calendar days */}
            {generateCalendarDays().map((day, index) => (
              <div 
                key={index} 
                className={`aspect-square p-2 rounded-lg ${
                  day.isEmpty 
                    ? 'bg-transparent' 
                    : day.isSelected
                    ? 'bg-primary text-white'
                    : day.isToday
                    ? 'bg-primary/10 border border-primary'
                    : 'bg-white hover:bg-gray-50 cursor-pointer'
                } ${day.hasSessions && !day.isSelected ? 'border-2 border-primary/40' : ''}`}
                onClick={() => handleDaySelect(day)}
              >
                {!day.isEmpty && (
                  <div className="h-full flex flex-col">
                    <div className={`text-right mb-1 ${day.isSelected ? 'text-white' : ''}`}>
                      {day.day}
                    </div>
                    {day.hasSessions && (
                      <div className="mt-auto">
                        <div className={`text-xs font-medium rounded-full px-1.5 py-0.5 inline-flex items-center ${
                          day.isSelected 
                            ? 'bg-white/20 text-white' 
                            : 'bg-primary/10 text-primary'
                        }`}>
                          <CalendarIcon className="w-3 h-3 mr-1" />
                          {day.sessionCount} {day.sessionCount === 1 ? 'session' : 'sessions'}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
          {/* Selected day sessions */}
          <Card className="overflow-hidden">
            <div className="p-6 border-b">
              <h2 className="text-lg font-medium">
                Sessions for {selectedDate.toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
              </h2>
            </div>
            {sessionsForSelectedDate.length > 0 ? (
              <div className="divide-y">
                {sessionsForSelectedDate.map(session => (
                  <div 
                    key={session.id} 
                    className="p-6 hover:bg-gray-50 transition-colors cursor-pointer"
                    onClick={() => navigate(`/portal/sessions/${session.id}`)}
                  >
                    <div className="flex items-start">
                      <div className={`p-3 rounded-lg mr-4 ${
                        session.type === 'video' 
                          ? 'bg-blue-50' 
                          : session.type === 'workshop'
                          ? 'bg-green-50'
                          : session.type === 'lecture'
                          ? 'bg-purple-50'
                          : 'bg-gray-50'
                      }`}>
                        {getSessionTypeIcon(session.type)}
                      </div>
                      <div className="flex-1">
                        <div className="flex justify-between items-start">
                          <div>
                            <h3 className="font-medium">{session.title}</h3>
                            <p className="text-sm text-gray-500 capitalize">{session.type}</p>
                          </div>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            new Date(session.date) < new Date() 
                              ? 'bg-gray-100 text-gray-800' 
                              : 'bg-blue-100 text-blue-800'
                          }`}>
                            {new Date(session.date) < new Date() ? 'Past' : 'Upcoming'}
                          </span>
                        </div>
                        <div className="mt-3 flex items-center text-sm text-gray-500 space-x-4">
                          <div className="flex items-center">
                            <Clock className="w-4 h-4 mr-1.5" />
                            <span>{formatTime(session.date)}</span>
                          </div>
                          {session.duration && (
                            <div>
                              <span>{session.duration} min</span>
                            </div>
                          )}
                          {session.trainer && (
                            <div className="flex items-center">
                              <Users className="w-4 h-4 mr-1.5" />
                              <span>with {session.trainer}</span>
                            </div>
                          )}
                        </div>
                        {session.description && (
                          <p className="mt-2 text-sm text-gray-600">{session.description}</p>
                        )}
                        <div className="mt-3">
                          <Button
                            variant="link"
                            className="text-primary p-0 h-auto flex items-center"
                          >
                            View Session Details
                            <ArrowRight className="w-4 h-4 ml-1" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center">
                <CalendarIcon className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">No sessions scheduled for this day</p>
              </div>
            )}
          </Card>
        </div>
      ) : (
        <div className="space-y-6">
          <Card className="overflow-hidden">
            <div className="p-6 border-b">
              <h2 className="text-lg font-medium">Upcoming Sessions</h2>
            </div>
            {getUpcomingSessions().length > 0 ? (
              <div className="divide-y">
                {getUpcomingSessions().map(session => (
                  <div 
                    key={session.id} 
                    className="p-6 hover:bg-gray-50 transition-colors cursor-pointer"
                    onClick={() => navigate(`/portal/sessions/${session.id}`)}
                  >
                    <div className="flex items-start">
                      <div className={`p-3 rounded-lg mr-4 ${
                        session.type === 'video' 
                          ? 'bg-blue-50' 
                          : session.type === 'workshop'
                          ? 'bg-green-50'
                          : session.type === 'lecture'
                          ? 'bg-purple-50'
                          : 'bg-gray-50'
                      }`}>
                        {getSessionTypeIcon(session.type)}
                      </div>
                      <div className="flex-1">
                        <div className="flex justify-between items-start">
                          <div>
                            <h3 className="font-medium">{session.title}</h3>
                            <p className="text-sm text-gray-500 capitalize">{session.type}</p>
                          </div>
                          <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                            Upcoming
                          </span>
                        </div>
                        <div className="mt-3 flex flex-wrap items-center text-sm text-gray-500 gap-4">
                          <div className="flex items-center">
                            <CalendarIcon className="w-4 h-4 mr-1.5" />
                            <span>{formatDate(session.date)}</span>
                          </div>
                          <div className="flex items-center">
                            <Clock className="w-4 h-4 mr-1.5" />
                            <span>{formatTime(session.date)}</span>
                          </div>
                          {session.duration && (
                            <div>
                              <span>{session.duration} min</span>
                            </div>
                          )}
                          {session.trainer && (
                            <div className="flex items-center">
                              <Users className="w-4 h-4 mr-1.5" />
                              <span>with {session.trainer}</span>
                            </div>
                          )}
                        </div>
                        {session.description && (
                          <p className="mt-2 text-sm text-gray-600">{session.description}</p>
                        )}
                        <div className="mt-3">
                          <Button
                            variant="link"
                            className="text-primary p-0 h-auto flex items-center"
                          >
                            View Session Details
                            <ArrowRight className="w-4 h-4 ml-1" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center">
                <CalendarIcon className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">No upcoming sessions scheduled</p>
              </div>
            )}
          </Card>
        </div>
      )}
    </div>
  );
};
export default PortalCalendarPage;
import { 
  generateCalendarData, 
  generateAvailableSlots, 
  generateAppointmentTypes,
  generateTeachingSchedule 
} from './mockCalendarData';
export const setupCalendarMockApi = (api, originalGet, originalPost, originalPut, originalDelete) => {
  const originalFunctions = {
    get: originalGet || api.get.bind(api),
    post: originalPost || api.post.bind(api),
    put: originalPut || api.put.bind(api),
    delete: originalDelete || api.delete.bind(api)
  };
  // Calendar events endpoint
  api.get = function(url, ...args) {
    if (url === '/api/calendar/events' || url.startsWith('/api/calendar/events?')) {
      try {
        const userRole = localStorage.getItem('userRole') || 'student';
        const calendarData = generateCalendarData(userRole);
        // Parse query parameters for date range
        const urlObj = new URL(url, 'http://localhost');
        const start = urlObj.searchParams.get('start');
        const end = urlObj.searchParams.get('end');
        // Return empty array with google calendar not connected info
        // This simulates the actual server behavior when Google Calendar is not connected
        return Promise.resolve({
          status: 200,
          data: {
            events: [], // Empty array for now
            google_calendar_connected: false,
            google_events: [],
            total_events: 0
          }
        });
      } catch (error) {
        console.error('Mock API Error:', error);
        return Promise.reject({
          response: {
            status: 500,
            data: {
              error: 'mock_error',
              message: 'Error in mock API'
            }
          }
        });
      }
    }
    // Available slots endpoint
    if (url === '/api/calendar/available-slots' || url.startsWith('/api/calendar/available-slots?')) {
      const slots = generateAvailableSlots();
      return Promise.resolve({
        status: 200,
        data: {
          slots,
          total: slots.length
        }
      });
    }
    // Availability endpoint (enhanced version)
    if (url === '/api/calendar/availability') {
      return Promise.resolve({
        status: 200,
        data: {
          schedule: {
            id: 1,
            name: 'Default Schedule',
            is_active: true,
            timezone: 'America/New_York',
            created_at: new Date().toISOString()
          },
          slots: [
            {
              id: 1,
              day_of_week: 1, // Monday
              start_time: '09:00',
              end_time: '12:00',
              is_available: true
            },
            {
              id: 2,
              day_of_week: 1, // Monday
              start_time: '14:00',
              end_time: '17:00',
              is_available: true
            },
            {
              id: 3,
              day_of_week: 3, // Wednesday
              start_time: '09:00',
              end_time: '12:00',
              is_available: true
            },
            {
              id: 4,
              day_of_week: 3, // Wednesday
              start_time: '14:00',
              end_time: '17:00',
              is_available: true
            },
            {
              id: 5,
              day_of_week: 5, // Friday
              start_time: '09:00',
              end_time: '12:00',
              is_available: true
            }
          ]
        }
      });
    }
    // Appointment types endpoint
    if (url === '/api/calendar/appointment-types') {
      const types = generateAppointmentTypes();
      return Promise.resolve({
        status: 200,
        data: {
          types
        }
      });
    }
    // Teaching schedule endpoint
    if (url === '/api/calendar/teaching-schedule') {
      const schedule = generateTeachingSchedule();
      return Promise.resolve({
        status: 200,
        data: {
          schedule
        }
      });
    }
    // Specific event endpoint
    if (url.match(/^\/api\/calendar\/events\/\d+$/)) {
      const eventId = parseInt(url.split('/').pop());
      const userRole = localStorage.getItem('userRole') || 'student';
      const calendarData = generateCalendarData(userRole);
      const event = calendarData.events.find(e => e.id === eventId);
      if (event) {
        return Promise.resolve({
          status: 200,
          data: event
        });
      } else {
        return Promise.reject({
          response: {
            status: 404,
            data: {
              error: 'not_found',
              message: 'Event not found'
            }
          }
        });
      }
    }
    // Pass through to original function for other endpoints
    return originalFunctions.get.call(this, url, ...args);
  };
  // Create appointment endpoint
  api.post = function(url, data, ...args) {
    if (url === '/api/calendar/appointments') {
      const newAppointment = {
        id: Date.now(),
        ...data,
        status: 'scheduled',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      return Promise.resolve({
        status: 201,
        data: newAppointment
      });
    }
    // Update availability endpoint
    if (url === '/api/calendar/availability') {
      return Promise.resolve({
        status: 200,
        data: {
          message: 'Availability updated successfully',
          schedule_id: 1
        }
      });
    }
    // Pass through to original function for other endpoints
    return originalFunctions.post.call(this, url, data, ...args);
  };
  // Update appointment endpoint
  api.put = function(url, data, ...args) {
    if (url.match(/^\/api\/calendar\/appointments\/\d+$/)) {
      const appointmentId = parseInt(url.split('/').pop());
      const updatedAppointment = {
        id: appointmentId,
        ...data,
        updated_at: new Date().toISOString()
      };
      return Promise.resolve({
        status: 200,
        data: updatedAppointment
      });
    }
    // Pass through to original function for other endpoints
    return originalFunctions.put.call(this, url, data, ...args);
  };
  // Delete appointment endpoint
  api.delete = function(url, ...args) {
    if (url.match(/^\/api\/calendar\/appointments\/\d+$/)) {
      return Promise.resolve({
        status: 200,
        data: {
          message: 'Appointment deleted successfully'
        }
      });
    }
    // Delete availability slot endpoint
    if (url.match(/^\/api\/calendar\/availability\/slots\/\d+$/)) {
      return Promise.resolve({
        status: 200,
        data: {
          message: 'Availability slot deleted successfully'
        }
      });
    }
    // Pass through to original function for other endpoints
    return originalFunctions.delete.call(this, url, ...args);
  };
};
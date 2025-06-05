import { useState, useEffect } from 'react';
import { format, addHours, parseISO } from 'date-fns';
import { Calendar, Clock, MapPin, Users, User, Tag, AlertTriangle, Trash2, Save, X, ExternalLink } from 'lucide-react';
import { AnimatedModal } from '@/components/animations';
import { AnimatedButton, AnimatedInput } from '@/components/animations';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '@/components/ui/modal';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/toast';
import api from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
/**
 * AppointmentModal component for creating and editing appointments
 * 
 * @param {Object} props - Component props
 * @param {boolean} props.isOpen - Whether the modal is open
 * @param {Function} props.onClose - Function to close the modal
 * @param {Date} props.selectedDate - The selected date for new appointments
 * @param {Object} props.appointment - Existing appointment data for editing
 * @param {Function} props.onAppointmentUpdated - Callback when an appointment is created or updated
 * @param {Function} props.onAppointmentDeleted - Callback when an appointment is deleted
 * @returns {JSX.Element} Appointment modal component
 */
const AppointmentModal = ({ 
  isOpen, 
  onClose, 
  selectedDate, 
  appointment = null,
  onAppointmentUpdated,
  onAppointmentDeleted
}) => {
  const { toast } = useToast();
  const { user } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    start_date: format(new Date(), 'yyyy-MM-dd'),
    start_time: format(new Date(), 'HH:mm'),
    end_date: format(new Date(), 'yyyy-MM-dd'),
    end_time: format(addHours(new Date(), 1), 'HH:mm'),
    location: '',
    type: 'session',
    status: 'confirmed',
    beneficiary_id: '',
    trainer_id: '',
    is_google_synced: false,
    notify_participants: true,
    notes: '',
  });
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [errors, setErrors] = useState({});
  // Initialize form with appointment data or defaults
  useEffect(() => {
    if (appointment) {
      // Format dates for form inputs
      const startDate = parseISO(appointment.start_time);
      const endDate = parseISO(appointment.end_time);
      setFormData({
        title: appointment.title || '',
        description: appointment.description || '',
        start_date: format(startDate, 'yyyy-MM-dd'),
        start_time: format(startDate, 'HH:mm'),
        end_date: format(endDate, 'yyyy-MM-dd'),
        end_time: format(endDate, 'HH:mm'),
        location: appointment.location || '',
        type: appointment.type || 'session',
        status: appointment.status || 'confirmed',
        beneficiary_id: appointment.beneficiary_id?.toString() || '',
        trainer_id: appointment.trainer_id?.toString() || '',
        is_google_synced: appointment.is_google_synced || false,
        notify_participants: true,
        notes: appointment.notes || '',
      });
    } else if (selectedDate) {
      // Set default date and time for new appointment
      const endTime = addHours(selectedDate, 1);
      setFormData(prev => ({
        ...prev,
        start_date: format(selectedDate, 'yyyy-MM-dd'),
        start_time: format(selectedDate, 'HH:mm'),
        end_date: format(selectedDate, 'yyyy-MM-dd'),
        end_time: format(endTime, 'HH:mm'),
      }));
    }
    // Reset errors when modal opens
    setErrors({});
    setShowDeleteConfirm(false);
  }, [appointment, selectedDate, isOpen]);
  // Handle form field changes
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };
  // Validate form fields
  const validateForm = () => {
    const newErrors = {};
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    if (!formData.start_date) {
      newErrors.start_date = 'Start date is required';
    }
    if (!formData.start_time) {
      newErrors.start_time = 'Start time is required';
    }
    if (!formData.end_date) {
      newErrors.end_date = 'End date is required';
    }
    if (!formData.end_time) {
      newErrors.end_time = 'End time is required';
    }
    // Check that end time is after start time
    const startDateTime = new Date(`${formData.start_date}T${formData.start_time}`);
    const endDateTime = new Date(`${formData.end_date}T${formData.end_time}`);
    if (endDateTime <= startDateTime) {
      newErrors.end_time = 'End time must be after start time';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) {
      return;
    }
    try {
      setIsSubmitting(true);
      // Format dates for API
      const startDateTime = new Date(`${formData.start_date}T${formData.start_time}`);
      const endDateTime = new Date(`${formData.end_date}T${formData.end_time}`);
      const appointmentData = {
        title: formData.title,
        description: formData.description,
        start_time: startDateTime.toISOString(),
        end_time: endDateTime.toISOString(),
        location: formData.location,
        type: formData.type,
        status: formData.status,
        beneficiary_id: formData.beneficiary_id ? parseInt(formData.beneficiary_id) : null,
        trainer_id: formData.trainer_id ? parseInt(formData.trainer_id) : null,
        is_google_synced: formData.is_google_synced,
        notes: formData.notes,
      };
      let response;
      if (appointment) {
        // Update existing appointment
        response = await api.put(`/api/appointments/${appointment.id}`, appointmentData);
        toast({
          title: 'Success',
          description: 'Appointment updated successfully',
          type: 'success',
        });
      } else {
        // Create new appointment
        response = await api.post('/api/appointments', appointmentData);
        toast({
          title: 'Success',
          description: 'Appointment created successfully',
          type: 'success',
        });
      }
      // If notification is enabled, send notifications
      if (formData.notify_participants) {
        await api.post(`/api/appointments/${response.data.id}/notify`);
      }
      // Call the callback with the updated/created appointment
      onAppointmentUpdated(response.data);
    } catch (error) {
      console.error('Error saving appointment:', error);
      toast({
        title: 'Error',
        description: 'Failed to save appointment',
        type: 'error',
      });
    } finally {
      setIsSubmitting(false);
    }
  };
  // Handle appointment deletion
  const handleDelete = async () => {
    if (!appointment) return;
    try {
      setIsSubmitting(true);
      await api.delete(`/api/appointments/${appointment.id}`);
      toast({
        title: 'Success',
        description: 'Appointment deleted successfully',
        type: 'success',
      });
      onAppointmentDeleted(appointment.id);
    } catch (error) {
      console.error('Error deleting appointment:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete appointment',
        type: 'error',
      });
    } finally {
      setIsSubmitting(false);
      setShowDeleteConfirm(false);
    }
  };
  // Handle cancellation (soft delete)
  const handleCancel = async () => {
    if (!appointment) return;
    try {
      setIsSubmitting(true);
      const response = await api.put(`/api/appointments/${appointment.id}`, {
        ...formData,
        status: 'canceled',
      });
      toast({
        title: 'Success',
        description: 'Appointment canceled successfully',
        type: 'success',
      });
      onAppointmentUpdated(response.data);
    } catch (error) {
      console.error('Error canceling appointment:', error);
      toast({
        title: 'Error',
        description: 'Failed to cancel appointment',
        type: 'error',
      });
    } finally {
      setIsSubmitting(false);
    }
  };
  return (
    <AnimatedModal
      isOpen={isOpen}
      onClose={onClose}
    >
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {appointment ? 'Edit Appointment' : 'Create Appointment'}
          </h2>
        </div>
        <div className="px-6 py-4 max-h-[70vh] overflow-y-auto">
          <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic info section */}
          <div className="space-y-4 mb-6">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                Title*
              </label>
              <AnimatedInput
                id="title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="Appointment title"
                error={errors.title}
              />
            </div>
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Description
              </label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Description or agenda"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                rows="2"
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="type" className="block text-sm font-medium text-gray-700">
                  Appointment Type
                </label>
                <div className="flex items-center mt-1">
                  <Tag className="w-4 h-4 text-gray-400 mr-2" />
                  <select
                    id="type"
                    name="type"
                    value={formData.type}
                    onChange={handleChange}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                  >
                    <option value="session">Training Session</option>
                    <option value="evaluation">Evaluation</option>
                    <option value="meeting">Meeting</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>
              <div>
                <label htmlFor="location" className="block text-sm font-medium text-gray-700">
                  Location
                </label>
                <div className="flex items-center mt-1">
                  <MapPin className="w-4 h-4 text-gray-400 mr-2" />
                  <Input
                    id="location"
                    name="location"
                    value={formData.location}
                    onChange={handleChange}
                    placeholder="Location or virtual link"
                  />
                </div>
              </div>
            </div>
          </div>
          {/* Date and time section */}
          <div className="space-y-4 mb-6">
            <h3 className="font-medium flex items-center text-gray-700">
              <Calendar className="w-4 h-4 mr-2" />
              Date and Time
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="start_date" className="block text-sm font-medium text-gray-700">
                  Start Date*
                </label>
                <Input
                  id="start_date"
                  type="date"
                  name="start_date"
                  value={formData.start_date}
                  onChange={handleChange}
                  error={errors.start_date}
                />
              </div>
              <div>
                <label htmlFor="start_time" className="block text-sm font-medium text-gray-700">
                  Start Time*
                </label>
                <Input
                  id="start_time"
                  type="time"
                  name="start_time"
                  value={formData.start_time}
                  onChange={handleChange}
                  error={errors.start_time}
                />
              </div>
              <div>
                <label htmlFor="end_date" className="block text-sm font-medium text-gray-700">
                  End Date*
                </label>
                <Input
                  id="end_date"
                  type="date"
                  name="end_date"
                  value={formData.end_date}
                  onChange={handleChange}
                  error={errors.end_date}
                />
              </div>
              <div>
                <label htmlFor="end_time" className="block text-sm font-medium text-gray-700">
                  End Time*
                </label>
                <Input
                  id="end_time"
                  type="time"
                  name="end_time"
                  value={formData.end_time}
                  onChange={handleChange}
                  error={errors.end_time}
                />
              </div>
            </div>
          </div>
          {/* Participants section */}
          <div className="space-y-4 mb-6">
            <h3 className="font-medium flex items-center text-gray-700">
              <Users className="w-4 h-4 mr-2" />
              Participants
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="beneficiary_id" className="block text-sm font-medium text-gray-700">
                  Beneficiary
                </label>
                <select
                  id="beneficiary_id"
                  name="beneficiary_id"
                  value={formData.beneficiary_id}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                >
                  <option value="">Select Beneficiary</option>
                  {/* In a real app, this would be populated from an API */}
                  <option value="1">John Doe</option>
                  <option value="2">Jane Smith</option>
                  <option value="3">Robert Johnson</option>
                </select>
              </div>
              <div>
                <label htmlFor="trainer_id" className="block text-sm font-medium text-gray-700">
                  Trainer
                </label>
                <select
                  id="trainer_id"
                  name="trainer_id"
                  value={formData.trainer_id}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                >
                  <option value="">Select Trainer</option>
                  {/* In a real app, this would be populated from an API */}
                  <option value="1">Sarah Johnson</option>
                  <option value="2">Michael Chen</option>
                  <option value="3">Emily Davis</option>
                </select>
              </div>
            </div>
          </div>
          {/* Additional options */}
          <div className="space-y-4 mb-6">
            <h3 className="font-medium text-gray-700">Additional Options</h3>
            <div className="space-y-3">
              <div className="flex items-center">
                <input
                  id="is_google_synced"
                  name="is_google_synced"
                  type="checkbox"
                  checked={formData.is_google_synced}
                  onChange={handleChange}
                  className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                />
                <label htmlFor="is_google_synced" className="ml-2 block text-sm text-gray-700">
                  Sync with Google Calendar
                </label>
              </div>
              <div className="flex items-center">
                <input
                  id="notify_participants"
                  name="notify_participants"
                  type="checkbox"
                  checked={formData.notify_participants}
                  onChange={handleChange}
                  className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                />
                <label htmlFor="notify_participants" className="ml-2 block text-sm text-gray-700">
                  Send notifications to participants
                </label>
              </div>
            </div>
            <div>
              <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
                Private Notes
              </label>
              <textarea
                id="notes"
                name="notes"
                value={formData.notes}
                onChange={handleChange}
                placeholder="Notes visible only to you"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                rows="2"
              />
            </div>
          </div>
          {/* Status section for existing appointments */}
          {appointment && (
            <div className="mb-6">
              <label htmlFor="status" className="block text-sm font-medium text-gray-700">
                Status
              </label>
              <select
                id="status"
                name="status"
                value={formData.status}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                disabled={formData.status === 'canceled'}
              >
                <option value="confirmed">Confirmed</option>
                <option value="pending">Pending</option>
                <option value="canceled">Canceled</option>
              </select>
            </div>
          )}
          {/* Google Calendar integration info */}
          {appointment && appointment.google_event_id && (
            <div className="bg-blue-50 p-3 rounded-lg flex items-start mb-6">
              <div className="flex-shrink-0 text-blue-500 mt-0.5">
                <Calendar className="w-5 h-5" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-800">Synced with Google Calendar</h3>
                <div className="mt-2 text-sm text-blue-700">
                  <p>This appointment is synced with Google Calendar. Changes made here will be reflected in your Google Calendar.</p>
                  <a
                    href={`https://calendar.google.com/calendar/event?eid=${appointment.google_event_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center mt-1 text-blue-600 hover:text-blue-800"
                  >
                    View in Google Calendar
                    <ExternalLink className="w-3 h-3 ml-1" />
                  </a>
                </div>
              </div>
            </div>
          )}
          {/* Delete confirmation */}
          {showDeleteConfirm && (
            <div className="bg-red-50 p-4 rounded-lg mb-6">
              <div className="flex">
                <div className="flex-shrink-0">
                  <AlertTriangle className="h-5 w-5 text-red-400" />
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Delete Confirmation</h3>
                  <div className="mt-2 text-sm text-red-700">
                    <p>Are you sure you want to delete this appointment? This action cannot be undone.</p>
                  </div>
                  <div className="mt-4">
                    <div className="flex space-x-3">
                      <Button
                        type="button"
                        onClick={() => setShowDeleteConfirm(false)}
                        variant="outline"
                        className="text-sm"
                      >
                        Cancel
                      </Button>
                      <Button
                        type="button"
                        onClick={handleDelete}
                        variant="danger"
                        className="text-sm"
                        disabled={isSubmitting}
                      >
                        {isSubmitting ? 'Deleting...' : 'Yes, Delete'}
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          </form>
        </div>
        <div className="px-6 py-4 border-t border-gray-200">
          <div className="flex justify-between w-full">
          <div>
            {appointment && (
              <>
                {appointment.status !== 'canceled' ? (
                  <AnimatedButton
                    type="button"
                    variant="outline"
                    onClick={handleCancel}
                    className="text-amber-600 border-amber-600 hover:bg-amber-50 mr-2"
                    disabled={isSubmitting}
                  >
                    Cancel Appointment
                  </AnimatedButton>
                ) : null}
                <Button
                  type="button"
                  variant="danger"
                  onClick={() => setShowDeleteConfirm(true)}
                  disabled={isSubmitting}
                  className="flex items-center"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete
                </Button>
              </>
            )}
          </div>
          <div className="flex space-x-2">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isSubmitting}
            >
              <X className="w-4 h-4 mr-2" />
              Cancel
            </Button>
            <Button
              type="button"
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="flex items-center"
            >
              <Save className="w-4 h-4 mr-2" />
              {isSubmitting ? 'Saving...' : appointment ? 'Update' : 'Create'}
            </Button>
          </div>
        </div>
        </div>
      </div>
    </AnimatedModal>
  );
};
export default AppointmentModal;
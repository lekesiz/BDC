import { format, parseISO } from 'date-fns';
import { tr } from 'date-fns/locale';
import { Clock, Calendar, MapPin, Users, User, Tag } from 'lucide-react';

/**
 * AppointmentCard displays an appointment in a card format
 * 
 * @param {Object} props - Component props
 * @param {Object} props.appointment - The appointment data
 * @param {Function} props.onClick - Click handler for the card
 * @returns {JSX.Element} Appointment card component
 */
const AppointmentCard = ({ appointment, onClick }) => {
  // Default colors based on appointment type
  const getTypeColor = (type) => {
    switch (type) {
      case 'session':
        return 'blue';
      case 'evaluation':
        return 'purple';
      case 'meeting':
        return 'green';
      default:
        return 'gray';
    }
  };
  
  const color = appointment.color || getTypeColor(appointment.type);
  
  // Status badge style
  const getStatusStyle = (status) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-amber-100 text-amber-800';
      case 'canceled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  return (
    <div 
      className={`
        p-4 rounded-lg border border-gray-200 hover:border-${color}-500 cursor-pointer 
        transition-colors ${appointment.status === 'canceled' ? 'bg-gray-50' : 'bg-white'}
      `}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-2">
        <h3 className={`font-medium ${appointment.status === 'canceled' ? 'text-gray-500 line-through' : ''}`}>
          {appointment.title}
        </h3>
        
        <div className={`text-xs px-2 py-1 rounded-full ${getStatusStyle(appointment.status)}`}>
          {appointment.status === 'confirmed' ? 'Confirmed' : 
           appointment.status === 'pending' ? 'Pending' : 
           appointment.status === 'canceled' ? 'Canceled' : 'Unknown'}
        </div>
      </div>
      
      <div className="text-sm text-gray-600 mb-3">
        {appointment.description}
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-700">
        <div className="flex items-center">
          <Calendar className="w-4 h-4 text-gray-400 mr-2" />
          <span>{format(parseISO(appointment.start_time), 'EEE, d MMM yyyy', { locale: tr })}</span>
        </div>
        
        <div className="flex items-center">
          <Clock className="w-4 h-4 text-gray-400 mr-2" />
          <span>
            {format(parseISO(appointment.start_time), 'HH:mm')} - 
            {format(parseISO(appointment.end_time), 'HH:mm')}
          </span>
        </div>
        
        {appointment.location && (
          <div className="flex items-center">
            <MapPin className="w-4 h-4 text-gray-400 mr-2" />
            <span>{appointment.location}</span>
          </div>
        )}
        
        {appointment.type && (
          <div className="flex items-center">
            <Tag className="w-4 h-4 text-gray-400 mr-2" />
            <span className="capitalize">{appointment.type}</span>
          </div>
        )}
        
        {appointment.beneficiary && (
          <div className="flex items-center">
            <Users className="w-4 h-4 text-gray-400 mr-2" />
            <span>{appointment.beneficiary.name}</span>
          </div>
        )}
        
        {appointment.trainer && (
          <div className="flex items-center">
            <User className="w-4 h-4 text-gray-400 mr-2" />
            <span>{appointment.trainer.name}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default AppointmentCard;
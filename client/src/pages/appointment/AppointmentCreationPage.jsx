import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Calendar, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import AppointmentModal from '@/components/appointment/AppointmentModal';
/**
 * AppointmentCreationPage for creating new appointments
 */
const AppointmentCreationPage = () => {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(true);
  const [selectedDate] = useState(new Date());
  const handleClose = () => {
    setIsModalOpen(false);
    navigate('/calendar');
  };
  const handleAppointmentCreated = (appointment) => {
    // Appointment was created successfully
    navigate('/calendar', { 
      state: { 
        message: 'Appointment created successfully!',
        appointmentId: appointment.id 
      }
    });
  };
  return (
    <div className="container mx-auto py-8">
      <div className="mb-8">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate('/calendar')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Calendar
        </Button>
        <div className="flex items-center gap-2 mb-6">
          <Calendar className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-bold">Create New Appointment</h1>
        </div>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Plus className="h-5 w-5" />
            Schedule Appointment
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-4">
            Create a new appointment by filling out the form below. You can schedule meetings
            with beneficiaries, team members, or external stakeholders.
          </p>
          <div className="flex justify-center">
            <Button
              onClick={() => setIsModalOpen(true)}
              className="flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              Open Appointment Form
            </Button>
          </div>
        </CardContent>
      </Card>
      {/* Appointment Modal */}
      <AppointmentModal
        isOpen={isModalOpen}
        onClose={handleClose}
        selectedDate={selectedDate}
        appointment={null}
        onAppointmentUpdated={handleAppointmentCreated}
        onAppointmentDeleted={() => {}}
      />
    </div>
  );
};
export default AppointmentCreationPage;
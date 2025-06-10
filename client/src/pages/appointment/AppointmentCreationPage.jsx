// TODO: i18n - processed
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Calendar, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import AppointmentModal from '@/components/appointment/AppointmentModal';
/**
 * AppointmentCreationPage for creating new appointments
 */import { useTranslation } from "react-i18next";
const AppointmentCreationPage = () => {const { t } = useTranslation();
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
          className="mb-4">

          <ArrowLeft className="h-4 w-4 mr-2" />{t("pages.back_to_calendar")}

        </Button>
        <div className="flex items-center gap-2 mb-6">
          <Calendar className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-bold">{t("pages.create_new_appointment")}</h1>
        </div>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Plus className="h-5 w-5" />{t("pages.schedule_appointment")}

          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-4">{t("pages.create_a_new_appointment_by_filling_out_the_form_b")}


          </p>
          <div className="flex justify-center">
            <Button
              onClick={() => setIsModalOpen(true)}
              className="flex items-center gap-2">

              <Plus className="h-4 w-4" />{t("pages.open_appointment_form")}

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
        onAppointmentDeleted={() => {}} />

    </div>);

};
export default AppointmentCreationPage;
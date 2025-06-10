// TODO: i18n - processed
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CalendarCheck, Clock, Users, ChevronRight, Loader } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
/**
 * Displays upcoming sessions for the student
 */import { useTranslation } from "react-i18next";
const UpcomingSessionsWidget = ({ data, isLoading, error }) => {const { t } = useTranslation();
  const navigate = useNavigate();
  // Format date
  const formatDate = (dateString) => {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };
  // Format time
  const formatTime = (dateString) => {
    const options = { hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleTimeString(undefined, options);
  };
  if (isLoading) {
    return (
      <Card className="overflow-hidden h-full">
        <div className="p-6 flex justify-between items-center border-b">
          <h2 className="text-lg font-medium">{t("components.upcoming_sessions")}</h2>
        </div>
        <div className="flex justify-center items-center p-12">
          <Loader className="h-8 w-8 text-primary animate-spin" />
        </div>
      </Card>);

  }
  if (error) {
    return (
      <Card className="overflow-hidden h-full">
        <div className="p-6 flex justify-between items-center border-b">
          <h2 className="text-lg font-medium">{t("components.upcoming_sessions")}</h2>
        </div>
        <div className="p-6 text-center text-red-500">{t("components.failed_to_load_sessions")}

        </div>
      </Card>);

  }
  return (
    <Card className="overflow-hidden h-full">
      <div className="p-6 flex justify-between items-center border-b">
        <h2 className="text-lg font-medium">{t("components.upcoming_sessions")}</h2>
        <Button
          variant="outline"
          size="sm"
          onClick={() => navigate('/portal/calendar')}>{t("archive-components.view_calendar")}


        </Button>
      </div>
      {data && data.length > 0 ?
      <div className="divide-y">
          {data.map((session) =>
        <div key={session.id} className="p-4 hover:bg-gray-50">
              <div className="flex items-start mb-2">
                <div className="p-2 rounded-full bg-blue-50 mr-3">
                  <CalendarCheck className="h-4 w-4 text-blue-500" />
                </div>
                <div>
                  <h4 className="font-medium">{session.title}</h4>
                  <p className="text-sm text-gray-500">{session.type}</p>
                </div>
              </div>
              <div className="ml-10 text-sm space-y-1">
                <div className="flex items-center">
                  <Clock className="h-4 w-4 text-gray-400 mr-2" />
                  <span>
                    {formatDate(session.date)} at {formatTime(session.date)}
                  </span>
                </div>
                {session.trainer &&
            <div className="flex items-center">
                    <Users className="h-4 w-4 text-gray-400 mr-2" />
                    <span>{t("components.with")}{session.trainer}</span>
                  </div>
            }
                <div className="mt-2">
                  <Button
                variant="link"
                size="sm"
                className="p-0 h-auto"
                onClick={() => navigate(`/portal/sessions/${session.id}`)}>{t("components.session_details")}


                <ChevronRight className="h-4 w-4 ml-1" />
                  </Button>
                </div>
              </div>
            </div>
        )}
        </div> :

      <div className="p-8 text-center">
          <CalendarCheck className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">{t("components.no_upcoming_sessions")}</p>
          <Button
          variant="link"
          onClick={() => navigate('/portal/calendar')}
          className="mt-2">{t("archive-components.view_calendar")}


        </Button>
        </div>
      }
    </Card>);

};
export default UpcomingSessionsWidget;
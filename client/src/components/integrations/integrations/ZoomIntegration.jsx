// TODO: i18n - processed
import React, { useState } from 'react';
import BaseIntegration from '../BaseIntegration';
import { Card } from '../../ui/card';
import { Button } from '../../ui/button';
import { Badge } from '../../ui/badge';
import {
  Video,
  Users,
  Calendar,
  Clock,
  Monitor,
  Mic,
  MicOff,
  Settings,
  Link,
  BarChart3,
  Recording } from
'lucide-react';import { useTranslation } from "react-i18next";
const ZoomIntegration = ({ integration, onBack }) => {const { t } = useTranslation();
  const [accountInfo, setAccountInfo] = useState({
    type: 'Pro',
    email: 'admin@bdcacademy.com',
    meetingsHosted: 234,
    totalParticipants: 3456,
    storageUsed: '15.2 GB'
  });
  const [meetingDefaults, setMeetingDefaults] = useState({
    enableWaitingRoom: true,
    muteOnEntry: true,
    requirePassword: true,
    autoRecording: 'cloud',
    allowScreenShare: true,
    enableBreakoutRooms: true
  });
  const [upcomingMeetings, setUpcomingMeetings] = useState([
  { id: '1', topic: 'Python Programming - Session 5', time: '2024-11-18 10:00 AM', duration: 90, participants: 25, status: 'scheduled' },
  { id: '2', topic: 'Web Development Workshop', time: '2024-11-18 2:00 PM', duration: 120, participants: 30, status: 'scheduled' },
  { id: '3', topic: 'Trainer Meeting', time: '2024-11-19 9:00 AM', duration: 60, participants: 8, status: 'scheduled' },
  { id: '4', topic: 'Beneficiary Q&A Session', time: '2024-11-19 3:00 PM', duration: 45, participants: 15, status: 'scheduled' }]
  );
  const configFields = [
  {
    name: 'accountId',
    label: 'Account ID',
    type: 'text',
    placeholder: 'Your Zoom Account ID',
    required: true
  },
  {
    name: 'clientId',
    label: 'Client ID',
    type: 'text',
    placeholder: 'OAuth App Client ID',
    required: true
  },
  {
    name: 'clientSecret',
    label: 'Client Secret',
    type: 'password',
    placeholder: 'OAuth App Client Secret',
    required: true
  },
  {
    name: 'webhookToken',
    label: 'Webhook Verification Token',
    type: 'password',
    placeholder: 'For webhook security',
    required: false
  },
  {
    name: 'defaultMeetingType',
    label: 'Default Meeting Type',
    type: 'select',
    options: [
    { value: 'instant', label: 'Instant Meeting' },
    { value: 'scheduled', label: 'Scheduled Meeting' },
    { value: 'recurring', label: 'Recurring Meeting' },
    { value: 'webinar', label: 'Webinar' }],

    required: true
  }];

  const oauthConfig = {
    authUrl: 'https://zoom.us/oauth/authorize',
    tokenUrl: 'https://zoom.us/oauth/token',
    clientId: process.env.REACT_APP_ZOOM_CLIENT_ID,
    redirectUri: `${window.location.origin}/integrations/zoom/callback`,
    scopes: [
    'meeting:read',
    'meeting:write',
    'user:read',
    'recording:read',
    'webinar:read',
    'webinar:write']

  };
  const webhookEvents = [
  'meeting.started',
  'meeting.ended',
  'meeting.participant_joined',
  'meeting.participant_left',
  'recording.completed',
  'webinar.created'];

  const apiEndpoints = [
  {
    method: 'GET',
    path: '/api/integrations/zoom/meetings',
    description: 'List all meetings'
  },
  {
    method: 'POST',
    path: '/api/integrations/zoom/meetings',
    description: 'Create a new meeting'
  },
  {
    method: 'GET',
    path: '/api/integrations/zoom/recordings',
    description: 'List cloud recordings'
  },
  {
    method: 'POST',
    path: '/api/integrations/zoom/meetings/:id/start',
    description: 'Start a meeting'
  }];

  const customOverview =
  <>
      {/* Account Overview */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                <Video className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold">{t("components.zoom_account")}</h3>
                <p className="text-sm text-gray-500">{accountInfo.email}</p>
              </div>
            </div>
            <Badge variant="success">{accountInfo.type}{t("components.account")}</Badge>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold">{accountInfo.meetingsHosted}</p>
              <p className="text-sm text-gray-600">{t("components.meetings_hosted")}</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold">{accountInfo.totalParticipants.toLocaleString()}</p>
              <p className="text-sm text-gray-600">{t("components.total_participants")}</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold">{accountInfo.storageUsed}</p>
              <p className="text-sm text-gray-600">{t("components.storage_used")}</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold">98.5%</p>
              <p className="text-sm text-gray-600">{t("archive-components.attendance_rate")}</p>
            </div>
          </div>
        </div>
      </Card>
      {/* Upcoming Meetings */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">{t("components.upcoming_meetings")}</h3>
            <Button variant="primary" size="sm">
              <Video className="w-4 h-4 mr-2" />{t("components.schedule_meeting")}

          </Button>
          </div>
          <div className="space-y-3">
            {upcomingMeetings.map((meeting) =>
          <div key={meeting.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-start">
                  <Calendar className="w-5 h-5 text-gray-400 mt-1 mr-3" />
                  <div>
                    <p className="font-medium">{meeting.topic}</p>
                    <div className="flex items-center space-x-4 mt-1">
                      <span className="text-sm text-gray-500 flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        {meeting.time}
                      </span>
                      <span className="text-sm text-gray-500">
                        {meeting.duration} min
                      </span>
                      <span className="text-sm text-gray-500 flex items-center">
                        <Users className="w-3 h-3 mr-1" />
                        {meeting.participants} participants
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Button variant="ghost" size="sm">
                    <Link className="w-4 h-4" />
                  </Button>
                  <Button variant="primary" size="sm">{t("components.start")}

              </Button>
                </div>
              </div>
          )}
          </div>
        </div>
      </Card>
      {/* Meeting Defaults */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">{t("components.meeting_defaults")}</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Users className="w-4 h-4 text-gray-400 mr-3" />
                <div>
                  <p className="font-medium">{t("components.waiting_room")}</p>
                  <p className="text-sm text-gray-500">{t("components.participants_wait_for_host_approval")}</p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                type="checkbox"
                checked={meetingDefaults.enableWaitingRoom}
                onChange={() => setMeetingDefaults({
                  ...meetingDefaults,
                  enableWaitingRoom: !meetingDefaults.enableWaitingRoom
                })}
                className="sr-only peer" />

                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <MicOff className="w-4 h-4 text-gray-400 mr-3" />
                <div>
                  <p className="font-medium">{t("components.mute_on_entry")}</p>
                  <p className="text-sm text-gray-500">{t("components.participants_join_muted")}</p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                type="checkbox"
                checked={meetingDefaults.muteOnEntry}
                onChange={() => setMeetingDefaults({
                  ...meetingDefaults,
                  muteOnEntry: !meetingDefaults.muteOnEntry
                })}
                className="sr-only peer" />

                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Recording className="w-4 h-4 text-gray-400 mr-3" />
                <div>
                  <p className="font-medium">{t("components.auto_recording")}</p>
                  <p className="text-sm text-gray-500">{t("components.automatically_record_meetings")}</p>
                </div>
              </div>
              <select
              value={meetingDefaults.autoRecording}
              onChange={(e) => setMeetingDefaults({
                ...meetingDefaults,
                autoRecording: e.target.value
              })}
              className="form-select rounded-md border-gray-300 text-sm">

                <option value="none">{t("components.disabled")}</option>
                <option value="local">{t("components.local_recording")}</option>
                <option value="cloud">{t("components.cloud_recording")}</option>
              </select>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Monitor className="w-4 h-4 text-gray-400 mr-3" />
                <div>
                  <p className="font-medium">{t("components.screen_sharing")}</p>
                  <p className="text-sm text-gray-500">{t("components.allow_participants_to_share_screen")}</p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                type="checkbox"
                checked={meetingDefaults.allowScreenShare}
                onChange={() => setMeetingDefaults({
                  ...meetingDefaults,
                  allowScreenShare: !meetingDefaults.allowScreenShare
                })}
                className="sr-only peer" />

                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </div>
      </Card>
      {/* Quick Actions */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">{t("archive-components.quick_actions")}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Video className="w-5 h-5 text-blue-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">{t("components.start_instant_meeting")}</p>
                <p className="text-sm text-gray-500">{t("components.begin_a_meeting_right_now")}</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Calendar className="w-5 h-5 text-green-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">{t("components.schedule_meeting")}</p>
                <p className="text-sm text-gray-500">{t("components.plan_a_future_session")}</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Recording className="w-5 h-5 text-red-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">{t("components.view_recordings")}</p>
                <p className="text-sm text-gray-500">{t("components.access_cloud_recordings")}</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <BarChart3 className="w-5 h-5 text-purple-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">{t("components.meeting_analytics")}</p>
                <p className="text-sm text-gray-500">{t("components.view_attendance_reports")}</p>
              </div>
            </button>
          </div>
        </div>
      </Card>
      {/* Recent Meetings */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">{t("components.recent_meetings")}</h3>
          <div className="space-y-3">
            {[
          { topic: 'Data Science Fundamentals', date: '2024-11-17', duration: 75, participants: 28, recording: true },
          { topic: 'Career Counseling Session', date: '2024-11-16', duration: 45, participants: 12, recording: false },
          { topic: 'JavaScript Advanced Topics', date: '2024-11-16', duration: 90, participants: 34, recording: true },
          { topic: 'Monthly Trainer Sync', date: '2024-11-15', duration: 60, participants: 8, recording: true }].
          map((meeting, index) =>
          <div key={index} className="flex items-center justify-between py-3 border-b">
                <div>
                  <p className="font-medium">{meeting.topic}</p>
                  <div className="flex items-center space-x-4 mt-1">
                    <span className="text-sm text-gray-500">{meeting.date}</span>
                    <span className="text-sm text-gray-500">{meeting.duration} min</span>
                    <span className="text-sm text-gray-500">{meeting.participants} participants</span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {meeting.recording &&
              <Badge variant="secondary">
                      <Recording className="w-3 h-3 mr-1" />{t("components.recorded")}

              </Badge>
              }
                  <Button variant="ghost" size="sm">{t("components.view_details")}

              </Button>
                </div>
              </div>
          )}
          </div>
        </div>
      </Card>
    </>;

  return (
    <BaseIntegration
      integration={integration}
      onBack={onBack}
      configFields={configFields}
      oauthConfig={oauthConfig}
      webhookEvents={webhookEvents}
      apiEndpoints={apiEndpoints}>

      {customOverview}
    </BaseIntegration>);

};
export default ZoomIntegration;
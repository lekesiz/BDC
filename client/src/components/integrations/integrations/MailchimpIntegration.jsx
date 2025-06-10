// TODO: i18n - processed
import React, { useState } from 'react';
import BaseIntegration from '../BaseIntegration';
import { Card } from '../../ui/card';
import { Button } from '../../ui/button';
import { Badge } from '../../ui/badge';
import { Progress } from '../../ui/progress';
import {
  Mail,
  Users,
  Send,
  BarChart3,
  Target,
  Clock,
  TrendingUp,
  UserPlus,
  Settings,
  Calendar,
  FileText,
  Eye } from
'lucide-react';import { useTranslation } from "react-i18next";
const MailchimpIntegration = ({ integration, onBack }) => {const { t } = useTranslation();
  const [accountInfo, setAccountInfo] = useState({
    accountName: 'BDC Academy',
    email: 'marketing@bdcacademy.com',
    plan: 'Standard',
    contacts: 12456,
    monthlyEmails: 45000,
    emailLimit: 100000
  });
  const [lists, setLists] = useState([
  { id: '1', name: 'All Beneficiaries', subscribers: 5678, growth: '+12%', lastCampaign: '3 days ago' },
  { id: '2', name: 'Active Students', subscribers: 3245, growth: '+8%', lastCampaign: '1 week ago' },
  { id: '3', name: 'Alumni Network', subscribers: 2345, growth: '+5%', lastCampaign: '2 weeks ago' },
  { id: '4', name: 'Newsletter Subscribers', subscribers: 1188, growth: '+15%', lastCampaign: '5 days ago' }]
  );
  const [campaigns, setCampaigns] = useState([
  { id: '1', name: 'November Course Updates', status: 'sent', recipients: 4567, opens: '68%', clicks: '23%', date: '2024-11-15' },
  { id: '2', name: 'New Python Program Launch', status: 'scheduled', recipients: 3245, date: '2024-11-20' },
  { id: '3', name: 'Alumni Success Stories', status: 'draft', recipients: 2345 },
  { id: '4', name: 'End of Year Summary', status: 'sent', recipients: 5678, opens: '72%', clicks: '31%', date: '2024-11-10' }]
  );
  const [automations, setAutomations] = useState([
  { id: '1', name: 'Welcome Series', status: 'active', triggered: 234, inProgress: 45 },
  { id: '2', name: 'Course Completion', status: 'active', triggered: 156, inProgress: 23 },
  { id: '3', name: 'Re-engagement Campaign', status: 'paused', triggered: 89, inProgress: 0 },
  { id: '4', name: 'Birthday Wishes', status: 'active', triggered: 567, inProgress: 12 }]
  );
  const configFields = [
  {
    name: 'apiKey',
    label: 'API Key',
    type: 'password',
    placeholder: 'Your Mailchimp API key',
    required: true,
    description: 'Found in Account Settings > Extras > API keys'
  },
  {
    name: 'dataCenter',
    label: 'Data Center',
    type: 'text',
    placeholder: 'us1',
    required: true,
    description: 'The data center for your account (e.g., us1, us2)'
  },
  {
    name: 'defaultListId',
    label: 'Default List',
    type: 'select',
    options: lists.map((list) => ({ value: list.id, label: list.name })),
    required: true
  },
  {
    name: 'syncContacts',
    label: 'Sync contacts automatically',
    type: 'checkbox',
    description: 'Keep Mailchimp lists updated with BDC contacts'
  },
  {
    name: 'trackEngagement',
    label: 'Track email engagement',
    type: 'checkbox',
    description: 'Import open and click data back to BDC'
  }];

  const webhookEvents = [
  'subscribe',
  'unsubscribe',
  'profile_update',
  'email_opened',
  'email_clicked',
  'campaign_sent'];

  const apiEndpoints = [
  {
    method: 'GET',
    path: '/api/integrations/mailchimp/lists',
    description: 'Get all email lists'
  },
  {
    method: 'POST',
    path: '/api/integrations/mailchimp/subscribers',
    description: 'Add or update a subscriber'
  },
  {
    method: 'POST',
    path: '/api/integrations/mailchimp/campaigns',
    description: 'Create a new campaign'
  },
  {
    method: 'GET',
    path: '/api/integrations/mailchimp/reports',
    description: 'Get campaign reports'
  }];

  const emailUsagePercentage = accountInfo.monthlyEmails / accountInfo.emailLimit * 100;
  const customOverview =
  <>
      {/* Account Overview */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mr-4">
                <Mail className="w-6 h-6 text-yellow-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold">{accountInfo.accountName}</h3>
                <p className="text-sm text-gray-500">{accountInfo.plan}{t("components.plan_")}{accountInfo.email}</p>
              </div>
            </div>
            <Badge variant="success">{t("components.connected")}</Badge>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <Users className="w-5 h-5 mx-auto mb-2 text-gray-600" />
              <p className="text-2xl font-bold">{accountInfo.contacts.toLocaleString()}</p>
              <p className="text-sm text-gray-600">{t("components.total_contacts")}</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <Send className="w-5 h-5 mx-auto mb-2 text-gray-600" />
              <p className="text-2xl font-bold">{accountInfo.monthlyEmails.toLocaleString()}</p>
              <p className="text-sm text-gray-600">{t("components.emails_this_month")}</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <TrendingUp className="w-5 h-5 mx-auto mb-2 text-gray-600" />
              <p className="text-2xl font-bold">71.2%</p>
              <p className="text-sm text-gray-600">{t("components.avg_open_rate")}</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <Target className="w-5 h-5 mx-auto mb-2 text-gray-600" />
              <p className="text-2xl font-bold">28.5%</p>
              <p className="text-sm text-gray-600">{t("components.avg_click_rate")}</p>
            </div>
          </div>
          <div className="mt-4">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-600">{t("components.monthly_email_usage")}</span>
              <span className="text-gray-600">
                {accountInfo.monthlyEmails.toLocaleString()} / {accountInfo.emailLimit.toLocaleString()}
              </span>
            </div>
            <Progress value={emailUsagePercentage} className="h-2" />
          </div>
        </div>
      </Card>
      {/* Email Lists */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">{t("components.email_lists")}</h3>
            <Button variant="primary" size="sm">
              <UserPlus className="w-4 h-4 mr-2" />{t("components.create_list")}

          </Button>
          </div>
          <div className="space-y-3">
            {lists.map((list) =>
          <div key={list.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center">
                  <Users className="w-5 h-5 text-yellow-500 mr-3" />
                  <div>
                    <p className="font-medium">{list.name}</p>
                    <p className="text-sm text-gray-500">
                      {list.subscribers.toLocaleString()}{t("components.subscribers_")}{list.growth}{t("components.this_month")}
                </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">{t("components.last_campaign")}
                {list.lastCampaign}
                  </span>
                  <Button variant="ghost" size="sm">{t("components.manage")}

              </Button>
                </div>
              </div>
          )}
          </div>
        </div>
      </Card>
      {/* Recent Campaigns */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">{t("components.recent_campaigns")}</h3>
            <Button variant="primary" size="sm">
              <Mail className="w-4 h-4 mr-2" />{t("components.create_campaign")}

          </Button>
          </div>
          <div className="space-y-3">
            {campaigns.map((campaign) =>
          <div key={campaign.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <p className="font-medium">{campaign.name}</p>
                  <div className="flex items-center space-x-4 mt-1">
                    <span className="text-sm text-gray-500">
                      {campaign.recipients?.toLocaleString()} recipients
                    </span>
                    {campaign.status === 'sent' &&
                <>
                        <span className="text-sm text-gray-500">
                          Opens: {campaign.opens}
                        </span>
                        <span className="text-sm text-gray-500">
                          Clicks: {campaign.clicks}
                        </span>
                      </>
                }
                    {campaign.date &&
                <span className="text-sm text-gray-500">
                        {campaign.status === 'scheduled' ? 'Scheduled for' : 'Sent on'} {campaign.date}
                      </span>
                }
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant={
              campaign.status === 'sent' ? 'success' :
              campaign.status === 'scheduled' ? 'warning' :
              'secondary'
              }>
                    {campaign.status}
                  </Badge>
                  <Button variant="ghost" size="sm">
                    <Eye className="w-4 h-4" />
                  </Button>
                </div>
              </div>
          )}
          </div>
        </div>
      </Card>
      {/* Automations */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">{t("components.email_automations")}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {automations.map((automation) =>
          <div key={automation.id} className="p-4 border rounded-lg">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="font-medium">{automation.name}</p>
                    <p className="text-sm text-gray-500">
                      {automation.triggered}{t("components.triggered_")}{automation.inProgress}{t("components.in_progress")}
                </p>
                  </div>
                  <Badge variant={automation.status === 'active' ? 'success' : 'secondary'}>
                    {automation.status}
                  </Badge>
                </div>
                <div className="flex space-x-2">
                  <Button variant="ghost" size="sm">
                    <BarChart3 className="w-4 h-4 mr-1" />{t("components.stats")}

              </Button>
                  <Button variant="ghost" size="sm">
                    <Settings className="w-4 h-4 mr-1" />{t("components.configure")}

              </Button>
                </div>
              </div>
          )}
          </div>
        </div>
      </Card>
      {/* Quick Actions */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">{t("archive-components.quick_actions")}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Send className="w-5 h-5 text-yellow-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">{t("components.send_campaign")}</p>
                <p className="text-sm text-gray-500">{t("components.create_and_send_an_email")}</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <UserPlus className="w-5 h-5 text-blue-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">{t("components.import_contacts")}</p>
                <p className="text-sm text-gray-500">{t("components.add_beneficiaries_to_lists")}</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <FileText className="w-5 h-5 text-green-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">{t("components.email_templates")}</p>
                <p className="text-sm text-gray-500">{t("components.manage_email_designs")}</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <BarChart3 className="w-5 h-5 text-purple-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">{t("components.analytics")}</p>
                <p className="text-sm text-gray-500">{t("components.view_detailed_reports")}</p>
              </div>
            </button>
          </div>
        </div>
      </Card>
    </>;

  return (
    <BaseIntegration
      integration={integration}
      onBack={onBack}
      configFields={configFields}
      webhookEvents={webhookEvents}
      apiEndpoints={apiEndpoints}>

      {customOverview}
    </BaseIntegration>);

};
export default MailchimpIntegration;
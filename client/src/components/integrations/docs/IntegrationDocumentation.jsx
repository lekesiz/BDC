import React, { useState } from 'react';
import { Card } from '../../ui/card';
import { Button } from '../../ui/button';
import { Badge } from '../../ui/badge';
import { Tabs } from '../../ui/tabs';
import {
  Book,
  Code,
  FileText,
  Copy,
  ExternalLink,
  ChevronRight,
  Terminal,
  Settings,
  AlertCircle,
  CheckCircle
} from 'lucide-react';

const IntegrationDocumentation = ({ integrationId }) => {
  const [activeTab, setActiveTab] = useState('quickstart');
  const [copiedCode, setCopiedCode] = useState(null);

  const handleCopyCode = (id) => {
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const documentation = {
    'google-calendar': {
      quickstart: {
        title: 'Google Calendar Quick Start',
        steps: [
          {
            title: 'Create Google Cloud Project',
            description: 'Set up a new project in Google Cloud Console',
            substeps: [
              'Go to Google Cloud Console',
              'Create a new project or select existing',
              'Enable Google Calendar API',
              'Create OAuth 2.0 credentials'
            ]
          },
          {
            title: 'Configure OAuth',
            description: 'Set up authentication for your application',
            substeps: [
              'Add authorized redirect URIs',
              'Download client configuration',
              'Set up consent screen',
              'Add required scopes'
            ]
          },
          {
            title: 'Connect in BDC',
            description: 'Complete the integration setup',
            substeps: [
              'Enter Client ID and Secret',
              'Select calendars to sync',
              'Configure sync settings',
              'Test the connection'
            ]
          }
        ],
        codeExamples: [
          {
            id: 'webhook-endpoint',
            title: 'Webhook Endpoint Example',
            language: 'javascript',
            code: `// Express.js webhook endpoint
app.post('/webhooks/google-calendar', async (req, res) => {
  const { event, data } = req.body;
  
  // Verify webhook signature
  if (!verifySignature(req)) {
    return res.status(401).send('Unauthorized');
  }
  
  // Handle different event types
  switch (event) {
    case 'calendar.event.created':
      await handleEventCreated(data);
      break;
    case 'calendar.event.updated':
      await handleEventUpdated(data);
      break;
    case 'calendar.event.deleted':
      await handleEventDeleted(data);
      break;
  }
  
  res.status(200).send('OK');
});`
          }
        ]
      },
      api: {
        endpoints: [
          {
            method: 'GET',
            path: '/api/integrations/google-calendar/calendars',
            description: 'List all available calendars',
            response: `{
  "calendars": [
    {
      "id": "primary",
      "name": "Primary Calendar",
      "color": "#4285F4",
      "selected": true
    }
  ]
}`
          },
          {
            method: 'POST',
            path: '/api/integrations/google-calendar/events',
            description: 'Create a new calendar event',
            request: `{
  "summary": "Team Meeting",
  "start": "2024-11-20T10:00:00Z",
  "end": "2024-11-20T11:00:00Z",
  "attendees": ["user@example.com"],
  "meetingLink": true
}`
          }
        ]
      },
      troubleshooting: [
        {
          issue: 'Authentication Failed',
          solution: 'Ensure your OAuth credentials are correct and the redirect URI matches exactly'
        },
        {
          issue: 'Calendar Not Syncing',
          solution: 'Check that the calendar is selected for sync and you have the necessary permissions'
        },
        {
          issue: 'Rate Limit Errors',
          solution: 'Google Calendar API has quotas. Implement exponential backoff for retries'
        }
      ]
    },
    'slack': {
      quickstart: {
        title: 'Slack Integration Quick Start',
        steps: [
          {
            title: 'Create Slack App',
            description: 'Set up a new app in Slack',
            substeps: [
              'Go to api.slack.com',
              'Create a new app',
              'Choose workspace',
              'Add bot user'
            ]
          },
          {
            title: 'Configure Permissions',
            description: 'Set up OAuth scopes',
            substeps: [
              'Add required bot token scopes',
              'Install app to workspace',
              'Copy bot token',
              'Set up event subscriptions'
            ]
          },
          {
            title: 'Connect in BDC',
            description: 'Complete the integration',
            substeps: [
              'Enter bot token',
              'Select channels',
              'Configure notifications',
              'Test message sending'
            ]
          }
        ],
        codeExamples: [
          {
            id: 'send-message',
            title: 'Send Slack Message',
            language: 'javascript',
            code: `const { WebClient } = require('@slack/web-api');

const slack = new WebClient(process.env.SLACK_BOT_TOKEN);

async function sendNotification(channel, message) {
  try {
    const result = await slack.chat.postMessage({
      channel: channel,
      text: message,
      blocks: [
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: message
          }
        }
      ]
    });
    
    return result;
  } catch (error) {
    console.error('Failed to send Slack message:', error);
    throw error;
  }
}`
          }
        ]
      },
      api: {
        endpoints: [
          {
            method: 'POST',
            path: '/api/integrations/slack/messages',
            description: 'Send a message to Slack',
            request: `{
  "channel": "#general",
  "text": "New course enrollment!",
  "attachments": [{
    "color": "good",
    "fields": [{
      "title": "Student",
      "value": "John Doe"
    }]
  }]
}`
          }
        ]
      },
      troubleshooting: [
        {
          issue: 'Bot not responding',
          solution: 'Ensure the bot is added to the channels and has proper permissions'
        },
        {
          issue: 'Rate limiting',
          solution: 'Slack has rate limits. Implement queuing for bulk messages'
        }
      ]
    },
    'stripe': {
      quickstart: {
        title: 'Stripe Payment Integration',
        steps: [
          {
            title: 'Set up Stripe Account',
            description: 'Create and configure your Stripe account',
            substeps: [
              'Sign up at stripe.com',
              'Complete business verification',
              'Set up payment methods',
              'Configure webhook endpoints'
            ]
          },
          {
            title: 'Get API Keys',
            description: 'Retrieve your integration credentials',
            substeps: [
              'Access Stripe Dashboard',
              'Navigate to Developers > API keys',
              'Copy publishable and secret keys',
              'Set up webhook signing secret'
            ]
          },
          {
            title: 'Configure in BDC',
            description: 'Complete payment setup',
            substeps: [
              'Enter API keys',
              'Configure payment methods',
              'Set up products and prices',
              'Test payment flow'
            ]
          }
        ],
        codeExamples: [
          {
            id: 'create-payment',
            title: 'Create Payment Intent',
            language: 'javascript',
            code: `const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

async function createPayment(amount, currency = 'eur') {
  try {
    const paymentIntent = await stripe.paymentIntents.create({
      amount: amount * 100, // Convert to cents
      currency: currency,
      payment_method_types: ['card'],
      metadata: {
        order_id: '12345',
        customer_email: 'customer@example.com'
      }
    });
    
    return {
      clientSecret: paymentIntent.client_secret,
      paymentIntentId: paymentIntent.id
    };
  } catch (error) {
    console.error('Payment creation failed:', error);
    throw error;
  }
}`
          },
          {
            id: 'webhook-handler',
            title: 'Webhook Handler',
            language: 'javascript',
            code: `app.post('/webhooks/stripe', express.raw({type: 'application/json'}), (req, res) => {
  const sig = req.headers['stripe-signature'];
  
  let event;
  try {
    event = stripe.webhooks.constructEvent(
      req.body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    return res.status(400).send(\`Webhook Error: \${err.message}\`);
  }
  
  // Handle the event
  switch (event.type) {
    case 'payment_intent.succeeded':
      console.log('Payment succeeded:', event.data.object);
      break;
    case 'payment_intent.failed':
      console.log('Payment failed:', event.data.object);
      break;
    default:
      console.log(\`Unhandled event type \${event.type}\`);
  }
  
  res.send();
});`
          }
        ]
      },
      api: {
        endpoints: [
          {
            method: 'POST',
            path: '/api/integrations/stripe/create-payment-intent',
            description: 'Create a payment intent for checkout',
            request: `{
  "amount": 299,
  "currency": "eur",
  "description": "Python Programming Course"
}`
          }
        ]
      },
      troubleshooting: [
        {
          issue: 'Payment declining',
          solution: 'Check Stripe Radar settings and ensure test mode is disabled for production'
        },
        {
          issue: 'Webhook not receiving events',
          solution: 'Verify webhook endpoint URL and signing secret are correct'
        }
      ]
    }
  };

  const currentDocs = documentation[integrationId] || documentation['google-calendar'];

  const tabs = [
    { id: 'quickstart', label: 'Quick Start', icon: Book },
    { id: 'api', label: 'API Reference', icon: Code },
    { id: 'troubleshooting', label: 'Troubleshooting', icon: AlertCircle }
  ];

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="bg-white border-b">
        <nav className="flex space-x-8 px-6" aria-label="Tabs">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center py-4 px-1 border-b-2 font-medium text-sm
                  ${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <Icon className="w-4 h-4 mr-2" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Quick Start */}
      {activeTab === 'quickstart' && currentDocs.quickstart && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4">{currentDocs.quickstart.title}</h2>
              <div className="space-y-6">
                {currentDocs.quickstart.steps.map((step, index) => (
                  <div key={index}>
                    <div className="flex items-start">
                      <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-semibold">
                        {index + 1}
                      </div>
                      <div className="ml-4 flex-1">
                        <h3 className="font-semibold">{step.title}</h3>
                        <p className="text-gray-600 text-sm mt-1">{step.description}</p>
                        <ul className="mt-2 space-y-1">
                          {step.substeps.map((substep, i) => (
                            <li key={i} className="flex items-center text-sm text-gray-600">
                              <ChevronRight className="w-4 h-4 mr-1 text-gray-400" />
                              {substep}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          {currentDocs.quickstart.codeExamples && (
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">Code Examples</h3>
                <div className="space-y-4">
                  {currentDocs.quickstart.codeExamples.map((example) => (
                    <div key={example.id}>
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">{example.title}</h4>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            navigator.clipboard.writeText(example.code);
                            handleCopyCode(example.id);
                          }}
                        >
                          {copiedCode === example.id ? (
                            <>
                              <CheckCircle className="w-4 h-4 mr-1 text-green-500" />
                              Copied
                            </>
                          ) : (
                            <>
                              <Copy className="w-4 h-4 mr-1" />
                              Copy
                            </>
                          )}
                        </Button>
                      </div>
                      <div className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
                        <pre className="text-sm">
                          <code>{example.code}</code>
                        </pre>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          )}
        </div>
      )}

      {/* API Reference */}
      {activeTab === 'api' && currentDocs.api && (
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-4">API Reference</h2>
            <div className="space-y-6">
              {currentDocs.api.endpoints.map((endpoint, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <Badge variant={
                      endpoint.method === 'GET' ? 'info' :
                      endpoint.method === 'POST' ? 'success' :
                      endpoint.method === 'PUT' ? 'warning' :
                      'danger'
                    }>
                      {endpoint.method}
                    </Badge>
                    <code className="font-mono text-sm">{endpoint.path}</code>
                  </div>
                  <p className="text-gray-600 mb-4">{endpoint.description}</p>
                  
                  {endpoint.request && (
                    <div>
                      <p className="font-medium text-sm mb-2">Request Body:</p>
                      <div className="bg-gray-100 p-3 rounded">
                        <pre className="text-sm">{endpoint.request}</pre>
                      </div>
                    </div>
                  )}
                  
                  {endpoint.response && (
                    <div className="mt-4">
                      <p className="font-medium text-sm mb-2">Response:</p>
                      <div className="bg-gray-100 p-3 rounded">
                        <pre className="text-sm">{endpoint.response}</pre>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* Troubleshooting */}
      {activeTab === 'troubleshooting' && currentDocs.troubleshooting && (
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-4">Common Issues & Solutions</h2>
            <div className="space-y-4">
              {currentDocs.troubleshooting.map((item, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-start">
                    <AlertCircle className="w-5 h-5 text-orange-500 mt-0.5 mr-3" />
                    <div className="flex-1">
                      <h4 className="font-medium">{item.issue}</h4>
                      <p className="text-gray-600 text-sm mt-1">{item.solution}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* External Links */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Additional Resources</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <a
              href="#"
              className="flex items-center p-3 border rounded-lg hover:bg-gray-50"
            >
              <FileText className="w-5 h-5 text-gray-400 mr-3" />
              <div>
                <p className="font-medium">Official Documentation</p>
                <p className="text-sm text-gray-500">View provider's docs</p>
              </div>
              <ExternalLink className="w-4 h-4 ml-auto text-gray-400" />
            </a>
            <a
              href="#"
              className="flex items-center p-3 border rounded-lg hover:bg-gray-50"
            >
              <Terminal className="w-5 h-5 text-gray-400 mr-3" />
              <div>
                <p className="font-medium">API Playground</p>
                <p className="text-sm text-gray-500">Test endpoints</p>
              </div>
              <ExternalLink className="w-4 h-4 ml-auto text-gray-400" />
            </a>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default IntegrationDocumentation;
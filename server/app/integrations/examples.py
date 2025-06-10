"""
Examples and usage patterns for BDC integrations.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List

from .config import IntegrationManager
from .registry import integration_registry
from .calendar import GoogleCalendarIntegration, CalendarEventInput
from .payments import StripeIntegration, PaymentIntent
from .video import ZoomIntegration, VideoMeetingInput, MeetingType
from .email import SendGridIntegration, EmailMessage


class IntegrationExamples:
    """Example usage patterns for integrations."""
    
    def __init__(self):
        self.manager = IntegrationManager()
    
    async def calendar_example(self):
        """Example of using calendar integration."""
        print("=== Calendar Integration Example ===")
        
        # Get Google Calendar integration
        config = self.manager.get_config('google_calendar')
        if not config:
            print("Google Calendar not configured")
            return
        
        calendar_integration = GoogleCalendarIntegration(config)
        
        try:
            # Connect to Google Calendar
            await calendar_integration.connect()
            
            # Get list of calendars
            calendars = await calendar_integration.get_calendars()
            print(f"Found {len(calendars)} calendars")
            
            # Get primary calendar
            primary_calendar = await calendar_integration.get_primary_calendar()
            if primary_calendar:
                print(f"Primary calendar: {primary_calendar.name}")
                
                # Create a meeting event
                meeting_data = CalendarEventInput(
                    title="BDC Team Meeting",
                    start_time=datetime.now() + timedelta(hours=1),
                    end_time=datetime.now() + timedelta(hours=2),
                    description="Weekly team sync meeting",
                    attendees=["team@bdc.com", "manager@bdc.com"]
                )
                
                event = await calendar_integration.create_event(
                    primary_calendar.id, 
                    meeting_data
                )
                print(f"Created event: {event.title} (ID: {event.id})")
                
                # Get availability for next week
                next_week = datetime.now() + timedelta(days=7)
                week_end = next_week + timedelta(days=7)
                
                availability = await calendar_integration.get_availability(
                    primary_calendar.id,
                    next_week,
                    week_end,
                    duration_minutes=60
                )
                print(f"Found {len(availability)} available slots next week")
        
        except Exception as e:
            print(f"Calendar example failed: {e}")
        finally:
            await calendar_integration.disconnect()
    
    async def payment_example(self):
        """Example of using payment integration."""
        print("=== Payment Integration Example ===")
        
        # Get Stripe integration
        config = self.manager.get_config('stripe')
        if not config:
            print("Stripe not configured")
            return
        
        payment_integration = StripeIntegration(config)
        
        try:
            # Connect to Stripe
            await payment_integration.connect()
            
            # Create a customer
            customer = await payment_integration.create_customer(
                email="customer@example.com",
                name="John Doe",
                description="BDC customer"
            )
            print(f"Created customer: {customer.name} (ID: {customer.id})")
            
            # Create a payment intent
            from decimal import Decimal
            payment_intent = await payment_integration.create_payment_intent(
                amount=Decimal('29.99'),
                currency='usd',
                customer_id=customer.id,
                description="BDC Service Payment"
            )
            print(f"Created payment intent: {payment_intent.id} for ${payment_intent.amount}")
            
            # Get payment methods for customer
            payment_methods = await payment_integration.list_payment_methods(customer.id)
            print(f"Customer has {len(payment_methods)} payment methods")
            
            # Get transaction history
            transactions = await payment_integration.list_transactions(
                customer_id=customer.id,
                limit=10
            )
            print(f"Found {len(transactions)} transactions for customer")
        
        except Exception as e:
            print(f"Payment example failed: {e}")
        finally:
            await payment_integration.disconnect()
    
    async def video_example(self):
        """Example of using video conferencing integration."""
        print("=== Video Integration Example ===")
        
        # Get Zoom integration
        config = self.manager.get_config('zoom')
        if not config:
            print("Zoom not configured")
            return
        
        video_integration = ZoomIntegration(config)
        
        try:
            # Connect to Zoom
            await video_integration.connect()
            
            # Create a scheduled meeting
            meeting_data = VideoMeetingInput(
                topic="BDC Client Consultation",
                start_time=datetime.now() + timedelta(days=1),
                duration=60,
                participants=["client@example.com", "consultant@bdc.com"],
                waiting_room=True,
                auto_recording="cloud"
            )
            
            meeting = await video_integration.create_meeting(meeting_data)
            print(f"Created meeting: {meeting.topic} (ID: {meeting.id})")
            print(f"Join URL: {meeting.join_url}")
            
            # Create an instant meeting
            instant_meeting = await video_integration.create_instant_meeting(
                "Quick Team Sync",
                "team@bdc.com"
            )
            print(f"Created instant meeting: {instant_meeting.topic}")
            
            # List upcoming meetings
            upcoming_meetings = await video_integration.list_meetings(
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(days=30)
            )
            print(f"Found {len(upcoming_meetings)} upcoming meetings")
            
            # Schedule recurring meeting
            recurrence = {
                "type": "weekly",
                "repeat_interval": 1,
                "weekly_days": ["monday"],
                "end_times": 10
            }
            
            recurring_meeting = await video_integration.schedule_recurring_meeting(
                "Weekly Team Meeting",
                datetime.now() + timedelta(days=7),
                60,
                recurrence,
                ["team@bdc.com"]
            )
            print(f"Created recurring meeting: {recurring_meeting.topic}")
        
        except Exception as e:
            print(f"Video example failed: {e}")
        finally:
            await video_integration.disconnect()
    
    async def email_example(self):
        """Example of using email integration."""
        print("=== Email Integration Example ===")
        
        # Get SendGrid integration
        config = self.manager.get_config('sendgrid')
        if not config:
            print("SendGrid not configured")
            return
        
        email_integration = SendGridIntegration(config)
        
        try:
            # Connect to SendGrid
            await email_integration.connect()
            
            # Send a welcome email
            message_id = await email_integration.send_welcome_email(
                "newuser@example.com",
                "Jane Smith",
                "https://bdc.com/login"
            )
            print(f"Sent welcome email (ID: {message_id})")
            
            # Send a notification email
            notification_id = await email_integration.send_notification_email(
                ["admin@bdc.com", "manager@bdc.com"],
                "New User Registration",
                "A new user has registered: Jane Smith (newuser@example.com)"
            )
            print(f"Sent notification email (ID: {notification_id})")
            
            # Create an email template
            from .email.base_email import EmailTemplate
            template = EmailTemplate(
                id="",
                name="appointment_reminder",
                subject="Appointment Reminder - {{appointment_date}}",
                html_content="""
                <h2>Appointment Reminder</h2>
                <p>Hello {{client_name}},</p>
                <p>This is a reminder about your upcoming appointment:</p>
                <ul>
                    <li>Date: {{appointment_date}}</li>
                    <li>Time: {{appointment_time}}</li>
                    <li>Service: {{service_name}}</li>
                </ul>
                <p>Please confirm your attendance.</p>
                """,
                text_content="""
                Appointment Reminder
                
                Hello {{client_name}},
                
                This is a reminder about your upcoming appointment:
                - Date: {{appointment_date}}
                - Time: {{appointment_time}}
                - Service: {{service_name}}
                
                Please confirm your attendance.
                """
            )
            
            template_id = await email_integration.create_template(template)
            print(f"Created email template (ID: {template_id})")
            
            # Send email using template
            template_email_id = await email_integration.send_template_email(
                template_id,
                ["client@example.com"],
                {
                    "client_name": "John Doe",
                    "appointment_date": "2024-01-15",
                    "appointment_time": "2:00 PM",
                    "service_name": "Consultation"
                }
            )
            print(f"Sent template email (ID: {template_email_id})")
            
            # Get email statistics
            stats = await email_integration.get_email_stats()
            print(f"Email stats - Sent: {stats.sent}, Delivered: {stats.delivered}, Opened: {stats.opened}")
        
        except Exception as e:
            print(f"Email example failed: {e}")
        finally:
            await email_integration.disconnect()
    
    async def integration_registry_example(self):
        """Example of using integration registry."""
        print("=== Integration Registry Example ===")
        
        # List all registered integration classes
        registered_classes = integration_registry.list_integration_classes()
        print(f"Registered integration classes: {registered_classes}")
        
        # Get integration info
        info = integration_registry.get_integration_info()
        print(f"Registry info: {info}")
        
        # Create integration instances for available configs
        created_instances = []
        
        for config_name in self.manager.list_enabled_configs():
            config = self.manager.get_config(config_name)
            if config:
                try:
                    # Try to create integration instance
                    instance = integration_registry.create_integration(config_name, config)
                    created_instances.append(config_name)
                    print(f"Created {config_name} integration instance")
                except Exception as e:
                    print(f"Failed to create {config_name}: {e}")
        
        print(f"Successfully created {len(created_instances)} integration instances")
        
        # Get integrations by type
        calendar_integrations = integration_registry.get_integrations_by_type("calendar")
        payment_integrations = integration_registry.get_integrations_by_type("payment")
        video_integrations = integration_registry.get_integrations_by_type("video")
        email_integrations = integration_registry.get_integrations_by_type("email")
        
        print(f"Calendar integrations: {len(calendar_integrations)}")
        print(f"Payment integrations: {len(payment_integrations)}")
        print(f"Video integrations: {len(video_integrations)}")
        print(f"Email integrations: {len(email_integrations)}")
    
    async def webhook_example(self):
        """Example of handling webhooks."""
        print("=== Webhook Handling Example ===")
        
        # Example Stripe webhook payload
        stripe_payload = {
            "id": "evt_test_webhook",
            "object": "event",
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_test_payment",
                    "amount": 2999,
                    "currency": "usd",
                    "status": "succeeded"
                }
            }
        }
        
        config = self.manager.get_config('stripe')
        if config:
            stripe_integration = StripeIntegration(config)
            webhook_result = await stripe_integration.handle_webhook(stripe_payload)
            print(f"Stripe webhook processed: {webhook_result}")
        
        # Example SendGrid webhook payload
        sendgrid_payload = [
            {
                "email": "test@example.com",
                "event": "delivered",
                "timestamp": 1640995200,
                "sg_message_id": "msg_test_123"
            }
        ]
        
        config = self.manager.get_config('sendgrid')
        if config:
            sendgrid_integration = SendGridIntegration(config)
            events = await sendgrid_integration.process_webhook_event(sendgrid_payload)
            print(f"SendGrid webhook processed {len(events)} events")
    
    async def run_all_examples(self):
        """Run all integration examples."""
        print("Running BDC Integrations Examples")
        print("=" * 50)
        
        await self.integration_registry_example()
        await self.calendar_example()
        await self.payment_example()
        await self.video_example()
        await self.email_example()
        await self.webhook_example()
        
        print("=" * 50)
        print("Examples completed!")


async def main():
    """Main function to run examples."""
    examples = IntegrationExamples()
    await examples.run_all_examples()


if __name__ == "__main__":
    asyncio.run(main())
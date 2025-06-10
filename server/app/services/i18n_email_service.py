"""
Email service with i18n support
Sends localized emails based on recipient's language preference
"""

from flask import render_template, current_app
from flask_mail import Message
from app.extensions import mail
from app.i18n import translate, get_user_language, SUPPORTED_LANGUAGES
from app.models import User
from threading import Thread
import os


class I18nEmailService:
    """Service for sending internationalized emails"""
    
    @staticmethod
    def send_async_email(app, msg):
        """Send email asynchronously"""
        with app.app_context():
            mail.send(msg)
    
    @staticmethod
    def send_email(to, subject, template, attachments=None, **kwargs):
        """
        Send an email with i18n support
        
        Args:
            to: Email recipient (can be email string or User object)
            subject: Email subject (will be translated)
            template: Email template name (without extension)
            attachments: List of attachments
            **kwargs: Additional context for template
        """
        app = current_app._get_current_object()
        
        # Determine recipient language
        if isinstance(to, User):
            recipient_email = to.email
            recipient_name = f"{to.first_name} {to.last_name}"
            language = to.language or 'en'
        else:
            recipient_email = to
            recipient_name = kwargs.get('recipient_name', '')
            language = kwargs.get('language', 'en')
        
        # Ensure language is supported
        if language not in SUPPORTED_LANGUAGES:
            language = 'en'
        
        # Set language context for translation
        with app.test_request_context():
            # Get language direction
            direction = 'rtl' if language in ['ar', 'he'] else 'ltr'
            
            # Common email context
            common_context = {
                'lang': language,
                'direction': direction,
                'recipient_name': recipient_name,
                'support_url': app.config.get('SUPPORT_URL', '#'),
                'unsubscribe_url': kwargs.get('unsubscribe_url'),
                
                # Footer translations
                'footer_regards': translate('email.footer.regards'),
                'footer_team': translate('email.footer.team'),
                'footer_unsubscribe': translate('email.footer.unsubscribe'),
                'footer_help': translate('email.footer.help'),
                'footer_copyright': translate('email.footer.copyright')
            }
            
            # Merge with provided context
            context = {**common_context, **kwargs}
            
            # Translate subject if it's a translation key
            if subject.startswith('email.subject.'):
                translated_subject = translate(subject, **context)
            else:
                translated_subject = subject
            
            # Create message
            msg = Message(
                translated_subject,
                sender=app.config.get('MAIL_DEFAULT_SENDER'),
                recipients=[recipient_email]
            )
            
            # Render templates with language context
            msg.body = render_template(f'emails/{template}.txt', **context)
            msg.html = render_template(f'emails/{template}.html', **context)
            
            # Add attachments if any
            if attachments:
                for attachment in attachments:
                    msg.attach(
                        attachment['filename'],
                        attachment['content_type'],
                        attachment['data']
                    )
            
            # Send email asynchronously
            Thread(
                target=I18nEmailService.send_async_email,
                args=(app, msg)
            ).start()
    
    @staticmethod
    def send_welcome_email(user):
        """Send welcome email to new user"""
        language = user.language or 'en'
        
        # Prepare context with translations
        context = {
            'subject': translate('email.subject.welcome'),
            'greeting': translate('email.greeting.formal', name=user.first_name),
            'welcome_message': translate('email.welcome.message', app_name='BDC'),
            'get_started_message': translate('email.welcome.get_started'),
            'login_button': translate('auth.signIn'),
            'login_url': f"{current_app.config.get('FRONTEND_URL')}/login",
            'features_intro': translate('email.welcome.features_intro'),
            'features': [
                translate('email.welcome.feature_1'),
                translate('email.welcome.feature_2'),
                translate('email.welcome.feature_3')
            ],
            'help_message': translate('email.welcome.help_message')
        }
        
        I18nEmailService.send_email(
            user,
            'email.subject.welcome',
            'welcome',
            **context
        )
    
    @staticmethod
    def send_password_reset_email(user, reset_token):
        """Send password reset email"""
        language = user.language or 'en'
        reset_url = f"{current_app.config.get('FRONTEND_URL')}/reset-password?token={reset_token}"
        
        context = {
            'subject': translate('email.subject.password_reset'),
            'greeting': translate('email.greeting.formal', name=user.first_name),
            'reset_message': translate('email.password_reset.message'),
            'instruction_message': translate('email.password_reset.instruction'),
            'reset_button': translate('auth.resetPassword'),
            'reset_url': reset_url,
            'alternative_message': translate('email.password_reset.alternative'),
            'expiry_message': translate('email.password_reset.expiry', hours=24),
            'ignore_message': translate('email.password_reset.ignore'),
            'security_message': translate('email.password_reset.security')
        }
        
        I18nEmailService.send_email(
            user,
            'email.subject.password_reset',
            'password_reset',
            **context
        )
    
    @staticmethod
    def send_appointment_reminder(appointment):
        """Send appointment reminder email"""
        user = appointment.user
        language = user.language or 'en'
        
        # Format date and time according to user's locale
        from app.i18n import translate
        appointment_date = appointment.start_time.strftime('%B %d, %Y')
        appointment_time = appointment.start_time.strftime('%I:%M %p')
        
        context = {
            'subject': translate('email.subject.appointment_reminder'),
            'greeting': translate('email.greeting.formal', name=user.first_name),
            'reminder_message': translate('email.appointment.reminder_message'),
            'appointment_details_title': translate('email.appointment.details_title'),
            'date_label': translate('common.date'),
            'time_label': translate('common.time'),
            'location_label': translate('calendar.fields.location'),
            'with_label': translate('email.appointment.with_label'),
            'notes_label': translate('calendar.fields.notes'),
            'appointment_date': appointment_date,
            'appointment_time': appointment_time,
            'location': appointment.location,
            'with_person': appointment.trainer_name if hasattr(appointment, 'trainer_name') else None,
            'notes': appointment.notes,
            'view_calendar_button': translate('email.appointment.view_calendar'),
            'calendar_url': f"{current_app.config.get('FRONTEND_URL')}/calendar?event={appointment.id}",
            'reschedule_message': translate('email.appointment.reschedule'),
            'contact_message': translate('email.appointment.contact')
        }
        
        I18nEmailService.send_email(
            user,
            'email.subject.appointment_reminder',
            'appointment_reminder',
            **context
        )
    
    @staticmethod
    def send_evaluation_assigned_email(user, evaluation):
        """Send email when evaluation is assigned"""
        language = user.language or 'en'
        
        context = {
            'subject': translate('email.subject.evaluation_assigned'),
            'greeting': translate('email.greeting.formal', name=user.first_name),
            'evaluation_title': evaluation.title,
            'due_date': evaluation.due_date.strftime('%B %d, %Y'),
            'evaluation_url': f"{current_app.config.get('FRONTEND_URL')}/evaluations/{evaluation.id}"
        }
        
        I18nEmailService.send_email(
            user,
            'email.subject.evaluation_assigned',
            'evaluation_assigned',
            **context
        )
    
    @staticmethod
    def send_bulk_email(users, subject, template, **kwargs):
        """Send bulk email to multiple users with their respective languages"""
        for user in users:
            I18nEmailService.send_email(user, subject, template, **kwargs)


# Convenience functions
def send_welcome_email(user):
    """Convenience function to send welcome email"""
    I18nEmailService.send_welcome_email(user)


def send_password_reset_email(user, reset_token):
    """Convenience function to send password reset email"""
    I18nEmailService.send_password_reset_email(user, reset_token)


def send_appointment_reminder(appointment):
    """Convenience function to send appointment reminder"""
    I18nEmailService.send_appointment_reminder(appointment)


def send_evaluation_assigned_email(user, evaluation):
    """Convenience function to send evaluation assigned email"""
    I18nEmailService.send_evaluation_assigned_email(user, evaluation)
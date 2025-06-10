"""Push notification service for multiple providers."""

import logging
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from flask import current_app
from app.models.user import User
from app.models.push_notification import PushNotificationDevice, PushNotificationLog
from app.extensions import db
import requests

# Provider imports
try:
    from firebase_admin import messaging, credentials, initialize_app as init_firebase
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

try:
    import apns2
    APNS_AVAILABLE = True
except ImportError:
    APNS_AVAILABLE = False

logger = logging.getLogger(__name__)


class PushNotificationService:
    """Service for sending push notifications."""
    
    def __init__(self):
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize notification providers based on configuration."""
        # Firebase Cloud Messaging (Android + iOS + Web)
        if FIREBASE_AVAILABLE and current_app.config.get('FCM_CREDENTIALS_PATH'):
            try:
                cred = credentials.Certificate(current_app.config['FCM_CREDENTIALS_PATH'])
                init_firebase(cred)
                self.providers['fcm'] = FCMProvider()
                logger.info("FCM provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize FCM: {str(e)}")
        
        # Apple Push Notification Service (iOS)
        if APNS_AVAILABLE and current_app.config.get('APNS_CERT_PATH'):
            try:
                self.providers['apns'] = APNSProvider(
                    cert_path=current_app.config['APNS_CERT_PATH'],
                    use_sandbox=current_app.config.get('APNS_USE_SANDBOX', False)
                )
                logger.info("APNS provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize APNS: {str(e)}")
        
        # Web Push (PWA)
        if current_app.config.get('VAPID_PRIVATE_KEY'):
            try:
                self.providers['webpush'] = WebPushProvider(
                    vapid_private_key=current_app.config['VAPID_PRIVATE_KEY'],
                    vapid_public_key=current_app.config['VAPID_PUBLIC_KEY'],
                    vapid_claims_email=current_app.config['VAPID_CLAIMS_EMAIL']
                )
                logger.info("WebPush provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize WebPush: {str(e)}")
    
    def register_device(self, user_id: int, token: str, device_type: str, 
                       provider: str, **device_info) -> PushNotificationDevice:
        """Register a device for push notifications."""
        try:
            device = PushNotificationDevice.register_device(
                user_id=user_id,
                device_token=token,
                device_type=device_type,
                provider=provider,
                **device_info
            )
            
            logger.info(f"Device registered for user {user_id}: {device_type}/{provider}")
            return device
            
        except Exception as e:
            logger.error(f"Failed to register device: {str(e)}")
            raise
    
    def unregister_device(self, user_id: int, device_token: str) -> bool:
        """Unregister a device."""
        try:
            device = PushNotificationDevice.query.filter_by(
                user_id=user_id,
                device_token=device_token
            ).first()
            
            if device:
                device.deactivate()
                logger.info(f"Device unregistered for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to unregister device: {str(e)}")
            return False
    
    def send_to_user(self, user_id: int, title: str, body: str, 
                     data: Optional[Dict] = None, **options) -> Dict[str, any]:
        """Send notification to all devices of a user."""
        devices = PushNotificationDevice.get_active_devices(user_id)
        
        if not devices:
            logger.warning(f"No active devices found for user {user_id}")
            return {'success': False, 'error': 'No registered devices'}
        
        results = []
        success_count = 0
        
        for device in devices:
            # Create notification log
            notification_log = PushNotificationLog.create_notification(
                user_id=user_id,
                title=title,
                body=body,
                device_id=device.id,
                data=json.dumps(data) if data else None,
                notification_type=options.get('notification_type'),
                priority=options.get('priority', 'normal'),
                provider=device.provider
            )
            
            # Send via appropriate provider
            success, error = self._send_to_device(
                device, title, body, data, notification_log, **options
            )
            
            results.append({
                'device_id': device.id,
                'success': success,
                'error': error
            })
            
            if success:
                success_count += 1
        
        return {
            'success': success_count > 0,
            'devices_reached': success_count,
            'total_devices': len(devices),
            'results': results
        }
    
    def send_to_users(self, user_ids: List[int], title: str, body: str, 
                      data: Optional[Dict] = None, **options) -> Dict[str, any]:
        """Send notification to multiple users."""
        results = {}
        total_success = 0
        
        for user_id in user_ids:
            result = self.send_to_user(user_id, title, body, data, **options)
            results[user_id] = result
            if result['success']:
                total_success += 1
        
        return {
            'success': total_success > 0,
            'users_reached': total_success,
            'total_users': len(user_ids),
            'results': results
        }
    
    def send_to_topic(self, topic: str, title: str, body: str, 
                      data: Optional[Dict] = None, **options) -> Dict[str, any]:
        """Send notification to a topic (FCM only)."""
        if 'fcm' not in self.providers:
            return {'success': False, 'error': 'FCM provider not available'}
        
        try:
            result = self.providers['fcm'].send_to_topic(topic, title, body, data, **options)
            return {'success': True, 'result': result}
        except Exception as e:
            logger.error(f"Failed to send to topic {topic}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_to_device(self, device: PushNotificationDevice, title: str, 
                        body: str, data: Optional[Dict], 
                        notification_log: PushNotificationLog, **options) -> Tuple[bool, Optional[str]]:
        """Send notification to a specific device."""
        provider = self.providers.get(device.provider)
        
        if not provider:
            error = f"Provider {device.provider} not available"
            notification_log.mark_as_failed(error)
            return False, error
        
        try:
            # Send notification
            result = provider.send(
                device_token=device.device_token,
                title=title,
                body=body,
                data=data,
                **options
            )
            
            # Update device and log
            device.mark_as_used()
            notification_log.mark_as_sent(result.get('message_id'))
            
            return True, None
            
        except InvalidTokenError as e:
            # Token is invalid, deactivate device
            device.deactivate()
            notification_log.mark_as_failed(str(e))
            return False, str(e)
            
        except Exception as e:
            # Other error, increment failure count
            error_msg = str(e)
            device.mark_as_failed(error_msg)
            notification_log.mark_as_failed(error_msg)
            return False, error_msg
    
    def get_user_devices(self, user_id: int) -> List[Dict]:
        """Get all devices for a user."""
        devices = PushNotificationDevice.query.filter_by(user_id=user_id).all()
        return [device.to_dict() for device in devices]
    
    def get_notification_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get notification history for a user."""
        notifications = PushNotificationLog.query.filter_by(
            user_id=user_id
        ).order_by(
            PushNotificationLog.created_at.desc()
        ).limit(limit).all()
        
        return [notif.to_dict() for notif in notifications]
    
    def cleanup_old_logs(self, days: int = 30):
        """Clean up old notification logs."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted = PushNotificationLog.query.filter(
            PushNotificationLog.created_at < cutoff_date
        ).delete()
        
        db.session.commit()
        logger.info(f"Deleted {deleted} old notification logs")
        return deleted


class InvalidTokenError(Exception):
    """Raised when a device token is invalid."""
    pass


class FCMProvider:
    """Firebase Cloud Messaging provider."""
    
    def send(self, device_token: str, title: str, body: str, 
             data: Optional[Dict] = None, **options) -> Dict:
        """Send notification via FCM."""
        if not FIREBASE_AVAILABLE:
            raise Exception("Firebase Admin SDK not available")
        
        # Build message
        notification = messaging.Notification(
            title=title,
            body=body
        )
        
        # Add Android specific config
        android_config = messaging.AndroidConfig(
            priority=options.get('priority', 'normal'),
            notification=messaging.AndroidNotification(
                icon=options.get('icon', 'ic_notification'),
                color=options.get('color', '#3498db'),
                sound=options.get('sound', 'default')
            )
        )
        
        # Add iOS specific config  
        apns_config = messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    alert=messaging.ApsAlert(
                        title=title,
                        body=body
                    ),
                    badge=options.get('badge'),
                    sound=options.get('sound', 'default')
                )
            )
        )
        
        # Add web specific config
        webpush_config = messaging.WebpushConfig(
            notification=messaging.WebpushNotification(
                title=title,
                body=body,
                icon=options.get('icon'),
                badge=options.get('badge_icon')
            )
        )
        
        message = messaging.Message(
            notification=notification,
            data=data or {},
            token=device_token,
            android=android_config,
            apns=apns_config,
            webpush=webpush_config
        )
        
        try:
            # Send message
            response = messaging.send(message)
            return {'message_id': response}
            
        except messaging.UnregisteredError:
            raise InvalidTokenError("Device token is invalid or unregistered")
        except Exception as e:
            logger.error(f"FCM send error: {str(e)}")
            raise
    
    def send_to_topic(self, topic: str, title: str, body: str, 
                      data: Optional[Dict] = None, **options) -> str:
        """Send notification to a topic."""
        notification = messaging.Notification(
            title=title,
            body=body
        )
        
        message = messaging.Message(
            notification=notification,
            data=data or {},
            topic=topic
        )
        
        response = messaging.send(message)
        return response


class APNSProvider:
    """Apple Push Notification Service provider."""
    
    def __init__(self, cert_path: str, use_sandbox: bool = False):
        if not APNS_AVAILABLE:
            raise Exception("APNS2 library not available")
            
        self.cert_path = cert_path
        self.use_sandbox = use_sandbox
        self._client = None
    
    @property
    def client(self):
        """Get or create APNS client."""
        if not self._client:
            self._client = apns2.APNSClient(
                cert_file=self.cert_path,
                use_sandbox=self.use_sandbox,
                use_alternative_port=False
            )
        return self._client
    
    def send(self, device_token: str, title: str, body: str, 
             data: Optional[Dict] = None, **options) -> Dict:
        """Send notification via APNS."""
        payload = apns2.Payload(
            alert={
                'title': title,
                'body': body
            },
            badge=options.get('badge'),
            sound=options.get('sound', 'default'),
            custom=data or {}
        )
        
        notification = apns2.Notification(
            token=device_token,
            payload=payload,
            priority=apns2.PRIORITY_HIGH if options.get('priority') == 'high' else apns2.PRIORITY_LOW
        )
        
        try:
            response = self.client.send_notification(notification)
            return {'message_id': response}
        except apns2.errors.BadDeviceToken:
            raise InvalidTokenError("Invalid device token")
        except Exception as e:
            logger.error(f"APNS send error: {str(e)}")
            raise


class WebPushProvider:
    """Web Push provider for PWA notifications."""
    
    def __init__(self, vapid_private_key: str, vapid_public_key: str, vapid_claims_email: str):
        self.vapid_private_key = vapid_private_key
        self.vapid_public_key = vapid_public_key
        self.vapid_claims = {"sub": f"mailto:{vapid_claims_email}"}
    
    def send(self, device_token: str, title: str, body: str, 
             data: Optional[Dict] = None, **options) -> Dict:
        """Send web push notification."""
        # Parse subscription info from device token
        try:
            subscription = json.loads(device_token)
        except:
            raise InvalidTokenError("Invalid subscription format")
        
        payload = {
            'notification': {
                'title': title,
                'body': body,
                'icon': options.get('icon', '/icon-192x192.png'),
                'badge': options.get('badge', '/badge-72x72.png'),
                'vibrate': options.get('vibrate', [200, 100, 200]),
                'data': data or {}
            }
        }
        
        headers = {
            'Content-Type': 'application/json',
            'TTL': str(options.get('ttl', 86400))  # 24 hours default
        }
        
        # Send via web push protocol
        try:
            from pywebpush import webpush
            
            response = webpush(
                subscription_info=subscription,
                data=json.dumps(payload),
                vapid_private_key=self.vapid_private_key,
                vapid_claims=self.vapid_claims,
                headers=headers
            )
            
            return {'message_id': response.headers.get('Location', 'sent')}
            
        except Exception as e:
            if '410' in str(e):  # Gone - subscription expired
                raise InvalidTokenError("Subscription expired")
            logger.error(f"WebPush send error: {str(e)}")
            raise
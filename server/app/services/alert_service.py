"""
Real-time Alert Service for BDC Application
Handles notifications for critical events via multiple channels
"""

import json
import logging
import asyncio
import aiohttp
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict
from threading import Thread
import os
import requests
from urllib.parse import urljoin

from app.utils.logger import get_logger
from app.security.audit_logger import audit_logger

logger = get_logger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertChannel(Enum):
    """Available alert channels"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    TEAMS = "teams"
    DISCORD = "discord"

@dataclass
class AlertEvent:
    """Alert event data structure"""
    id: str
    title: str
    message: str
    severity: AlertSeverity
    timestamp: datetime
    source: str
    event_type: str
    metadata: Dict[str, Any]
    affected_users: List[str] = None
    correlation_id: str = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['severity'] = self.severity.value
        return data

class AlertService:
    """
    Central alert service for handling real-time notifications
    """
    
    def __init__(self):
        self.enabled_channels = self._load_enabled_channels()
        self.rate_limits = {}
        self.alert_history = []
        self.max_history = 1000
        
        # Configuration
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        self.slack_token = os.getenv('SLACK_BOT_TOKEN')
        self.email_config = self._load_email_config()
        self.webhook_urls = self._load_webhook_config()
        
        # Rate limiting configuration
        self.rate_limit_config = {
            AlertSeverity.CRITICAL: {"max_alerts": 50, "window_minutes": 60},
            AlertSeverity.HIGH: {"max_alerts": 30, "window_minutes": 60},
            AlertSeverity.MEDIUM: {"max_alerts": 20, "window_minutes": 60},
            AlertSeverity.LOW: {"max_alerts": 10, "window_minutes": 60}
        }
        
        logger.info(f"Alert service initialized with channels: {[c.value for c in self.enabled_channels]}")
    
    def _load_enabled_channels(self) -> List[AlertChannel]:
        """Load enabled alert channels from configuration"""
        channels = []
        
        if os.getenv('SLACK_WEBHOOK_URL') or os.getenv('SLACK_BOT_TOKEN'):
            channels.append(AlertChannel.SLACK)
        
        if all([os.getenv('MAIL_SERVER'), os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD')]):
            channels.append(AlertChannel.EMAIL)
        
        if os.getenv('ALERT_WEBHOOK_URL'):
            channels.append(AlertChannel.WEBHOOK)
        
        if os.getenv('TEAMS_WEBHOOK_URL'):
            channels.append(AlertChannel.TEAMS)
        
        if os.getenv('DISCORD_WEBHOOK_URL'):
            channels.append(AlertChannel.DISCORD)
        
        return channels
    
    def _load_email_config(self) -> Dict[str, str]:
        """Load email configuration"""
        return {
            'server': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
            'port': int(os.getenv('MAIL_PORT', '587')),
            'username': os.getenv('MAIL_USERNAME'),
            'password': os.getenv('MAIL_PASSWORD'),
            'use_tls': os.getenv('MAIL_USE_TLS', 'true').lower() == 'true',
            'from_email': os.getenv('MAIL_DEFAULT_SENDER', 'noreply@bdc.com'),
            'admin_emails': os.getenv('ADMIN_EMAILS', '').split(',')
        }
    
    def _load_webhook_config(self) -> Dict[str, str]:
        """Load webhook configuration"""
        return {
            'primary': os.getenv('ALERT_WEBHOOK_URL'),
            'backup': os.getenv('BACKUP_WEBHOOK_URL'),
            'teams': os.getenv('TEAMS_WEBHOOK_URL'),
            'discord': os.getenv('DISCORD_WEBHOOK_URL')
        }
    
    def send_alert(self, event: AlertEvent, channels: List[AlertChannel] = None) -> bool:
        """
        Send alert through specified channels
        
        Args:
            event: Alert event to send
            channels: Specific channels to use (defaults to all enabled)
        
        Returns:
            True if alert was sent successfully through at least one channel
        """
        if not self._should_send_alert(event):
            logger.warning(f"Alert rate limited: {event.title}")
            return False
        
        # Use specified channels or all enabled channels
        target_channels = channels or self.enabled_channels
        
        # Record alert in history
        self._record_alert(event)
        
        # Send through each channel asynchronously
        success_count = 0
        
        for channel in target_channels:
            try:
                if self._send_to_channel(event, channel):
                    success_count += 1
                    logger.info(f"Alert sent via {channel.value}: {event.title}")
                else:
                    logger.error(f"Failed to send alert via {channel.value}: {event.title}")
            except Exception as e:
                logger.error(f"Error sending alert via {channel.value}: {str(e)}")
        
        # Log alert attempt
        audit_logger.log_security_event(
            event_type="ALERT_SENT",
            user_id="system",
            ip_address="localhost",
            metadata={
                "alert_id": event.id,
                "severity": event.severity.value,
                "channels": [c.value for c in target_channels],
                "success_count": success_count
            },
            risk_level="low" if success_count > 0 else "medium"
        )
        
        return success_count > 0
    
    def _should_send_alert(self, event: AlertEvent) -> bool:
        """Check if alert should be sent based on rate limiting"""
        now = datetime.now(timezone.utc)
        severity = event.severity
        
        # Get rate limit config for this severity
        config = self.rate_limit_config.get(severity)
        if not config:
            return True
        
        # Check rate limit
        key = f"{severity.value}_{event.event_type}"
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        # Clean old entries
        window_start = now.timestamp() - (config["window_minutes"] * 60)
        self.rate_limits[key] = [
            timestamp for timestamp in self.rate_limits[key]
            if timestamp > window_start
        ]
        
        # Check if we're within rate limit
        if len(self.rate_limits[key]) >= config["max_alerts"]:
            return False
        
        # Add current timestamp
        self.rate_limits[key].append(now.timestamp())
        return True
    
    def _record_alert(self, event: AlertEvent):
        """Record alert in history for analysis"""
        self.alert_history.append(event)
        
        # Keep history size manageable
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history:]
    
    def _send_to_channel(self, event: AlertEvent, channel: AlertChannel) -> bool:
        """Send alert to specific channel"""
        try:
            if channel == AlertChannel.SLACK:
                return self._send_slack_alert(event)
            elif channel == AlertChannel.EMAIL:
                return self._send_email_alert(event)
            elif channel == AlertChannel.WEBHOOK:
                return self._send_webhook_alert(event)
            elif channel == AlertChannel.TEAMS:
                return self._send_teams_alert(event)
            elif channel == AlertChannel.DISCORD:
                return self._send_discord_alert(event)
            else:
                logger.warning(f"Unsupported alert channel: {channel}")
                return False
        except Exception as e:
            logger.error(f"Error sending to {channel.value}: {str(e)}")
            return False
    
    def _send_slack_alert(self, event: AlertEvent) -> bool:
        """Send alert to Slack"""
        if not (self.slack_webhook or self.slack_token):
            return False
        
        # Prepare Slack message
        color = {
            AlertSeverity.CRITICAL: "#FF0000",
            AlertSeverity.HIGH: "#FF8C00",
            AlertSeverity.MEDIUM: "#FFD700",
            AlertSeverity.LOW: "#32CD32"
        }.get(event.severity, "#808080")
        
        attachment = {
            "color": color,
            "title": f"🚨 {event.title}",
            "text": event.message,
            "fields": [
                {"title": "Severity", "value": event.severity.value.upper(), "short": True},
                {"title": "Source", "value": event.source, "short": True},
                {"title": "Time", "value": event.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"), "short": True},
                {"title": "Event Type", "value": event.event_type, "short": True}
            ],
            "footer": "BDC Alert System",
            "ts": int(event.timestamp.timestamp())
        }
        
        if event.correlation_id:
            attachment["fields"].append({
                "title": "Correlation ID",
                "value": event.correlation_id,
                "short": True
            })
        
        payload = {
            "text": f"Alert: {event.title}",
            "attachments": [attachment]
        }
        
        # Send via webhook
        if self.slack_webhook:
            response = requests.post(
                self.slack_webhook,
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        
        return False
    
    def _send_email_alert(self, event: AlertEvent) -> bool:
        """Send alert via email"""
        if not self.email_config['username']:
            return False
        
        try:
            # Create message
            msg = MimeMultipart('alternative')
            msg['Subject'] = f"[BDC Alert - {event.severity.value.upper()}] {event.title}"
            msg['From'] = self.email_config['from_email']
            msg['To'] = ', '.join(self.email_config['admin_emails'])
            
            # HTML content
            html_content = f"""
            <html>
            <body>
                <h2 style="color: {'red' if event.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH] else 'orange'};">
                    🚨 BDC Alert - {event.severity.value.upper()}
                </h2>
                <h3>{event.title}</h3>
                <p><strong>Message:</strong> {event.message}</p>
                <p><strong>Source:</strong> {event.source}</p>
                <p><strong>Event Type:</strong> {event.event_type}</p>
                <p><strong>Timestamp:</strong> {event.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                {f'<p><strong>Correlation ID:</strong> {event.correlation_id}</p>' if event.correlation_id else ''}
                
                <h4>Metadata:</h4>
                <pre>{json.dumps(event.metadata, indent=2)}</pre>
                
                <hr>
                <p><small>This alert was generated by the BDC Alert System</small></p>
            </body>
            </html>
            """
            
            # Text content
            text_content = f"""
            BDC Alert - {event.severity.value.upper()}
            
            Title: {event.title}
            Message: {event.message}
            Source: {event.source}
            Event Type: {event.event_type}
            Timestamp: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
            {f'Correlation ID: {event.correlation_id}' if event.correlation_id else ''}
            
            Metadata:
            {json.dumps(event.metadata, indent=2)}
            
            ---
            This alert was generated by the BDC Alert System
            """
            
            # Attach parts
            msg.attach(MimeText(text_content, 'plain'))
            msg.attach(MimeText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(self.email_config['server'], self.email_config['port']) as server:
                if self.email_config['use_tls']:
                    server.starttls()
                server.login(self.email_config['username'], self.email_config['password'])
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {str(e)}")
            return False
    
    def _send_webhook_alert(self, event: AlertEvent) -> bool:
        """Send alert to webhook endpoint"""
        webhook_url = self.webhook_urls.get('primary')
        if not webhook_url:
            return False
        
        payload = {
            "alert": event.to_dict(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "bdc-alert-system"
        }
        
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {os.getenv('ALERT_API_KEY')}" if os.getenv('ALERT_API_KEY') else None
                },
                timeout=10
            )
            return response.status_code in [200, 201, 202]
        except Exception as e:
            logger.error(f"Webhook alert failed: {str(e)}")
            return False
    
    def _send_teams_alert(self, event: AlertEvent) -> bool:
        """Send alert to Microsoft Teams"""
        teams_url = self.webhook_urls.get('teams')
        if not teams_url:
            return False
        
        color = {
            AlertSeverity.CRITICAL: "attention",
            AlertSeverity.HIGH: "warning",
            AlertSeverity.MEDIUM: "accent",
            AlertSeverity.LOW: "good"
        }.get(event.severity, "default")
        
        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": f"BDC Alert: {event.title}",
            "themeColor": color,
            "sections": [{
                "activityTitle": f"🚨 BDC Alert - {event.severity.value.upper()}",
                "activitySubtitle": event.title,
                "text": event.message,
                "facts": [
                    {"name": "Source", "value": event.source},
                    {"name": "Event Type", "value": event.event_type},
                    {"name": "Timestamp", "value": event.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')},
                    {"name": "Severity", "value": event.severity.value.upper()}
                ]
            }]
        }
        
        if event.correlation_id:
            payload["sections"][0]["facts"].append({
                "name": "Correlation ID",
                "value": event.correlation_id
            })
        
        try:
            response = requests.post(teams_url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Teams alert failed: {str(e)}")
            return False
    
    def _send_discord_alert(self, event: AlertEvent) -> bool:
        """Send alert to Discord"""
        discord_url = self.webhook_urls.get('discord')
        if not discord_url:
            return False
        
        color = {
            AlertSeverity.CRITICAL: 0xFF0000,
            AlertSeverity.HIGH: 0xFF8C00,
            AlertSeverity.MEDIUM: 0xFFD700,
            AlertSeverity.LOW: 0x32CD32
        }.get(event.severity, 0x808080)
        
        embed = {
            "title": f"🚨 {event.title}",
            "description": event.message,
            "color": color,
            "fields": [
                {"name": "Severity", "value": event.severity.value.upper(), "inline": True},
                {"name": "Source", "value": event.source, "inline": True},
                {"name": "Event Type", "value": event.event_type, "inline": True},
                {"name": "Timestamp", "value": event.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'), "inline": False}
            ],
            "footer": {"text": "BDC Alert System"},
            "timestamp": event.timestamp.isoformat()
        }
        
        if event.correlation_id:
            embed["fields"].append({
                "name": "Correlation ID",
                "value": event.correlation_id,
                "inline": True
            })
        
        payload = {"embeds": [embed]}
        
        try:
            response = requests.post(discord_url, json=payload, timeout=10)
            return response.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Discord alert failed: {str(e)}")
            return False
    
    def create_alert(self, 
                    title: str,
                    message: str,
                    severity: AlertSeverity,
                    source: str,
                    event_type: str,
                    metadata: Dict[str, Any] = None,
                    affected_users: List[str] = None,
                    correlation_id: str = None) -> AlertEvent:
        """
        Create and send an alert event
        
        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity level
            source: Source of the alert (e.g., 'flask-app', 'nginx', 'database')
            event_type: Type of event (e.g., 'error', 'security', 'performance')
            metadata: Additional metadata
            affected_users: List of affected user IDs
            correlation_id: Correlation ID for tracking
        
        Returns:
            Created AlertEvent
        """
        event = AlertEvent(
            id=f"alert_{int(datetime.now().timestamp())}_{hash(title) % 10000}",
            title=title,
            message=message,
            severity=severity,
            timestamp=datetime.now(timezone.utc),
            source=source,
            event_type=event_type,
            metadata=metadata or {},
            affected_users=affected_users or [],
            correlation_id=correlation_id
        )
        
        # Send alert asynchronously
        Thread(target=self.send_alert, args=(event,), daemon=True).start()
        
        return event
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics"""
        now = datetime.now(timezone.utc)
        last_hour = now.timestamp() - 3600
        last_day = now.timestamp() - 86400
        
        recent_alerts = [
            alert for alert in self.alert_history
            if alert.timestamp.timestamp() > last_day
        ]
        
        hour_alerts = [
            alert for alert in recent_alerts
            if alert.timestamp.timestamp() > last_hour
        ]
        
        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = len([
                alert for alert in recent_alerts
                if alert.severity == severity
            ])
        
        return {
            "total_alerts_24h": len(recent_alerts),
            "alerts_last_hour": len(hour_alerts),
            "severity_breakdown_24h": severity_counts,
            "enabled_channels": [c.value for c in self.enabled_channels],
            "rate_limits": {k: len(v) for k, v in self.rate_limits.items()},
            "last_alert": recent_alerts[-1].to_dict() if recent_alerts else None
        }

# Global alert service instance
alert_service = AlertService()

def send_critical_alert(title: str, message: str, source: str, **kwargs):
    """Convenience function for sending critical alerts"""
    return alert_service.create_alert(
        title=title,
        message=message,
        severity=AlertSeverity.CRITICAL,
        source=source,
        event_type="critical_error",
        **kwargs
    )

def send_security_alert(title: str, message: str, **kwargs):
    """Convenience function for sending security alerts"""
    return alert_service.create_alert(
        title=title,
        message=message,
        severity=AlertSeverity.HIGH,
        source="security",
        event_type="security_incident",
        **kwargs
    )

def send_performance_alert(title: str, message: str, severity: AlertSeverity = AlertSeverity.MEDIUM, **kwargs):
    """Convenience function for sending performance alerts"""
    return alert_service.create_alert(
        title=title,
        message=message,
        severity=severity,
        source="performance",
        event_type="performance_issue",
        **kwargs
    )
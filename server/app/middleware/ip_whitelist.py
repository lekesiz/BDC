"""IP Whitelist middleware for Flask."""

import os
import ipaddress
from flask import request, abort
from werkzeug.wrappers import Request, Response
from werkzeug.wsgi import ClosingIterator

class IPWhitelistMiddleware:
    """WSGI middleware that restricts access based on IP address whitelist."""
    
    def __init__(self, app):
        self.app = app
        self.ip_whitelist = self._parse_whitelist()
        
    def __call__(self, environ, start_response):
        request = Request(environ)
        ip = self._get_client_ip(request)
        
        # Bypass whitelist for health check endpoint
        if request.path == '/api/health':
            return self.app(environ, start_response)
        
        # Check if IP is allowed
        if not self._is_ip_allowed(ip):
            res = Response('Access denied: Your IP is not authorized', status=403)
            return res(environ, start_response)
            
        return self.app(environ, start_response)
    
    def _parse_whitelist(self):
        """Parse IP whitelist from environment variable."""
        whitelist_str = os.environ.get('IP_WHITELIST', '0.0.0.0/0')  # Default to allow all
        whitelist = []
        
        # Split and strip IPs/networks
        for item in whitelist_str.split(','):
            item = item.strip()
            if not item:
                continue
                
            try:
                # Parse as network if contains slash
                if '/' in item:
                    network = ipaddress.ip_network(item)
                    whitelist.append(network)
                else:
                    # Parse as single IP
                    ip = ipaddress.ip_address(item)
                    whitelist.append(ip)
            except ValueError:
                # Log invalid IP/network
                from flask import current_app
                current_app.logger.warning(f"Invalid IP or network in whitelist: {item}")
                
        return whitelist
    
    def _get_client_ip(self, request):
        """Get client IP from request, handling proxies."""
        if 'X-Forwarded-For' in request.headers:
            # X-Forwarded-For header format: client, proxy1, proxy2, ...
            ip = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
        else:
            ip = request.remote_addr or '127.0.0.1'
            
        try:
            return ipaddress.ip_address(ip)
        except ValueError:
            from flask import current_app
            current_app.logger.warning(f"Invalid IP address: {ip}")
            return ipaddress.ip_address('0.0.0.0')  # Default fallback
    
    def _is_ip_allowed(self, ip):
        """Check if IP is allowed based on whitelist."""
        # Empty whitelist means allow all
        if not self.ip_whitelist:
            return True
            
        # Check if IP is in any of the allowed networks/IPs
        for entry in self.ip_whitelist:
            if isinstance(entry, ipaddress.IPv4Network) or isinstance(entry, ipaddress.IPv6Network):
                if ip in entry:
                    return True
            elif ip == entry:
                return True
                
        return False
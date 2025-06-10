"""
PayPal payment integration.
"""

import base64
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from decimal import Decimal
import logging

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from ..base import OAuth2Integration, IntegrationConfig, ServiceUnavailableError, AuthenticationError
from ..registry import register_integration
from .base_payment import (
    BasePaymentIntegration, PaymentIntent, PaymentMethod, Customer, Transaction,
    PaymentStatus, PaymentMethodType, RefundRequest, Refund
)

logger = logging.getLogger(__name__)


@register_integration('paypal')
class PayPalIntegration(BasePaymentIntegration, OAuth2Integration):
    """PayPal payment integration."""
    
    SANDBOX_BASE_URL = 'https://api.sandbox.paypal.com'
    LIVE_BASE_URL = 'https://api.paypal.com'
    
    def __init__(self, config: IntegrationConfig):
        if not AIOHTTP_AVAILABLE:
            raise ImportError("aiohttp is required for PayPal integration")
        
        super().__init__(config)
        self.client_id = config.credentials.get('client_id')
        self.client_secret = config.credentials.get('client_secret')
        self.environment = config.credentials.get('environment', 'sandbox')
        self.base_url = self.SANDBOX_BASE_URL if self.environment == 'sandbox' else self.LIVE_BASE_URL
        self._session = None
        
    @property
    def provider_name(self) -> str:
        return "paypal"
    
    async def get_authorization_url(self, state: str = None) -> str:
        """PayPal doesn't use traditional OAuth for payments."""
        # PayPal uses client credentials flow for merchants
        raise NotImplementedError("PayPal uses client credentials, not authorization URL")
    
    async def exchange_code_for_tokens(self, code: str, state: str = None) -> Dict[str, Any]:
        """PayPal doesn't use authorization code flow for payments."""
        raise NotImplementedError("PayPal uses client credentials, not authorization code")
    
    async def refresh_access_token(self) -> bool:
        """Refresh PayPal access token using client credentials."""
        return await self._get_access_token()
    
    async def _authenticate(self) -> bool:
        """Authenticate with PayPal using client credentials."""
        return await self._get_access_token()
    
    async def _get_access_token(self) -> bool:
        """Get access token using client credentials flow."""
        try:
            auth_string = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
            
            headers = {
                'Authorization': f'Basic {auth_string}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = 'grant_type=client_credentials'
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/v1/oauth2/token",
                    headers=headers,
                    data=data
                ) as response:
                    if response.status != 200:
                        logger.error(f"PayPal auth failed: {response.status}")
                        return False
                    
                    token_data = await response.json()
                    self.access_token = token_data.get('access_token')
                    return self.access_token is not None
                    
        except Exception as e:
            logger.error(f"PayPal authentication failed: {e}")
            return False
    
    async def connect(self) -> bool:
        """Connect to PayPal API."""
        try:
            if not await self._authenticate():
                return False
            
            self._session = aiohttp.ClientSession(
                headers={'Authorization': f'Bearer {self.access_token}'}
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to connect to PayPal: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from PayPal API."""
        if self._session:
            await self._session.close()
            self._session = None
        return True
    
    async def test_connection(self) -> bool:
        """Test PayPal connection."""
        try:
            if not self._session:
                return False
            
            async with self._session.get(f"{self.base_url}/v1/identity/oauth2/userinfo") as response:
                return response.status in [200, 403]  # 403 is OK, means we're authenticated but don't have user info scope
        except Exception as e:
            logger.error(f"PayPal connection test failed: {e}")
            return False
    
    async def create_customer(
        self,
        email: Optional[str] = None,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Customer:
        """Create PayPal customer (PayPal doesn't have dedicated customer objects)."""
        # PayPal doesn't have customer objects like Stripe
        # We'll create a minimal customer representation
        import uuid
        customer_id = str(uuid.uuid4())
        
        return Customer(
            id=customer_id,
            email=email,
            name=name,
            phone=phone,
            description=description,
            created_at=datetime.now(timezone.utc),
            metadata=metadata or {}
        )
    
    async def get_customer(self, customer_id: str) -> Optional[Customer]:
        """PayPal doesn't have customer objects."""
        # Would need to be stored externally
        return None
    
    async def update_customer(
        self,
        customer_id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Customer:
        """PayPal doesn't have customer objects."""
        raise NotImplementedError("PayPal doesn't support customer objects")
    
    async def delete_customer(self, customer_id: str) -> bool:
        """PayPal doesn't have customer objects."""
        return True
    
    async def create_payment_method(
        self,
        type: PaymentMethodType,
        customer_id: Optional[str] = None,
        **kwargs
    ) -> PaymentMethod:
        """PayPal doesn't have separate payment method objects."""
        # PayPal handles payment methods during payment flow
        import uuid
        pm_id = str(uuid.uuid4())
        
        return PaymentMethod(
            id=pm_id,
            type=type,
            metadata=kwargs
        )
    
    async def get_payment_method(self, payment_method_id: str) -> Optional[PaymentMethod]:
        """PayPal doesn't have separate payment method objects."""
        return None
    
    async def list_payment_methods(
        self,
        customer_id: str,
        type: Optional[PaymentMethodType] = None
    ) -> List[PaymentMethod]:
        """PayPal doesn't have separate payment method objects."""
        return []
    
    async def detach_payment_method(self, payment_method_id: str) -> bool:
        """PayPal doesn't have separate payment method objects."""
        return True
    
    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        customer_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
        description: Optional[str] = None,
        receipt_email: Optional[str] = None,
        confirmation_method: str = "automatic",
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentIntent:
        """Create PayPal order (equivalent to payment intent)."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to PayPal", "payment")
        
        try:
            order_data = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": currency.upper(),
                        "value": str(amount)
                    }
                }]
            }
            
            if description:
                order_data["purchase_units"][0]["description"] = description
            
            async with self._session.post(
                f"{self.base_url}/v2/checkout/orders",
                json=order_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status not in [200, 201]:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to create PayPal order: {text}", "payment")
                
                order = await response.json()
                return self._convert_paypal_order_to_payment_intent(order, amount, currency)
                
        except Exception as e:
            logger.error(f"Failed to create PayPal order: {e}")
            raise ServiceUnavailableError(f"Failed to create payment intent: {e}", "payment")
    
    async def get_payment_intent(self, payment_intent_id: str) -> Optional[PaymentIntent]:
        """Get PayPal order by ID."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to PayPal", "payment")
        
        try:
            async with self._session.get(f"{self.base_url}/v2/checkout/orders/{payment_intent_id}") as response:
                if response.status == 404:
                    return None
                elif response.status != 200:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to get PayPal order: {text}", "payment")
                
                order = await response.json()
                amount = Decimal(order['purchase_units'][0]['amount']['value'])
                currency = order['purchase_units'][0]['amount']['currency_code']
                return self._convert_paypal_order_to_payment_intent(order, amount, currency)
                
        except Exception as e:
            logger.error(f"Failed to get PayPal order: {e}")
            raise ServiceUnavailableError(f"Failed to get payment intent: {e}", "payment")
    
    async def update_payment_intent(
        self,
        payment_intent_id: str,
        amount: Optional[Decimal] = None,
        currency: Optional[str] = None,
        customer_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
        description: Optional[str] = None,
        receipt_email: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentIntent:
        """Update PayPal order."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to PayPal", "payment")
        
        try:
            patches = []
            
            if amount is not None and currency is not None:
                patches.append({
                    "op": "replace",
                    "path": "/purchase_units/@reference_id=='default'/amount",
                    "value": {
                        "currency_code": currency.upper(),
                        "value": str(amount)
                    }
                })
            
            if description is not None:
                patches.append({
                    "op": "replace",
                    "path": "/purchase_units/@reference_id=='default'/description",
                    "value": description
                })
            
            if patches:
                async with self._session.patch(
                    f"{self.base_url}/v2/checkout/orders/{payment_intent_id}",
                    json=patches,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status not in [200, 204]:
                        text = await response.text()
                        raise ServiceUnavailableError(f"Failed to update PayPal order: {text}", "payment")
            
            # Return updated order
            return await self.get_payment_intent(payment_intent_id)
            
        except Exception as e:
            logger.error(f"Failed to update PayPal order: {e}")
            raise ServiceUnavailableError(f"Failed to update payment intent: {e}", "payment")
    
    async def confirm_payment_intent(
        self,
        payment_intent_id: str,
        payment_method_id: Optional[str] = None
    ) -> PaymentIntent:
        """Capture PayPal order."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to PayPal", "payment")
        
        try:
            async with self._session.post(
                f"{self.base_url}/v2/checkout/orders/{payment_intent_id}/capture",
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status not in [200, 201]:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to capture PayPal order: {text}", "payment")
                
                capture_result = await response.json()
                amount = Decimal(capture_result['purchase_units'][0]['payments']['captures'][0]['amount']['value'])
                currency = capture_result['purchase_units'][0]['payments']['captures'][0]['amount']['currency_code']
                return self._convert_paypal_capture_to_payment_intent(capture_result, amount, currency)
                
        except Exception as e:
            logger.error(f"Failed to capture PayPal order: {e}")
            raise ServiceUnavailableError(f"Failed to confirm payment intent: {e}", "payment")
    
    async def cancel_payment_intent(self, payment_intent_id: str) -> PaymentIntent:
        """Cancel PayPal order (not directly supported, just return current state)."""
        current_pi = await self.get_payment_intent(payment_intent_id)
        if current_pi:
            current_pi.status = PaymentStatus.CANCELLED
        return current_pi
    
    async def capture_payment_intent(
        self,
        payment_intent_id: str,
        amount_to_capture: Optional[Decimal] = None
    ) -> PaymentIntent:
        """Same as confirm for PayPal."""
        return await self.confirm_payment_intent(payment_intent_id)
    
    async def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get PayPal capture by ID."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to PayPal", "payment")
        
        try:
            async with self._session.get(f"{self.base_url}/v2/payments/captures/{transaction_id}") as response:
                if response.status == 404:
                    return None
                elif response.status != 200:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to get PayPal capture: {text}", "payment")
                
                capture = await response.json()
                return self._convert_paypal_capture_to_transaction(capture)
                
        except Exception as e:
            logger.error(f"Failed to get PayPal capture: {e}")
            raise ServiceUnavailableError(f"Failed to get transaction: {e}", "payment")
    
    async def list_transactions(
        self,
        customer_id: Optional[str] = None,
        payment_intent_id: Optional[str] = None,
        limit: int = 10,
        starting_after: Optional[str] = None
    ) -> List[Transaction]:
        """List PayPal transactions."""
        # PayPal API doesn't have a simple way to list all transactions
        # Would need to use PayPal's reporting API or transaction search
        return []
    
    async def create_refund(self, refund_request: RefundRequest) -> Refund:
        """Create PayPal refund."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to PayPal", "payment")
        
        try:
            refund_data = {}
            
            if refund_request.amount is not None:
                # Get capture to determine currency
                capture = await self.get_transaction(refund_request.transaction_id)
                if not capture:
                    raise ServiceUnavailableError("Transaction not found", "payment")
                
                refund_data["amount"] = {
                    "value": str(refund_request.amount),
                    "currency_code": capture.currency
                }
            
            if refund_request.reason:
                refund_data["note_to_payer"] = refund_request.reason
            
            async with self._session.post(
                f"{self.base_url}/v2/payments/captures/{refund_request.transaction_id}/refund",
                json=refund_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status not in [200, 201]:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to create PayPal refund: {text}", "payment")
                
                refund_result = await response.json()
                return self._convert_paypal_refund(refund_result)
                
        except Exception as e:
            logger.error(f"Failed to create PayPal refund: {e}")
            raise ServiceUnavailableError(f"Failed to create refund: {e}", "payment")
    
    async def get_refund(self, refund_id: str) -> Optional[Refund]:
        """Get PayPal refund by ID."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to PayPal", "payment")
        
        try:
            async with self._session.get(f"{self.base_url}/v2/payments/refunds/{refund_id}") as response:
                if response.status == 404:
                    return None
                elif response.status != 200:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to get PayPal refund: {text}", "payment")
                
                refund_result = await response.json()
                return self._convert_paypal_refund(refund_result)
                
        except Exception as e:
            logger.error(f"Failed to get PayPal refund: {e}")
            raise ServiceUnavailableError(f"Failed to get refund: {e}", "payment")
    
    async def list_refunds(
        self,
        transaction_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Refund]:
        """List PayPal refunds."""
        # PayPal doesn't have a direct way to list refunds
        # Would need to use reporting API
        return []
    
    def _convert_paypal_order_to_payment_intent(
        self, 
        paypal_order: Dict[str, Any],
        amount: Decimal,
        currency: str
    ) -> PaymentIntent:
        """Convert PayPal order to PaymentIntent."""
        status = self._convert_paypal_status(paypal_order.get('status', 'CREATED'))
        
        return PaymentIntent(
            id=paypal_order['id'],
            amount=amount,
            currency=currency.upper(),
            status=status,
            description=paypal_order.get('purchase_units', [{}])[0].get('description'),
            created_at=datetime.now(timezone.utc),  # PayPal doesn't provide creation time in order
            client_secret=paypal_order['id'],  # Use order ID as client secret
            confirmation_method="manual"
        )
    
    def _convert_paypal_capture_to_payment_intent(
        self,
        paypal_capture: Dict[str, Any],
        amount: Decimal,
        currency: str
    ) -> PaymentIntent:
        """Convert PayPal capture result to PaymentIntent."""
        return PaymentIntent(
            id=paypal_capture['id'],
            amount=amount,
            currency=currency.upper(),
            status=PaymentStatus.SUCCEEDED,
            created_at=datetime.now(timezone.utc),
            client_secret=paypal_capture['id']
        )
    
    def _convert_paypal_capture_to_transaction(self, paypal_capture: Dict[str, Any]) -> Transaction:
        """Convert PayPal capture to Transaction."""
        amount = Decimal(paypal_capture['amount']['value'])
        currency = paypal_capture['amount']['currency_code']
        status = self._convert_paypal_status(paypal_capture.get('status', 'COMPLETED'))
        
        # Calculate fees
        fee_amount = Decimal('0')
        seller_receivable_breakdown = paypal_capture.get('seller_receivable_breakdown', {})
        if seller_receivable_breakdown.get('paypal_fee'):
            fee_amount = Decimal(seller_receivable_breakdown['paypal_fee']['value'])
        
        return Transaction(
            id=paypal_capture['id'],
            payment_intent_id=paypal_capture.get('invoice_id', ''),  # PayPal doesn't have direct mapping
            amount=amount,
            currency=currency,
            status=status,
            fee_amount=fee_amount,
            created_at=datetime.fromisoformat(
                paypal_capture.get('create_time', '').replace('Z', '+00:00')
            ) if paypal_capture.get('create_time') else datetime.now(timezone.utc)
        )
    
    def _convert_paypal_refund(self, paypal_refund: Dict[str, Any]) -> Refund:
        """Convert PayPal refund to Refund."""
        amount = Decimal(paypal_refund['amount']['value'])
        currency = paypal_refund['amount']['currency_code']
        status = self._convert_paypal_status(paypal_refund.get('status', 'COMPLETED'))
        
        return Refund(
            id=paypal_refund['id'],
            transaction_id=paypal_refund.get('invoice_id', ''),  # Would need to track this separately
            amount=amount,
            currency=currency,
            reason=paypal_refund.get('note_to_payer'),
            status=status,
            created_at=datetime.fromisoformat(
                paypal_refund.get('create_time', '').replace('Z', '+00:00')
            ) if paypal_refund.get('create_time') else datetime.now(timezone.utc)
        )
    
    def _convert_paypal_status(self, paypal_status: str) -> PaymentStatus:
        """Convert PayPal status to PaymentStatus."""
        mapping = {
            'CREATED': PaymentStatus.PENDING,
            'SAVED': PaymentStatus.PENDING,
            'APPROVED': PaymentStatus.PROCESSING,
            'VOIDED': PaymentStatus.CANCELLED,
            'COMPLETED': PaymentStatus.SUCCEEDED,
            'PAYER_ACTION_REQUIRED': PaymentStatus.PENDING,
            'PENDING': PaymentStatus.PROCESSING,
            'DENIED': PaymentStatus.FAILED,
            'FAILED': PaymentStatus.FAILED,
        }
        return mapping.get(paypal_status.upper(), PaymentStatus.PENDING)
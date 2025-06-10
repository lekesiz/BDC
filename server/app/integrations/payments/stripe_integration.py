"""
Stripe payment integration.
"""

import hmac
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from decimal import Decimal
import logging

try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False

from ..base import APIKeyIntegration, IntegrationConfig, ServiceUnavailableError, RateLimitError
from ..registry import register_integration
from .base_payment import (
    BasePaymentIntegration, PaymentIntent, PaymentMethod, Customer, Transaction,
    PaymentStatus, PaymentMethodType, RefundRequest, Refund
)

logger = logging.getLogger(__name__)


@register_integration('stripe')
class StripeIntegration(BasePaymentIntegration, APIKeyIntegration):
    """Stripe payment integration."""
    
    def __init__(self, config: IntegrationConfig):
        if not STRIPE_AVAILABLE:
            raise ImportError("Stripe library not available. Install stripe")
        
        super().__init__(config)
        self.publishable_key = config.credentials.get('publishable_key')
        self.webhook_secret = config.credentials.get('webhook_secret')
        
    @property
    def provider_name(self) -> str:
        return "stripe"
    
    async def connect(self) -> bool:
        """Initialize Stripe client."""
        try:
            if not self.api_key:
                return False
            
            stripe.api_key = self.api_key
            
            # Test the connection
            await self.test_connection()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Stripe: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Clear Stripe API key."""
        stripe.api_key = None
        return True
    
    async def test_connection(self) -> bool:
        """Test Stripe connection."""
        try:
            # Try to retrieve account info
            stripe.Account.retrieve()
            return True
        except stripe.error.AuthenticationError:
            logger.error("Stripe authentication failed")
            return False
        except Exception as e:
            logger.error(f"Stripe connection test failed: {e}")
            return False
    
    async def create_customer(
        self,
        email: Optional[str] = None,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Customer:
        """Create a Stripe customer."""
        try:
            params = {}
            if email:
                params['email'] = email
            if name:
                params['name'] = name
            if phone:
                params['phone'] = phone
            if description:
                params['description'] = description
            if metadata:
                params['metadata'] = metadata
            
            stripe_customer = stripe.Customer.create(**params)
            return self._convert_stripe_customer(stripe_customer)
            
        except stripe.error.RateLimitError as e:
            raise RateLimitError(str(e), "payment")
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise ServiceUnavailableError(f"Failed to create customer: {e}", "payment")
    
    async def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get Stripe customer by ID."""
        try:
            stripe_customer = stripe.Customer.retrieve(customer_id)
            return self._convert_stripe_customer(stripe_customer)
        except stripe.error.InvalidRequestError:
            return None
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get Stripe customer: {e}")
            raise ServiceUnavailableError(f"Failed to get customer: {e}", "payment")
    
    async def update_customer(
        self,
        customer_id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Customer:
        """Update Stripe customer."""
        try:
            params = {}
            if email is not None:
                params['email'] = email
            if name is not None:
                params['name'] = name
            if phone is not None:
                params['phone'] = phone
            if description is not None:
                params['description'] = description
            if metadata is not None:
                params['metadata'] = metadata
            
            stripe_customer = stripe.Customer.modify(customer_id, **params)
            return self._convert_stripe_customer(stripe_customer)
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to update Stripe customer: {e}")
            raise ServiceUnavailableError(f"Failed to update customer: {e}", "payment")
    
    async def delete_customer(self, customer_id: str) -> bool:
        """Delete Stripe customer."""
        try:
            stripe.Customer.delete(customer_id)
            return True
        except stripe.error.InvalidRequestError:
            return False
        except stripe.error.StripeError as e:
            logger.error(f"Failed to delete Stripe customer: {e}")
            return False
    
    async def create_payment_method(
        self,
        type: PaymentMethodType,
        customer_id: Optional[str] = None,
        **kwargs
    ) -> PaymentMethod:
        """Create Stripe payment method."""
        try:
            stripe_type = self._convert_to_stripe_payment_method_type(type)
            params = {
                'type': stripe_type,
                **kwargs
            }
            
            stripe_pm = stripe.PaymentMethod.create(**params)
            
            # Attach to customer if provided
            if customer_id:
                stripe_pm.attach(customer=customer_id)
            
            return self._convert_stripe_payment_method(stripe_pm)
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe payment method: {e}")
            raise ServiceUnavailableError(f"Failed to create payment method: {e}", "payment")
    
    async def get_payment_method(self, payment_method_id: str) -> Optional[PaymentMethod]:
        """Get Stripe payment method by ID."""
        try:
            stripe_pm = stripe.PaymentMethod.retrieve(payment_method_id)
            return self._convert_stripe_payment_method(stripe_pm)
        except stripe.error.InvalidRequestError:
            return None
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get Stripe payment method: {e}")
            raise ServiceUnavailableError(f"Failed to get payment method: {e}", "payment")
    
    async def list_payment_methods(
        self,
        customer_id: str,
        type: Optional[PaymentMethodType] = None
    ) -> List[PaymentMethod]:
        """List Stripe payment methods for customer."""
        try:
            params = {'customer': customer_id}
            if type:
                params['type'] = self._convert_to_stripe_payment_method_type(type)
            
            stripe_pms = stripe.PaymentMethod.list(**params)
            
            payment_methods = []
            for stripe_pm in stripe_pms.data:
                pm = self._convert_stripe_payment_method(stripe_pm)
                payment_methods.append(pm)
            
            return payment_methods
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to list Stripe payment methods: {e}")
            raise ServiceUnavailableError(f"Failed to list payment methods: {e}", "payment")
    
    async def detach_payment_method(self, payment_method_id: str) -> bool:
        """Detach Stripe payment method from customer."""
        try:
            stripe.PaymentMethod.detach(payment_method_id)
            return True
        except stripe.error.InvalidRequestError:
            return False
        except stripe.error.StripeError as e:
            logger.error(f"Failed to detach Stripe payment method: {e}")
            return False
    
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
        """Create Stripe payment intent."""
        try:
            params = {
                'amount': self.format_amount_for_api(amount, currency),
                'currency': currency.lower(),
                'confirmation_method': confirmation_method
            }
            
            if customer_id:
                params['customer'] = customer_id
            if payment_method_id:
                params['payment_method'] = payment_method_id
            if description:
                params['description'] = description
            if receipt_email:
                params['receipt_email'] = receipt_email
            if metadata:
                params['metadata'] = metadata
            
            stripe_pi = stripe.PaymentIntent.create(**params)
            return self._convert_stripe_payment_intent(stripe_pi)
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe payment intent: {e}")
            raise ServiceUnavailableError(f"Failed to create payment intent: {e}", "payment")
    
    async def get_payment_intent(self, payment_intent_id: str) -> Optional[PaymentIntent]:
        """Get Stripe payment intent by ID."""
        try:
            stripe_pi = stripe.PaymentIntent.retrieve(payment_intent_id)
            return self._convert_stripe_payment_intent(stripe_pi)
        except stripe.error.InvalidRequestError:
            return None
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get Stripe payment intent: {e}")
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
        """Update Stripe payment intent."""
        try:
            params = {}
            if amount is not None:
                params['amount'] = self.format_amount_for_api(amount, currency or 'usd')
            if currency is not None:
                params['currency'] = currency.lower()
            if customer_id is not None:
                params['customer'] = customer_id
            if payment_method_id is not None:
                params['payment_method'] = payment_method_id
            if description is not None:
                params['description'] = description
            if receipt_email is not None:
                params['receipt_email'] = receipt_email
            if metadata is not None:
                params['metadata'] = metadata
            
            stripe_pi = stripe.PaymentIntent.modify(payment_intent_id, **params)
            return self._convert_stripe_payment_intent(stripe_pi)
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to update Stripe payment intent: {e}")
            raise ServiceUnavailableError(f"Failed to update payment intent: {e}", "payment")
    
    async def confirm_payment_intent(
        self,
        payment_intent_id: str,
        payment_method_id: Optional[str] = None
    ) -> PaymentIntent:
        """Confirm Stripe payment intent."""
        try:
            params = {}
            if payment_method_id:
                params['payment_method'] = payment_method_id
            
            stripe_pi = stripe.PaymentIntent.confirm(payment_intent_id, **params)
            return self._convert_stripe_payment_intent(stripe_pi)
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to confirm Stripe payment intent: {e}")
            raise ServiceUnavailableError(f"Failed to confirm payment intent: {e}", "payment")
    
    async def cancel_payment_intent(self, payment_intent_id: str) -> PaymentIntent:
        """Cancel Stripe payment intent."""
        try:
            stripe_pi = stripe.PaymentIntent.cancel(payment_intent_id)
            return self._convert_stripe_payment_intent(stripe_pi)
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel Stripe payment intent: {e}")
            raise ServiceUnavailableError(f"Failed to cancel payment intent: {e}", "payment")
    
    async def capture_payment_intent(
        self,
        payment_intent_id: str,
        amount_to_capture: Optional[Decimal] = None
    ) -> PaymentIntent:
        """Capture Stripe payment intent."""
        try:
            params = {}
            if amount_to_capture is not None:
                # Need to get current PI to determine currency
                current_pi = stripe.PaymentIntent.retrieve(payment_intent_id)
                params['amount_to_capture'] = self.format_amount_for_api(
                    amount_to_capture, current_pi.currency
                )
            
            stripe_pi = stripe.PaymentIntent.capture(payment_intent_id, **params)
            return self._convert_stripe_payment_intent(stripe_pi)
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to capture Stripe payment intent: {e}")
            raise ServiceUnavailableError(f"Failed to capture payment intent: {e}", "payment")
    
    async def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get Stripe charge (transaction) by ID."""
        try:
            stripe_charge = stripe.Charge.retrieve(transaction_id)
            return self._convert_stripe_charge(stripe_charge)
        except stripe.error.InvalidRequestError:
            return None
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get Stripe transaction: {e}")
            raise ServiceUnavailableError(f"Failed to get transaction: {e}", "payment")
    
    async def list_transactions(
        self,
        customer_id: Optional[str] = None,
        payment_intent_id: Optional[str] = None,
        limit: int = 10,
        starting_after: Optional[str] = None
    ) -> List[Transaction]:
        """List Stripe charges (transactions)."""
        try:
            params = {'limit': limit}
            if customer_id:
                params['customer'] = customer_id
            if payment_intent_id:
                params['payment_intent'] = payment_intent_id
            if starting_after:
                params['starting_after'] = starting_after
            
            stripe_charges = stripe.Charge.list(**params)
            
            transactions = []
            for stripe_charge in stripe_charges.data:
                transaction = self._convert_stripe_charge(stripe_charge)
                transactions.append(transaction)
            
            return transactions
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to list Stripe transactions: {e}")
            raise ServiceUnavailableError(f"Failed to list transactions: {e}", "payment")
    
    async def create_refund(self, refund_request: RefundRequest) -> Refund:
        """Create Stripe refund."""
        try:
            params = {'charge': refund_request.transaction_id}
            
            if refund_request.amount is not None:
                # Get charge to determine currency
                stripe_charge = stripe.Charge.retrieve(refund_request.transaction_id)
                params['amount'] = self.format_amount_for_api(
                    refund_request.amount, stripe_charge.currency
                )
            
            if refund_request.reason:
                params['reason'] = refund_request.reason
            if refund_request.metadata:
                params['metadata'] = refund_request.metadata
            
            stripe_refund = stripe.Refund.create(**params)
            return self._convert_stripe_refund(stripe_refund)
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe refund: {e}")
            raise ServiceUnavailableError(f"Failed to create refund: {e}", "payment")
    
    async def get_refund(self, refund_id: str) -> Optional[Refund]:
        """Get Stripe refund by ID."""
        try:
            stripe_refund = stripe.Refund.retrieve(refund_id)
            return self._convert_stripe_refund(stripe_refund)
        except stripe.error.InvalidRequestError:
            return None
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get Stripe refund: {e}")
            raise ServiceUnavailableError(f"Failed to get refund: {e}", "payment")
    
    async def list_refunds(
        self,
        transaction_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Refund]:
        """List Stripe refunds."""
        try:
            params = {'limit': limit}
            if transaction_id:
                params['charge'] = transaction_id
            
            stripe_refunds = stripe.Refund.list(**params)
            
            refunds = []
            for stripe_refund in stripe_refunds.data:
                refund = self._convert_stripe_refund(stripe_refund)
                refunds.append(refund)
            
            return refunds
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to list Stripe refunds: {e}")
            raise ServiceUnavailableError(f"Failed to list refunds: {e}", "payment")
    
    async def validate_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        webhook_secret: str
    ) -> bool:
        """Validate Stripe webhook signature."""
        try:
            stripe.Webhook.construct_event(payload, signature, webhook_secret)
            return True
        except (stripe.error.SignatureVerificationError, ValueError):
            return False
    
    def _convert_stripe_customer(self, stripe_customer) -> Customer:
        """Convert Stripe customer to Customer object."""
        return Customer(
            id=stripe_customer.id,
            email=stripe_customer.email,
            name=stripe_customer.name,
            phone=stripe_customer.phone,
            description=stripe_customer.description,
            created_at=datetime.fromtimestamp(stripe_customer.created, timezone.utc),
            default_payment_method=stripe_customer.default_source,
            metadata=dict(stripe_customer.metadata) if stripe_customer.metadata else {}
        )
    
    def _convert_stripe_payment_method(self, stripe_pm) -> PaymentMethod:
        """Convert Stripe payment method to PaymentMethod object."""
        pm_type = self._convert_from_stripe_payment_method_type(stripe_pm.type)
        
        # Extract type-specific details
        last4 = None
        brand = None
        exp_month = None
        exp_year = None
        country = None
        funding = None
        
        if stripe_pm.type == 'card' and stripe_pm.card:
            last4 = stripe_pm.card.last4
            brand = stripe_pm.card.brand
            exp_month = stripe_pm.card.exp_month
            exp_year = stripe_pm.card.exp_year
            country = stripe_pm.card.country
            funding = stripe_pm.card.funding
        
        return PaymentMethod(
            id=stripe_pm.id,
            type=pm_type,
            last4=last4,
            brand=brand,
            exp_month=exp_month,
            exp_year=exp_year,
            country=country,
            funding=funding,
            metadata=dict(stripe_pm.metadata) if stripe_pm.metadata else {}
        )
    
    def _convert_stripe_payment_intent(self, stripe_pi) -> PaymentIntent:
        """Convert Stripe payment intent to PaymentIntent object."""
        status = self._convert_stripe_payment_status(stripe_pi.status)
        
        return PaymentIntent(
            id=stripe_pi.id,
            amount=self.format_amount_from_api(stripe_pi.amount, stripe_pi.currency),
            currency=stripe_pi.currency.upper(),
            status=status,
            customer_id=stripe_pi.customer,
            payment_method_id=stripe_pi.payment_method,
            description=stripe_pi.description,
            receipt_email=stripe_pi.receipt_email,
            created_at=datetime.fromtimestamp(stripe_pi.created, timezone.utc),
            client_secret=stripe_pi.client_secret,
            confirmation_method=stripe_pi.confirmation_method,
            metadata=dict(stripe_pi.metadata) if stripe_pi.metadata else {}
        )
    
    def _convert_stripe_charge(self, stripe_charge) -> Transaction:
        """Convert Stripe charge to Transaction object."""
        status = self._convert_stripe_payment_status(stripe_charge.status)
        
        fee_amount = Decimal('0')
        if stripe_charge.balance_transaction:
            bt = stripe.BalanceTransaction.retrieve(stripe_charge.balance_transaction)
            fee_amount = self.format_amount_from_api(bt.fee, stripe_charge.currency)
        
        return Transaction(
            id=stripe_charge.id,
            payment_intent_id=stripe_charge.payment_intent,
            amount=self.format_amount_from_api(stripe_charge.amount, stripe_charge.currency),
            currency=stripe_charge.currency.upper(),
            status=status,
            customer_id=stripe_charge.customer,
            payment_method_id=stripe_charge.payment_method,
            description=stripe_charge.description,
            receipt_url=stripe_charge.receipt_url,
            refunded_amount=self.format_amount_from_api(
                stripe_charge.amount_refunded, stripe_charge.currency
            ),
            fee_amount=fee_amount,
            created_at=datetime.fromtimestamp(stripe_charge.created, timezone.utc),
            metadata=dict(stripe_charge.metadata) if stripe_charge.metadata else {}
        )
    
    def _convert_stripe_refund(self, stripe_refund) -> Refund:
        """Convert Stripe refund to Refund object."""
        status = self._convert_stripe_payment_status(stripe_refund.status)
        
        return Refund(
            id=stripe_refund.id,
            transaction_id=stripe_refund.charge,
            amount=self.format_amount_from_api(stripe_refund.amount, stripe_refund.currency),
            currency=stripe_refund.currency.upper(),
            reason=stripe_refund.reason,
            status=status,
            created_at=datetime.fromtimestamp(stripe_refund.created, timezone.utc),
            metadata=dict(stripe_refund.metadata) if stripe_refund.metadata else {}
        )
    
    def _convert_to_stripe_payment_method_type(self, pm_type: PaymentMethodType) -> str:
        """Convert PaymentMethodType to Stripe type."""
        mapping = {
            PaymentMethodType.CARD: 'card',
            PaymentMethodType.BANK_ACCOUNT: 'us_bank_account',
            PaymentMethodType.PAYPAL: 'paypal',
            PaymentMethodType.APPLE_PAY: 'card',  # Apple Pay uses card
            PaymentMethodType.GOOGLE_PAY: 'card',  # Google Pay uses card
        }
        return mapping.get(pm_type, 'card')
    
    def _convert_from_stripe_payment_method_type(self, stripe_type: str) -> PaymentMethodType:
        """Convert Stripe type to PaymentMethodType."""
        mapping = {
            'card': PaymentMethodType.CARD,
            'us_bank_account': PaymentMethodType.BANK_ACCOUNT,
            'sepa_debit': PaymentMethodType.BANK_ACCOUNT,
            'paypal': PaymentMethodType.PAYPAL,
        }
        return mapping.get(stripe_type, PaymentMethodType.OTHER)
    
    def _convert_stripe_payment_status(self, stripe_status: str) -> PaymentStatus:
        """Convert Stripe status to PaymentStatus."""
        mapping = {
            'requires_payment_method': PaymentStatus.PENDING,
            'requires_confirmation': PaymentStatus.PENDING,
            'requires_action': PaymentStatus.PENDING,
            'processing': PaymentStatus.PROCESSING,
            'requires_capture': PaymentStatus.PROCESSING,
            'canceled': PaymentStatus.CANCELLED,
            'succeeded': PaymentStatus.SUCCEEDED,
            'failed': PaymentStatus.FAILED,
        }
        return mapping.get(stripe_status, PaymentStatus.PENDING)
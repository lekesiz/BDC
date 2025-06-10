"""
Base payment integration functionality.
"""

from abc import abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal

from ..base import BaseIntegration, IntegrationConfig


class PaymentStatus(Enum):
    """Payment status."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentMethodType(Enum):
    """Payment method types."""
    CARD = "card"
    BANK_ACCOUNT = "bank_account"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    OTHER = "other"


@dataclass
class PaymentMethod:
    """Represents a payment method."""
    id: str
    type: PaymentMethodType
    last4: Optional[str] = None
    brand: Optional[str] = None
    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    country: Optional[str] = None
    funding: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Customer:
    """Represents a customer."""
    id: str
    email: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    default_payment_method: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PaymentIntent:
    """Represents a payment intent."""
    id: str
    amount: Decimal
    currency: str
    status: PaymentStatus
    customer_id: Optional[str] = None
    payment_method_id: Optional[str] = None
    description: Optional[str] = None
    receipt_email: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    client_secret: Optional[str] = None
    confirmation_method: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Transaction:
    """Represents a completed transaction."""
    id: str
    payment_intent_id: str
    amount: Decimal
    currency: str
    status: PaymentStatus
    customer_id: Optional[str] = None
    payment_method_id: Optional[str] = None
    description: Optional[str] = None
    receipt_url: Optional[str] = None
    refunded_amount: Decimal = Decimal('0')
    fee_amount: Decimal = Decimal('0')
    net_amount: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.net_amount is None:
            self.net_amount = self.amount - self.fee_amount


@dataclass
class RefundRequest:
    """Request for refunding a payment."""
    transaction_id: str
    amount: Optional[Decimal] = None  # None = full refund
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Refund:
    """Represents a refund."""
    id: str
    transaction_id: str
    amount: Decimal
    currency: str
    reason: Optional[str] = None
    status: PaymentStatus = PaymentStatus.SUCCEEDED
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BasePaymentIntegration(BaseIntegration):
    """Base class for payment integrations."""
    
    @property
    def integration_type(self) -> str:
        return "payment"
    
    @abstractmethod
    async def create_customer(
        self,
        email: Optional[str] = None,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Customer:
        """Create a new customer."""
        pass
    
    @abstractmethod
    async def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID."""
        pass
    
    @abstractmethod
    async def update_customer(
        self,
        customer_id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Customer:
        """Update customer information."""
        pass
    
    @abstractmethod
    async def delete_customer(self, customer_id: str) -> bool:
        """Delete a customer."""
        pass
    
    @abstractmethod
    async def create_payment_method(
        self,
        type: PaymentMethodType,
        customer_id: Optional[str] = None,
        **kwargs
    ) -> PaymentMethod:
        """Create a payment method."""
        pass
    
    @abstractmethod
    async def get_payment_method(self, payment_method_id: str) -> Optional[PaymentMethod]:
        """Get payment method by ID."""
        pass
    
    @abstractmethod
    async def list_payment_methods(
        self,
        customer_id: str,
        type: Optional[PaymentMethodType] = None
    ) -> List[PaymentMethod]:
        """List payment methods for a customer."""
        pass
    
    @abstractmethod
    async def detach_payment_method(self, payment_method_id: str) -> bool:
        """Detach payment method from customer."""
        pass
    
    @abstractmethod
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
        """Create a payment intent."""
        pass
    
    @abstractmethod
    async def get_payment_intent(self, payment_intent_id: str) -> Optional[PaymentIntent]:
        """Get payment intent by ID."""
        pass
    
    @abstractmethod
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
        """Update payment intent."""
        pass
    
    @abstractmethod
    async def confirm_payment_intent(
        self,
        payment_intent_id: str,
        payment_method_id: Optional[str] = None
    ) -> PaymentIntent:
        """Confirm a payment intent."""
        pass
    
    @abstractmethod
    async def cancel_payment_intent(self, payment_intent_id: str) -> PaymentIntent:
        """Cancel a payment intent."""
        pass
    
    @abstractmethod
    async def capture_payment_intent(
        self,
        payment_intent_id: str,
        amount_to_capture: Optional[Decimal] = None
    ) -> PaymentIntent:
        """Capture a payment intent (for manual confirmation)."""
        pass
    
    @abstractmethod
    async def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get transaction by ID."""
        pass
    
    @abstractmethod
    async def list_transactions(
        self,
        customer_id: Optional[str] = None,
        payment_intent_id: Optional[str] = None,
        limit: int = 10,
        starting_after: Optional[str] = None
    ) -> List[Transaction]:
        """List transactions with optional filters."""
        pass
    
    @abstractmethod
    async def create_refund(self, refund_request: RefundRequest) -> Refund:
        """Create a refund for a transaction."""
        pass
    
    @abstractmethod
    async def get_refund(self, refund_id: str) -> Optional[Refund]:
        """Get refund by ID."""
        pass
    
    @abstractmethod
    async def list_refunds(
        self,
        transaction_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Refund]:
        """List refunds with optional filters."""
        pass
    
    async def calculate_fee(
        self,
        amount: Decimal,
        currency: str,
        payment_method_type: PaymentMethodType
    ) -> Decimal:
        """Calculate processing fee for a payment."""
        # Default implementation - can be overridden by specific providers
        # Standard rate: 2.9% + $0.30 for cards
        if payment_method_type == PaymentMethodType.CARD:
            percentage_fee = amount * Decimal('0.029')
            fixed_fee = Decimal('0.30') if currency.lower() == 'usd' else Decimal('0')
            return percentage_fee + fixed_fee
        return Decimal('0')
    
    async def validate_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        webhook_secret: str
    ) -> bool:
        """Validate webhook signature."""
        # Default implementation - should be overridden by providers
        return True
    
    def format_amount_for_api(self, amount: Decimal, currency: str) -> int:
        """Convert decimal amount to API format (usually cents)."""
        # Most APIs expect amounts in cents for currencies like USD, EUR
        zero_decimal_currencies = ['jpy', 'krw', 'clp', 'pyg']
        if currency.lower() in zero_decimal_currencies:
            return int(amount)
        return int(amount * 100)
    
    def format_amount_from_api(self, amount: int, currency: str) -> Decimal:
        """Convert API amount format to decimal."""
        zero_decimal_currencies = ['jpy', 'krw', 'clp', 'pyg']
        if currency.lower() in zero_decimal_currencies:
            return Decimal(amount)
        return Decimal(amount) / 100
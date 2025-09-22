from typing import List, Optional, Dict, Any, Literal
import requests
from pydantic import BaseModel

# Request Models
class CreateEventRequest(BaseModel):
    external_id: str
    unit: str
    value: float
    properties: Optional[Dict[str, str]] = None

class BillingAddress(BaseModel):
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

class CreateCustomerRequest(BaseModel):
    name: str
    external_id: str
    email: str
    payment_provider: Optional[str] = None
    payment_provider_id: Optional[str] = None
    billing_address: Optional[BillingAddress] = None
    plan: Optional[str] = None

class UpdateCustomerRequest(BaseModel):
    name: str
    email: str
    external_id: str
    billing_address: Optional[BillingAddress] = None

# Response Models
class Unit(BaseModel):
    id: str
    created_at: str
    organization_id: str
    type: Literal["variable", "fixed"]
    name: str
    key: str
    archived_at: Optional[str] = None

class Customer(BaseModel):
    id: str
    created_at: str
    name: str
    email: str
    billing_address: Optional[BillingAddress] = None
    organization_id: str
    external_id: str
    payment_provider: str
    payment_provider_id: str
    portal_token: Optional[str] = None
    archived_at: Optional[str] = None
    balance: str

class Contract(BaseModel):
    id: str
    created_at: str
    customer_id: str
    anchor: Optional[str] = None
    status: Literal["active", "pending", "canceled"]
    next_billing_date: Optional[str] = None

class CustomerWithContract(Customer):
    contract: Contract


class Event(BaseModel):
    id: str
    created_at: str
    customer_id: str
    unit_id: str
    value: float
    properties: Optional[Dict[str, str]] = None
    idempotency_key: Optional[str] = None

class EventDetails(BaseModel):
    id: str
    created_at: str
    customer_id: str
    unit_id: str
    value: str
    properties: Optional[Dict[str, str]] = None
    customer_name: str

class LineItem(BaseModel):
    id: str
    created_at: str
    invoice_id: str
    description: str
    quantity: float
    price: float
    amount: float
    pricing_rule_id: Optional[str] = None

class Invoice(BaseModel):
    id: str
    created_at: str
    issued_at: Optional[str] = None
    due_at: Optional[str] = None
    paid_at: Optional[str] = None
    voided_at: Optional[str] = None
    customer_id: str
    status: Literal["draft", "issued", "paid", "overdue", "void"]
    amount: float
    subtotal: float
    tax_amount: float
    total: float
    period_start: str
    period_end: str
    provider: Literal["skope", "stripe"]
    provider_invoice_id: Optional[str] = None

class InvoiceWithLineItems(Invoice):
    line_items: List[LineItem]
    customer_name: Optional[str] = None

class UsageResponse(BaseModel):
    usage: Dict[str, Any]

class PaginationMetadata(BaseModel):
    limit: int
    has_more: bool
    next_cursor: Optional[str] = None
    previous_cursor: Optional[str] = None

class PricingRule(BaseModel):
    id: str
    created_at: str
    price: Optional[float] = None
    limit: Optional[int] = None
    unit_id: Optional[str] = None
    plan_id: Optional[str] = None
    customer_id: Optional[str] = None
    multiplier: Optional[int] = None
    aggregation_type: Optional[Literal["SUM", "LAST", "COUNT"]] = None
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    rates: Optional[Dict[str, float]] = None
    rate_field: Optional[str] = None

class PricingRuleWithUnit(PricingRule):
    unit: Unit

class CustomerPricing(BaseModel):
    pricing_rules: List[PricingRuleWithUnit]
    plan: Optional[str] = None

class UpdateCustomerPricingRequest(BaseModel):
    plan: Optional[str] = None
    apply_immediately: bool = False

class EventsEnqueueResponse(BaseModel):
    job_id: str
    status: Literal["enqueued"]
    events_count: int

class EventsAPI:
    def __init__(self, session: requests.Session, base_url: str):
        self.session = session
        self.base_url = base_url

    def create(self, events: List[CreateEventRequest]) -> EventsEnqueueResponse:
        """Upload multiple events to Skope in batch.

        Args:
            events: List of CreateEventRequest objects to upload

        Returns:
            EventsEnqueueResponse containing job details

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self.session.post(
            f"{self.base_url}/v1/events",
            json=[event.model_dump() for event in events]
        )
        response.raise_for_status()
        return EventsEnqueueResponse(**response.json())

    def get(self, customer_id: Optional[str] = None, external_id: Optional[str] = None, limit: int = 50, cursor: Optional[str] = None, cursor_direction: str = "next") -> Dict[str, Any]:
        """Get events from Skope.

        Args:
            customer_id: Optional customer ID to filter events for specific customer
            external_id: Optional external ID to filter events for specific customer
            limit: Number of items to return (default: 50)
            cursor: Cursor for cursor-based pagination
            cursor_direction: Direction for cursor pagination ("next" or "previous")

        Returns:
            Dict containing data (list of EventDetails) and pagination metadata

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        params = {"limit": limit, "cursor_direction": cursor_direction}
        if customer_id:
            params["customer_id"] = customer_id
        if external_id:
            params["external_id"] = external_id
        if cursor:
            params["cursor"] = cursor

        response = self.session.get(
            f"{self.base_url}/v1/events",
            params=params
        )
        response.raise_for_status()
        result = response.json()
        return {
            "data": [EventDetails(**event) for event in result["data"]],
            "pagination": PaginationMetadata(**result["pagination"])
        }

class InvoicesAPI:
    def __init__(self, session: requests.Session, base_url: str):
        self.session = session
        self.base_url = base_url

    def get(self, customer_id: Optional[str] = None, external_id: Optional[str] = None, limit: int = 50, cursor: Optional[str] = None, cursor_direction: str = "next") -> Dict[str, Any]:
        """Get invoices from Skope.

        Args:
            customer_id: Optional customer ID to filter invoices for specific customer
            external_id: Optional external ID to filter invoices for specific customer
            limit: Number of items to return (default: 50)
            cursor: Cursor for cursor-based pagination
            cursor_direction: Direction for cursor pagination ("next" or "previous")

        Returns:
            Dict containing data (list of InvoiceWithLineItems) and pagination metadata

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        params = {"limit": limit, "cursor_direction": cursor_direction}
        if customer_id:
            params["customer_id"] = customer_id
        if external_id:
            params["external_id"] = external_id
        if cursor:
            params["cursor"] = cursor

        response = self.session.get(
            f"{self.base_url}/v1/invoices",
            params=params
        )
        response.raise_for_status()
        result = response.json()
        return {
            "data": [InvoiceWithLineItems(**invoice) for invoice in result["data"]],
            "pagination": PaginationMetadata(**result["pagination"])
        }

    def get_pdf(self, invoice_id: str):
        """Get invoice PDF.
        
        Args:
            invoice_id: ID of the invoice to get PDF for
            
        Returns:
            PDF content
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self.session.get(
            f"{self.base_url}/v1/invoices/{invoice_id}/pdf"
        )
        response.raise_for_status()
        return response.content

class CustomersAPI:
    def __init__(self, session: requests.Session, base_url: str):
        self.session = session
        self.base_url = base_url

    def list(self, limit: int = 50, cursor: Optional[str] = None, cursor_direction: str = "next") -> Dict[str, Any]:
        """Get customers from Skope.

        Args:
            limit: Number of items to return (default: 50)
            cursor: Cursor for cursor-based pagination
            cursor_direction: Direction for cursor pagination ("next" or "previous")

        Returns:
            Dict containing data (list of CustomerWithContract) and pagination metadata

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        params = {"limit": limit, "cursor_direction": cursor_direction}
        if cursor:
            params["cursor"] = cursor

        response = self.session.get(
            f"{self.base_url}/v1/customers",
            params=params
        )
        response.raise_for_status()
        result = response.json()
        return {
            "data": [CustomerWithContract(**customer) for customer in result["data"]],
            "pagination": PaginationMetadata(**result["pagination"])
        }

    def get(self, external_id: str) -> CustomerWithContract:
        """Get customer by external ID.
        
        Args:
            external_id: External ID of the customer
            
        Returns:
            CustomerWithContract object
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self.session.get(
            f"{self.base_url}/v1/customers/external-id/{external_id}"
        )
        response.raise_for_status()
        return CustomerWithContract(**response.json())

    def create(self, req: CreateCustomerRequest) -> Customer:
        """Create a customer.
        
        Args:
            req: CreateCustomerRequest object with customer details
            
        Returns:
            Customer object
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self.session.post(
            f"{self.base_url}/v1/customers",
            json=req.model_dump()
        )
        response.raise_for_status()
        return Customer(**response.json())

    def update(self, external_id: str, req: UpdateCustomerRequest) -> Customer:
        """Update customer by external ID.
        
        Args:
            external_id: External ID of the customer
            req: UpdateCustomerRequest object with updated details
            
        Returns:
            Customer object
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self.session.put(
            f"{self.base_url}/v1/customers/external-id/{external_id}",
            json=req.model_dump()
        )
        response.raise_for_status()
        return Customer(**response.json())

    def archive(self, external_id: str) -> Customer:
        """Archive customer by external ID.
        
        Args:
            external_id: External ID of the customer
            
        Returns:
            Customer object
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self.session.delete(
            f"{self.base_url}/v1/customers/external-id/{external_id}"
        )
        response.raise_for_status()
        return Customer(**response.json())

    def activate_contract(self, external_id: str) -> Contract:
        """Activate contract for customer by external ID.
        
        Args:
            external_id: External ID of the customer
            
        Returns:
            Contract object
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self.session.post(
            f"{self.base_url}/v1/customers/external-id/{external_id}/contract/activate"
        )
        response.raise_for_status()
        return Contract(**response.json())

    def cancel_contract(self, external_id: str) -> Contract:
        """Cancel contract for customer by external ID.

        Args:
            external_id: External ID of the customer

        Returns:
            Contract object

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self.session.post(
            f"{self.base_url}/v1/customers/external-id/{external_id}/contract/cancel"
        )
        response.raise_for_status()
        return Contract(**response.json())

    def get_usage(self, external_id: str, unit: str) -> UsageResponse:
        """Get usage for customer by external ID and unit.

        Args:
            external_id: External ID of the customer
            unit: Unit to get usage for

        Returns:
            UsageResponse object

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self.session.get(
            f"{self.base_url}/v1/customers/external-id/{external_id}/usage",
            params={"unit": unit}
        )
        response.raise_for_status()
        return UsageResponse(usage=response.json())

    def get_pricing(self, external_id: str, status: str = "active") -> CustomerPricing:
        """Get pricing rules for customer by external ID.

        Args:
            external_id: External ID of the customer
            status: Status filter for pricing rules (default: "active")

        Returns:
            CustomerPricing object

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self.session.get(
            f"{self.base_url}/v1/customers/external-id/{external_id}/pricing",
            params={"status": status}
        )
        response.raise_for_status()
        return CustomerPricing(**response.json())

    def update_pricing(self, external_id: str, req: UpdateCustomerPricingRequest) -> CustomerPricing:
        """Update pricing rules for customer by external ID.

        Args:
            external_id: External ID of the customer
            req: UpdateCustomerPricingRequest object with pricing updates

        Returns:
            CustomerPricing object

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self.session.put(
            f"{self.base_url}/v1/customers/external-id/{external_id}/pricing",
            json=req.model_dump()
        )
        response.raise_for_status()
        return CustomerPricing(**response.json())

class Skope:
    def __init__(self, api_key: str, base_url: str = "https://api.useskope.com"):
        """Initialize the Skope client.
        
        Args:
            api_key: Your Skope API key
            base_url: The base URL of the Skope API (default: https://api.useskope.com)
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        })
        
        # Initialize namespaced APIs
        self.customers = CustomersAPI(self.session, self.base_url)
        self.events = EventsAPI(self.session, self.base_url)
        self.invoices = InvoicesAPI(self.session, self.base_url)

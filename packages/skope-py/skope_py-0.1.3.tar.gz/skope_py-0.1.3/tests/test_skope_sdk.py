import pytest
from unittest.mock import Mock, patch
import requests
from skope import Skope, CreateEventRequest


class TestCreateEventRequest:
    def test_event_creation(self):
        event = CreateEventRequest(
            external_id="customer_123",
            unit="requests",
            value=10.0,
        )
        assert event.external_id == "customer_123"
        assert event.unit == "requests"
        assert event.value == 10.0

    def test_event_creation_with_properties(self):
        event = CreateEventRequest(
            external_id="customer_123",
            unit="requests",
            value=10.0,
            properties={"region": "us-east-1"}
        )
        assert event.properties == {"region": "us-east-1"}

class TestSkope:
    def test_client_initialization_default_url(self):
        client = Skope("test_api_key")
        assert client.base_url == "https://api.useskope.com"
        assert client.session.headers["x-api-key"] == "test_api_key"
        assert client.session.headers["Content-Type"] == "application/json"
        # Test that namespaced APIs are initialized
        assert client.events is not None
        assert client.invoices is not None
        assert client.customers is not None

    def test_client_initialization_custom_url(self):
        custom_url = "https://custom.api.com/"
        client = Skope("test_key", custom_url)
        assert client.base_url == "https://custom.api.com"

    @patch('skope.requests.Session.post')
    def test_events_create_success(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"job_id": "job_123", "status": "enqueued", "events_count": 2}
        mock_post.return_value = mock_response

        client = Skope("test_key")
        events = [
            CreateEventRequest(external_id="cust1", unit="units", value=10.0),
            CreateEventRequest(external_id="cust2", unit="requests", value=20.0)
        ]

        result = client.events.create(events)

        mock_post.assert_called_once_with(
            "https://api.useskope.com/v1/events",
            json=[
                {"external_id": "cust1", "unit": "units", "value": 10.0, "properties": None},
                {"external_id": "cust2", "unit": "requests", "value": 20.0, "properties": None}
            ]
        )
        mock_response.raise_for_status.assert_called_once()
        assert result.job_id == "job_123"
        assert result.status == "enqueued"
        assert result.events_count == 2

    @patch('skope.requests.Session.post')
    def test_events_create_http_error(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("API Error")
        mock_post.return_value = mock_response

        client = Skope("test_key")
        events = [CreateEventRequest(external_id="cust", unit="units", value=10.0)]

        with pytest.raises(requests.exceptions.HTTPError):
            client.events.create(events)

    def test_events_create_empty_list(self):
        with patch('skope.requests.Session.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"job_id": "job_456", "status": "enqueued", "events_count": 0}
            mock_post.return_value = mock_response

            client = Skope("test_key")
            result = client.events.create([])

            mock_post.assert_called_once_with(
                "https://api.useskope.com/v1/events",
                json=[]
            )
            assert result.job_id == "job_456"
            assert result.status == "enqueued"
            assert result.events_count == 0

    @patch('skope.requests.Session.get')
    def test_events_get_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "event_123",
                    "created_at": "2023-01-01T00:00:00Z",
                    "customer_id": "cust_123",
                    "unit_id": "unit_123",
                    "value": "10.0",
                    "properties": None,
                    "customer_name": "Test User"
                }
            ],
            "pagination": {
                "limit": 50,
                "has_more": False,
                "next_cursor": None,
                "previous_cursor": None
            }
        }
        mock_get.return_value = mock_response

        client = Skope("test_key")
        result = client.events.get()

        mock_get.assert_called_once_with(
            "https://api.useskope.com/v1/events",
            params={"limit": 50, "cursor_direction": "next"}
        )
        mock_response.raise_for_status.assert_called_once()
        assert len(result["data"]) == 1
        assert result["data"][0].id == "event_123"
        assert result["data"][0].customer_name == "Test User"
        assert result["pagination"].limit == 50
        assert result["pagination"].has_more == False

    @patch('skope.requests.Session.get')
    def test_events_get_with_customer_id(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [],
            "pagination": {
                "limit": 50,
                "has_more": False,
                "next_cursor": None,
                "previous_cursor": None
            }
        }
        mock_get.return_value = mock_response

        client = Skope("test_key")
        client.events.get(customer_id="test_customer")

        mock_get.assert_called_once_with(
            "https://api.useskope.com/v1/events",
            params={"customer_id": "test_customer", "limit": 50, "cursor_direction": "next"}
        )

    @patch('skope.requests.Session.get')
    def test_invoices_get_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "inv_123",
                    "created_at": "2023-01-01T00:00:00Z",
                    "issued_at": None,
                    "due_at": None,
                    "paid_at": None,
                    "voided_at": None,
                    "customer_id": "rel_123",
                    "status": "paid",
                    "amount": 100.0,
                    "subtotal": 90.0,
                    "tax_amount": 10.0,
                    "total": 100.0,
                    "period_start": "2023-01-01T00:00:00Z",
                    "period_end": "2023-01-31T23:59:59Z",
                    "provider": "skope",
                    "provider_invoice_id": None,
                    "line_items": [],
                    "customer_name": "Test User"
                }
            ],
            "pagination": {
                "limit": 50,
                "has_more": False,
                "next_cursor": None,
                "previous_cursor": None
            }
        }
        mock_get.return_value = mock_response

        client = Skope("test_key")
        result = client.invoices.get()

        mock_get.assert_called_once_with(
            "https://api.useskope.com/v1/invoices",
            params={"limit": 50, "cursor_direction": "next"}
        )
        assert len(result["data"]) == 1
        assert result["data"][0].id == "inv_123"
        assert result["data"][0].status == "paid"

    @patch('skope.requests.Session.get')
    def test_customers_get_usage_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "used": 50,
            "remaining": 50,
            "limit": 100
        }
        mock_get.return_value = mock_response

        client = Skope("test_key")
        result = client.customers.get_usage("user_123", "requests")

        mock_get.assert_called_once_with(
            "https://api.useskope.com/v1/customers/external-id/user_123/usage",
            params={"unit": "requests"}
        )
        assert result.usage["used"] == 50
        assert result.usage["remaining"] == 50
        assert result.usage["limit"] == 100

    @patch('skope.requests.Session.get')
    def test_customers_get_pricing_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "pricing_rules": [
                {
                    "id": "rule_123",
                    "created_at": "2023-01-01T00:00:00Z",
                    "price": 10.0,
                    "limit": None,
                    "unit_id": "unit_123",
                    "plan_id": None,
                    "customer_id": "cust_123",
                    "multiplier": None,
                    "aggregation_type": "SUM",
                    "effective_from": None,
                    "effective_to": None,
                    "rates": None,
                    "rate_field": None,
                    "unit": {
                        "id": "unit_123",
                        "created_at": "2023-01-01T00:00:00Z",
                        "organization_id": "org_123",
                        "type": "variable",
                        "name": "API Requests",
                        "key": "api_requests",
                        "archived_at": None
                    }
                }
            ],
            "plan": "basic_plan"
        }
        mock_get.return_value = mock_response

        client = Skope("test_key")
        result = client.customers.get_pricing("user_123")

        mock_get.assert_called_once_with(
            "https://api.useskope.com/v1/customers/external-id/user_123/pricing",
            params={"status": "active"}
        )
        assert len(result.pricing_rules) == 1
        assert result.pricing_rules[0].price == 10.0
        assert result.plan == "basic_plan"

    @patch('skope.requests.Session.put')
    def test_customers_update_pricing_success(self, mock_put):
        from skope import UpdateCustomerPricingRequest

        mock_response = Mock()
        mock_response.json.return_value = {
            "pricing_rules": [],
            "plan": "premium_plan"
        }
        mock_put.return_value = mock_response

        client = Skope("test_key")
        req = UpdateCustomerPricingRequest(plan="premium_plan", apply_immediately=True)
        result = client.customers.update_pricing("user_123", req)

        mock_put.assert_called_once_with(
            "https://api.useskope.com/v1/customers/external-id/user_123/pricing",
            json={"plan": "premium_plan", "apply_immediately": True}
        )
        assert result.plan == "premium_plan"
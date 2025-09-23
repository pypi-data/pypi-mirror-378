import json
from hashlib import sha256
from types import SimpleNamespace

import httpx
import pytest

from fbnconfig import identity, notifications

TEST_BASE = "https://foo.lusid.com"


@pytest.mark.respx(base_url=TEST_BASE)
class TestSubscriptionRef:
    """Test SubscriptionRef functionality."""

    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [lambda x: x.raise_for_status()]})

    @pytest.fixture
    def subscription_ref(self):
        """Create a subscription reference for testing."""
        return notifications.SubscriptionRef(
            id="test-subscription-ref",
            scope="test",
            code="basic_sub"
        )

    def test_subscription_ref_properties(self, subscription_ref):
        """Test that scope and code are set correctly."""
        assert subscription_ref.scope == "test"
        assert subscription_ref.code == "basic_sub"
        assert subscription_ref.id == "test-subscription-ref"

    def test_subscription_ref_attach_success(self, respx_mock, subscription_ref):
        """Test attach method validates subscription exists."""
        respx_mock.get("/notification/api/subscriptions/test/basic_sub").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": {"scope": "test", "code": "basic_sub"},
                    "displayName": "Test Subscription",
                    "status": "Active"
                }
            )
        )
        # Should not raise an error for existing subscription
        subscription_ref.attach(self.client)

    def test_subscription_ref_attach_not_found(self, respx_mock, subscription_ref):
        """Test attach method raises error for non-existent subscription."""
        respx_mock.get("/notification/api/subscriptions/test/basic_sub").mock(
            return_value=httpx.Response(404)
        )
        with pytest.raises(RuntimeError, match="Subscription test/basic_sub does not exist"):
            subscription_ref.attach(self.client)
        assert "Subscription test/basic_sub does not exist"

    def test_subscription_ref_attach_when_http_error(self, respx_mock, subscription_ref):

        respx_mock.get("/notification/api/subscriptions/test/basic_sub").mock(
            return_value=httpx.Response(500, json={})
        )
        client = self.client
        sut = subscription_ref
        with pytest.raises(httpx.HTTPError):
            sut.attach(client)


@pytest.mark.respx(base_url=TEST_BASE)
class TestSubscriptionResource:
    """Test SubscriptionResource functionality."""
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [lambda x: x.raise_for_status()]})

    @pytest.fixture
    def simple_subscription(self):
        return notifications.SubscriptionResource(
            id="testId",
            scope="test",
            code="basic_sub",
            display_name="Basic Test Subscription",
            description="Testing subscription",
            event_type="Manual",
            status=notifications.SubscriptionStatus.ACTIVE,
            filter="Body.Message eq 'Test'"
        )

    def test_read_subscription(self, respx_mock, simple_subscription):
        respx_mock.get(
            "/notification/api/subscriptions/old_state_scope/old_state_code"
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": {"scope": "old_state_scope", "code": "old_state_code"},
                    "displayName": "Old state display name",
                    "description": "Testing subscription",
                    "status": "Active",
                    "eventType": "Manual",
                    "matchingPattern": {
                        "eventType": "Manual",
                        "filter": "Body.Message eq 'Test'"
                    }
                }
            )
        )
        client = self.client
        old_state = SimpleNamespace(scope="old_state_scope", code="old_state_code")
        response = simple_subscription.read(client, old_state)
        assert response["id"]["scope"] == "old_state_scope"
        assert response["id"]["code"] == "old_state_code"
        assert response["displayName"] == "Old state display name"
        assert response["status"] == "Active"

    def test_read_subscription_raises_on_404(self, respx_mock, simple_subscription):
        """Test that read raises exception on 404 since resource should exist."""
        respx_mock.get(
            f"/notification/api/subscriptions/{simple_subscription.scope}/{simple_subscription.code}"
        ).mock(return_value=httpx.Response(404))

        client = self.client
        old_state = SimpleNamespace(scope="test", code="basic_sub")

        with pytest.raises(httpx.HTTPStatusError):
            simple_subscription.read(client, old_state)

    def test_create_subscription(self, respx_mock, simple_subscription):
        respx_mock.post("/notification/api/subscriptions").mock(
            return_value=httpx.Response(
                200,
                json={"id": {"scope": "test", "code": "basic_sub"}, "status": "Active"}
            )
        )
        client = self.client
        state = simple_subscription.create(client)
        req = respx_mock.calls.last.request
        body = json.loads(req.content)

        # Verify request body structure
        assert body == {
            "eventType": "Manual",
            "status": "Active",
            "description": "Testing subscription",
            "displayName": "Basic Test Subscription",
            "matchingPattern": {
                "eventType": "Manual",
                "filter": "Body.Message eq 'Test'"
            },
            "id": {
                "scope": "test",
                "code": "basic_sub"
            }
        }

        assert state["scope"] == "test"
        assert state["code"] == "basic_sub"
        # Verify version hashes are included
        assert "source_version" in state
        assert "remote_version" in state

    def test_create_subscription_with_no_filter(self, respx_mock):
        respx_mock.post("/notification/api/subscriptions").mock(
            return_value=httpx.Response(
                200,
                json={"id": {"scope": "test", "code": "basic_sub"}, "status": "Active"}
            )
        )
        client = self.client
        simple_sub_no_filter = notifications.SubscriptionResource(
            id="testId",
            scope="test",
            code="basic_sub",
            display_name="Basic Test Subscription",
            description="Testing subscription",
            event_type="Manual",
            status=notifications.SubscriptionStatus.ACTIVE,
        )

        state = simple_sub_no_filter.create(client)
        req = respx_mock.calls.last.request
        body = json.loads(req.content)

        # Verify request body structure - filter not present
        assert body == {
            "eventType": "Manual",
            "status": "Active",
            "description": "Testing subscription",
            "displayName": "Basic Test Subscription",
            "matchingPattern": {
                "eventType": "Manual",
            },
            "id": {
                "scope": "test",
                "code": "basic_sub"
            }
        }

        assert state["scope"] == "test"
        assert state["code"] == "basic_sub"
        # Verify version hashes are included
        assert "source_version" in state
        assert "remote_version" in state

    def test_create_subscription_with_no_description(self, respx_mock):
        respx_mock.post("/notification/api/subscriptions").mock(
            return_value=httpx.Response(
                200,
                json={"id": {"scope": "test", "code": "basic_sub"}, "status": "Active"}
            )
        )
        client = self.client
        simple_sub_no_description = notifications.SubscriptionResource(
            id="testId",
            scope="test",
            code="basic_sub",
            display_name="Basic Test Subscription",
            event_type="Manual",
            status=notifications.SubscriptionStatus.ACTIVE,
            filter="Body.Message eq 'Test'"
        )

        state = simple_sub_no_description.create(client)
        req = respx_mock.calls.last.request
        body = json.loads(req.content)

        # Verify request body structure - description not present
        assert body == {
            "eventType": "Manual",
            "status": "Active",
            "displayName": "Basic Test Subscription",
            "matchingPattern": {
                "eventType": "Manual",
                "filter": "Body.Message eq 'Test'"
            },
            "id": {
                "scope": "test",
                "code": "basic_sub"
            }
        }

        assert state["scope"] == "test"
        assert state["code"] == "basic_sub"
        # Verify version hashes are included
        assert "source_version" in state
        assert "remote_version" in state

    def test_create_subscription_defaults_status(self, respx_mock, simple_subscription):
        respx_mock.post("/notification/api/subscriptions").mock(
            return_value=httpx.Response(
                200,
                json={"id": {"scope": "test", "code": "basic_sub"}, "status": "Active"}
            )
        )
        client = self.client
        simple_sub_no_status = notifications.SubscriptionResource(
            id="testId",
            scope="test",
            code="basic_sub",
            display_name="Basic Test Subscription",
            description="Testing subscription",
            event_type="Manual",
            filter="Body.Message eq 'Test'"
        )

        state = simple_sub_no_status.create(client)
        req = respx_mock.calls.last.request
        body = json.loads(req.content)

        # Verify request body structure - status should default to active
        assert body == {
            "eventType": "Manual",
            "status": "Active",
            "description": "Testing subscription",
            "displayName": "Basic Test Subscription",
            "matchingPattern": {
                "eventType": "Manual",
                "filter": "Body.Message eq 'Test'"
            },
            "id": {
                "scope": "test",
                "code": "basic_sub"
            }
        }

        assert state["scope"] == "test"
        assert state["code"] == "basic_sub"
        # Verify version hashes are included
        assert "source_version" in state
        assert "remote_version" in state

    def test_create_subscription_failure(self, respx_mock, simple_subscription):
        """Test handling of invalid subscription creation."""
        respx_mock.post("/notification/api/subscriptions").mock(
            return_value=httpx.Response(400, json={"error": "Invalid subscription"})
        )
        client = self.client
        with pytest.raises(httpx.HTTPStatusError):
            simple_subscription.create(client)

    def test_update_subscription_without_change(self, respx_mock, simple_subscription):
        """Test update functionality."""
        remote_response = {
            "id": {"scope": "test", "code": "basic_sub"},
            "displayName": "Basic Test Subscription",
            "description": "Testing subscription",
            "status": "Active",
            "eventType": "Manual",
            "matchingPattern": {
                "eventType": "Manual",
                "filter": "Body.Message eq 'Test'"
            }
        }

        respx_mock.get(
            f"/notification/api/subscriptions/{simple_subscription.scope}/{simple_subscription.code}"
        ).mock(
            return_value=httpx.Response(
                200,
                json=remote_response
            )
        )

        # Set source_version hash to the same to test no change
        source_version = simple_subscription.__get_content_hash__()

        remote_hash = sha256(json.dumps(remote_response, sort_keys=True).encode()).hexdigest()

        old_state = SimpleNamespace(
            scope="test",
            code="basic_sub",
            source_version=source_version,
            remote_version=remote_hash)

        # Same hash so we expect to return None
        result = simple_subscription.update(self.client, old_state)
        assert result is None

    def test_update_subscription_with_change(self, respx_mock, simple_subscription):
        """Test update functionality."""
        respx_mock.get(
            "/notification/api/subscriptions/test/basic_sub"
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": {"scope": "test", "code": "basic_sub"},
                    "displayName": "Old state display name",
                    "description": "Testing subscription",
                    "status": "Active",
                    "eventType": "Manual",
                    "matchingPattern": {
                        "eventType": "Manual",
                        "filter": "Body.Message eq 'Test'"
                    }
                }
            )
        )
        respx_mock.put("/notification/api/subscriptions/test/basic_sub").mock(
            return_value=httpx.Response(
                200,
                json={
                }
            )
        )
        old_state = SimpleNamespace(
            scope="test",
            code="basic_sub",
            source_version="different_source",
            remote_version="different_remote")
        result = simple_subscription.update(self.client, old_state)
        # Verify PUT was called
        put_calls = [call for call in respx_mock.calls if call.request.method == "PUT"]
        assert len(put_calls) == 1
        assert result is not None

        req = respx_mock.calls.last.request
        body = json.loads(req.content)

        # Verify request body structure
        assert body == {
            "eventType": "Manual",
            "status": "Active",
            "description": "Testing subscription",
            "displayName": "Basic Test Subscription",
            "matchingPattern": {
                "eventType": "Manual",
                "filter": "Body.Message eq 'Test'"
            },
            "id": {
                "scope": "test",
                "code": "basic_sub"
            }
        }

        assert result["scope"] == "test"
        assert result["code"] == "basic_sub"
        # Verify version hashes are included
        assert "source_version" in result
        assert "remote_version" in result

    def test_cannot_update_if_scope_changes(self, respx_mock, simple_subscription):
        old_state = SimpleNamespace(
            scope="different_scope",
            code="basic_sub",
            source_version="different_source",
            remote_version="different_remote")

        error_message = "Cannot change the scope on an existing subscription"
        with pytest.raises(RuntimeError, match=error_message):
            simple_subscription.update(self.client, old_state)

    def test_cannot_update_if_code_changes(self, respx_mock, simple_subscription):
        old_state = SimpleNamespace(
            scope="test",
            code="different_code",
            source_version="different_source",
            remote_version="different_remote")

        error_message = "Cannot change the code on an existing subscription"
        with pytest.raises(RuntimeError, match=error_message):
            simple_subscription.update(self.client, old_state)

    def test_delete_subscription(self, respx_mock):
        respx_mock.delete(
            "/notification/api/subscriptions/test/basic_sub"
        ).mock(return_value=httpx.Response(200))
        client = self.client
        old_state = SimpleNamespace(scope="test", code="basic_sub")
        notifications.SubscriptionResource.delete(client, old_state)
        assert respx_mock.calls.last.request.method == "DELETE"

    def test_delete_subscription_not_found(self, respx_mock):
        """Test delete handles 404 gracefully."""
        respx_mock.delete(
            "/notification/api/subscriptions/test/basic_sub"
        ).mock(return_value=httpx.Response(404))

        # Create a client without automatic error raising for this specific test
        client_no_raise = httpx.Client(base_url=TEST_BASE)
        old_state = SimpleNamespace(scope="test", code="basic_sub")

        # Should not raise an error for 404
        notifications.SubscriptionResource.delete(client_no_raise, old_state)

    def test_deps(self):
        user = identity.UserResource(
            id="user",
            login="match",
            first_name="Jess",
            last_name="Blofeldt",
            email_address="jess@blo.com",
            type=identity.UserType.SERVICE,
        )

        sut = notifications.SubscriptionResource(
            id="testId",
            scope="test",
            code="basic_sub",
            display_name="Basic Test Subscription",
            description="Testing subscription",
            event_type="Manual",
            status=notifications.SubscriptionStatus.ACTIVE,
            filter="Body.Message eq 'Test'",
            use_as_auth=user
        )

        assert sut.deps() == [user]

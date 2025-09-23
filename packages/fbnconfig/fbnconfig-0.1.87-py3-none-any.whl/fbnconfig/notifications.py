from __future__ import annotations

import json
from hashlib import sha256
from typing import Any, Dict, List, Union

import httpx
from pydantic import BaseModel, Field, computed_field

from fbnconfig.identity import UserRef, UserResource

from .resource_abc import CamelAlias, Ref, Resource, register_resource


class SubscriptionStatus:
    ACTIVE = "Active"
    INACTIVE = "Inactive"


@register_resource()
class SubscriptionRef(BaseModel, Ref):
    """
    Reference to a subscription resource.

    Example
    ----------
    >>> from fbnconfig import subscription
    >>> subscription.SubscriptionRef(
    ...  id="subscription-ref",
    ...  scope="myScope",
    ...  code="mySubscription")

    Attributes
    ----------
    id : str
         Resource identifier.
    scope : str
        Scope of the subscription.
    code: str
        Code of the subscription.
    """

    id: str = Field(exclude=True)
    scope: str
    code: str

    def attach(self, client):
        """Attach to an existing subscription resource."""
        try:
            client.get(f"/notification/api/subscriptions/{self.scope}/{self.code}")
        except httpx.HTTPStatusError as ex:
            if ex.response.status_code == 404:
                raise RuntimeError(f"Subscription {self.scope}/{self.code} does not exist")
            else:
                raise ex


@register_resource()
class SubscriptionResource(CamelAlias, BaseModel, Resource):
    """Subscription resource"""

    id: str = Field(exclude=True)
    scope: str = Field(exclude=True, init=True)
    code: str = Field(exclude=True, init=True)

    filter: str | None = Field(default=None, exclude=True)
    event_type: str
    status: str = Field(default=SubscriptionStatus.ACTIVE)
    description: str | None = None
    display_name: str
    use_as_auth: UserResource | UserRef | None = None

    @computed_field
    def matching_pattern(self) -> Dict[str, Any]:
        """Compute the matching pattern for the subscription."""
        pattern = {"eventType": self.event_type}
        if self.filter:
            pattern["filter"] = self.filter
        return pattern

    @computed_field(alias="id")
    def resource_id(self) -> dict[str, str]:
        return {"scope": self.scope, "code": self.code}

    def __get_content_hash__(self) -> str:
        dump = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        return sha256(json.dumps(dump, sort_keys=True).encode()).hexdigest()

    def read(self, client: httpx.Client, old_state) -> Dict[str, Any]:
        response = client.get(f"/notification/api/subscriptions/{old_state.scope}/{old_state.code}")
        result = response.json()
        # Remove read-only fields
        result.pop("href", None)
        result.pop("createdAt", None)
        result.pop("userIdCreated", None)
        result.pop("modifiedAt", None)
        result.pop("userIdModified", None)
        return result

    def create(self, client: httpx.Client) -> Dict[str, Any]:
        body = self.model_dump(mode="json", exclude_none=True, by_alias=True)

        response = client.post("/notification/api/subscriptions", json=body)
        result = response.json()

        # Remove read-only fields
        result.pop("href", None)
        result.pop("createdAt", None)
        result.pop("userIdCreated", None)
        result.pop("modifiedAt", None)
        result.pop("userIdModified", None)

        # Calculate version hashes - convert to string for hashability
        source_version = self.__get_content_hash__()
        remote_version = sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()

        return {
            "scope": self.scope,
            "code": self.code,
            "source_version": source_version,
            "remote_version": remote_version
        }

    def update(self, client: httpx.Client, old_state) -> Union[None, Dict[str, Any]]:
        if old_state.code != self.code:
            raise (RuntimeError("Cannot change the code on an existing subscription"))

        if old_state.scope != self.scope:
            raise (RuntimeError("Cannot change the scope on an existing subscription"))

        # Check if source version changed - convert to string for hashability
        source_hash = self.__get_content_hash__()
        remote = self.read(client, old_state)
        remote_hash = sha256(json.dumps(remote, sort_keys=True).encode()).hexdigest()

        if remote_hash == old_state.remote_version and source_hash == old_state.source_version:
            return None

        body = self.model_dump(mode="json", exclude_none=True, by_alias=True)

        scope = self.scope
        code = self.code

        response = client.put(f"/notification/api/subscriptions/{scope}/{code}", json=body)
        result = response.json()

        # Remove read-only fields
        result.pop("href", None)
        result.pop("createdAt", None)
        result.pop("userIdCreated", None)
        result.pop("modifiedAt", None)
        result.pop("userIdModified", None)

        return {
            "scope": scope,
            "code": code,
            "source_version": self.__get_content_hash__(),
            "remote_version": sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()
        }

    @staticmethod
    def delete(client: httpx.Client, old_state) -> None:
        client.delete(f"/notification/api/subscriptions/{old_state.scope}/{old_state.code}")

    def deps(self) -> List:
        """Dependencies."""
        return [self.use_as_auth] if self.use_as_auth else []

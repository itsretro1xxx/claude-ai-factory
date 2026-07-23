"""Worker 5: Publisher.

Pushes a product + listing copy live on Etsy. Printful/Printify can sync
directly to a connected Etsy shop from their own dashboards (no code
needed for that path); this module instead calls the Etsy Open API v3
directly for programmatic control, per the room README's "or via the Etsy
API directly for more control" option.

Requires ETSY_API_KEY (app keystring), ETSY_ACCESS_TOKEN (OAuth 2.0 token
with listings_w scope), and ETSY_SHOP_ID. Etsy's OAuth flow is not
implemented here — obtain a token via Etsy's standard OAuth 2.0 PKCE flow
first: https://developer.etsy.com/documentation/essentials/authentication

Etsy Open API v3 listings: https://developer.etsy.com/documentation/reference#tag/ShopListing
"""

from dataclasses import dataclass

import requests

from .config import ETSY_API_KEY, ETSY_ACCESS_TOKEN, ETSY_SHOP_ID
from .listing import ListingCopy

ETSY_API_BASE = "https://openapi.etsy.com/v3/application"


@dataclass(frozen=True)
class PublishResult:
    listing_id: int
    state: str


class Publisher:
    def __init__(self, api_key: str | None = None, access_token: str | None = None, shop_id: str | None = None):
        self.api_key = api_key or ETSY_API_KEY
        self.access_token = access_token or ETSY_ACCESS_TOKEN
        self.shop_id = shop_id or ETSY_SHOP_ID
        missing = [
            name
            for name, val in [
                ("ETSY_API_KEY", self.api_key),
                ("ETSY_ACCESS_TOKEN", self.access_token),
                ("ETSY_SHOP_ID", self.shop_id),
            ]
            if not val
        ]
        if missing:
            raise RuntimeError(
                f"Missing Etsy credentials: {', '.join(missing)}. Set up an Etsy app, "
                "complete the OAuth 2.0 flow to get an access token, and set these in "
                "your environment (see .env.example) before publishing."
            )

    def _headers(self) -> dict:
        return {
            "x-api-key": self.api_key,
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def publish_draft_listing(self, listing: ListingCopy, quantity: int = 999, taxonomy_id: int = 0) -> PublishResult:
        """Create a draft Etsy listing from generated copy.

        Created as `state: draft` intentionally — the room README calls for
        "a lightweight review/approval gate before anything goes public"
        (see ROADMAP.md Phase 3). Publish the draft manually in Etsy Shop
        Manager, or extend this with an explicit approval step before
        calling the Etsy "update listing" endpoint to set state=active.
        """
        response = requests.post(
            f"{ETSY_API_BASE}/shops/{self.shop_id}/listings",
            headers=self._headers(),
            json={
                "quantity": quantity,
                "title": listing.title,
                "description": listing.description,
                "price": listing.price_usd,
                "who_made": "i_did",
                "when_made": "made_to_order",
                "taxonomy_id": taxonomy_id,
                "tags": listing.tags,
                "state": "draft",
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return PublishResult(listing_id=data["listing_id"], state=data["state"])

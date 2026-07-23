"""Worker 3: Product/mockup builder.

Applies a rendered design image to product mockups via the Printful API
(Printful and Printify both provide a mockup generator + Etsy sync; this
module targets Printful's API since it's the more commonly used of the two
— swap the endpoint/payload shape if using Printify instead).

Requires PRINTFUL_API_KEY (Printful Developer account) and a rendered image
URL for the design (the output of feeding `design.image_prompt` from
design.py into an image-generation tool — not done here).

Printful mockup generator API: https://developers.printful.com/docs/#tag/Mockup-Generator-API
"""

from dataclasses import dataclass
import time

import requests

from .config import PRINTFUL_API_KEY

PRINTFUL_API_BASE = "https://api.printful.com"


@dataclass(frozen=True)
class MockupResult:
    product_id: int
    variant_ids: list
    mockup_urls: list


class MockupBuilder:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or PRINTFUL_API_KEY
        if not self.api_key:
            raise RuntimeError(
                "PRINTFUL_API_KEY is not set. Create a Printful account, generate an "
                "API key (Settings > Stores > API), and set it in your environment "
                "(see .env.example) before building mockups."
            )

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def build(self, product_id: int, variant_ids: list, image_url: str, poll_interval: float = 2.0, timeout: float = 60.0) -> MockupResult:
        """Submit a mockup generation task and poll until it completes.

        `product_id` and `variant_ids` come from Printful's catalog API
        (GET /products, GET /products/{id}) — pick these once per product
        type (t-shirt, mug, poster, ...) you plan to offer.
        """
        create_resp = requests.post(
            f"{PRINTFUL_API_BASE}/mockup-generator/create-task/{product_id}",
            headers=self._headers(),
            json={
                "variant_ids": variant_ids,
                "files": [{"placement": "front", "image_url": image_url}],
            },
            timeout=30,
        )
        create_resp.raise_for_status()
        task_key = create_resp.json()["result"]["task_key"]

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            status_resp = requests.get(
                f"{PRINTFUL_API_BASE}/mockup-generator/task",
                headers=self._headers(),
                params={"task_key": task_key},
                timeout=30,
            )
            status_resp.raise_for_status()
            result = status_resp.json()["result"]
            if result["status"] == "completed":
                mockup_urls = [m["mockup_url"] for m in result.get("mockups", [])]
                return MockupResult(product_id=product_id, variant_ids=variant_ids, mockup_urls=mockup_urls)
            if result["status"] == "failed":
                raise RuntimeError(f"Printful mockup task failed: {result}")
            time.sleep(poll_interval)

        raise TimeoutError(f"Printful mockup task {task_key} did not complete within {timeout}s")

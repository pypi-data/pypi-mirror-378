from __future__ import annotations
from typing import Dict, Any, Optional
from ..types import CreatePaymentRequest


class Payments:
    def __init__(self, client: Any, business_id: str):
        self.client = client
        self.business_id = business_id
        self.base_url = client.payments_base_url

    async def create(self, data: CreatePaymentRequest) -> Dict[str, Any]:
        return await self.client.request("POST", f"/v1/businesses/{self.business_id}/payments", data=data.__dict__, base_url=self.base_url)

    async def list(
        self, search_string: Optional[str] = None, page_size: Optional[int] = None, page_number: Optional[int] = None
    ) -> Dict[str, Any]:
        params = {}
        if search_string:
            params["searchString"] = search_string
        if page_size:
            params["PageSize"] = str(page_size)
        if page_number:
            params["PageNumber"] = str(page_number)
        return await self.client.request(
            "GET", f"/v1/businesses/{self.business_id}/payments", params=params, base_url=self.base_url)

    async def get(self, payment_id: str) -> Dict[str, Any]:
        return await self.client.request(
            "GET", f"/v1/businesses/{self.business_id}/payments/{payment_id}", base_url=self.base_url)

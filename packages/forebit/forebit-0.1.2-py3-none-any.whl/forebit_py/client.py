from __future__ import annotations
import aiohttp
from typing import Dict, Any, cast
from .exceptions import ForebitAPIError, ForebitAuthError
from .resources.payments import Payments
from .resources.customers import Customers
from .resources.wallets import Wallets


class ForebitClient:
    def __init__(self, api_key: str, business_id: str):
        self.api_key = api_key
        self.business_id = business_id
        self.payments_base_url = "https://prod-payments-api.forebit.io"
        self.wallet_base_url = "https://prod-wallet-api.forebit.io"
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        self.public_session = aiohttp.ClientSession(
            headers={"Content-Type": "application/json"}
        )
        self.payments = Payments(self, business_id)
        self.customers = Customers(self, business_id)
        self.wallets = Wallets(self)

    async def request(
        self,
        method: str,
        endpoint: str,
        data: Dict[str, Any] | None = None,
        params: Dict[str, Any] | None = None,
        auth_required: bool = True,
        base_url: str | None = None,
    ) -> Dict[str, Any]:
        if base_url is None:
            base_url = self.payments_base_url
        url = f"{base_url}{endpoint}"
        session = self.session if auth_required else self.public_session
        async with session.request(method, url, json=data, params=params) as response:
            if response.status >= 400:
                if response.status == 401:
                    raise ForebitAuthError("Authentication failed")
                raise ForebitAPIError(
                    f"API error: {await response.text()}", response.status
                )
            return cast(Dict[str, Any], await response.json())

    async def close(self):
        await self.session.close()
        await self.public_session.close()

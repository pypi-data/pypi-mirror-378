from __future__ import annotations
from typing import Optional, List
from ..types import Wallet, WalletAccountListResponse, DepositAddress


class Wallets:
    def __init__(self, client):
        self.client = client

    async def list(self, include_deleted: Optional[bool] = None) -> List[Wallet]:
        query = {}
        if include_deleted is not None:
            query['IsDeletedFilter'] = str(not include_deleted).lower()
        else:
            # Default to excluding deleted wallets
            query['IsDeletedFilter'] = 'false'
        return await self.client.request('GET', '/api/wallets', params=query)

    async def list_accounts(
        self,
        wallet_id: str,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
    ) -> WalletAccountListResponse:
        query = {}
        if page_size:
            query['pageSize'] = str(page_size)
        if page_number:
            query['pageNumber'] = str(page_number)
        return await self.client.request('GET', f'/api/wallets/{wallet_id}/accounts', params=query)

    async def list_deposit_addresses(
        self,
        wallet_id: str,
        account_id: str,
        has_balance: Optional[bool] = None,
        is_used: Optional[bool] = None,
    ) -> List[DepositAddress]:
        query = {}
        if has_balance is not None:
            query['hasBalance'] = str(has_balance).lower()
        if is_used is not None:
            query['isUsed'] = str(is_used).lower()
        return await self.client.request('GET', f'/api/wallets/{wallet_id}/accounts/{account_id}/addresses', params=query)

    async def get_deposit_address(self, wallet_id: str, account_id: str) -> DepositAddress:
        return await self.client.request('GET', f'/api/wallets/{wallet_id}/accounts/{account_id}/deposit-address')

    async def create_deposit_address(self, wallet_id: str, account_id: str) -> DepositAddress:
        return await self.client.request(
            'GET',
            f'/api/wallets/{wallet_id}/accounts/{account_id}/deposit-address',
            params={'createNew': 'true'},
        )

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from typing_extensions import Literal


CryptoCode = Literal[
    "BITCOIN",
    "LITECOIN",
    "ETH_TETHER",
    "ETH_USD_COIN",
    "ETHEREUM",
    "TRON",
    "TRX_TETHER",
    "TRX_USD_C",
    "SOL_TETHER",
    "SOL_USD_COIN",
    "SOLANA",
]


@dataclass
class CreatePaymentRequest:
    amount: float
    currency: str
    name: str
    description: Optional[str] = None
    redirectUrl: Optional[str] = None
    notifyUrl: Optional[str] = None
    customerEmail: Optional[str] = None
    paymentMethods: Optional[Dict[str, List[CryptoCode]]] = None


@dataclass
class CreatePaymentResponseData:
    url: str
    id: str


@dataclass
class CreatePaymentResponse:
    data: CreatePaymentResponseData
    message: str


@dataclass
class ForebitCryptoCharge:
    amount: float
    coinName: str
    exchangeRate: float
    isUnderpaid: bool
    address: str
    walletName: Optional[str] = None


@dataclass
class IpAddress:
    city: str
    ip: str
    country: str
    riskScore: float
    connectionType: str
    isp: str
    dateCreated: str


@dataclass
class Customer:
    id: int
    email: str
    ipAddresses: List[IpAddress]


@dataclass
class TimelineEntry:
    time: str
    paymentStatus: str


@dataclass
class Payment:
    id: str
    description: str
    endAmount: float
    currency: str
    status: str
    createdAt: str
    selectedPaymentMethod: str
    name: Optional[str] = None
    prePaymentAmount: Optional[float] = None
    expiresAt: Optional[str] = None
    timeline: Optional[List[TimelineEntry]] = None
    customer: Optional[Customer] = None
    forebitCryptoCharge: Optional[ForebitCryptoCharge] = None
    forebitFee: Optional[float] = None
    onBehalfOfBusinessId: Optional[int] = None
    netAmountUsd: Optional[float] = None
    customerEmail: Optional[str] = None


@dataclass
class PaymentListResponse:
    data: List[Payment]
    message: str


@dataclass
class PaymentResponse:
    data: Payment


@dataclass
class CustomerStat:
    id: int
    email: str
    totalPayments: int
    totalSpend: float
    firstSeen: str
    lastPayment: Optional[str] = None
    ipAddresses: Optional[List[IpAddress]] = None


@dataclass
class CustomerListResponse:
    data: List[CustomerStat]
    message: str


@dataclass
class CustomerResponse:
    data: CustomerStat
    message: str


@dataclass
class WalletToken:
    symbol: str
    balance: float
    usdValue: float


@dataclass
class WalletAccount:
    id: str
    blockchainNetwork: str
    name: str
    index: int
    freshAddressIndex: int
    nativeBalance: float
    isFavorite: bool
    createdAt: str
    tokens: List[WalletToken]
    allocation: float
    isStale: bool
    notes: Optional[str] = None


@dataclass
class WalletAccountListResponse:
    items: List[WalletAccount]
    pageIndex: int
    totalPages: int
    hasPreviousPage: bool
    hasNextPage: bool


@dataclass
class DepositAddress:
    id: str
    addressValue: str
    createdAt: str
    walletName: Optional[str] = None
    balance: Optional[float] = None
    isUsed: Optional[bool] = None
    reservedUntil: Optional[str] = None
    hasBalance: Optional[bool] = None
    index: Optional[int] = None
    isStale: Optional[bool] = None
    tokens: Optional[List[Any]] = None


@dataclass
class Wallet:
    id: str
    name: str
    isActivated: bool
    isDeleted: bool
    dateCreated: str
    permissions: List[str]

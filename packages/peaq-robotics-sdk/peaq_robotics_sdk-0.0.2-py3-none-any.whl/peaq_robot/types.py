"""
Shared types for Peaq Robot SDK (non-breaking, internal use)

These types improve readability and maintainability without changing
public method names or call structures.
"""

from typing import TypedDict, Dict, Any, Optional, List, Union, Awaitable, Callable
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class ReadStatus(TypedDict, total=False):
    read_status: str
    exists: bool
    note: str
    error: str


class IdentityDecodedDoc(TypedDict, total=False):
    id: str
    controller: str
    verificationMethods: List[Dict[str, Any]]
    authentications: List[str]
    services: List[Dict[str, Any]]
    signature: Optional[Dict[str, Any]]


class IdentityReadResult(ReadStatus, total=False):
    did_account: str
    name: str
    value: str
    decoded_data: Optional[IdentityDecodedDoc]
    validity: Union[int, str]
    created: Union[int, str]


class StorageReadResult(ReadStatus, total=False):
    account: str
    data_type: str
    data: Union[str, Dict[str, Any]]
    raw: str


class RoleReadResult(ReadStatus, total=False):
    role_name: str
    role_id: str
    data: Union[str, Dict[str, Any]]


# Transaction status and options
class TransactionStatus(str, Enum):
    BROADCAST = 'BROADCAST'
    IN_BLOCK = 'IN_BLOCK'
    FINALIZED = 'FINALIZED'


class ConfirmationMode(str, Enum):
    FAST = 'FAST'
    FINAL = 'FINAL'


class TransactionStatusCallback(BaseModel):
    status: TransactionStatus
    confirmation_mode: ConfirmationMode = Field(alias="confirmationMode")
    total_confirmations: int = Field(alias="totalConfirmations")
    hash: str
    receipt: Optional[dict] = None
    nonce: Optional[int] = None

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


class TxOptions(BaseModel):
    mode: Optional[ConfirmationMode] = None
    confirmations: Optional[int] = None  # kept for parity; not used on Substrate

    def model_post_init(self, __context) -> None:
        if self.mode is None:
            self.mode = ConfirmationMode.FAST


StatusCallback = Callable[[TransactionStatusCallback], None]


class SubstrateSendResult(BaseModel):
    tx_hash: str = Field(alias="txHash")
    unsubscribe: Optional[Callable[[], None]] = None
    finalize: Optional[Awaitable[Any]] = None

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)



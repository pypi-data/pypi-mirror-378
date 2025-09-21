"""
Peaq Robot SDK - Wallet Module

Handles blockchain connections, transactions, and wallet operations.
"""

from typing import Dict, Any, Optional, Awaitable, Union
from substrateinterface.base import SubstrateInterface
from substrateinterface.keypair import Keypair
from .utils.config import resolve_network_url
from .types import (
    TxOptions,
    TransactionStatus,
    ConfirmationMode,
    TransactionStatusCallback,
    StatusCallback,
    SubstrateSendResult,
)


class TransactionFailedError(Exception):
    """Raised when a submitted extrinsic is finalized with failure."""
    def __init__(self, message: str, extrinsic_hash: Optional[str] = None, details: Optional[str] = None):
        super().__init__(message)
        self.extrinsic_hash = extrinsic_hash
        self.details = details


class RobotWallet:
    """Robot wallet for blockchain transactions."""
    
    def __init__(self, network_url: str):
        """
        Initialize wallet connection.
        
        Args:
            network_url (str): Blockchain network endpoint
        """
        resolved = resolve_network_url(network_url)
        self.network_url = resolved
        self.client = SubstrateInterface(url=resolved)
    
    def get_balance(self, address: str) -> float:
        """
        Get wallet balance.
        
        Args:
            address (str): Wallet address
            
        Returns:
            float: Balance in AGUNG tokens
        """
        try:
            balance_info = self.client.query('System', 'Account', [address])
            if balance_info.value:
                return balance_info.value['data']['free'] / 10**18
            return 0.0
        except Exception:
            return 0.0
    
    def send_transaction(
        self, 
        module: str, 
        function: str, 
        params: Dict[str, Any], 
        keypair: Keypair,
        tx_options: Optional[TxOptions] = None,
        on_status: Optional[StatusCallback] = None,
    ) -> Union[SubstrateSendResult, str]:
        """
        Send blockchain transaction.
        
        Args:
            module (str): Blockchain module name
            function (str): Function name 
            params (dict): Function parameters
            keypair (Keypair): Signing keypair
            
        Returns:
            str: Transaction hash
            
        Raises:
            Exception: If transaction fails
        """
        try:
            call = self.client.compose_call(
                call_module=module,
                call_function=function,
                call_params=params
            )

            extrinsic = self.client.create_signed_extrinsic(
                call=call,
                keypair=keypair
            )

            receipt = self.client.submit_extrinsic(
                extrinsic=extrinsic,
                wait_for_finalization=True
            )
            
            # Emit BROADCAST status (hash known from extrinsic)
            tx_hash = getattr(receipt, 'extrinsic_hash', None)
            if on_status and tx_hash:
                on_status(TransactionStatusCallback(
                    status=TransactionStatus.BROADCAST,
                    confirmationMode=(tx_options.mode if tx_options else ConfirmationMode.FAST),
                    totalConfirmations=0,
                    hash=tx_hash,
                    nonce=None,
                ))

            # Try to detect chain-level failure after finalization
            is_success = getattr(receipt, 'is_success', None)
            if is_success is False:
                # Extract best-effort error details
                error_msg = getattr(receipt, 'error_message', None)
                details = None
                if not error_msg:
                    try:
                        events = getattr(receipt, 'triggered_events', []) or []
                        for ev in events:
                            try:
                                value = getattr(ev, 'value', {}) or {}
                                if value.get('event_id') == 'ExtrinsicFailed':
                                    details = str(value)
                                    break
                            except Exception:
                                continue
                    except Exception:
                        pass
                raise TransactionFailedError(error_msg or "Extrinsic failed", extrinsic_hash=tx_hash, details=details)

            if not tx_hash:
                # Fallback in unexpected cases
                raise TransactionFailedError("Missing extrinsic hash after submission")

            # Emit IN_BLOCK status (we already waited for finalization; keep parity)
            if on_status:
                on_status(TransactionStatusCallback(
                    status=TransactionStatus.IN_BLOCK,
                    confirmationMode=(tx_options.mode if tx_options else ConfirmationMode.FAST),
                    totalConfirmations=1,
                    hash=tx_hash,
                    receipt=getattr(receipt, '__dict__', None),
                    nonce=None,
                ))

            # Confirmation handling (Substrate):
            # FAST: return immediately with tx_hash string for backwards compat
            # FINAL: emit FINALIZED and return structured result
            mode = tx_options.mode if tx_options else ConfirmationMode.FAST
            if mode == ConfirmationMode.FAST:
                return tx_hash

            # FINAL: finalize result object
            if on_status:
                on_status(TransactionStatusCallback(
                    status=TransactionStatus.FINALIZED,
                    confirmationMode=ConfirmationMode.FINAL,
                    totalConfirmations=1,
                    hash=tx_hash,
                    receipt=getattr(receipt, '__dict__', None),
                    nonce=None,
                ))

            async def _finalize() -> dict:
                # Already finalized; return cleaned dict
                return getattr(receipt, '__dict__', {})

            return SubstrateSendResult(txHash=tx_hash, unsubscribe=None, finalize=_finalize())

        except TransactionFailedError:
            raise
        except Exception as e:
            # Wrap any unexpected client/composition errors consistently
            raise TransactionFailedError(f"Transaction error: {e}")
    
    def close(self):
        """Close blockchain connection."""
        if hasattr(self.client, 'close'):
            self.client.close()